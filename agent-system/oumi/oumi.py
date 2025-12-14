from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = FastAPI()

class FailurePayload(BaseModel):
    repository: str
    workflow: str
    job: str
    logs: str

# Load model
tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-135M-Instruct")
model = AutoModelForCausalLM.from_pretrained("HuggingFaceTB/SmolLM2-135M-Instruct")

@app.post("/analyze")
def analyze_failure(payload: FailurePayload):
    print("Received payload:", payload)
    prompt = f"Analyze this CI/CD log and explain failure:\n{payload.logs}"
    inputs = tokenizer(prompt, return_tensors="pt")
    output = model.generate(**inputs, max_new_tokens=200)
    analysis = tokenizer.decode(output[0], skip_special_tokens=True)
    print(analysis)
    return {"analysis": analysis}
