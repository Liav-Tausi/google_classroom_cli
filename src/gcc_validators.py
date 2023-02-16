import re


# email validator
def is_email(email: str) -> bool:
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

    if re.fullmatch(regex, email):
        return True
    else:
        return False


# work_space account validator
def is_work_space_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    match = re.search(pattern, email)
    if match:
        return True
    else:
        return False


def are_params_string(*args, **kwargs):
    if not all(isinstance(param, str) for param in args):
        raise TypeError()


def are_params_int(*args, **kwargs):
    if not all(isinstance(param, int) for param in args):
        raise TypeError()

