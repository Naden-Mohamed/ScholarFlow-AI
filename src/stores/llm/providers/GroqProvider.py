from ..LLMInterface import LLMInterface
from ..LLMEnums import LLMEnums, GROQEnums
from groq import Groq
import logging

class GROQProvider(LLMInterface):
    def __init__(self, api_key: str,
                       default_input_max_characters: int=1000,
                       default_generation_max_output_tokens: int=1000,
                       default_generation_temperature: float=0.1):
        
        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens    
        self.default_generation_temperature = default_generation_temperature        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = Groq(api_key=self.api_key)

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        if len(text) > self.default_input_max_characters:
            self.logger.warning(f"Input text exceeds maximum character limit of {self.default_input_max_characters}. Truncating input.")
            return text[:self.default_input_max_characters]
        return text
    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                            temperature: float = None):
        if not self.generation_model_id:
            self.logger.error("GROQ client was not set")
            return None
        
        if not self.client:
            self.logger.error("GROQ client is not initialized properly.")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature
        
        chat_history.append(
            self.construct_prompt(prompt=prompt, role=GROQEnums.USER.value)
        )
        try:
            response = self.client.chat.completions.create(
                model=self.generation_model_id,
                messages=chat_history,
                max_tokens=max_output_tokens,
                temperature=temperature
            )
            if not response or not response.choices[0].message:
                self.logger.warning("GROQ generation returned empty response.")
                return ""
            
            return response.choices[0].message
        
        except Exception as e:
            self.logger.error(f"GROQ generation error: {e}")
            raise

    def embed_text(self, text: str, document_type: str = None):
        
        if not self.client:
            self.logger.error("GROQ client was not set")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for GROQ was not set")
            return None
        
        response = self.client.embeddings.create(
            model = self.embedding_model_id,
            input = text,
        )

        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Error while embedding text with GROQ")
            return None

        return response.data[0].embedding

    def construct_prompt(self, prompt: str, role: str):
        if role == GROQEnums.SYSTEM.value:
            return f"<system>{prompt}</system>"
        elif role == GROQEnums.USER.value:
            return f"<user>{prompt}</user>"
        elif role == GROQEnums.ASSISTANT.value:
            return f"<assistant>{prompt}</assistant>"
        else:
            raise ValueError(f"Unsupported role: {role}")