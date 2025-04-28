import openai
from app.core.config import settings

class AnswerGenerator:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    def generate_answer(self, question: str, context: str) -> str:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

answer_generator = AnswerGenerator() 