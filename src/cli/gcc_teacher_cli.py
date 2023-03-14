from src import gcc_exceptions
from src.gcc_teacher import *


class TeacherCli:
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
        teacher_user: Teacher = Teacher(
            role='teacher',
            ref_cache_month=self.params.get('ref_cache'),
            email=self.params.get('a'),
            work_space=self.params.get('a'))

        if self.service == 'announcements':
            if self.method == 'd_create':
                return teacher_user.detailed_create_announcement(
                    detailed_json=self.params.get('d_json')
                )
            elif self.method == 'q_create':
                return teacher_user.quick_create_announcement(
                    course_id=self.params.get('c_id'),
                    announcement_text=self.params.get('ann_text'),
                    materials=self.params.get('materials'),
                    state=self.params.get('state'),
                    scheduled_time=self.params.get('s_time'),
                    update_time=self.params.get('u_time'),
                    assignee_mode=self.params.get('assi_mode'),
                    students_options=self.params.get('s_options')
                )
            elif self.method == 'delete':
                return teacher_user.delete_announcement(
                    course_id=self.params.get('c_id'),
                    announcement_id=self.params.get('ann_id')
                )
            elif self.method == 'get':
                return teacher_user.get_announcement(
                    course_id=self.params.get('c_id'),
                    announcement_id=self.params.get('ann_id')
                )
            elif self.method == 'list':
                return teacher_user.list_announcements(
                    states=self.params.get('states'),
                    page_size=self.params.get('p_size'),
                    order_by=self.params.get('o_by'),
                    page_token=self.params.get('p_token')
                )
            elif self.method == 'modify':
                return teacher_user.modify_announcement_assignees(
                    course_id=self.params.get('c_id'),
                    announcement_id=self.params.get('ann_id'),
                    assignee_mode=self.params.get('assi_mode'),
                    add_student_ids=self.params.get('a_s_ids'),
                    remove_student_ids=self.params.get('r_s_ids')
                )
            elif self.method == 'd_patch':
                return teacher_user.detailed_patch_announcement(
                    detailed_json=self.params.get('d_json')
                )
            elif self.method == 'q_patch':
                return teacher_user.quick_patch_announcement(
                    course_id=self.params.get('c_id'),
                    announcement_id=self.params.get('ann_id'),
                    state=self.params.get('state'),
                    text=self.params.get('ann_text'),
                    scheduled_time=self.params.get('s_time')
                )
            else:
                if self.service in ['accept', 'return', 'update']:
                    raise NotImplementedError()
                else:
                    raise gcc_exceptions.MethodError()

        elif self.service == 'course_work':
            if self.method == 'd_create':
                return teacher_user.detailed_course_work_create(
                    detailed_json=self.params.get('d_json')
                )
            elif self.method == 'q_create':
                return teacher_user.quick_course_work_create(
                    course_id=self.params.get('c_id'),
                    title=self.params.get('title'),
                    description=self.params.get('desc'),
                    materials=self.params.get('materials'),
                    work_type=self.params.get('w_type'),
                    state=self.params.get('state')
                )
            elif self.method == 'delete':
                return teacher_user.delete_course_work(
                    course_id=self.params.get('c_id'),
                    course_work_id=self.params.get('c_w_id')
                )
            elif self.method == 'get':
                return teacher_user.get_course_work(
                    course_id=self.params.get('c_id'),
                    course_work_id=self.params.get('c_w_id')
                )
            elif self.method == 'list':
                return teacher_user.list_course_work(
                    course_id=self.params.get('c_id'),
                    states=self.params.get('states'),
                    order_by=self.params.get('o_by'),
                    page_size=self.params.get('p_size'),
                    page_token=self.params.get('p_token')
                )
            elif self.method == 'modify':
                return teacher_user.modify_course_work_assignees(
                    course_id=self.params.get('c_id'),
                    course_work_id=self.params.get('c_w_id'),
                    assignee_mode=self.params.get('assi_mode'),
                    add_student_ids=self.params.get('a_s_ids'),
                    remove_student_ids=self.params.get('r_s_ids')
                )
            elif self.method == 'd_patch':
                return teacher_user.detailed_patch_course_work(
                    detailed_json=self.params.get('d_json')
                )
            elif self.method == 'q_patch':
                return teacher_user.quick_patch_course_work(
                    course_id=self.params.get('c_id'),
                    course_work_id=self.params.get('c_w_id'),
                    title=self.params.get('title'),
                    description=self.params.get('desc'),
                    due_date=self.params.get('due_date'),
                    due_time=self.params.get('due_time'),
                    scheduled_time=self.params.get('s_time'),
                    states=self.params.get('states'),
                    materials=self.params.get('materials')
                )
            else:
                if self.method in ['accept', 'return', 'tern_in', 'reclaim', 'update']:
                    raise NotImplementedError()
                else:
                    raise gcc_exceptions.MethodError()

        elif self.service == 'student_submissions':
            if self.method == 'get':
                return teacher_user.get_student_submissions(
                    course_id=self.params.get('c_id'),
                    course_work_id=self.params.get('c_w_id'),
                    submission_id=self.params.get('s_id')
                )
            elif self.method == 'list':
                return teacher_user.list_student_submissions(
                    course_id=self.params.get('c_id'),
                    course_work_id=self.params.get('c_w_id'),
                    user_id=self.params.get('u_id'),
                    page_size=self.params.get('p_size'),
                    sub_states=self.params.get('sub_states'),
                    late=self.params.get('late'),
                    page_token=self.params.get('p_token')
                )
            elif self.method == 'modify':
                return teacher_user.modify_submissions_attachments(
                    course_id=self.params.get('c_id'),
                    course_work_id=self.params.get('c_w_id'),
                    submission_id=self.params.get('s_id'),
                    materials=self.params.get('materials')
                )
            elif self.method == 'd_patch':
                return teacher_user.detailed_patch_student_submissions(
                    detailed_json=self.params.get('d_json')
                )
            elif self.method == 'q_patch':
                return teacher_user.quick_patch_student_submissions(
                    course_id=self.params.get('c_id'),
                    course_work_id=self.params.get('c_w_id'),
                    submission_id=self.params.get('s_id'),
                    sub_states=self.params.get('sub_states'),
                    assigned_grade=self.params.get('assi_grade'),
                    short_answer=self.params.get('s_answer'),
                    alternate_link=self.params.get('alt_link'),
                    assignment_submission=self.params.get('assi_sub')
                )
            elif self.method == 'return':
                return teacher_user.return_student_submissions(
                    course_id=self.params.get('c_id'),
                    course_work_id=self.params.get('c_w_id'),
                    submission_id=self.params.get('s_id')
                )
            else:
                if self.method in ['accept', 'd_create', 'q_create',
                                   'tern_in', 'reclaim', 'update']:
                    raise NotImplementedError()
                else:
                    raise gcc_exceptions.MethodError()

        elif self.service == 'course_work_materials':
            if self.method == 'd_create':
                return teacher_user.detailed_create_course_work_materials(
                    detailed_json=self.params.get('d_json')
                )
            elif self.method == 'q_create':
                return teacher_user.quick_create_course_work_materials(
                    course_id=self.params.get('c_id'),
                    title=self.params.get('title'),
                    description=self.params.get('desc'),
                    materials=self.params.get('materials')
                )
            elif self.method == 'delete':
                return teacher_user.delete_course_work_materials(
                    course_id=self.params.get('c_id'),
                    c_w_m_id=self.params.get('c_w_m_id')
                )
            elif self.method == 'get':
                return teacher_user.get_course_work_materials(
                    course_id=self.params.get('c_id'),
                    c_w_m_id=self.params.get('c_w_m_id')
                )
            elif self.method == 'list':
                return teacher_user.list_course_work_materials(
                    course_id=self.params.get('c_id'),
                    c_w_m_states=self.params.get('c_w_m_states'),
                    page_size=self.params.get('p_size'),
                    page_token=self.params.get('p_token'),
                    order_by=self.params.get('o_by'),
                    material_link=self.params.get('m_link'),
                    material_drive_id=self.params.get('m_drive_id')
                )
            elif self.method == 'd_patch':
                return teacher_user.detailed_patch_course_work_material(
                    detailed_json=self.params.get('d_json')
                )
            elif self.method == 'q_patch':
                return teacher_user.quick_patch_course_work_material(
                    course_id=self.params.get('c_id'),
                    c_w_m_id=self.params.get('c_w_m_id'),
                    title=self.params.get('title'),
                    description=self.params.get('desc'),
                    material=self.params.get('material'),
                    scheduled_time=self.params.get('s_time'),
                    states=self.params.get('states'),
                    individual_students_options=self.params.get('i_s_options')
                )
            else:
                if self.method in ['modify', 'return', 'accept',
                                   'tern_in', 'reclaim', 'update']:
                    raise NotImplementedError()
                else:
                    raise gcc_exceptions.MethodError()

        elif self.service == 'students':
            if self.method == 'q_create':
                return teacher_user.quick_add_student(
                    course_id=self.params.get('c_id'),
                    enrollment_code=self.params.get('enr_code'),
                    user_id=self.params.get('u_id')
                )
            elif self.method == 'd_create':
                return teacher_user.detailed_add_student(
                    detailed_json=self.params.get('d_json')
                )
            elif self.method == 'delete':
                return teacher_user.delete_student(
                    course_id=self.params.get('c_id'),
                    user_id=self.params.get('u_id')
                )
            elif self.method == 'get':
                return teacher_user.get_student(
                    course_id=self.params.get('c_id'),
                    user_id=self.params.get('u_id')
                )
            elif self.method == 'list':
                return teacher_user.list_students(
                    course_id=self.params.get('c_id'),
                    page_size=self.params.get('p_size'),
                    page_token=self.params.get('p_token')
                )
            else:
                if self.method in ['d_patch', 'q_patch', 'modify', 'return',
                                   'accept', 'tern_in', 'reclaim', 'update']:
                    raise NotImplementedError()
                else:
                    return gcc_exceptions.MethodError()

        elif self.service == 'topics':
            if self.method == 'q_create':
                return teacher_user.create_topic(
                    course_id=self.params.get('c_id'),
                    topic_name=self.params.get('t_name')
                )
            elif self.method == 'delete':
                return teacher_user.delete_topic(
                    course_id=self.params.get('c_id'),
                    topic_id=self.params.get('top_id')
                )
            elif self.method == 'get':
                return teacher_user.get_topic(
                    course_id=self.params.get('c_id'),
                    topic_id=self.params.get('top_id')
                )
            elif self.method == 'list':
                return teacher_user.list_topics(
                    course_id=self.params.get('c_id'),
                    page_size=self.params.get('p_size'),
                    page_token=self.params.get('p_token')
                )
            elif self.method == 'q_patch':
                return teacher_user.patch_topic(
                    course_id=self.params.get('c_id'),
                    topic_id=self.params.get('top_id'),
                    topic_name=self.params.get('t_name')
                )
            else:
                if self.method in ['d_create', 'd_patch', 'modify', 'return',
                                   'accept', 'tern_in', 'reclaim', 'update']:
                    raise NotImplementedError()
                else:
                    raise gcc_exceptions.MethodError()

        elif self.service == 'invitations':
            if self.method == 'accept':
                return teacher_user.accept_invitation(
                    invitation_id=self.params.get('inv_id')
                )
            else:
                if self.method in ['d_create', 'q_create', 'delete', 'get', 'list', 'd_patch',
                                   'q_patch', 'modify', 'return', 'tern_in','reclaim', 'update']:
                    raise NotImplementedError()
                else:
                    raise gcc_exceptions.MethodError()
        else:
            raise gcc_exceptions.ServiceError()
