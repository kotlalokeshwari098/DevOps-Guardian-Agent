from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import logging
logger = logging.getLogger(__name__)

app = FastAPI()

class FailurePayload(BaseModel):
    repository: str
    workflow: str
    job: str
    logs: str

# Load model
try:
    tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-135M-Instruct")
    model = AutoModelForCausalLM.from_pretrained("HuggingFaceTB/SmolLM2-135M-Instruct")
except Exception as e:
    raise RuntimeError(f"Failed to load model: {e}")

@app.post("/analyze")
def analyze_failure(payload: FailurePayload):
    try:
        logger.info(f"Analyzing logs for {payload.repository}/{payload.workflow}/{payload.job}")
        truncated_logs = payload.logs[:1000]
        
        prompt = f"""
            You are an expert CI/CD assistant. Analyze the following logs and provide:

            1. **Summary**: What happened.
            2. **Root Cause**: The main reason the job failed.
            3. **Suggested Action**: Commands or steps the developer should take to fix the issue.

            CI/CD logs:
            {truncated_logs}
        """
    
        inputs = tokenizer(prompt, return_tensors="pt")
        output = model.generate(**inputs, max_new_tokens=200)
        full_output = tokenizer.decode(output[0], skip_special_tokens=True)

        analysis = full_output[len(prompt):].strip()
        logger.info("Analysis completed successfully")
        return {"analysis": analysis}
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return {"analysis": "Error analyzing logs", "error": str(e)}
