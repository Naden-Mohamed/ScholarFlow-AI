import json 
from controllers.RAGController import RAGController
from helpers.config import get_settings
from helpers.bootstrap import build_clients

async def evaluate_rag(top_k:int = 5):

    _, _, generation_client, embedding_client, vectordb_client, template_parser = await build_clients()
    dataset_path = get_settings().TEST_SET_PATH

    with open(dataset_path) as f:
        qa_pairs = json.load(f)

    retrieval_results, generation_samples = [], []

    for pair in qa_pairs:
        project_id = pair["project_id"]
        rag_controller = RAGController(vectordb_client,generation_client,embedding_client,template_parser)

        retrieved = await rag_controller.search_vector_db_collection(project=project_id,text=pair["query"],limit=top_k)
        answer = await rag_controller.answer_rag_question(project=project_id, query=pair["query"],limit=top_k)

        retrieval_results.append({"target_id": pair["id"], "retrieved_ids": [str(d.id) for d in retrieved]})
        generation_samples.append({
            "query": pair["query"],
            "answer": answer,
            "contexts": [d.text for d in retrieved],
            "ground_truth": pair["ground_truth_answer"],
        })
    return retrieval_results, generation_samples

