from .BaseDataModel import BaseDataModel
from .db_schemas.data_chunk import DataChunk
from .Enums.DataBaseEnum import DataBaseEnums
from bson.objectid import ObjectId
from pymongo import InsertOne

class  DataChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client = db_client)
        self.db = self.db_client[DataBaseEnums.DATABASE_NAME.value] 
        self.collection = self.db[DataBaseEnums.DATA_CHUNKS_COLLECTION.value]  
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client=db_client) # Call the constructor __init__
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db.list_collection_names() 
        if DataBaseEnums.DATA_CHUNKS_COLLECTION.value not in all_collections:
            indexes = DataChunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    async def create_chunk(self, chunk:DataChunk):

        result = await self.collection.insert_one(chunk.dict())
        chunk.id = result.inserted_id
        return chunk
    async def get_chunk_by_id(self, chunk_id: str):
        chunk = await self.collection.find_one({"_id": ObjectId(chunk_id)})

        if chunk is None:
            return None
        
        return DataChunk(**chunk)

    async def insert_many_chunks(self, patch_size: int = 100, chunks: list = []):
        for i in range(0, len(chunks), patch_size):
            batch = chunks[i:i + patch_size]
            operations = [InsertOne(chunk.dict()) for chunk in batch]
            await self.collection.bulk_write(operations) # Bulk write instead of insert many for efficiency

        return len(chunks)

    async def get_chunks_by_project_id(self, project_id: ObjectId, page_num: int = 1, page_size: int = 10):
        records = await self.collection.find({"chunk_project_id": project_id}).skip((page_num - 1) * page_size).limit(page_size).to_list(length=None)
        return [DataChunk(**record) for record in records]
    
    async def delete_chunk_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return result.deleted_count
