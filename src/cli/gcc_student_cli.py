from .. import gcc_exceptions
from ..gcc_student import Student


class StudentCli:
    def __init__(self, **kwargs):
        if kwargs.get("service"):
            self.__service: str = kwargs["service"]
        else:
            raise gcc_exceptions.ServiceError()
        if kwargs.get("method"):
            self.__method: str = kwargs["method"]
        else:
            raise gcc_exceptions.MethodError()

        self.__params: dict = kwargs

    @property
    def params(self):
        return self.__params

    @property
    def method(self):
        return self.__method

    @property
    def service(self):
        return self.__service

    def method_nav(self):
        student_user: Student = Student(
            role='student',
            ref_cache_month=self.params.get('ref_cache'),
            email=self.params.get('a'),
            work_space=self.params.get('a'))

        if self.service == 'student_submissions':
            if self.method == 'turn_in':
                return student_user.tern_in_submission(
                    course_id=self.params.get('c_id'),
                    course_work_id=self.params.get('c_w_id'),
                    submission_id=self.params.get('s_id')
                )
            elif self.method == 'reclaim':
                return student_user.reclaim_submission(
                    course_id=self.params.get('c_id'),
                    course_work_id=self.params.get('c_w_id'),
                    submission_id=self.params.get('s_id')
                )
            else:
                if self.service in ['d_create', 'q_create', 'delete', 'get', 'list',
                                    'd_patch', 'q_patch', 'modify', 'return', 'accept', 'update']:
                    raise NotImplementedError()
                else:
                    raise gcc_exceptions.MethodError()

        elif self.service == 'invitations':
            if self.method == 'accept':
                return student_user.accept_invitation(
                    invitation_id=self.params.get('inv_id')
                )
            else:
                if self.service in ['d_create', 'q_create', 'delete', 'get', 'list',
                                    'd_patch', 'q_patch', 'modify', 'return', 'reclaim',
                                    'turn_in', 'update']:
                    raise NotImplementedError()
                else:
                    raise gcc_exceptions.MethodError()

        else:
            raise gcc_exceptions.ServiceError()
