from groq import Groq

client = Groq(api_key="GROQ_API_KEY")

def generate_response(prompt: str):
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="llama3-70b-8192"  # fast + powerful
    )

    return chat_completion.choices[0].message.content