class GccErrors(Exception):
    pass


class UserError(GccErrors):
    def __init__(self):
        super().__init__('Role must be (student, teacher, admin).')


class InvalidEmail(GccErrors):
    def __init__(self):
        super().__init__('Invalid Email.')


class InvalidRole(GccErrors):
    def __init__(self):
        super().__init__('Invalid Role.')


class CourseStateError(GccErrors):
    def __init__(self):
        super().__init__('Course_state must be one of [PROVISIONED, ACTIVE, ARCHIVED, DECLINED, SUSPENDED].')


class AlreadyInCache(GccErrors):
    def __init__(self):
        super().__init__('Course already made.')


class NotInCache(GccErrors):
    def __init__(self):
        super().__init__('Not in cache.')