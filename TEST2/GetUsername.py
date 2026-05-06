import ctypes
import getpass


def get_windows_display_name():
    NameDisplay = 3
    GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
    size = ctypes.pointer(ctypes.c_ulong(0))
    GetUserNameEx(NameDisplay, None, size)

    buffer = ctypes.create_unicode_buffer(size.contents.value)
    GetUserNameEx(NameDisplay, buffer, size)
    return buffer.value

print("Username:", getpass.getuser())         # O.Feronel
print("Full Name:", get_windows_display_name())  # Oliver Feronel


full_name = "Queen x y z Deme Feronel".split()
osram_name = full_name[0][0] + "." + full_name[-1]
print(osram_name)
