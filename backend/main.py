import asyncio
import json
import time
import os
import re
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import config

app = FastAPI(title="Second Brain Semantic Agent")

# Allow CORS for the local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics Storage (Simulating Prometheus metrics in memory for dashboard)
metrics_store = {
    "total_requests": 0,
    "last_ttft_ms": 0,
    "last_tps": 0.0,
    "cpu_usage_pct": 0, # simulated
    "ram_usage_mb": 0   # simulated
}

class NoteRequest(BaseModel):
    content: str
    
# Try to load llama-cpp-python, fallback to Emulator if model doesn't exist
try:
    if not os.path.exists(config.MODEL_PATH):
        raise FileNotFoundError
    from llama_cpp import Llama
    print(f"Loading GGUF model from {config.MODEL_PATH}...")
    llm = Llama(
        model_path=config.MODEL_PATH,
        n_ctx=config.N_CTX,
        n_threads=config.N_THREADS,
        n_gpu_layers=config.N_GPU_LAYERS,
        verbose=False
    )
    USE_EMULATOR = False
except Exception as e:
    print(f"⚠️ Model not found or failed to load. Using High-Fidelity Emulator Mode.")
    print(f"Error: {e}")
    USE_EMULATOR = True

def _emulate_semantic_analysis(content: str):
    """
    Analyzes markdown and generates a realistic JSON response for demonstration.
    """
    content_lower = content.lower()
    
    # Simple heuristics to generate tags and categories
    tags = []
    category = "General/Uncategorized"
    links = []
    
    if "docker" in content_lower or "kubernetes" in content_lower:
        tags.extend(["#devops", "#infrastructure"])
        category = "Engineering/DevOps"
        links.extend(["[[Docker Architecture]]", "[[Containerization]]"])
    elif "python" in content_lower or "fastapi" in content_lower:
        tags.extend(["#python", "#backend"])
        category = "Engineering/Backend"
        links.extend(["[[Python Best Practices]]", "[[API Design]]"])
    elif "machine learning" in content_lower or "llm" in content_lower or "ai" in content_lower:
        tags.extend(["#ai", "#machine-learning", "#llms"])
        category = "Research/AI"
        links.extend(["[[LLM Architecture]]", "[[Prompt Engineering]]"])
    elif "meeting" in content_lower or "sync" in content_lower:
        tags.extend(["#meeting-notes", "#team"])
        category = "Meetings/2023"
        links.extend(["[[Action Items]]", "[[Project Syncs]]"])
    else:
        tags.extend(["#notes", "#draft"])
        category = "Inbox"
        links.extend(["[[Daily Journal]]"])
        
    summary = "A brief markdown note capturing recent thoughts or information."
    if len(content) > 20:
        summary = "Notes regarding: " + " ".join(content.split()[:10]) + "..."
        
    result_dict = {
        "semantic_tags": list(set(tags)),
        "folder_category": category,
        "suggested_backlinks": list(set(links)),
        "brief_summary": summary
    }
    
    return json.dumps(result_dict, indent=2)

async def _stream_emulator(text_to_stream: str):
    """Simulates LLM token streaming"""
    start_time = time.time()
    first_token_time = None
    token_count = 0
    
    chunk_size = 3
    for i in range(0, len(text_to_stream), chunk_size):
        chunk = text_to_stream[i:i+chunk_size]
        await asyncio.sleep(0.015) # Emulate latency ~20 tokens/sec
        
        if not first_token_time:
            first_token_time = time.time()
            
        token_count += 1
        yield f"data: {json.dumps({'text': chunk})}\n\n"
        
    end_time = time.time()
    
    # Update metrics
    if first_token_time:
        metrics_store["last_ttft_ms"] = int((first_token_time - start_time) * 1000)
    
    generation_time = end_time - (first_token_time or start_time)
    if generation_time > 0:
        metrics_store["last_tps"] = round(token_count / generation_time, 2)
        
    metrics_store["total_requests"] += 1
    yield "data: [DONE]\n\n"

@app.post("/analyze")
async def analyze_note(req: NoteRequest):
    """
    Receives markdown content and streams back semantic analysis JSON.
    """
    if USE_EMULATOR:
        output_json = _emulate_semantic_analysis(req.content)
        return StreamingResponse(_stream_emulator(output_json), media_type="text/event-stream")
        
    # Actual GGUF streaming
    prompt = f"<|im_start|>system\n{config.SYSTEM_PROMPT}<|im_end|>\n<|im_start|>user\n{req.content}<|im_end|>\n<|im_start|>assistant\n"
    
    def llm_generator():
        start_time = time.time()
        first_token_time = None
        token_count = 0
        
        stream = llm(
            prompt,
            max_tokens=config.MAX_TOKENS,
            temperature=config.TEMPERATURE,
            stream=True
        )
        
        for output in stream:
            if not first_token_time:
                first_token_time = time.time()
            
            chunk = output["choices"][0]["text"]
            token_count += 1
            yield f"data: {json.dumps({'text': chunk})}\n\n"
            
        end_time = time.time()
        
        if first_token_time:
            metrics_store["last_ttft_ms"] = int((first_token_time - start_time) * 1000)
        generation_time = end_time - (first_token_time or start_time)
        if generation_time > 0:
            metrics_store["last_tps"] = round(token_count / generation_time, 2)
            
        metrics_store["total_requests"] += 1
        yield "data: [DONE]\n\n"

    return StreamingResponse(llm_generator(), media_type="text/event-stream")

@app.get("/metrics")
async def get_metrics():
    """Returns real-time performance metrics."""
    # Simulate some resource usage variations
    metrics_store["cpu_usage_pct"] = 40 + (int(time.time()) % 20)
    metrics_store["ram_usage_mb"] = 1024 + (int(time.time()) % 100)
    return metrics_store
