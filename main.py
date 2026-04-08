from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from rag import hybrid_search
import requests
import json

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


# ========================================
# PROMPT TEMPLATE
# ========================================
template = """
You are a helpful bank customer service assistant for Bank Sumsel Babel.

Below is FAQ information retrieved from our database. Use it to answer the customer's question.

FAQ Information:
{reviews}

Customer Question: {question}

Instructions:
- Answer based on the FAQ information above
- If the question is unrelated to banking, say you can only help with banking topics
- If truly no relevant information exists in the FAQ, direct customer to Helpdesk at 08-222-333
- Always respond in the same language as the customer's question
- Never make up information not found in the FAQ

Answer:
"""


# ========================================
# CLI ANSWER
# ========================================
def get_answer_cli(question: str):

    docs = hybrid_search(question)

    reviews = "\n\n".join([
        f"{i+1}. {doc.page_content}"
        for i, doc in enumerate(docs)
    ])

     # ✅ Tambahkan debug ini
    print(f"\n[DEBUG] Reviews:\n{reviews[:500]}\n")

    formatted_prompt = template.format(
        reviews=reviews,
        question=question
    )

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:7b",
            "prompt": formatted_prompt,
            "stream": True
        },
        stream=True
    )

    print("\n🤖 Jawaban:\n")

    full_response = ""

    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode())
            token = data.get("response", "")

            if token:
                print(token, end="", flush=True)
                full_response += token

    print("\n")
    return full_response


# ========================================
# API ANSWER
# ========================================
def get_answer_api(question: str):

    docs = hybrid_search(question)

    reviews = "\n\n".join([
        f"{i+1}. {doc.page_content}"
        for i, doc in enumerate(docs)
    ])

    formatted_prompt = template.format(
        reviews=reviews,
        question=question
    )

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:7b",
            "prompt": formatted_prompt,
            "stream": True
        },
        stream=True
    )

    def stream():

        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode())
                token = data.get("response", "")

                if token:
                    yield token

    return StreamingResponse(stream(), media_type="text/plain")


# ========================================
# API CHAT
# ========================================
@app.post("/chat")
def chat(request: ChatRequest):
    return get_answer_api(request.message)


# ========================================
# CLI MODE
# ========================================
def main():

    print("=" * 50)
    print("🏦 Bank Sumsel Babel Helpdesk AI")
    print("=" * 50)

    while True:

        try:
            user_input = input("Anda: ")

            if user_input.lower() in ["exit", "quit"]:
                break

            get_answer_cli(user_input)

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()