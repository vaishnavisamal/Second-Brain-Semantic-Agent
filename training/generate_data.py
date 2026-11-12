import json
import random
from pathlib import Path

# Sample Obsidian notes
NOTES = [
    {
        "content": "# Dockerizing FastAPI\nToday I learned how to dockerize a FastAPI application. The main thing is to use a python slim image, set up the working directory, copy requirements, install them with no-cache-dir, and then copy the app code. Finally, expose port 8000 and run uvicorn.\n\nHere is a snippet:\n```dockerfile\nFROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n```",
        "semantic_tags": ["#docker", "#fastapi", "#python", "#deployment"],
        "folder_category": "Engineering/Backend",
        "suggested_backlinks": ["[[Docker Basics]]", "[[FastAPI Setup]]", "[[Python Web Servers]]"],
        "brief_summary": "A guide on dockerizing a FastAPI app using a slim Python image and uvicorn."
    },
    {
        "content": "# Attention Mechanism in Transformers\nReading the 'Attention is All You Need' paper. The core idea is self-attention, computed as $Attention(Q, K, V) = softmax(QK^T / \\sqrt{d_k})V$. This allows the model to weigh the importance of different words in a sequence regardless of their positional distance, unlike RNNs which suffer from vanishing gradients over long distances.",
        "semantic_tags": ["#machine-learning", "#transformers", "#deep-learning", "#nlp"],
        "folder_category": "Research/AI",
        "suggested_backlinks": ["[[Self-Attention]]", "[[Transformer Architecture]]", "[[RNN limitations]]"],
        "brief_summary": "Notes on the attention mechanism from 'Attention is All You Need', highlighting its mathematical formulation and advantages over RNNs."
    },
    {
        "content": "# Weekly Sync - 2023-10-15\nAttendees: Alice, Bob, Charlie\n\nUpdates:\n- Alice: Finished the auth module migration to OAuth2. Need review on PR #45.\n- Bob: Working on the frontend dashboard redesign. Delay due to missing Figma assets.\n- Charlie: Investigating the database deadlock issue seen in production last night.\n\nAction Items:\n- [ ] Review Alice's PR (Bob)\n- [ ] Follow up with design team for assets (Bob)\n- [ ] Post RCA for database issue (Charlie)",
        "semantic_tags": ["#meeting-notes", "#weekly-sync", "#engineering", "#action-items"],
        "folder_category": "Meetings/2023/Q4",
        "suggested_backlinks": ["[[Auth Migration Project]]", "[[Frontend Redesign]]", "[[Production Incidents]]"],
        "brief_summary": "Weekly engineering sync covering OAuth migration, frontend redesign delays, and a production DB deadlock, with assigned action items."
    },
    {
        "content": "# Book Summary: Atomic Habits\nAuthor: James Clear\n\nKey takeaways:\n1. 1% better every day leads to massive compounding over time.\n2. Goals are about the results you want to achieve. Systems are about the processes that lead to those results.\n3. The Four Laws of Behavior Change:\n   - Make it obvious (Cue)\n   - Make it attractive (Craving)\n   - Make it easy (Response)\n   - Make it satisfying (Reward)\n\nTo break a bad habit, invert these laws.",
        "semantic_tags": ["#books", "#self-improvement", "#habits", "#productivity"],
        "folder_category": "Reading/Summaries",
        "suggested_backlinks": ["[[Systems vs Goals]]", "[[Behavioral Psychology]]", "[[James Clear]]"],
        "brief_summary": "Summary of 'Atomic Habits' emphasizing the power of 1% daily improvements and the Four Laws of Behavior Change."
    },
    {
        "content": "# Setting up Neovim for Rust\nTo get a solid Rust development environment in Neovim, you need `rust-analyzer`. \n\nI'm using `lazy.nvim` as my plugin manager. Here's my LSP config setup:\n\n```lua\nrequire(\"lspconfig\").rust_analyzer.setup {\n  settings = {\n    ['rust-analyzer'] = {\n      checkOnSave = {\n        command = \"clippy\"\n      },\n    }\n  }\n}\n```\nThis ensures clippy runs every time I save, catching potential issues early.",
        "semantic_tags": ["#neovim", "#rust", "#developer-tools", "#lsp"],
        "folder_category": "Engineering/DevEnv",
        "suggested_backlinks": ["[[Neovim Config]]", "[[Rust-Analyzer]]", "[[Lazy.nvim]]"],
        "brief_summary": "Configuring Neovim for Rust development by setting up rust-analyzer with clippy integration via lazy.nvim."
    }
]

def format_prompt(note):
    """
    Formats the prompt for the LLM to learn the instruction-following task.
    """
    instruction = "Analyze the following markdown note from an Obsidian vault. Extract semantic tags, determine an appropriate folder category, suggest relevant backlinks, and provide a 1-sentence brief summary. Output valid JSON only."
    
    input_text = note['content']
    
    output_dict = {
        "semantic_tags": note['semantic_tags'],
        "folder_category": note['folder_category'],
        "suggested_backlinks": note['suggested_backlinks'],
        "brief_summary": note['brief_summary']
    }
    
    output_text = json.dumps(output_dict, indent=2)
    
    # Using ChatML-like format
    text = f"<|im_start|>system\n{instruction}<|im_end|>\n<|im_start|>user\n{input_text}<|im_end|>\n<|im_start|>assistant\n{output_text}<|im_end|>"
    return text

def generate_dataset(num_samples=100):
    dataset = []
    # In a real scenario, we would use LLM to synthesize hundreds of variations.
    # For this script, we'll duplicate and slightly jitter the examples to create a valid dataset.
    for _ in range(num_samples):
        base_note = random.choice(NOTES)
        dataset.append({
            "text": format_prompt(base_note)
        })
    
    return dataset

if __name__ == "__main__":
    output_file = Path("dataset.jsonl")
    print(f"Generating synthetic dataset with 100 examples...")
    
    dataset = generate_dataset(100)
    
    with open(output_file, "w") as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")
            
    print(f"✅ Generated dataset saved to {output_file.absolute()}")
