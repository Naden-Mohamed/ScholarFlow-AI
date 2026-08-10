from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vector_db.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

async def build_clients():
    settings = get_settings()
    postgres_conn = (
        f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    )

    db_engine = create_async_engine(postgres_conn)
    db_client = async_sessionmaker(db_engine, expire_on_commit=False)

    llm_factory = LLMProviderFactory(settings)
    vdb_factory = VectorDBProviderFactory(config=settings, db_client=db_client)

    generation_client = llm_factory.create(provider_type=settings.GENERATION_BACKEND)
    generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    embedding_client = llm_factory.create(provider_type=settings.EMBEDDING_BACKEND)
    embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_MODEL_SIZE,
    )

    vectordb_client = vdb_factory.create(provider=settings.VECTOR_DB_BACKEND)
    await vectordb_client.connect()

    template_parser = TemplateParser(language=settings.PRIMARY_LANG, default_language=settings.DEFAULT_LANG)

    return db_engine, db_client, generation_client, embedding_client, vectordb_client, template_parser