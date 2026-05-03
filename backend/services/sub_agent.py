from services.llm import generate_response

def verify_response(response: str) -> str:
    prompt = f"""
    Improve this answer if needed and fix any mistakes:

    {response}
    """

    return generate_response(prompt)