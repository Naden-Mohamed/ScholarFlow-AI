import logging

from sentence_transformers import SentenceTransformer

from ..LLMEnums import DocumentTypeEnum
from ..LLMInterface import LLMInterface


class BGEProvider(LLMInterface):
    def __init__(
        self,
        default_input_max_characters: int = 1000,
        default_generation_max_output_tokens: int = 1000,
        default_generation_temperature: float = 0.1,
    ):

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        self.client = None

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.logger.warning("BGE models do not support text generation.")
        self.generation_model_id = None

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        # Load the model locally via sentence-transformers
        try:
            self.client = SentenceTransformer(
                model_id,
                trust_remote_code=True,  # required for BAAI/bge-multilingual-gemma2
            )
            self.logger.info(f"BGE model '{model_id}' loaded successfully.")
        except Exception as e:
            self.logger.error(f"Failed to load BGE model '{model_id}': {e}")
            self.client = None

    def process_text(self, text: str):
        if len(text) > self.default_input_max_characters:
            self.logger.warning(
                f"Input text exceeds maximum character limit of {self.default_input_max_characters}. Truncating."
            )
            return text[: self.default_input_max_characters]
        return text

    def generate_text(
        self,
        prompt: str,
        chat_history: list | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
    ):
        self.logger.error("BGE models do not support text generation.")

    # Batch Embedding
    def embed_text(self, text: str | list[str], document_type: str = ""):
        if not self.client:
            self.logger.error(
                "BGE model is not loaded. Call set_embedding_model() first."
            )
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for BGE was not set.")
            return None

        if isinstance(text, str):
            text = [text]

        try:
            text = [self.process_text(t) for t in text]

            # bge-multilingual-gemma2 uses instruction-based embedding
            # document_type differentiates query vs passage for better accuracy
            if document_type == DocumentTypeEnum.QUERY.value:
                instruction = "Represent this query for searching relevant passages: "
            else:
                instruction = "Represent this passage for retrieval: "

            embedding = self.client.encode(
                [instruction + t for t in text],
                normalize_embeddings=True,  # recommended for BGE models
            )

            if embedding is None or len(embedding) == 0:
                self.logger.error("BGE embedding returned empty result.")
                return None

            return embedding

        except Exception as e:
            self.logger.error(f"BGE embedding error: {e}")
            raise

    def construct_prompt(self, prompt: str, role: str):
        self.logger.error("BGE models do not support prompt construction.")
