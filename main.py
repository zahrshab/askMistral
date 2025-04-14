from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class PromptInput(BaseModel):
    prompt: str

@app.post("/ask")
def ask_model(input: PromptInput):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",  
            "prompt": input.prompt,
            "stream": False
        }
    )
    result = response.json()
    return {"response": result["response"]}