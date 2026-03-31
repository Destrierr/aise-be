from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import requests
import json

app = FastAPI()

class ChatRequest(BaseModel):
    message: str


@app.post("/chat-stream")
def chat_stream(req: ChatRequest):
    print("REQUEST DARI FLUTTER:", req.message)

    def generate():
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": req.message,
                "stream": True   # 🔥 IMPORTANT
            },
            stream=True
        )

        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                token = data.get("response", "")
                yield token

    return StreamingResponse(generate(), media_type="text/plain")