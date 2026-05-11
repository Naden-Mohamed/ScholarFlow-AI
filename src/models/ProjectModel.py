from .BaseDataModel import BaseDataModel
from .db_schemas.project import Project
from .Enums.DataBaseEnum import DataBaseEnums
from src.models.Enums import DataBaseEnum

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client = db_client)
        self.collection = self.db_client[DataBaseEnums.DATABASE_NAME.value][DataBaseEnums.PROJECTS_COLLECTION.value]

    # Static method to create an instance of ProjectModel asynchronously since __init__ can't be async 
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client=db_client) # Call the constructor __init__
        await instance.init_collection()
        return instance


    # Initialize collection if not found and it's indexes
    async def init_collection(self):
        all_collections = await self.db_client[DataBaseEnums.DATABASE_NAME.value].list_collection_names()
        if DataBaseEnums.PROJECTS_COLLECTION.value not in all_collections:
            self.collection = self.db_client[DataBaseEnums.DATABASE_NAME.value][DataBaseEnums.PROJECTS_COLLECTION.value]

        indexes = Project.get_indexes()
        for index in indexes:
            await self.collection.create_index(
                    index["key"],
                    name = index["name"],
                    unique=index["unique"]
            )


    async def create_project(self, project:Project):

        result = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))

# In Pydantic, by_alias and exclude_unset are parameters used when exporting a Pydantic model to a dictionary or JSON string
# by_alias Purpose: This boolean parameter controls whether field aliases should be used as keys in the resulting dictionary or JSON.
   
# exclude_unset Purpose: This boolean parameter controls whether fields that were not explicitly set when the model instance was created, 
# and thus retain their default values, should be excluded from the resulting dictionary or JSON.

        project.id = result.inserted_id
        return project
    
    async def get_project_or_create_one(self, project_id):
        existing_project = await self.collection.find_one({"project_id": project_id})

        if existing_project is None:
            project = Project(_id = None, project_id=project_id) # How does _id val supposed to be assigned
            project = await self.create_project(project=project)
            return project
        
        return Project(**existing_project)   

    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        total_documents = await self.collection.count_documents({})

        total_pages = total_documents // page_size
        if total_documents % page_size != 0:
            total_pages += 1

        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size) # Pagination logic: skip and limit
        projects = []
        async for document in cursor:
            projects.append(Project(**document))
        return projects, total_pages   
    
