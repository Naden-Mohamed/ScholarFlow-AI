from .LLMEnums import LLMEnums
from .providers.BGEProvider import BGEProvider
from .providers.GroqProvider import GROQProvider


class LLMProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider_type: str):
        if provider_type == LLMEnums.GROQ.value:
            return GROQProvider(
                api_key=self.config.GROQ_API_KEY,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
            )
        if provider_type == LLMEnums.BGE.value:
            return BGEProvider(
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
            )

        raise ValueError(f"Unsupported provider type: {provider_type}")
