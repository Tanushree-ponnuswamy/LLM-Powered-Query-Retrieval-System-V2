# LLM-Powered Intelligent Query-Retrieval System Setup

## Prerequisites

1. Python 3.11+
2. Docker and Docker Compose
3. Git

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd project
pip install -r requirements.txt
```

### 2. Start Services with Docker

```bash
# Start all services
docker-compose up -d

# Check if Ollama is running
curl http://localhost:11434/api/tags

# Pull required models
docker exec -it project_ollama_1 ollama pull llama3
docker exec -it project_ollama_1 ollama pull deepseek-r1
```

### 3. Alternative Local Setup

```bash
# Install Ollama locally
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Pull models
ollama pull llama3
ollama pull deepseek-r1

# Start PostgreSQL (if not using Docker)
sudo systemctl start postgresql

# Create database
createdb hackrx_db
```

### 4. Run the Application

```bash
# Development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Test the API

```bash
curl -X POST "http://localhost:8000/api/v1/hackrx/run" \
  -H "Authorization: Bearer 59d150e97f686fcc6859251c02b719e661203b21d4fb2eae792e07e727f07bff" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/policy.pdf",
    "questions": ["What is the grace period for premium payment?"]
  }'
```

## Deployment

### Google Cloud Platform

1. Create a new GCP project
2. Enable required APIs:
   - Cloud Run
   - Cloud SQL
   - Cloud Storage

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/hackrx-api
gcloud run deploy hackrx-api --image gcr.io/PROJECT_ID/hackrx-api --platform managed
```

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export API_TOKEN="your-token"
export DATABASE_URL="your-db-url"

# Run with gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Configuration

Edit `.env` file or set environment variables:

- `API_TOKEN`: Authentication token
- `DATABASE_URL`: PostgreSQL connection string
- `OLLAMA_BASE_URL`: Ollama server URL
- `LLM_MODEL`: Model name (llama3, deepseek-r1)
- `CHUNK_SIZE`: Document chunk size
- `TOP_K_RESULTS`: Number of similar chunks to retrieve

## Monitoring and Logs

```bash
# View application logs
tail -f app.log

# Docker logs
docker-compose logs -f app

# Health check
curl http://localhost:8000/health
```