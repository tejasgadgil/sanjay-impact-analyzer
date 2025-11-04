"""
Sample Module D
Aggregates data from multiple sources
"""
# Would import from B and C:
# from repo_b.module_b import send_notification
# from repo_c.module_c import transform_user_data

def aggregate_user_info(user_id: int):
    """Aggregate user information from B and C"""
    # Calls send_notification and transform_user_data
    return {
        "notification": f"sent_{user_id}",
        "transformed": {}
    }

def generate_report(user_id: int):
    """Generate user report"""
    return aggregate_user_info(user_id)
