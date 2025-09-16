import sys
from app.core.config import OPENAI_API_KEY
from app.services.expense_rag import SimpleExpenseRAG
from app.core.utils import fetch_expense_data
from app.core.config import API_BASE_URL


def initialize_rag_system() -> SimpleExpenseRAG:
    """Initialize the RAG system"""
    
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is not set!")
        return None
    
    try:
        # Initialize RAG system
        rag_instance = SimpleExpenseRAG(API_BASE_URL, openai_api_key=OPENAI_API_KEY)
        
        # Note: We don't load expense data at startup since it's user-specific
        # Data will be loaded when a user makes a request
        print("RAG system initialized successfully (ready for user-specific data)")
        print("Expense data will be loaded per user request")
        
        print("RAG system initialization completed")
        return rag_instance
        
    except Exception as e:
        print(f"Error initializing RAG system: {str(e)}")
        return None
