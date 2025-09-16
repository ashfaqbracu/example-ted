# Teddy - Personal Finance Assistant API

A FastAPI-based personal finance assistant that uses RAG (Retrieval-Augmented Generation) to help manage expenses and provide financial insights.

## Project Structure

```
expense_app-fast_api/
├── requirements.txt           # Python dependencies
├── config.py                  # Configuration file
├── expense_data_debug.json    # Debug data file
├── README_API.md             # API documentation
├── app/                      # Main application package
│   ├── __init__.py
│   ├── main.py              # 🎯 Main entry point & FastAPI app
│   ├── core/                # Core utilities and configuration
│   │   ├── __init__.py
│   │   ├── config.py        # Application configuration
│   │   └── utils.py         # Utility functions
│   ├── models/              # Pydantic schemas
│   │   ├── __init__.py
│   │   └── schemas.py       # Request/Response models
│   ├── routes/              # API routes
│   │   ├── __init__.py
│   │   ├── chat.py          # Chat endpoints
│   │   └── status.py        # Status and health check endpoints
│   └── services/            # Business logic
│       ├── __init__.py
│       ├── expense_rag.py   # RAG implementation
│       └── rag_manager.py   # RAG system initialization
```

## Features

- **RESTful API**: FastAPI-based REST API with automatic documentation
- **RAG System**: Retrieval-Augmented Generation for intelligent financial assistance
- **Chat Interface**: Conversational AI for expense management
- **Data Integration**: Fetches and processes expense data from external APIs
- **History Management**: Maintains conversation history
- **Health Monitoring**: Status endpoints for system monitoring.

## Installation

1. **Clone or download the project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Running the Application

### From App Directory (Recommended)
```bash
cd app
python main.py
```

### Alternative with Uvicorn
From the root directory:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Health Check
- **GET** `/` - Root endpoint with basic info
- **GET** `/status` - Detailed system status
- **GET** `/data-summary` - Summary of available expense data

### Chat
- **POST** `/chat` - Chat with Teddy financial assistant

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Configuration

The application configuration is centralized in `app/core/config.py`:

- **API_BASE_URL**: External API base URL for expense data
- **USER_ID**: User identifier for personalized data
- **OPENAI_API_KEY**: OpenAI API key (from environment variables)

## Architecture

### Core Components

1. **app/core/**
   - `config.py`: Centralized configuration
   - `utils.py`: Utility functions for API calls and data processing

2. **app/models/**
   - `schemas.py`: Pydantic models for request/response validation

3. **app/routes/**
   - `chat.py`: Chat-related endpoints
   - `status.py`: Status and health check endpoints

4. **app/services/**
   - `expense_rag.py`: RAG system implementation
   - `rag_manager.py`: RAG system initialization and management

### Request Flow

1. **Startup**: Application initializes RAG system and loads data
2. **Request**: Client sends request to API endpoint
3. **Processing**: Route handler processes request using services
4. **RAG**: If chat request, RAG system generates response
5. **Response**: API returns structured response

## Development

### Adding New Endpoints

1. Create route functions in appropriate files under `app/routes/`
2. Import and include routers in `app/main.py`
3. Add corresponding schemas in `app/models/schemas.py` if needed

### Adding New Services

1. Create service modules under `app/services/`
2. Import and use in route handlers
3. Add configuration variables to `app/core/config.py` if needed

## Error Handling

The application includes comprehensive error handling:
- **503 Service Unavailable**: RAG system not initialized
- **400 Bad Request**: Invalid request data
- **500 Internal Server Error**: Processing errors

## Dependencies

- **FastAPI**: Modern, fast web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation using Python type hints
- **OpenAI**: OpenAI API client
- **Requests**: HTTP library for external API calls
- **Python-dotenv**: Environment variable management

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| OPENAI_API_KEY | OpenAI API key for RAG system | Yes |

## Security

- Environment variables for sensitive data
- Request validation using Pydantic
- Error handling to prevent information leakage

## Monitoring

Use the status endpoints to monitor system health:
- `/status`: System operational status
- `/data-summary`: Data availability summary
