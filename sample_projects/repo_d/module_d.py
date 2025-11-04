from repo_b.module_b import send_notification
from repo_c.module_c import transform_user_data

def aggregate_user_info(user_id: int):
    note = send_notification(user_id)
    transform = transform_user_data(user_id)
    return {
        "notification": note,
        "transformed": transform
    }

def generate_report(user_id: int):
    return aggregate_user_info(user_id)
