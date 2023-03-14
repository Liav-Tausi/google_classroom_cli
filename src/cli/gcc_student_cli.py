from src import gcc_exceptions
from src.gcc_student import Student


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

    def method_nav(self, email=None, work_space=None, ref_cache_month=12):
        student_user: Student = Student(
            role='student',
            ref_cache_month=ref_cache_month,
            email=email,
            work_space=work_space)

        if self.service == 'student_submissions':
            if self.method == 'turn_in':
                return student_user.tern_in_submission(
                    course_id=self.params.get('c_id'),
                    course_work_id=self.params.get('c_w_id'),
                    submission_id=self.params.get('sub_id')
                )
            elif self.method == 'reclaim':
                return student_user.reclaim_submission(
                    course_id=self.params.get('c_id'),
                    course_work_id=self.params.get('c_w_id'),
                    submission_id=self.params.get('sub_id')
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
