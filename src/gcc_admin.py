import json

from gcc_base import GccBase
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import gcc_exceptions
import gcc_validators

import google.auth
from googleapiclient.errors import HttpError


class Admin(GccBase):

    def __init__(self, email: str, role: str = 'admin'):
        if role != 'admin':
            raise gcc_exceptions.InvalidRole()
        super().__init__(email, role)
        if not gcc_validators.is_email(email):
            raise gcc_exceptions.InvalidEmail()
        self.__email: str = email

    @GccBase.cacher
    def detailed_create_course(self) -> tuple:
        """
        function that allows more detailed course creating
        :return:
        """
        with open('data/detailed_create_course.json', 'r') as fh:
            course_json = json.load(fh)
        try:
            course = self.classroom.courses().create(body=course_json).execute()
            print(f"""
            Created course: {course["name"]}
            Course id: {course["id"]}
            """)
            return course['id'], course["name"]
        except HttpError as error:
            print('An error occurred: %s' % error)

    @GccBase.cacher
    def create_course(self, name: str, section: str, description: str, room: str, owner_id='me',
                      course_state: str = 'PROVISIONED'):
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
            course = self.classroom.courses().create(body=course).execute()
            print(f"""
                   Created course: {course["name"]}
                   Course id: {course["id"]}
                   """)
            return course['id'], course["name"]
        except HttpError as error:
            print('An error occurred: %s' % error)

    def add_teacher(self, course_id: int, teacher_email: str) -> True:
        # if course_id not in self.cache:
        #     raise gcc_exceptions.NotInCache()
        if not gcc_validators.is_email(teacher_email):
            raise gcc_exceptions.InvalidEmail()
        data: dict = {
                "userId": teacher_email
                }
        try:
            teachers = self.classroom.courses().teachers()
            teacher = teachers.create(courseId=course_id, body=data).execute()
            print('User %s was added as a teacher to the course with ID %s'
                  % (teacher.get('profile').get('name').get('fullName'),
                     course_id))
            return True
        except HttpError as error:
            print('An error occurred: %s' % error)


if __name__ == '__main__':
    gcc = Admin(email='liavt242@gmail.com')
    # liav = gcc.create_course(name='daniel', section='liav', description='liav', room='fee')
    gcc.add_teacher(course_id=542083844142, teacher_email=r'liavtest36@gmail.com')
