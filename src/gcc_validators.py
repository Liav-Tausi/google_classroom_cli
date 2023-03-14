import json
import re
from src import gcc_exceptions


# email validator
def is_email(email: str) -> bool:
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

    if re.fullmatch(regex, email):
        return True
    else:
        gcc_exceptions.InvalidEmail()


# work_space account validator
def is_work_space_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    match = re.search(pattern, email)
    if match:
        return True
    else:
        return False


def validate_params(*types):
    def wrapper(func):
        def validator(*args, **kwargs):
            for arg, arg_type in zip(args[1::], types):
                if not isinstance(arg, arg_type):
                    raise TypeError(f"Argument {arg} must be of type {arg_type}")
            return func(*args, **kwargs)

        return validator

    return wrapper


def are_params_string(*args, **kwargs):
    if not all(isinstance(param, str) for param in args):
        raise TypeError()


def are_params_int(*args, **kwargs):
    if not all(isinstance(param, int) for param in args):
        raise TypeError()


def are_params_in_cache(*args, **kwargs):
    with open(r'C:\Users\liavt\PycharmProjects\google_classroom_cli\src\data_endpoint\gcc_cache.json', 'r') as fh:
        cache = json.load(fh)
    for param in args:
        if param not in cache:
            raise gcc_exceptions.NotInCache(param)
