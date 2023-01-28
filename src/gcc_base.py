from __future__ import print_function

import os.path
from abc import ABC

import gcc_exceptions
from src.configs import ini_config

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials


class GccBase(ABC):
    # ___Main_EndPoints___ #
    __SERVICE_ENDPOINT: str = r'https://classroom.googleapis.com'

    # ___Scopes ___ #
    __ADMIN_SCOPES: dict[str, str] = {
        "courses": r"https://www.googleapis.com/auth/classroom.courses"
    }

    __TEACHER_SCOPES: dict[str, str] = {
        "announcements": r"https://www.googleapis.com/auth/classroom.announcements",
        "courses": r"https://www.googleapis.com/auth/classroom.courses",
        "coursework_students": r"https://www.googleapis.com/auth/classroom.coursework.students",
        "guardians_for_students": r"https://www.googleapis.com/auth/classroom.guardianlinks.students",
        "profile_emails": r"https://www.googleapis.com/auth/classroom.profile.emails",
        "profile_photos": r"https://www.googleapis.com/auth/classroom.profile.photos",
        "push_notifications": r"https://www.googleapis.com/auth/classroom.push-notifications",
        "class_rosters": r"https://www.googleapis.com/auth/classroom.rosters",
        "student_submissions": r"https://www.googleapis.com/auth/classroom.student-submissions.students.readonly",
        "topics": r"https://www.googleapis.com/auth/classroom.topics"
    }

    __STUDENT_SCOPES: dict[str, str] = {
        "courses_readonly": r"https://www.googleapis.com/auth/classroom.courses.readonly",
        "coursework_me": r"https://www.googleapis.com/auth/classroom.coursework.me",
        "guardians": r"https://www.googleapis.com/auth/classroom.guardianlinks.me.readonly",
        "profile_emails": r"https://www.googleapis.com/auth/classroom.profile.emails",
        "profile_photos": r"https://www.googleapis.com/auth/classroom.profile.photos",
        "push_notifications": r"https://www.googleapis.com/auth/classroom.push-notifications",
        "class_rosters_readonly": r"https://www.googleapis.com/auth/classroom.rosters.readonly",
        "student_submissions_me": r"https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
        "topics_readonly": r"https://www.googleapis.com/auth/classroom.topics.readonly"
    }

    def __init__(self, role: str):
        self.__role: str = role.lower()

        if self.__role not in ['student', 'teacher', 'admin']:
            raise gcc_exceptions.UserError()
        else:
            match self.__role:
                case 'student':
                    scopes = self.student_scopes
                case 'teacher':
                    scopes = self.teacher_scopes
                case 'admin':
                    scopes = self.admin_scopes


        self.__credentials: 'InstalledAppFlow' = InstalledAppFlow.from_client_secrets_file(
            'data/credentials.json', scopes=list(scopes)
        )
        if os.path.exists(f'data/{self.__role}_token.json'):
            self.__creds = Credentials.from_authorized_user_file(f'data/{self.__role}_token.json',
                                                                 scopes=list(scopes))
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.__creds.refresh(Request())
            else:
                self.__creds = self.credentials.run_local_server(port=0)
            with open(f'data/{self.__role}_token.json', 'w') as token:
                token.write(self.creds.to_json())

    @property
    def credentials(self) -> 'InstalledAppFlow':
        return self.__credentials

    @property
    def creds(self):
        return self.__creds

    @property
    def teacher_scopes(self):
        return self.__TEACHER_SCOPES.values()

    @property
    def student_scopes(self):
        return self.__STUDENT_SCOPES.values()

    @property
    def admin_scopes(self):
        return self.__ADMIN_SCOPES.values()

    def get_params(self):
        return ini_config.get_config('configs/personal_config.ini', 'usage_limits')


if __name__ == '__main__':
    GccBase(role='teacher').get_params()
