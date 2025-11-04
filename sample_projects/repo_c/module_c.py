"""
Sample Module C
Transforms user data for API responses
"""

def transform_user_data(user_id: int):
    """Transform user data to API format"""
    # Would import: from repo_a.module_a import process_user
    return {
        "user_id": user_id,
        "data": {}
    }

def cache_user_data(user_id: int):
    """Cache transformed data"""
    return transform_user_data(user_id)
