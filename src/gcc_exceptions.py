class GccErrors(Exception):
    pass


class UserError(GccErrors):
    def __init__(self):
        super().__init__('Role must be (student, teacher, admin).')


class InvalidEmail(GccErrors):
    def __init__(self):
        super().__init__('Invalid Email.')


class InvalidParams(GccErrors):
    def __init__(self):
        super().__init__('Email or Workspace needed.')


class InvalidWorkSpace(GccErrors):
    def __init__(self):
        super().__init__('Invalid WorkSpace.')


class InvalidRole(GccErrors):
    def __init__(self):
        super().__init__('Invalid Role.')


class ExceededLimitError(GccErrors):
    def __init__(self):
        super().__init__('Exceeded limit 30.')


class CourseStateError(GccErrors):
    def __init__(self):
        super().__init__('Course_state must be one of [PROVISIONED, ACTIVE, ARCHIVED, DECLINED, SUSPENDED].')


class AlreadyInCache(GccErrors):
    def __init__(self):
        super().__init__('Course already made.')


class TeacherNotInCourse(GccErrors):
    def __init__(self):
        super().__init__('Teacher not in course.')


class NotInCache(GccErrors):
    def __init__(self):
        super().__init__('Not in cache.')
