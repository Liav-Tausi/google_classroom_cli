import argparse
import json
from src.cli.gcc_admin_cli import AdminCli
from src.cli.gcc_student_cli import StudentCli
from src.cli.gcc_teacher_cli import TeacherCli
from src.gcc_validators import is_email

possible_methods = [
    'd_create',
    'q_create',
    'delete',
    'get',
    'list',
    'd_patch',
    'q_patch',
    'modify',
    'return',
    'accept',
    'tern_in',
    'reclaim'
]

possible_services = [
    'courses',
    'aliases',
    'announcements',
    'course_work',
    'student_submissions',
    'course_work_materials',
    'students',
    'teachers',
    'topics',
    'invitations',
    'user_profiles'
]


class Sort:
    """
    orders the terminal command line.
    """

    def __init__(self, role: str, email: str = None, work_space: str = None, ref_cache: int = None):
        self.__work_space = work_space
        self.__email = email
        self.__role = role.lower()
        self.__ref_cache = ref_cache

    @property
    def email(self):
        return self.__email

    @property
    def work_space(self):
        return self.__work_space

    @property
    def ref_cache(self):
        return self.__ref_cache

    @property
    def role(self):
        return self.__role

    def cli_nav(self, service, method, **kwargs):

        if self.role == 'admin':
            admin_cli = AdminCli(service=service.lower(), method=method.lower(), **kwargs)
            return admin_cli.method_nav(email=self.email, work_space=self.work_space, ref_cache_month=self.ref_cache)

        elif self.role == 'teacher':
            teacher_cli = TeacherCli(service=service.lower(), method=method.lower(), **kwargs)
            return teacher_cli.method_nav(email=self.email, work_space=self.work_space, ref_cache_month=self.ref_cache)

        elif self.role == 'student':
            student_cli = StudentCli(service=service.lower(), method=method.lower(), **kwargs)
            return student_cli.method_nav(email=self.email, work_space=self.work_space, ref_cache_month=self.ref_cache)

        else:
            raise ValueError(f"Invalid scan role: {self.role}")


