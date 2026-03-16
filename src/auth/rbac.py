ROLES = {
    "admin": {
        "permissions": [
            "upload_document",
            "query_documents",
            "delete_document",
            "manage_users",
            "view_analytics",
            "manage_api_keys",
            "view_audit_logs"
        ],
        "max_documents": None,
        "max_queries_per_day": None
    },
    "editor": {
        "permissions": [
            "upload_document",
            "query_documents",
            "delete_document",
            "view_analytics",
            "manage_api_keys"
        ],
        "max_documents": 100,
        "max_queries_per_day": 1000
    },
    "viewer": {
        "permissions": [
            "query_documents"
        ],
        "max_documents": 0,
        "max_queries_per_day": 100
    }
}

def check_permission(user_role: str, required_permission: str) -> bool:
    return required_permission in ROLES.get(user_role, {}).get("permissions", [])

def get_rate_limit(user_role: str) -> dict:
    return {
        "max_documents": ROLES.get(user_role, {}).get("max_documents"),
        "max_queries_per_day": ROLES.get(user_role, {}).get("max_queries_per_day")
    }

def get_role_permissions(user_role: str) -> list:
    return ROLES.get(user_role, {}).get("permissions", [])