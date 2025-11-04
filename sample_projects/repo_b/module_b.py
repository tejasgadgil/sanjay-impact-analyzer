"""
Sample Module B
Depends on Module A for user processing
"""
# In real code: from repo_a.module_a import get_user_data
# For simplicity in our test: importing from module_a

def validate_user(user_id: int):
    """Validate user exists and is active"""
    # Would call: data = get_user_data(user_id)
    return True

def send_notification(user_id: int):
    """Send notification to user"""
    # validate_user(user_id)
    return f"Notification sent to user {user_id}"
