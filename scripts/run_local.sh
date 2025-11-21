#!/bin/bash
# BeatOven Local Run Script
# Starts the API server for local development

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting BeatOven Local Server${NC}"
echo "================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ -d "$PROJECT_DIR/venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source "$PROJECT_DIR/venv/bin/activate"
fi

# Set PYTHONPATH
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Default configuration
HOST="${BEATOVEN_HOST:-0.0.0.0}"
PORT="${BEATOVEN_PORT:-8000}"
WORKERS="${BEATOVEN_WORKERS:-1}"
RELOAD="${BEATOVEN_RELOAD:-true}"

echo "Configuration:"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Workers: $WORKERS"
echo "  Auto-reload: $RELOAD"
echo ""

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"
python3 -c "import numpy; import fastapi" 2>/dev/null || {
    echo -e "${RED}Missing dependencies. Installing...${NC}"
    pip install -e "$PROJECT_DIR"
}

# Run the server
echo -e "${GREEN}Starting server...${NC}"
echo "API docs will be available at http://$HOST:$PORT/docs"
echo ""

if [ "$RELOAD" = "true" ]; then
    python3 -m uvicorn beatoven.api.main:app \
        --host "$HOST" \
        --port "$PORT" \
        --reload \
        --reload-dir "$PROJECT_DIR/beatoven"
else
    python3 -m uvicorn beatoven.api.main:app \
        --host "$HOST" \
        --port "$PORT" \
        --workers "$WORKERS"
fi
