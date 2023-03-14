class GccErrors(Exception):
    pass


class UserError(GccErrors):
    def __init__(self):
        super().__init__('Role must be one of [student, teacher, admin].')


class ServiceError(GccErrors):
    def __init__(self):
        super().__init__('Service must be specified. ' 
                         '[courses, aliases, announcements, course_work, student_submissions, '
                         'course_work_materials, students, teachers, topics, invitations, user_profiles]')


class MethodError(GccErrors):
    def __init__(self):
        super().__init__('Method must be specified. '
                         '[d_create, q_create, delete, get, list, d_patch, q_patch, modify, return, accept]')


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
        super().__init__('CourseState should be in [PROVISIONED, ACTIVE, ARCHIVED, DECLINED, SUSPENDED].')


class AlreadyInCache(GccErrors):
    def __init__(self):
        super().__init__('Course already made.')


class TeacherNotInCourse(GccErrors):
    def __init__(self):
        super().__init__('Teacher not in course.')


class NotInCache(GccErrors):
    def __init__(self, param):
        super().__init__(f'{param} Not in cache.')


class ScopeError(GccErrors):
    def __init__(self):
        super().__init__('Scopes should be [student, teacher, admin].')


class AnnouncementStateError(GccErrors):
    def __init__(self):
        super().__init__('AnnouncementState should be in [ANNOUNCEMENT_STATE_UNSPECIFIED, PUBLISHED, DRAFT, DELETED,].')


class SubmissionStateError(GccErrors):
    def __init__(self):
        super().__init__(
            'SubmissionStateError should be [SUBMISSION_STATE_UNSPECIFIED, NEW, CREATED,TURNED_IN, RETURNED, RECLAIMED_BY_STUDENT')


class SubmissionLateValueError(GccErrors):
    def __init__(self):
        super().__init__('SubmissionLateValueError should be [LATE_VALUES_UNSPECIFIED, LATE_ONLY, NOT_LATE_ONLY')


class CourseWorkStateError(GccErrors):
    def __init__(self):
        super().__init__('CourseWorkState should be in [COURSE_WORK_STATE_UNSPECIFIED, PUBLISHED, DRAFT, DELETED].')


class CourseWorkTypeError(GccErrors):
    def __init__(self):
        super().__init__('CourseWorkType should be in [COURSE_WORK_TYPE_UNSPECIFIED, ASSIGNMENT,'
                         ' SHORT_ANSWER_QUESTION, MULTIPLE_CHOICE_QUESTION].')


class TimeStampError(GccErrors):
    def __init__(self):
        super().__init__('Time stamp error')


class AssigneeModeError(GccErrors):
    def __init__(self):
        super().__init__('AssigneeMode should be in [ASSIGNEE_MODE_UNSPECIFIED, ALL_STUDENTS, INDIVIDUAL_STUDENTS].')


class CourseWorkJsonEmpty(GccErrors):
    def __init__(self):
        super().__init__('CourseWork json is not full.')


class AnnouncementJsonEmpty(GccErrors):
    def __init__(self):
        super().__init__('Announcement json is not full.')


class StudentsSubmissionsJsonEmpty(GccErrors):
    def __init__(self):
        super().__init__('StudentsSubmissions json is not full.')


class CourseWorkMaterialJsonEmpty(GccErrors):
    def __init__(self):
        super().__init__('StudentsSubmissions json is not full.')


class DetailedStudentJsonEmpty(GccErrors):
    def __init__(self):
        super().__init__('DetailedStudent json is not full.')


class RoleError(GccErrors):
    def __init__(self):
        super().__init__('Role should be in [STUDENT, TEACHER, OWNER]')


class CourseWorkMaterialStateError(GccErrors):
    def __init__(self):
        super().__init__(
            'CourseWorkMaterial state should be in [DELETED, DRAFT, PUBLISHED, COURSEWORK_MATERIAL_STATE_UNSPECIFIED].')


class CourseJsonEmpty(GccErrors):
    def __init__(self):
        super().__init__('Course json is not full.')
