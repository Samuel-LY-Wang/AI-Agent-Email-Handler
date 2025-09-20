from ctypes import cdll, c_void_p, create_string_buffer, c_int, POINTER, c_char
from random import randint

class UwuRandom:
    _uwurandom_lib = None
    uwu_instance: c_void_p

    @staticmethod
    def get_lib():
        if UwuRandom._uwurandom_lib is not None:
            return UwuRandom._uwurandom_lib

        UwuRandom._uwurandom_lib = cdll.LoadLibrary('libuwurandom.so')

        # Define function prototypes
        lib = UwuRandom._uwurandom_lib

        # uwulib_init() -> void*
        lib.uwulib_init.argtypes = []
        lib.uwulib_init.restype = c_void_p

        # uwulib_write_chars(void* instance, char* dest, int len) -> void
        lib.uwulib_write_chars.argtypes = [c_void_p, POINTER(c_char), c_int]
        lib.uwulib_write_chars.restype = None

        # uwulib_free(void* instance) -> void
        lib.uwulib_free.argtypes = [c_void_p]
        lib.uwulib_free.restype = None

        return UwuRandom._uwurandom_lib

    def __init__(self) -> None:
        self.uwu_instance = c_void_p(UwuRandom.get_lib().uwulib_init())

    def generate(self, length: int) -> str:
        if length <= 0:
            return ""

        lib = UwuRandom.get_lib()
        dest = create_string_buffer(length)
        lib.uwulib_write_chars(self.uwu_instance, dest, length)

        return dest.raw.decode('utf-8', errors='replace')

    def __del__(self):
        UwuRandom.get_lib().uwulib_free(self.uwu_instance.value)

def draft_email_uwurandom(instance: UwuRandom, email):
    """
    Draft an email response using uwurandom.

    :param instance: An uwurandom instance
    :param email: An Email object containing all email data
    """

    new_email=email.create_new({"body": instance.generate(randint(500, 2000)), "subject": f"Re: {email.subject} :3"})

    return new_email
