# LLM-Powered Intelligent Query-Retrieval System

A comprehensive system that uses Large Language Models to process natural language queries and retrieve relevant information from large unstructured documents such as policy documents, contracts, and emails.

## ⁺₊✧ Features

- **Multi-format Document Processing**: Supports PDFs, DOCX, and email documents
- **Semantic Search**: Uses FAISS and sentence transformers for intelligent document retrieval
- **LLM Integration**: Supports Llama 3 and DeepSeek-R1 models via Ollama
- **RESTful API**: FastAPI-based API with authentication and rate limiting
- **Production Ready**: Includes monitoring, caching, and optimization features
- **Scalable Architecture**: Modular design with containerization support

## 🗒 Requirements

- Python 3.11+
- PostgreSQL 12+
- Ollama (for LLM models)
- Docker (optional, for containerized deployment)

## 🛠 Installation

### Quick Start (Docker)

```bash
# Clone the repository
git clone <repository-url>
cd hackrx-system

# Start all services
docker-compose up -d

# Pull required models
docker exec -it hackrx-system_ollama_1 ollama pull llama3
docker exec -it hackrx-system_ollama_1 ollama pull deepseek-r1

# Test the API
curl -X GET http://localhost:8000/health
```

### Manual Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install and start Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve

# Pull models
ollama pull llama3
ollama pull deepseek-r1

# Setup PostgreSQL
sudo -u postgres createdb hackrx_db

# Run database migrations
python database/migrate.py

# Start the application
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Configuration

Create a `.env` file in the root directory:

```env
API_TOKEN=DEFINE_YOUR_OWN_TOKEN
DATABASE_URL=postgresql://user:password@localhost:5432/hackrx_db
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
MAX_TOKENS=4000
TEMPERATURE=0.1
```

## 📖 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
All requests require a Bearer token in the Authorization header:
```
Authorization: Bearer API_TOKEN
```

### Endpoints

#### POST /hackrx/run
Process natural language queries against documents.

**Request:**
```json
{
    "documents": "https://example.com/policy.pdf",
    "questions": [
        "What is the grace period for premium payment?",
        "What are the coverage limits?"
    ]
}
```

**Response:**
```json
{
    "answers": [
        "The grace period for premium payment is 30 days...",
        "The coverage limits vary based on the plan..."
    ]
}
```

#### GET /health
Health check endpoint.

**Response:**
```json
{
    "status": "healthy",
    "version": "1.0.0"
}
```

## Testing

### Unit Tests
```bash
python -m pytest tests/ -v
```

### API Testing
```bash
python test_api.py
```

### Load Testing
```bash
python load_test.py --url http://localhost:8000 --token YOUR_TOKEN --users 10 --requests 5
```

## 📊 Performance Monitoring

### System Metrics
```bash
python monitor.py
```

### Performance Reports
The system automatically logs performance metrics to `performance.log` and the database.

### Batch Processing
```bash
python batch_processor.py
```

## 🚀 Deployment

### Google Cloud Platform

1. **Setup GCP Project**
```bash
gcloud projects create hackrx-system
gcloud config set project hackrx-system
```

2. **Deploy to Cloud Run**
```bash
gcloud builds submit --tag gcr.io/hackrx-system/api
gcloud run deploy hackrx-api --image gcr.io/hackrx-system/api --platform managed
```

3. **Setup Cloud SQL**
```bash
gcloud sql instances create hackrx-db --database-version=POSTGRES_13
gcloud sql databases create hackrx --instance=hackrx-db
```

### Manual Production Deployment

```bash
# Use the deployment script
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

## 🔍 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client API    │───▶│   FastAPI App   │───▶│  Query Processor │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                        ┌─────────────────┐            ▼
                        │   PostgreSQL    │    ┌─────────────────┐
                        │    Database     │◀───│Document Processor│
                        └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐            ▼
│     Ollama      │◀───│  LLM Service    │    ┌─────────────────┐
│  (Llama3/R1)    │    └─────────────────┘    │Embedding Service│
└─────────────────┘                           │   (FAISS)       │
                                               └─────────────────┘
```

## 🔧 Optimization Tips

1. **Document Processing**
   - Use smaller chunk sizes (800-1000) for better precision
   - Adjust overlap based on document structure
   - Cache processed documents for repeated queries

2. **LLM Usage**
   - Lower temperature (0.05-0.1) for consistent results
   - Limit max tokens to control costs
   - Use query caching for frequently asked questions

3. **Performance**
   - Enable query caching in production
   - Use connection pooling for database
   - Monitor system resources and scale as needed

## 🐛 Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Restart Ollama service
   ollama serve
   ```

2. **Database Connection Error**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Verify database exists
   psql -h localhost -U postgres -l
   ```

3. **Document Processing Timeout**
   - Increase timeout settings in configuration
   - Check document URL accessibility
   - Verify document format is supported

4. **Memory Issues**
   - Reduce chunk size and batch size
   - Monitor system resources
   - Consider scaling to multiple instances

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request


## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Added caching and performance optimizations
- **v1.2.0**: Enhanced error handling and monitoring

---
