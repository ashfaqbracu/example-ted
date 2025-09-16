import uvicorn
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI


# Add the parent directory to sys.path to allow imports from app package
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from app.core.config import APP_TITLE, APP_DESCRIPTION, APP_VERSION
from app.services.rag_manager import initialize_rag_system
from app.routes.chat import router as chat_router, set_rag_instance

# Load environment variables
load_dotenv()


# Initialize RAG system
rag_system = None

def startup_event():
    """Initialize services on startup"""
    global rag_system
    print("Initializing RAG system...")
    rag_system = initialize_rag_system()
    if rag_system:
        set_rag_instance(rag_system)
        print("RAG system initialized and set in chat router")
    else:
        print("Failed to initialize RAG system")

# Initialize FastAPI app
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION
)

# Call startup event
startup_event()

app.include_router(chat_router)

@app.get("/", tags=["root"])
def read_root():
    return {"message": "Welcome to Teddy Finance Assistant API!"}


def main():
    """Main entry point for the application"""
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable is not set!")
        print("Please set it in a .env file or in your environment variables.")
        api_key = input("Enter your OpenAI API key (or press Enter to exit): ").strip()
        if not api_key:
            print("No OpenAI API key provided. Exiting.")
            exit(1)
        os.environ["OPENAI_API_KEY"] = api_key
    
    print("Starting Teddy Finance Assistant API...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Interactive API: http://localhost:8000/redoc")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Change working directory to parent to ensure proper module loading
    os.chdir(str(parent_dir))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
