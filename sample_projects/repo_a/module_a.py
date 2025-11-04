"""
Sample Module A
Provides core functionality for user data processing
"""

def get_user_data(user_id: int):
    """Fetch user data from database"""
    return {
        "id": user_id,
        "name": "John Doe",
        "email": "john@example.com",
        "role": "admin"
    }

def process_user(user_id: int):
    """Process user data"""
    data = get_user_data(user_id)
    return {
        "user": data,
        "processed_at": "2024-01-01"
    }
