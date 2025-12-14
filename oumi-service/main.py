from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager

# Global variables for model and tokenizer
model = None
tokenizer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    global model, tokenizer
    try:
        base_model_id = "HuggingFaceTB/SmolLM2-135M-Instruct"
        # Absolute path to the adapter to avoid CWD issues
        adapter_path = os.path.abspath("../Finetuned Model/output")
        
        logger.info(f"Loading base model: {base_model_id}")
        tokenizer = AutoTokenizer.from_pretrained(base_model_id)
        
        # Determine device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")

        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_id,
            dtype=torch.float32, # float32 is safer for CPU
            device_map=device
        )
        
        logger.info(f"Loading adapter from: {adapter_path}")
        model = PeftModel.from_pretrained(base_model, adapter_path)
        model.eval()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
    
    yield
    
    # Shutdown logic (if any)
    model = None
    tokenizer = None

app = FastAPI(title="Oumi Agent Service", lifespan=lifespan)

class AnalyseRequest(BaseModel):
    repository: str
    workflow: str
    job: str
    logs: str

@app.get("/")
async def root():
    return {"message": "Oumi Agent Service is running"}

@app.get("/analyse")
async def analyse_info():
    return {"message": "Please use POST method to send logs for analysis."}

@app.post("/analyse")
async def analyse_logs(request: AnalyseRequest):
    logger.info(f"Received analysis request for repository: {request.repository}")
    
    if not model or not tokenizer:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Construct prompt using ChatML format
        # Truncate logs to fit in context (approx 2000 chars)
        truncated_logs = request.logs[-2000:] if len(request.logs) > 2000 else request.logs
        
        messages = [
            {"role": "system", "content": "You are a DevOps assistant. Analyze the logs and find the error."},
            {"role": "user", "content": f"Repository: {request.repository}\nWorkflow: {request.workflow}\nJob: {request.job}\n\nLogs:\n{truncated_logs}"}
        ]
        
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        input_length = inputs.input_ids.shape[1]
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.2,
                top_p=0.9,
                do_sample=True,
                repetition_penalty=1.2
            )
        
        # Decode only the generated tokens
        generated_tokens = outputs[0][input_length:]
        analysis = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

        return {
            "status": "success",
            "analysis": analysis,
            "data": {
                "repository": request.repository,
                "job": request.job
            }
        }
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
