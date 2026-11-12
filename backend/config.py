import os

# Model Configuration
MODEL_PATH = os.getenv("MODEL_PATH", "../training/model-q4_k_m.gguf")
N_CTX = int(os.getenv("N_CTX", "2048"))
N_THREADS = int(os.getenv("N_THREADS", "4"))
N_GPU_LAYERS = int(os.getenv("N_GPU_LAYERS", "0")) # Edge devices might not have GPU

# Generation Configuration
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2")) # Low temp for structured extraction
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "512"))

# System Prompts
SYSTEM_PROMPT = """ You are a highly meticulous Semantic Agent embedded in a personal Obsidian Knowledge Vault.
Your sole purpose is to analyze unstructured Markdown notes and output a strictly valid JSON object.
Do not output any introductory or concluding text. Do not wrap in markdown code blocks. Output raw JSON only.

The JSON MUST follow this exact schema:
{
    "semantic_tags": ["list", "of", "#tags"],
    "folder_category": "Category/Subcategory",
    "suggested_backlinks": ["[[Link1]]", "[[Link2]]"],
    "brief_summary": "A concise 1-sentence summary of the note."
}
"""
