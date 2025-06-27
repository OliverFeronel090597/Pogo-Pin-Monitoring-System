import psutil

def get_login_user():
    users = psutil.users()
    if users and not users[0].name.startswith("E100"):
        return users[0].name  # First logged-in user's name
    return None

# # Example usage
# print("Logged-in user:", get_login_user())
