import argparse
from ..gcc_validators import *

from gcc_student_cli import StudentCli
from gcc_teacher_cli import TeacherCli
from gcc_admin_cli import AdminCli

from ..gcc_teacher import Teacher
from ..gcc_student import Student
from ..gcc_admin import Admin

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
    'accept'
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

    def __init__(self, role: str, email: str = None, work_space: str = None):
        self.__work_space = work_space
        self.__email = email
        self.__role = role

    @property
    def email(self):
        return self.__email

    @property
    def work_space(self):
        return self.__work_space

    @property
    def role(self):
        return self.__role

    def cli_nav(self, service, method, **kwargs):

        if self.role == 'admin':
            if self.work_space:
                Admin(role=self.role, work_space=self.work_space)
            else:
                Admin(role=self.role, email=self.email)
            AdminCli(service=service, method=method)

        elif self.role == 'teacher':
            if self.work_space:
                Teacher(role=self.role, work_space=self.work_space)
            else:
                Teacher(role=self.role, email=self.email)

            TeacherCli(service=service, method=method, **kwargs)

        elif self.role == 'student':
            if self.work_space:
                Student(role=self.role, work_space=self.work_space)
            else:
                Student(role=self.role, email=self.email)

            StudentCli(service=service, method=method, **kwargs)

        else:
            raise ValueError(f"Invalid scan role: {self.role}")


parser = argparse.ArgumentParser(description='Google Classroom CLI is a command-line interface tool'
                                             'that allows users to interact with Google Classroom without leaving the terminal.'
                                             'This project is currently under construction and is still a work in progress.'
                                             'Created by Liav Tausi')

parser.add_argument('a', type=str, help='personal email or workspace account')
parser.add_argument('r', type=str, choices=["admin", "student", "teacher"], help='role, admin / student / teacher')
parser.add_argument('-s', choices=[service for service in possible_services], help=""" the service to use choose from: 
    [courses, aliases, announcements, course_work, student_submissions,
     course_work_materials, students, teachers, topics, invitations, user_profiles] """)
parser.add_argument('-m', choices=[method for method in possible_methods], help='the method to use')
parser.add_argument('course_id', type=int, help='the ID of the course')
parser.add_argument('--detailed_json', action='store_true', help='is detailed JSON full')
parser.add_argument('--announcement_text', type=str, help='the text of the announcement')
parser.add_argument('--announcement_id', type=str, help='the ID of the announcement')
parser.add_argument('--materials', type=json.loads, help='the materials to post')
parser.add_argument('--state', type=str, help='the state of the service')
parser.add_argument('--states', type=str, help='the states of the service')
parser.add_argument('--scheduled_time', type=str, help='the scheduled time')
parser.add_argument('--update_time', type=str, help='the update time')
parser.add_argument('--assignee_mode', type=json.loads, help='the assignee mode')
parser.add_argument('--students_options', type=list, help='the options for students')
parser.add_argument('--page_size', type=int, help='the page size')
parser.add_argument('--order_by', type=str, help='the order by')
parser.add_argument('--page_token', type=str, help='the page token')
parser.add_argument('--add_student_ids', type=list, help='the student IDs to add')
parser.add_argument('--remove_student_ids', type=list, help='the student IDs to remove')
parser.add_argument('--title', type=str, help='the title of the service')
parser.add_argument('--description', type=str, help='the description of the service')
parser.add_argument('--work_type', type=str, help='the type of the course work')
parser.add_argument('--course_work_id', type=str, help='the ID of the course work')
parser.add_argument('--due_date', type=json.loads, help='the due date of the service')
parser.add_argument('--due_time', type=json.loads, help='the due time of the service')
parser.add_argument('--user_id', type=str, help='the user ID')
parser.add_argument('--sub_states', type=list, help='the sub states of the service')
parser.add_argument('--late', type=str, help='whether the submission is late')
parser.add_argument('--assigned_grade', type=int, help='the assigned grade')
parser.add_argument('--short_answer', type=str, help='the short answer')
parser.add_argument('--alternate_link', type=str, help='the alternate link')
parser.add_argument('--assignment_submission', type=json.loads, help='the submission for the assignment')
parser.add_argument('--c_w_m_id', type=str, help='the ID of the course work material')
parser.add_argument('--material_link', type=str, help='the link to the material')
parser.add_argument('--material_drive_id', type=str, help='the Google Drive ID of the material')
parser.add_argument('--individual_students_options', type=list, help='the options for individual students')
parser.add_argument('--enrollment_code', type=str, help='the enrollment code for the course')
parser.add_argument('--topic_name', type=str, help='the name of the topic')
parser.add_argument('--topic_id', type=str, help='the ID of the topic')
parser.add_argument('--invitation_id', type=str, help='the ID of the invitation')

args = parser.parse_args()

if is_work_space_email(args.e):
    sorting: Sort = Sort(work_space=args.e, role=args.r)
else:
    sorting: Sort = Sort(email=args.e, role=args.r)

sorting.cli_nav(
    service=args.s, method=args.m,
    detailed_json=args.detailed_json,
    announcement_text=args.announcement_text,
    announcement_id=args.announcement_id,
    materials=args.materials,
    state=args.state,
    states=args.states,
    scheduled_time=args.scheduled_time,
    update_time=args.update_time,
    assignee_mode=args.assignee_mode,
    students_options=args.students_options,
    page_size=args.page_size,
    order_by=args.order_by,
    page_token=args.page_token,
    add_student_ids=args.add_student_ids,
    remove_student_ids=args.remove_student_ids,
    title=args.title,
    description=args.description,
    work_type=args.work_type,
    course_work_id=args.course_work_id,
    due_date=args.due_date,
    due_time=args.due_time,
    user_id=args.user_id,
    sub_states=args.sub_states,
    late=args.late,
    assigned_grade=args.assigned_grade,
    short_answer=args.short_answer,
    alternate_link=args.alternate_link,
    assignment_submission=args.assignment_submission,
    c_w_m_id=args.c_w_m_id,
    material_link=args.material_link,
    material_drive_id=args.material_drive_id,
    individual_students_options=args.individual_students_options,
    enrollment_code=args.enrollment_code,
    topic_name=args.topic_name,
    topic_id=args.topic_id,
    invitation_id=args.invitation_id
)
