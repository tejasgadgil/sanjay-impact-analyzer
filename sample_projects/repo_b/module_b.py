from repo_a.module_a import get_user_data

def validate_user(user_id: int):
    data = get_user_data(user_id)
    return data.get("id") == user_id

def send_notification(user_id: int):
    if validate_user(user_id):
        return f"Notification sent to user {user_id}"
    return "Invalid user"
