import json

from gcc_base import GccBase
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

import gcc_exceptions
import gcc_validators


class Admin(GccBase):

    def __init__(self, email: str, path_to_creds: str, role: str = 'admin'):
        if role != 'admin':
            raise gcc_exceptions.InvalidRole()
        super().__init__(email, role, path_to_creds)
        if not gcc_validators.is_email(email):
            raise gcc_exceptions.InvalidEmail()
        self.__email: str = email

    @GccBase.cacher
    def detailed_create_course(self) -> tuple:
        """
        function that allows more detailed course creating
        :return:
        """
        classroom = build('classroom', 'v1', credentials=self.creds)
        with open('data/detailed_create_course.json', 'r') as fh:
            course_json = json.load(fh)
        course = classroom.courses().create(body=course_json).execute()
        print(f"""
        Created course: {course["name"]}
        Course id: {course["id"]}
        """)
        return course['id'], course["name"]


    @GccBase.cacher
    def create_course(self, name: str, section: str, description: str, room: str, owner_id='me', course_state: str = 'PROVISIONED'):
        if not all(isinstance(param, str) for param in (name, section, description, room, owner_id)):
            raise TypeError()
        if course_state.upper() not in ['PROVISIONED', 'ACTIVE', 'ARCHIVED', 'DECLINED', 'SUSPENDED']:
            raise gcc_exceptions.CourseStateError()
        if name in self.cache:
            raise gcc_exceptions.AlreadyInCache()

        classroom = build('classroom', 'v1', credentials=self.creds)
        course = {f"""
            'name': {name},
            'section': {section},
            'descriptionHeading': {description},
            'room': {room},
            'ownerId': {owner_id},
            'courseState': {course_state.upper()}
        """}
        course = classroom.courses().create(body=course).execute()
        print(f"""
        Created course: {course["name"]}
        Course id: {course["id"]}
        """)
        return course['id'], course["name"]


if __name__ == '__main__':
    # # Replace with your own Google API credentials
    gcc = Admin(email='liavt242@gmail.com', path_to_creds='data/credentials.json')
    course_id = gcc.create_course(name='liav', section='liav', description='liav', room='fee')

