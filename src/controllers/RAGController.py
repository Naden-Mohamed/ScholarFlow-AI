from .BaseController import BaseController
from models import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum, GROQEnums
from utils.metrics import RAG_EMPTY_RETRIEVAL, RAG_TOP_SCORE
from typing import List
import json

class RAGController(BaseController):

    def __init__(self, vectordb_client, generation_client, 
                 embedding_client,template_parser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser


    def create_collection_name(self, project_id: str):
        return f"collection_{self.vectordb_client.default_vector_size}_{project_id}".strip()
    
    async def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=str(project.project_id))
        return await self.vectordb_client.delete_collection(collection_name=collection_name)
    
    async def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=str(project.project_id))
        collection_info = await self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )
    
    async def insert_into_vectordb(self, project: Project, data_chunks: List[DataChunk], chunks_ids: List[int], do_reset: int = 0):
        collection_name = self.create_collection_name(project_id=str(project.project_id))

        texts = [chunk.chunk_text for chunk in data_chunks]
        embedding_size = 1024  # for BGE models, embedding size is fixed and determined by the model, so we can set it as a constant here
        metadata = [chunk.chunk_metadata for chunk in data_chunks]
        vectors = [
            self.embedding_client.embed_text(text=text, document_type=DocumentTypeEnum.DOCUMENT.value)
            for text in texts
        ]

        # step3: create collection if not exists
        _ = await self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=embedding_size,
            do_reset=do_reset,
        )



        # step4: insert into vector db
        _ = await self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadata,
            vectors=vectors,
            record_ids=chunks_ids,
            batch_size=100
        )

        return True
    

    async def search_vector_db_collection(self, project: Project, text: str, limit: int = 3):

        collection_name = self.create_collection_name(project_id=str(project.project_id))

        vector = self.embedding_client.embed_text(text=text, 
                                                 document_type=DocumentTypeEnum.QUERY.value)

        if not vector.any() or len(vector) == 0:
            RAG_EMPTY_RETRIEVAL.inc()
            return False

        results = await self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )

        if not results:
            RAG_EMPTY_RETRIEVAL.inc()
            return False

        RAG_TOP_SCORE.observe(results[0].score)

        return results
    
    async def answer_rag_question(self, project: Project, query: str, limit: int = 10):
        
        answer, full_prompt, chat_history = None, None, None

        # step1: retrieve related documents
        retrieved_documents = await self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit,
        )

        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer, full_prompt, chat_history
        
        # step2: Construct LLM prompt
        system_prompt = self.template_parser.get("prompts", "system_prompt")

        documents_prompts = "\n".join([
            self.template_parser.get("prompts", "document_prompt", {
                    "doc_num": idx + 1,
                    "chunk_text": doc.text if hasattr(doc, "text") else doc.payload.get("text", "No content available"),
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get("prompts", "footer_prompt")

        # step3: Construct Generation Client Prompts
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=GROQEnums.SYSTEM.value,
            )
        ]

        full_prompt = "\n\n".join([ documents_prompts,  footer_prompt])

        # step4: Retrieve the Answer
        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )
        return answer, full_prompt, chat_history