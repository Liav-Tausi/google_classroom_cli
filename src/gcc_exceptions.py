class GccErrors(Exception):
    pass


class UserError(GccErrors):
    def __init__(self):
        super().__init__('Role must be (student, teacher, admin).')


class InvalidEmail(GccErrors):
    def __init__(self):
        super().__init__('Invalid Email.')
