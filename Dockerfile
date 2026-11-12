# Stage 1: Build the backend with native optimizations
FROM python:3.11-slim as backend

# Install build dependencies required for llama-cpp-python
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt .

# Install dependencies. (Assuming CPU environment for edge emulation)
RUN CMAKE_ARGS="-DLLAMA_BLAS=OFF" pip install --no-cache-dir -r requirements.txt

# Copy the backend source
COPY backend/ /app/

# Port for FastAPI
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
