import tempfile

from langchain_text_splitters import RecursiveCharacterTextSplitter
from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from models import ProcessingEnum
import gridfs
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from bson import ObjectId

class ProcessController(BaseController):
    def __init__(self,project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=self.project_id)

    def get_file_extension(self, file_id: str):
        return os.path.splitext(file_id)[-1].lower()
    
    def get_file_loader(self, file_id:str):
        file_ext = self.get_file_extension(file_id)
        file_path = os.path.join(self.project_path, file_id)

        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)

        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path,encoding='utf-8')

        return None

    def get_file_content(self, file_id: str):
        loader = self.get_file_loader(file_id=file_id)

        if not loader:
            raise ValueError(f"Unsupported file type for file: {file_id}")

        documents = loader.load()
        return documents

    async def load_pdf_from_mongodb(db, file_id: str):
        # 1. Download file from GridFS
        bucket = AsyncIOMotorGridFSBucket(db)
        
        # 2. Write to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_path = tmp_file.name
            await bucket.download_to_stream(
                ObjectId(file_id), 
                tmp_file
            )
        
        # 3. Load with LangChain
        try:
            loader = PyMuPDFLoader(tmp_path)
            documents = loader.load()
        finally:
            os.unlink(tmp_path)  # clean up temp file
        
        return documents



    def process_file_content(self, file_content: list,file_id: str, chunk_size: int = 100, overlap_size: int = 20):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size, 
            length_function=len
            )

        file_content_texts = [doc.page_content for doc in file_content]
        file_content_metadata = [doc.metadata for doc in file_content]

        chunks = text_splitter.create_documents(file_content_texts, metadatas=file_content_metadata)
        return chunks