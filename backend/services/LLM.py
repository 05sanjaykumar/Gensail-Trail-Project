from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

client = Groq(api_key=GROQ_API_KEY)

def generate_response(prompt: str) -> str:
    res = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=LLM_MODEL
    )

    return res.choices[0].message.content