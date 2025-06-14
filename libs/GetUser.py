import psutil

def get_login_user():
    users = psutil.users()
    if users:
        return users[0].name  # First logged-in user's name
    return None

# # Example usage
# print("Logged-in user:", get_login_user())
