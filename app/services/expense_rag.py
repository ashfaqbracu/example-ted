import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleExpenseRAG:
    def __init__(self, api_base_url: str, openai_api_key: str = None):
        """
        Initialize the RAG system with API connection
        Args:
            api_base_url: Base URL for the API
            openai_api_key: Your OpenAI API key (or set OPENAI_API_KEY env var)
        """
        # Set up OpenAI client
        api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY env var or pass it directly.")
        
        # Validate API key format (basic check)
        if not self._validate_api_key_format(api_key):
            raise ValueError("OpenAI API key appears to be invalid format. It should start with 'sk-' and be 51+ characters.")
        
        # Store the API key for potential error messaging
        self.openai_api_key = api_key
        
        try:
            self.client = openai.OpenAI(api_key=api_key)
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenAI client: {str(e)}")
        
        # API configuration
        self.api_base_url = api_base_url
        
        # Initialize memory for current conversation
        self.current_conversation = []
        self.chat_history = []
        
        # Load initial data
        self.expense_data = None
        self.processed_chunks = []

    def _validate_api_key_format(self, api_key: str) -> bool:
        """Basic validation of OpenAI API key format"""
        # Most OpenAI API keys start with "sk-" and are at least 51 characters long
        return isinstance(api_key, str) and api_key.startswith('sk-') and len(api_key) >= 51

    def test_openai_connection(self) -> str:
        """Test the OpenAI API connection with a simple request"""
        try:
            # Make a minimal request to test the API key
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'API connection successful!'"}
                ],
                max_tokens=15,
                temperature=0
            )
            return "Success! API connection is working."
        except Exception as e:
            error_msg = str(e)
            # Add details about the API key if it's an authentication issue
            if "invalid_api_key" in error_msg or "401" in error_msg:
                # Safely display part of the key for debugging
                key_preview = f"{self.openai_api_key[:5]}...{self.openai_api_key[-4:]}" if len(self.openai_api_key) > 10 else "[invalid format]"
                return f"API key error: {error_msg}. Key preview: {key_preview} (length: {len(self.openai_api_key)})"
            return f"Error testing API connection: {error_msg}"

    def set_expense_data(self, expense_data):
        """Set expense data from external source"""
        self.expense_data = expense_data
        if self.expense_data:
            self.processed_chunks = self._process_data()
            print(f"Loaded {len(self.processed_chunks)} expense data chunks")
        else:
            self.processed_chunks = []
            self.expense_data = None
            print("No expense data provided - will work with empty data")

    def reset_conversation_state(self):
        """Reset conversation state for a new user session"""
        self.current_conversation = []
        self.chat_history = []
        self.expense_data = None
        self.processed_chunks = []

    def load_chat_history(self, chat_history_data=None):
        """Load chat history from external source or API"""
        if chat_history_data:
            self.chat_history = chat_history_data
            print(f"Loaded {len(self.chat_history)} previous conversations")
        else:
            self.chat_history = []

    def load_user_chat_history(self, user_id: str):
        """Load chat history for a specific user after validating they exist"""
        from app.core.utils import validate_user_exists, fetch_chat_history_for_validated_user
        
        if not user_id or not user_id.strip():
            raise ValueError("Invalid user_id: User ID cannot be empty")
        
        # First validate the user exists
        is_valid_user, validated_user_id = validate_user_exists(user_id.strip())
        
        if not is_valid_user:
            raise ValueError(f"Invalid user_id: {user_id}. User not found.")
        
        try:
            # Fetch chat history for the validated user
            chat_history = fetch_chat_history_for_validated_user(validated_user_id)
            self.chat_history = chat_history
            print(f"Loaded {len(chat_history)} chat history entries for user {validated_user_id}")
            return validated_user_id
        except Exception as e:
            print(f"Error loading chat history for user {user_id}: {str(e)}")
            raise ValueError(f"Invalid user_id: {user_id}. Unable to load chat history.")

    def _process_data(self) -> List[Dict]:
        """Process expense data into searchable chunks"""
        chunks = []
        
        # Process daily transactions
        if 'daily' in self.expense_data:
            for day in self.expense_data['daily']:
                transactions = day['transactions']
                date = day['_id']
                total_income = sum([t['amount'] for t in transactions if t['transactionType'] == 'income'])
                total_expenses = sum([t['amount'] for t in transactions if t['transactionType'] == 'expense'])
                
                text = f"Date: {date}\n"
                text += f"Income: ${total_income:.2f}, Expenses: ${total_expenses:.2f}, Net: ${total_income - total_expenses:.2f}\n"
                text += "Transactions:\n"
                for t in transactions:
                    text += f"- {t['transactionType']}: ${t['amount']:.2f} - {t.get('description', 'N/A')}\n"
                
                chunks.append({
                    'type': 'daily',
                    'date': date,
                    'text': text,
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'net': total_income - total_expenses
                })

        # Process weekly summaries
        if 'weekly' in self.expense_data:
            for week in self.expense_data['weekly']:
                transactions = week['transactions']
                total_income = sum([t['amount'] for t in transactions if t['transactionType'] == 'income'])
                total_expenses = sum([t['amount'] for t in transactions if t['transactionType'] == 'expense'])
                
                text = f"Week: {week['weekStartDate']} to {week['weekEndDate']}\n"
                text += f"Income: ${total_income:.2f}, Expenses: ${total_expenses:.2f}\n"
                text += f"Net: ${total_income - total_expenses:.2f}\n"
                
                chunks.append({
                    'type': 'weekly',
                    'period': week['_id'],
                    'text': text,
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'net': total_income - total_expenses
                })

        # Process monthly summaries
        if 'monthly' in self.expense_data:
            for month in self.expense_data['monthly']:
                transactions = month['transactions']
                total_income = sum([t['amount'] for t in transactions if t['transactionType'] == 'income'])
                total_expenses = sum([t['amount'] for t in transactions if t['transactionType'] == 'expense'])
                
                text = f"Month: {month['_id']}\n"
                text += f"Income: ${total_income:.2f}, Expenses: ${total_expenses:.2f}\n"
                text += f"Net: ${total_income - total_expenses:.2f}\n"
                
                chunks.append({
                    'type': 'monthly',
                    'period': month['_id'],
                    'text': text,
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'net': total_income - total_expenses
                })

        return chunks

    def _simple_search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Simple keyword-based search for relevant expense data
        NOTE: Currently not used as we send ALL data in context instead of chunking
        Kept for potential future use if selective data becomes necessary
        """
        query_lower = query.lower()
        scored_chunks = []
        
        for chunk in self.processed_chunks:
            score = 0
            text_lower = chunk['text'].lower()
            
            # Simple keyword matching
            query_words = query_lower.split()
            for word in query_words:
                if word in text_lower:
                    score += text_lower.count(word)
            
            # Boost score based on query type
            if 'daily' in query_lower and chunk['type'] == 'daily':
                score += 5
            elif 'weekly' in query_lower and chunk['type'] == 'weekly':
                score += 5
            elif 'monthly' in query_lower and chunk['type'] == 'monthly':
                score += 5
                
            if score > 0:
                scored_chunks.append((score, chunk))
        
        # Sort by score and return top results
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        return [chunk for _, chunk in scored_chunks[:n_results]]

    def _build_context(self, query: str) -> str:
        """Build context from expense data and conversation history"""
        context_parts = []
        
        # Add ALL expense data instead of just relevant chunks
        if self.processed_chunks:
            context_parts.append("=== ALL EXPENSE DATA ===")
            for i, chunk in enumerate(self.processed_chunks, 1):
                context_parts.append(f"Data {i} ({chunk['type']}):\n{chunk['text']}")
        
        # Add recent conversation history (last 3 exchanges)
        if self.chat_history:
            context_parts.append("\n=== PREVIOUS CONVERSATIONS ===")
            recent_history = self.chat_history[-3:]  # Last 3 conversations
            for i, conv in enumerate(recent_history, 1):
                context_parts.append(f"Previous {i}:")
                context_parts.append(f"Human: {conv.get('human', '')}")
                context_parts.append(f"Assistant: {conv.get('assistant', '')}")
        
        # Add current conversation memory
        if self.current_conversation:
            context_parts.append("\n=== CURRENT CONVERSATION ===")
            for i, (human_msg, ai_msg) in enumerate(self.current_conversation, 1):
                context_parts.append(f"Exchange {i}:")
                context_parts.append(f"Human: {human_msg}")
                context_parts.append(f"Assistant: {ai_msg}")
        
        return "\n".join(context_parts)

    def chat(self, user_query: str, user_id: str = None) -> Tuple[str, str]:
        """
        Main chat function with RAG implementation
        Returns: (assistant_response, validated_user_id)
        """
        
        # Note: Don't clear current_conversation here - it should persist during the chat session
        # Only clear when starting a new user session via reset_conversation_state()
        
        # Validate and load user-specific chat history if user_id is provided
        validated_user_id = ""
        if user_id:
            if not user_id.strip():
                raise ValueError("Invalid user_id: User ID cannot be empty")
            
            # This will raise ValueError if user doesn't exist and return validated user_id
            validated_user_id = self.load_user_chat_history(user_id.strip())
        else:
            # If no user_id provided, use empty chat history
            self.chat_history = []
        
        # Build context from data and conversation history
        context = self._build_context(user_query)
        
        # Create prompt template
        prompt_template = """Use the information from the context to answer the question at the end. If you don't know the answer based on the provided data, just say that you don't know, definitely do not try to make up an answer.

