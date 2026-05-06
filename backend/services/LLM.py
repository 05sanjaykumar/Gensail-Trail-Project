from config import GROQ_API_KEY, LLM_MODEL
from pipecat.services.groq import GroqLLMService
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair

def get_llm_service():
    return GroqLLMService(
        api_key=GROQ_API_KEY,
        settings=GroqLLMService.Settings(
            model=LLM_MODEL,
            temperature=0.7,
            max_completion_tokens=1024,
        ),
    )

def get_llm_context():
    context = LLMContext(
        messages=[{
            "role": "system",
            "content": (
                "You are a helpful, concise voice assistant for Gensail. "
                "Keep all responses short and conversational — max 2-3 sentences. "
                "Never use markdown, bullet points, or formatting in responses."
            )
        }]
    )
    llm = get_llm_service()
    return llm.create_context_aggregator(context)