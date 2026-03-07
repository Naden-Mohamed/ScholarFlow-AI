from .BaseDataModel import BaseDataModel
from .db_schemas.asset import Asset
from .Enums.DataBaseEnum import DataBaseEnums
from bson import ObjectId
import gridfs
import os
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
import tempfile
from controllers.ProcessController import ProcessController

class AssetModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db = self.db_client[DataBaseEnums.DATABASE_NAME.value] 
        self.collection = self.db[DataBaseEnums.ASSET_COLLECTION.value]  
        # self.fs = gridfs.GridFSBucket(self.db)

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db.list_collection_names() 
        if DataBaseEnums.ASSET_COLLECTION.value not in all_collections:
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    async def create_asset(self, asset: Asset):
        result = await self.collection.insert_one(asset.dict(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id
        return asset

    async def get_all_project_assets(self, asset_project_id: str, asset_type: str):
        records = await self.collection.find({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_type": asset_type,
        }).to_list(length=None)

        return [Asset(**record) for record in records]

    async def get_asset_record(self, asset_project_id: str, asset_id: str):
        record = await self.collection.find_one({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "_id": ObjectId(asset_id) if isinstance(asset_id, str) else asset_id,

        })

        if record:
            return Asset(**record)
        return None
    