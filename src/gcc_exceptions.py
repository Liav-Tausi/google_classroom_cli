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


class ScopeError(GccErrors):
    def __init__(self):
        super().__init__('Scopes should be [student, teacher, admin].')


class AnnouncementStateError(GccErrors):
    def __init__(self):
        super().__init__('AnnouncementState should be [ANNOUNCEMENT_STATE_UNSPECIFIED, PUBLISHED, DRAFT, DELETED,].')


class CourseWorkStateError(GccErrors):
    def __init__(self):
        super().__init__('CourseWorkState should be [COURSE_WORK_STATE_UNSPECIFIED, PUBLISHED, DRAFT, DELETED].')


class CourseWorkTypeError(GccErrors):
    def __init__(self):
        super().__init__('CourseWorkType should be [COURSE_WORK_TYPE_UNSPECIFIED, ASSIGNMENT,'
                         ' SHORT_ANSWER_QUESTION, MULTIPLE_CHOICE_QUESTION].')


class TimeStampError(GccErrors):
    def __init__(self):
        super().__init__('Time stamp error')


class AssigneeModeError(GccErrors):
    def __init__(self):
        super().__init__('AssigneeMode should be [ASSIGNEE_MODE_UNSPECIFIED, ALL_STUDENTS, INDIVIDUAL_STUDENTS].')


class CourseWorkJsonEmpty(GccErrors):
    def __init__(self):
        super().__init__('CourseWork json is not full.')


class AnnouncementJsonEmpty(GccErrors):
    def __init__(self):
        super().__init__('Announcement json is not full.')


class CourseJsonEmpty(GccErrors):
    def __init__(self):
        super().__init__('Course json is not full.')
