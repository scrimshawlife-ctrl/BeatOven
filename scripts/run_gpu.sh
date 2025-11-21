#!/bin/bash
# BeatOven GPU Run Script
# Starts the API server with GPU acceleration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting BeatOven with GPU Acceleration${NC}"
echo "========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required${NC}"
    exit 1
fi

# Set PYTHONPATH
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# GPU Detection
echo -e "${YELLOW}Detecting GPU...${NC}"

# Check for NVIDIA GPU
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}NVIDIA GPU detected:${NC}"
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
    export BEATOVEN_DEVICE="cuda"
# Check for Apple Silicon
elif [[ "$(uname)" == "Darwin" ]] && [[ "$(uname -m)" == "arm64" ]]; then
    echo -e "${GREEN}Apple Silicon detected - using MPS${NC}"
    export BEATOVEN_DEVICE="mps"
else
    echo -e "${YELLOW}No GPU detected - falling back to CPU${NC}"
    export BEATOVEN_DEVICE="cpu"
fi

# Default configuration
HOST="${BEATOVEN_HOST:-0.0.0.0}"
PORT="${BEATOVEN_PORT:-8000}"
WORKERS="${BEATOVEN_WORKERS:-1}"

echo ""
echo "Configuration:"
echo "  Device: $BEATOVEN_DEVICE"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Workers: $WORKERS"
echo ""

# Check PyTorch CUDA availability
echo -e "${YELLOW}Checking PyTorch GPU support...${NC}"
python3 -c "
import torch
if torch.cuda.is_available():
    print(f'PyTorch CUDA: {torch.cuda.get_device_name(0)}')
    print(f'CUDA Version: {torch.version.cuda}')
elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
    print('PyTorch MPS: Available')
else:
    print('PyTorch: CPU only')
" 2>/dev/null || echo -e "${YELLOW}PyTorch not installed or GPU not available${NC}"

# Run the server
echo ""
echo -e "${GREEN}Starting GPU-accelerated server...${NC}"
echo "API docs: http://$HOST:$PORT/docs"
echo ""

python3 -m uvicorn beatoven.api.main:app \
    --host "$HOST" \
    --port "$PORT" \
    --workers "$WORKERS"
