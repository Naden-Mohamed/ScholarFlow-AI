import logging

from fastapi import APIRouter, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from tqdm.auto import tqdm

from controllers.RAGController import RAGController
from models import ResponseStatus
from models.ChunkModel import DataChunkModel
from models.ProjectModel import ProjectModel

from .schemas.data_requests import PushRequest, SearchRequest

logger = logging.getLogger("uvicorn.error")

rag_router = APIRouter(
    prefix="/api/rag",
    tags=["api", "rag"],
)


@rag_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: PushRequest):

    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )

    chunk_model = await DataChunkModel.create_instance(
        db_client=request.app.state.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseStatus.PROJECT_NOT_FOUND_ERROR.value},
        )

    rag_controller = RAGController(
        vectordb_client=request.app.state.vectordb_client,
        generation_client=request.app.state.generation_client,
        embedding_client=request.app.state.embedding_client,
        template_parser=request.app.state.template_parser,
    )

    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0

    # create collection if not exists
    collection_name = rag_controller.create_collection_name(
        project_id=str(project.project_id)
    )

    _ = await request.app.state.vectordb_client.create_collection(
        collection_name=collection_name,
        embedding_size=request.app.state.embedding_client.embedding_size,
        do_reset=push_request.do_reset,
    )

    # setup batching
    total_chunks_count = await chunk_model.get_total_chunks_count(
        project_id=str(project.project_id)
    )
    pbar = tqdm(total=total_chunks_count, desc="Vector Indexing", position=0)

    while has_records:
        page_chunks = await chunk_model.get_project_chunks(
            project_id=str(project.project_id), page_no=page_no
        )
        if len(page_chunks):
            page_no += 1

        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunks_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)

        is_inserted = await rag_controller.insert_into_vectordb(
            project=project,
            data_chunks=page_chunks,
            do_reset=push_request.do_reset,
            chunks_ids=chunks_ids,
        )

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseStatus.INSERT_INTO_VECTORDB_ERROR.value},
            )
        pbar.update(len(page_chunks))

        inserted_items_count += len(page_chunks)

    return JSONResponse(
        content={
            "signal": ResponseStatus.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count": inserted_items_count,
        }
    )


@rag_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):

    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    rag_controller = RAGController(
        vectordb_client=request.app.state.vectordb_client,
        generation_client=request.app.state.generation_client,
        embedding_client=request.app.state.embedding_client,
        template_parser=request.app.state.template_parser,
    )

    collection_info = await rag_controller.get_vector_db_collection_info(
        project=project
    )

    return JSONResponse(
        content={
            "signal": ResponseStatus.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info,
        }
    )


@rag_router.post("/index/search/{project_id}")
async def search_index(
    request: Request, project_id: str, search_request: SearchRequest
):

    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    rag_controller = RAGController(
        vectordb_client=request.app.state.vectordb_client,
        generation_client=request.app.state.generation_client,
        embedding_client=request.app.state.embedding_client,
        template_parser=request.app.state.template_parser,
    )

    results = await rag_controller.search_vector_db_collection(
        project=project, text=search_request.text, limit=search_request.limit
    )

    if not results:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseStatus.VECTORDB_SEARCH_ERROR.value},
        )

    # Use jsonable_encoder to handle the ScoredPoint objects automatically
    return JSONResponse(
        content=jsonable_encoder(
            {"signal": ResponseStatus.VECTORDB_SEARCH_SUCCESS.value, "results": results}
        )
    )


@rag_router.post("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id: str, search_request: SearchRequest):

    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    rag_controller = RAGController(
        vectordb_client=request.app.state.vectordb_client,
        generation_client=request.app.state.generation_client,
        embedding_client=request.app.state.embedding_client,
        template_parser=request.app.state.template_parser,
    )

    answer, full_prompt, chat_history = await rag_controller.answer_rag_question(
        project=project,
        query=search_request.text,
        limit=search_request.limit,
    )

    if not answer:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseStatus.RAG_ANSWER_ERROR.value},
        )

    return JSONResponse(
        content={
            "signal": ResponseStatus.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history,
        }
    )
