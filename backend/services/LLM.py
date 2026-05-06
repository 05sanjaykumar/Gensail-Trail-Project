from config import GROQ_API_KEY, LLM_MODEL
from pipecat.services.groq import GroqLLMService
from pipecat.processors.aggregators.openai_llm_context import (
    OpenAILLMContext,
    OpenAILLMContextAggregator,
)

def get_llm_service():
    return GroqLLMService(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
    )

def get_llm_context():
    context = OpenAILLMContext(
        messages=[{
            "role": "system",
            "content": (
                "You are a helpful, concise voice assistant for Gensail. "
                "Keep all responses short and conversational — max 2-3 sentences. "
                "Never use markdown, bullet points, or formatting in responses."
            )
        }]
    )
    return OpenAILLMContextAggregator(context)