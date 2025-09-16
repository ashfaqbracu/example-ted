import requests
import json
from typing import Optional, List, Dict, Any, Tuple
from app.core.config import API_BASE_URL


def fetch_expense_data(user_id: str = None) -> Optional[Dict[str, Any]]:
    """Fetch expense data from the API for a specific user"""
    try:
        headers = {
            "Content-Type": "application/json"
        }
        
        # If user_id is provided, fetch user-specific data
        if user_id and user_id.strip():
            url = f"{API_BASE_URL}/report/monthly"
            params = {"userId": user_id.strip()}
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 404:
                return None
            elif response.status_code != 200:
                return None
                
            try:
                data = response.json()
            except json.JSONDecodeError:
                return None
            
            if not isinstance(data, dict):
                return None
                
            return data
        else:
            # Return None if no user_id is provided since the API requires it
            print("No user_id provided for expense data fetch. User-specific data required.")
            return None
        
    except Exception:
        return None


def fetch_user_specific_expense_data(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch user-specific expense data from the external API
    This function specifically handles user-based data collection for the RAG system
    """
    if not user_id or not user_id.strip():
        print("Debug: Empty user_id provided")
        return None
    
    # First validate that the user exists before fetching expense data
    print(f"🔍 Debug: Validating user existence for: {user_id.strip()}")
    is_valid_user, validated_user_id = validate_user_exists(user_id.strip())
    
    if not is_valid_user:
        print(f"Debug: User validation failed for: {user_id.strip()}")
        return None
        
    try:
        headers = {
            "Content-Type": "application/json"
        }
        
        # Primary endpoint - this is the one that works
        primary_url = f"{API_BASE_URL}/report/monthly?userId={validated_user_id}"
        print(f"🔍 Debug: Trying primary URL with validated user: {primary_url}")
        
        try:
            response = requests.get(primary_url, headers=headers, timeout=30)
            print(f"🔍 Debug: Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"🔍 Debug: Got JSON data, type: {type(data)}")
                    print(f"🔍 Debug: Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    if isinstance(data, dict) and data:  # Valid non-empty data
                        print(f"Debug: Valid data found with {len(data)} keys for user {validated_user_id}")
                        return data
                    else:
                        print("Debug: Data is empty or not a dict")
                        return None
                except json.JSONDecodeError as e:
                    print(f"Debug: JSON decode error: {str(e)}")
                    return None
            elif response.status_code == 404:
                print("Debug: 404 - User not found in expense data")
                return None
            else:
                print(f"Debug: Unexpected status code: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Debug: Request exception: {str(e)}")
            return None
        
        # If we reach here, the primary endpoint failed
        print("Debug: Primary endpoint failed, no fallback needed")
        return None
        
    except Exception as e:
        print(f"Debug: General exception: {str(e)}")
        return None


def validate_user_exists(user_id: str) -> Tuple[bool, str]:
    """
    Validate if a user exists by checking with the API
    Returns: (is_valid_user, actual_user_id_from_response)
    """
    if not user_id or not user_id.strip():
        return False, ""
        
    try:
        # First, try to get user info or validate user existence
        headers = {
            "Content-Type": "application/json"
        }
        url = f"{API_BASE_URL}/history/get-history"
        params = {"userId": user_id.strip()}
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                if isinstance(response_data, list):
                    # User exists and has history or empty history
                    return True, user_id.strip()
                else:
                    return False, ""
            except json.JSONDecodeError:
                return False, ""
        elif response.status_code == 404:
            # User not found
            return False, ""
        elif response.status_code == 400:
            # Bad request - invalid user_id format
            return False, ""
        else:
            # For other status codes, treat as invalid user
            return False, ""
            
    except Exception:
        return False, ""


def fetch_chat_history_for_validated_user(user_id: str) -> List[Dict[str, Any]]:
    """
    Fetch chat history only for already validated users
    This assumes the user_id has already been validated
    """
    try:
        headers = {
            "Content-Type": "application/json"
        }
        url = f"{API_BASE_URL}/history/get-history"
        params = {"userId": user_id}
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            try:
                history_data = response.json()
                if isinstance(history_data, list):
                    return history_data
            except json.JSONDecodeError:
                pass
        
        return []
            
    except Exception:
        return []


def fetch_chat_history(user_id: str) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Fetch previous chat history from the API
    Returns: (chat_history, is_valid_user)
    """
    if not user_id or not user_id.strip():
        return [], False
        
    try:
        headers = {
            "Content-Type": "application/json"
        }
        url = f"{API_BASE_URL}/history/get-history"
        params = {"userId": user_id.strip()}
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            try:
                history_data = response.json()
                if isinstance(history_data, list):
                    return history_data, True
                else:
                    # Invalid response format
                    return [], False
            except json.JSONDecodeError:
                # Invalid JSON response
                return [], False
        elif response.status_code == 404:
            # User not found - invalid user_id
            return [], False
        elif response.status_code == 400:
            # Bad request - likely invalid user_id format
            return [], False
        else:
            # For other status codes (500, 503, etc.), treat as invalid user
            return [], False
            
    except requests.exceptions.RequestException:
        # Network error - treat as invalid user to be safe
        return [], False
    except Exception:
        # Any other error - treat as invalid user
        return [], False


def validate_and_send_to_history(user_message: str, assistant_response: str, user_id: str) -> bool:
    """
    Validate user and send chat interaction to history API only if user is valid
    """
    if not user_message or not assistant_response or not user_id or not user_id.strip():
        return False
    
    # First validate the user exists
    is_valid, validated_user_id = validate_user_exists(user_id.strip())
    if not is_valid:
        return False
        
    try:
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "userId": validated_user_id,
            "human": str(user_message).strip(),
            "assistant": str(assistant_response).strip()
        }
        url = f"{API_BASE_URL}/history/create-history"
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code in [200, 201]:
            return True
        return False
            
    except Exception:
        return False


def send_to_history(user_message: str, assistant_response: str, user_id: str) -> bool:
    """Send the chat interaction to the history API (legacy function - use validate_and_send_to_history instead)"""
    if not user_message or not assistant_response or not user_id or not user_id.strip():
        return False
        
    try:
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "userId": user_id.strip(),
            "human": str(user_message).strip(),
            "assistant": str(assistant_response).strip()
        }
        url = f"{API_BASE_URL}/history/create-history"
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code in [200, 201]:
            return True
        return False
            
    except Exception:
        return False
