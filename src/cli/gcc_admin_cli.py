from src import gcc_exceptions
from src.gcc_admin import Admin


class AdminCli:
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
        admin_user: Admin = Admin(
            role='admin',
            ref_cache_month=self.params.get('ref_cache'),
            email=self.params.get('a'),
            work_space=self.params.get('a')
        )
        if self.service == 'courses':
            if self.method == 'd_create':
                return admin_user.detailed_create_course(
                    detailed_json=self.params.get('d_json')
                )
            elif self.method == 'q_create':
                return admin_user.quick_create_course(
                    name=self.params.get('name'),
                    section=self.params.get('section'),
                    description=self.params.get('desc'),
                    room=self.params.get('room'),
                    owner_id=self.params.get('o_id'),
                    course_state=self.params.get('state')
                )
            elif self.method == 'delete':
                return admin_user.delete_course(
                    course_id=self.params.get('c_id'),
                )
            elif self.method == 'd_patch':
                return admin_user.detailed_patch_course(
                    detailed_json=self.params.get('d_json')
                )
            elif self.method == 'q_patch':
                return admin_user.quick_patch_course(
                    name=self.params.get('name'),
                    section=self.params.get('section'),
                    description=self.params.get('desc'),
                    description_heading=self.params.get('desc_h'),
                    materials=self.params.get('materials'),
                )
            elif self.method == 'update':
                return admin_user.update_course(
                    detailed_json=self.params.get('d_json')
                )
            elif self.method == 'get':
                return admin_user.get_course(
                    course_id=self.params.get('c_id')
                )
            elif self.method == 'list':
                return admin_user.list_courses(
                    student_id=self.params.get('s_id'),
                    teacher_id=self.params.get('t_id'),
                    states=self.params.get('states'),
                    page_size=self.params.get('p_size'),
                    page_token=self.params.get('p_token')
                )
            else:
                if self.method in ['tern_in', 'reclaim', 'update', 'return', 'accept', 'modify']:
                    raise NotImplementedError()
                else:
                    raise gcc_exceptions.MethodError()
        elif self.service == 'aliases':
            if self.method == 'q_create':
                return admin_user.create_alias(
                    course_id=self.params.get('c_id'),
                    alias=self.params.get('alias')
                )
            elif self.method == 'delete':
                return admin_user.delete_alias(
                    course_id=self.params.get('c_id'),
                    alias=self.params.get('alias')
                )
            elif self.method == 'list':
                return admin_user.list_alias(
                    course_id=self.params.get('c_id'),
                    page_size=self.params.get('p_size'),
                    page_token=self.params.get('p_token')
                )
            else:
                if self.method in ['d_create', 'get', 'tern_in', 'reclaim', 'update',
                                   'return', 'accept', 'modify', 'd_patch', 'q_patch']:
                    raise NotImplementedError()
                else:
                    gcc_exceptions.MethodError()
        elif self.service == 'teachers':
            if self.method == 'q_create':
                return admin_user.add_teacher(
                    course_id=self.params.get('c_id'),
                    teacher_email=self.params.get('t_email')
                )
            elif self.method == 'delete':
                return admin_user.delete_teacher(
                    course_id=self.params.get('c_id'),
                    teacher_email=self.params.get('t_email')
                )
            elif self.method == 'get':
                return admin_user.get_teacher(
                    course_id=self.params.get('c_id'),
                    teacher_email=self.params.get('t_email')
                )
            elif self.method == 'list':
                return admin_user.list_teachers(
                    course_id=self.params.get('c_id'),
                    page_size=self.params.get('p_size'),
                    page_token=self.params.get('p_token')
                )
            else:
                if self.method in ['d_create', 'tern_in', 'reclaim', 'update',
                                   'return', 'accept', 'modify', 'd_patch', 'q_patch']:
                    raise NotImplementedError()
                else:
                    gcc_exceptions.MethodError()

        elif self.service == 'invitations':
            if self.method == 'accept':
                return admin_user.accept_invitation(
                    invitation_id=self.params.get('inv_id')
                )
            elif self.method == 'q_create':
                return admin_user.create_invitation(
                    course_id=self.params.get('c_id'),
                    user_id=self.params.get('u_id'),
                    role=self.params.get('inv_role')
                )
            elif self.method == 'delete':
                return admin_user.delete_invitation(
                    invitation_id=self.params.get('inv_id')
                )
            elif self.method == 'get':
                return admin_user.get_invitation(
                    invitation_id=self.params.get('inv_id')
                )
            elif self.method == 'list':
                return admin_user.list_invitation(
                    course_id=self.params.get('c_id'),
                    user_id=self.params.get('u_id'),
                    page_size=self.params.get('p_size'),
                    page_token=self.params.get('p_token')
                )
            else:
                if self.method in ['d_create', 'tern_in', 'reclaim', 'update',
                                   'return', 'accept', 'modify', 'd_patch', 'q_patch']:
                    raise NotImplementedError()
                else:
                    gcc_exceptions.MethodError()

        elif self.service == 'user_profiles':
            if self.method == 'get':
                return admin_user.get_user(
                    user_id=self.params.get('u_id'),
                )
            else:
                if self.method in ['d_create', 'q_create', 'tern_in', 'reclaim', 'update', 'list',
                                   'delete', 'return', 'accept', 'modify', 'd_patch', 'q_patch']:
                    raise NotImplementedError()
                else:
                    gcc_exceptions.MethodError()
        else:
            raise gcc_exceptions.ServiceError()