def main():
    parser = argparse.ArgumentParser(description='Google Classroom CLI is a command-line interface tool'
                                                 'that allows users to interact with Google Classroom without leaving the terminal.'
                                                 'This project is currently under construction and is still a work in progress.'
                                                 'Created by Liav Tausi')

    parser.add_argument('a', type=str, help='personal email or workspace account')
    parser.add_argument('r', type=str, choices=["admin", "student", "teacher"], help='role, admin / student / teacher')

    parser.add_argument('-s', choices=[service for service in possible_services], help="""the service to use choose from: 
        [courses, aliases, announcements, course_work, student_submissions,
        course_work_materials, students, teachers, topics, invitations, user_profiles]""")

    parser.add_argument('-m', choices=[method for method in possible_methods], help=f"""the method to use choose from: 
        [d_create', q_create, delete, get, list, d_patch, q_patch, modify, return, accept]""")

    parser.add_argument('--ref_cache', type=int, help='refresh cache month in months, default 12 months')
    parser.add_argument('--c_id', type=int, help='the ID of the course')
    parser.add_argument('--d_json', action='store_true', help='is detailed JSON full')
    parser.add_argument('--ann_text', type=str, help='the text of the announcement')
    parser.add_argument('--ann_id', type=str, help='the ID of the announcement')
    parser.add_argument('--materials', type=json.loads, help='the materials to post')
    parser.add_argument('--state', type=str, help='the state of the service')
    parser.add_argument('--states', type=str, help='the states of the service')
    parser.add_argument('--s_time', type=str, help='the scheduled time')
    parser.add_argument('--u_time', type=str, help='the update time')
    parser.add_argument('--assi_mode', type=json.loads, help='the assignee mode')
    parser.add_argument('--s_options', type=list, help='the options for students')
    parser.add_argument('--p_size', type=int, help='the page size')
    parser.add_argument('--o_by', type=str, help='the order by')
    parser.add_argument('--p_token', type=str, help='the page token')
    parser.add_argument('--a_s_ids', type=list, help='the student IDs to add')
    parser.add_argument('--r_s_ids', type=list, help='the student IDs to remove')
    parser.add_argument('--title', type=str, help='the title of the service')
    parser.add_argument('--desc', type=str, help='the description of the service')
    parser.add_argument('--w_type', type=str, help='the type of the course work')
    parser.add_argument('--c_w_id', type=str, help='the ID of the course work')
    parser.add_argument('--sub_id', type=str, help='the ID of the student submission')
    parser.add_argument('--due_date', type=json.loads, help='the due date of the service')
    parser.add_argument('--due_time', type=json.loads, help='the due time of the service')
    parser.add_argument('--u_id', type=str, help='the user ID')
    parser.add_argument('--sub_states', type=list, help='the sub states of the service')
    parser.add_argument('--late', type=str, help='whether the submission is late')
    parser.add_argument('--assi_grade', type=int, help='the assigned grade')
    parser.add_argument('--s_answer', type=str, help='the short answer')
    parser.add_argument('--alt_link', type=str, help='the alternate link')
    parser.add_argument('--assi_sub', type=json.loads, help='the submission for the assignment')
    parser.add_argument('--c_w_m_id', type=str, help='the ID of the course work material')
    parser.add_argument('--c_w_m_states', type=list, help='status of this course work material')
    parser.add_argument('--m_link', type=str, help='the link to the material')
    parser.add_argument('--m_drive_id', type=str, help='the Google Drive ID of the material')
    parser.add_argument('--i_s_options', type=list, help='the options for individual students')
    parser.add_argument('--enr_code', type=str, help='the enrollment code for the course')
    parser.add_argument('--t_name', type=str, help='the name of the topic')
    parser.add_argument('--top_id', type=str, help='the ID of the topic')
    parser.add_argument('--inv_id', type=str, help='the ID of the invitation')
    parser.add_argument('--name', type=str, help='name of the course')
    parser.add_argument('--section', type=str, help='section of the course')
    parser.add_argument('--room', type=str, help='room of the course')
    parser.add_argument('--o_id', type=str, help='Id of the owner of course')
    parser.add_argument('--desc_h', type=str, help='description_heading of the course')
    parser.add_argument('--s_id', type=str, help='ID of a student')
    parser.add_argument('--t_id', type=str, help='ID of a teacher')
    parser.add_argument('--alias', type=str, help='The alias')
    parser.add_argument('--t_email', type=str, help='teacher email')
    parser.add_argument('--inv_role', type=str, help='role for invitation')

    args = parser.parse_args()
    if is_email(args.a):
        sorting: Sort = Sort(email=args.a, role=args.r, ref_cache=args.ref_cache)
    else:
        sorting: Sort = Sort(work_space=args.a, role=args.r, ref_cache=args.ref_cache)


    return sorting.cli_nav(
        service=args.s, method=args.m, ref_cache=args.ref_cache,
        d_json=args.d_json,
        ann_text=args.ann_text,
        ann_id=args.ann_id,
        materials=args.materials,
        state=args.state,
        states=args.states,
        s_time=args.s_time,
        u_time=args.u_time,
        assi_mode=args.assi_mode,
        s_options=args.s_options,
        p_size=args.p_size,
        o_by=args.o_by,
        p_token=args.p_token,
        a_s_ids=args.a_s_ids,
        r_s_ids=args.r_s_ids,
        title=args.title,
        desc=args.desc,
        w_type=args.w_type,
        c_w_id=args.c_w_id,
        due_date=args.due_date,
        due_time=args.due_time,
        u_id=args.u_id,
        sub_states=args.sub_states,
        late=args.late,
        assi_grade=args.assi_grade,
        s_answer=args.s_answer,
        alt_link=args.alt_link,
        assi_sub=args.assi_sub,
        c_w_m_id=args.c_w_m_id,
        m_link=args.m_link,
        m_drive_id=args.m_drive_id,
        i_s_options=args.i_s_options,
        enr_code=args.enr_code,
        t_name=args.t_name,
        top_id=args.top_id,
        inv_id=args.inv_id,
        name=args.name,
        section=args.section,
        room=args.room,
        o_id=args.o_id,
        desc_h=args.desc_h,
        sub_id=args.sub_id,
        t_id=args.t_id,
        alias=args.alias,
        t_email=args.t_email,
        inv_role=args.inv_role
    )
