# GLM-OCR Suite
# GPU-accelerated OCR with Streamlit UI and FastAPI server

FROM nvidia/cuda:12.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install PyTorch with CUDA support
RUN pip3 install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install latest transformers for GLM-OCR support
RUN pip3 install --no-cache-dir --upgrade git+https://github.com/huggingface/transformers.git

# Copy application code
COPY . .

# Expose ports: 8508 for API, 8501 for Streamlit
EXPOSE 8508 8501

# Health check for the API server
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8508/ || exit 1

# Default: run the FastAPI server
CMD ["python3", "server.py"]
