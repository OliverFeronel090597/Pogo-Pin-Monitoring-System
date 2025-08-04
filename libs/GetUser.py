import ctypes

def get_login_user():
    NameDisplay = 3
    GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
    size = ctypes.pointer(ctypes.c_ulong(0))
    GetUserNameEx(NameDisplay, None, size)

    buffer = ctypes.create_unicode_buffer(size.contents.value)
    GetUserNameEx(NameDisplay, buffer, size)
    full_name = str(buffer.value).split(" ")
    return f"{full_name[0][0]}.{full_name[-1]}"