# Teddy Finance Assistant API

A FastAPI-based personal finance assistant using RAG (Retrieval-Augmented Generation) to help manage expenses.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Server

### Option 1: Using the start script
```bash
python start_server.py
```

### Option 2: Direct uvicorn command
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Base URL: `http://localhost:8000`

### 1. Health Check
- **GET** `/`
- Returns system status

### 2. System Status
- **GET** `/status`
- Returns detailed system status and data summary

### 3. Chat with Teddy
- **POST** `/chat`
- Body: `{"message": "Your question here"}`
- Returns AI response from Teddy

### 4. Data Summary
- **GET** `/data-summary`
- Returns summary of available expense data

## Usage Examples

### Using curl:
```bash
# Health check
curl http://localhost:8000/

# Chat with Teddy
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "How much did I spend last month?"}'

# Get system status
curl http://localhost:8000/status
```

### Using Python requests:
```python
import requests

# Chat with Teddy
response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "Show me my expense summary"}
)
print(response.json())
```

## Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Features

- Real-time expense data integration
- Chat history persistence
- RAG-based responses using expense data
- OpenAI GPT integration
- RESTful API design
- Automatic API documentation
