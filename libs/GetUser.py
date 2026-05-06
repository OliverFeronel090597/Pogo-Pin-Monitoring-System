import ctypes
import inspect


def get_login_user():
    # Detect caller info
    # stack = inspect.stack()
    # if len(stack) > 1:
    #     caller_frame = stack[1]
    #     func_name = caller_frame.function
    #     file_name = caller_frame.filename
    #     line_no = caller_frame.lineno

    #     locals_ = caller_frame.frame.f_locals
    #     class_name = None
    #     if 'self' in locals_:
    #         class_name = type(locals_['self']).__name__
    #     elif 'cls' in locals_:
    #         class_name = locals_['cls'].__name__

    #     print(f"Called from function: {func_name} (line {line_no}) in {file_name}")
    #     if class_name:
    #         print(f"Called from class: {class_name}")

    # Original user-fetching logic
    NameDisplay = 3
    GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
    size = ctypes.pointer(ctypes.c_ulong(0))
    GetUserNameEx(NameDisplay, None, size)

    buffer = ctypes.create_unicode_buffer(size.contents.value)
    GetUserNameEx(NameDisplay, buffer, size)
    full_name = str(buffer.value).split(" ")
    print(f"User Login: {full_name}")
    return f"{full_name[0][0]}.{full_name[-1]}"