You are Teddy, a friendly and knowledgeable personal finance assistant. Use ALL the expense data and conversation history to provide helpful, specific financial advice.

{context}

Question: {question}

Guidelines:
- You have access to ALL expense data available - use it comprehensively to answer questions
- If someone asks about expenses, provide a summary of all the expenses, then ask if they specifically want to know about any particular aspect
- Use exact numbers from the expense data when available
- Be encouraging but honest about financial situations
- Provide specific recommendations based on the data
- Reference previous conversations when relevant
- If no relevant data is available, offer general financial advice
- Keep your response helpful and conversational
- If the user is engaging in normal conversation (greetings, casual chat), respond naturally and conversationally while maintaining your role as a finance assistant
"""

        # Prepare the full prompt
        full_prompt = prompt_template.format(context=context, question=user_query)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are Teddy, a helpful personal finance assistant."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            assistant_response = response.choices[0].message.content
            
            # Add to current conversation memory
            self.current_conversation.append((user_query, assistant_response))
            
            # Keep only last 5 exchanges in current conversation to manage memory
            if len(self.current_conversation) > 5:
                self.current_conversation = self.current_conversation[-5:]
            
            return assistant_response, validated_user_id
            
        except Exception as e:
            return f"Error generating response: {str(e)}", validated_user_id

    def get_data_summary(self) -> str:
        """Get a summary of available data"""
        summary = "Available Expense Data:\n\n"
        daily_count = len([c for c in self.processed_chunks if c['type'] == 'daily'])
        weekly_count = len([c for c in self.processed_chunks if c['type'] == 'weekly'])
        monthly_count = len([c for c in self.processed_chunks if c['type'] == 'monthly'])
        
        summary += f"• Daily records: {daily_count}\n"
        summary += f"• Weekly summaries: {weekly_count}\n"
        summary += f"• Monthly summaries: {monthly_count}\n"
        summary += f"• Previous conversations: {len(self.chat_history)}\n\n"
        
        # Show date ranges
        daily_dates = [c['date'] for c in self.processed_chunks if c['type'] == 'daily']
        if daily_dates:
            summary += f"Date range: {min(daily_dates)} to {max(daily_dates)}\n"
        
        return summary