import datetime
import json

from gcc_base import GccBase
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import gcc_exceptions
import gcc_validators

import google.auth
from googleapiclient.errors import HttpError


class Admin(GccBase):

    def __init__(self, role: str = 'admin', email: str = None,
                 work_space: str = None, ref_cache_month: int = 12):

        if role != 'admin':
            raise gcc_exceptions.InvalidRole()
        super().__init__(role, ref_cache_month, work_space, email)

    @GccBase.cacher
    def detailed_create_course(self) -> tuple:
        """
        function that allows more detailed course creating
        :return:
        """
        with open('data/detailed_create_course.json', 'r') as fh:
            course_json = json.load(fh)
        try:
            request = self.classroom.courses().create(body=course_json).execute()
            print(f"""
            Created course: {request["name"]}
            Course id: {request["id"]}
            """)
            return request['id'], request["name"]
        except HttpError as error:
            print('An error occurred: %s' % error)

    @GccBase.cacher
    def create_course(self, name: str, section: str, description: str, room: str, owner_id='me',
                      course_state: str = 'PROVISIONED') -> tuple:
        """
        Creates a course

        :param name: name of course
        :param section: section of course
        :param description: description of course
        :param room: room of course
        :param owner_id:
        :param course_state:
        :return:
        """
        if not all(isinstance(param, str) for param in (name, section, description, room, owner_id)):
            raise TypeError()
        if course_state.upper() not in ['PROVISIONED', 'ACTIVE', 'ARCHIVED', 'DECLINED', 'SUSPENDED']:
            raise gcc_exceptions.CourseStateError()
        if name in self.cache:
            raise gcc_exceptions.AlreadyInCache()

        course: dict = {
            'name': name,
            'section': section,
            'descriptionHeading': description,
            'room': room,
            'ownerId': owner_id,
            'courseState': course_state.upper()
        }
        try:
            request = self.classroom.courses().create(body=course).execute()
            print(f"""
                   Created course: {request["name"]}
                   Course id: {request["id"]}
                   """)
            return  request['id'],  request["name"], self.email
        except HttpError as error:
            print('An error occurred: %s' % error)

    def add_teacher(self, course_id: int, teacher_email: str) -> None:
        if self.workspace:
            check = self.workspace
        else:
            check = self.email
        if str(course_id) not in self.cache[check]:
            raise gcc_exceptions.NotInCache()
        if not gcc_validators.is_email(teacher_email) and teacher_email != 'me':
            raise gcc_exceptions.InvalidEmail()
        data: dict = {
            "userId": teacher_email,
        }
        try:
            request = self.classroom.courses().teachers().create(courseId=course_id,
                                                                 body=data).execute()

            print('User %s was added as a teacher to the course with ID %s'
                  % (request.get('profile').get('name').get('fullName'),
                     course_id))

            self._update_cache((course_id, request.get('profile').get('name').get('fullName'), teacher_email),
                               datetime.datetime.now().timestamp())
        except HttpError as error:
            print('An error occurred: %s' % error)

    def delete_teacher(self, course_id: int, teacher_email: str) -> None:
        if teacher_email not in self.cache[self.email][str(course_id)]['teachers']:
            raise gcc_exceptions.TeacherNotInCourse()
        if not gcc_validators.is_email(teacher_email):
            raise gcc_exceptions.InvalidEmail()
        try:
            self.classroom.courses().teachers().delete(courseId=str(course_id),
                                                       userId=teacher_email).execute()
            self._update_cache(result=(str(course_id),
                                       None, teacher_email), del_teacher=True)

            print(f'User {teacher_email} was deleted from course with ID {course_id}')
        except HttpError as error:
            print('An error occurred: %s' % error)


    def get_teacher(self, course_id: int, teacher_email: str) -> None:
        if str(course_id) not in self.cache[self.email]:
            raise Exception()
        if not gcc_validators.is_email(teacher_email):
            raise gcc_exceptions.InvalidEmail()
        try:
            request = self.classroom.courses().teachers().get(courseId=course_id,
                                                              userId=teacher_email).execute()
            return request
        except HttpError as error:
            print('An error occurred: %s' % error)


    def list_teachers(self, course_id: int, page_size: int = 10, page_token: str = None):
        if course_id not in self.cache[self.email]:
            raise Exception()
        if page_size >= 30:
            raise gcc_exceptions.ExceededLimitError()
        try:
            request = self.classroom.courses().teachers().list(courseId=course_id,
                                                               pageSize=page_size).execute()
            if page_token is not None:
                request.pageToken = page_token
            teacher = request.execute()
            return teacher
        except HttpError as error:
            print('An error occurred: %s' % error)




if __name__ == '__main__':
    gcc = Admin(email='liavt242@gmail.com')
    # liav = gcc.create_course(name='daniel', section='liav', description='liav', room='fee')
    # gcc.add_teacher(course_id=liav[0])
    # gcc.delete_teacher(course_id=542178731078, teacher_email='liavt242@gmail.com')
    print(gcc.get_teacher(course_id=588714514132, teacher_email='liavt242@gmail.com'))

