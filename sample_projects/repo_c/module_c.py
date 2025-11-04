from repo_a.module_a import process_user

def transform_user_data(user_id: int):
    processed = process_user(user_id)
    return {
        "user_id": user_id,
        "data": processed
    }

def cache_user_data(user_id: int):
    return transform_user_data(user_id)
