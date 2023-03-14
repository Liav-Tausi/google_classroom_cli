import json

import os.path
from datetime import timedelta, date

from src import gcc_exceptions

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from src import gcc_validators

import logging

from googleapiclient.errors import HttpError

from src.conf import ini_config


class GccBase:
    # ___Main_EndPoints___ #
    __SERVICE_ENDPOINT: str = r'https://classroom.googleapis.com'

    # ___Scopes ___ #
    __ADMIN_SCOPES: dict[str, str] = {
        "courses": r"https://www.googleapis.com/auth/classroom.courses",
        # "class_rosters": "https://www.googleapis.com/auth/classroom.rosters",
        # "profile_emails": r"https://www.googleapis.com/auth/classroom.profile.emails",
        # "profile_photos": r"https://www.googleapis.com/auth/classroom.profile.photos",
    }

    __TEACHER_SCOPES: dict[str, str] = {
        "announcements": r"https://www.googleapis.com/auth/classroom.announcements",
        "courses": r"https://www.googleapis.com/auth/classroom.courses",
        "coursework_students": r"https://www.googleapis.com/auth/classroom.coursework.students",
        "guardians_for_students": r"https://www.googleapis.com/auth/classroom.guardianlinks.students",
        # "profile_emails": r"https://www.googleapis.com/auth/classroom.profile.emails",
        # "profile_photos": r"https://www.googleapis.com/auth/classroom.profile.photos",
        "push_notifications": r"https://www.googleapis.com/auth/classroom.push-notifications",
        # "class_rosters": r"https://www.googleapis.com/auth/classroom.rosters",
        "student_submissions": r"https://www.googleapis.com/auth/classroom.student-submissions.students.readonly",
        "topics": r"https://www.googleapis.com/auth/classroom.topics"
    }

    __STUDENT_SCOPES: dict[str, str] = {
        "courses_readonly": r"https://www.googleapis.com/auth/classroom.courses.readonly",
        "coursework_me": r"https://www.googleapis.com/auth/classroom.coursework.me",
        "guardians": r"https://www.googleapis.com/auth/classroom.guardianlinks.me.readonly",
        # "profile_emails": r"https://www.googleapis.com/auth/classroom.profile.emails",
        # "profile_photos": r"https://www.googleapis.com/auth/classroom.profile.photos",
        "push_notifications": r"https://www.googleapis.com/auth/classroom.push-notifications",
        # "class_rosters_readonly": r"https://www.googleapis.com/auth/classroom.rosters.readonly",
        "student_submissions_me": r"https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
        "topics_readonly": r"https://www.googleapis.com/auth/classroom.topics.readonly"
    }

    def __init__(self, role: str, ref_cache_month: int = 12,
                 work_space: str = None, email: str = None):

        self.__logger = logging.getLogger(__name__)

        self.__creds = None

        if email:
            if not gcc_validators.is_email(email):
                raise gcc_exceptions.InvalidEmail()
            self.__email: str = email
        else:
            self.__email = None

        if work_space:
            if not gcc_validators.is_work_space_email(work_space):
                raise gcc_exceptions.InvalidWorkSpace()
            self.__workspace: str = work_space
        else:
            self.__workspace = None

        if not email and not work_space:
            raise gcc_exceptions.InvalidParams()

        if ref_cache_month < 1:
            ref_cache_month = 1
        ref_date = date.today() + timedelta(weeks=4 * ref_cache_month)
        self.__ref_cache_month: date.month = ref_date.month

        self.__role: str = role.lower()
        if self.__role not in ['student', 'teacher', 'admin']:
            raise gcc_exceptions.UserError()
        else:
            if self.__role == 'student':
                scopes = self.student_scopes
            elif self.__role == 'teacher':
                scopes = self.teacher_scopes
            elif self.__role == 'admin':
                scopes = self.admin_scopes
            else:
                raise gcc_exceptions.ScopeError()

        self.__creds = None
        if os.path.exists(f'data_endpoint/{self.__role}_token.json'):
            self.__creds = Credentials.from_authorized_user_file(f'data_endpoint/{self.__role}_token.json',
                                                                 scopes=list(scopes))

        if not self.__creds or not self.__creds.valid:
            if self.__creds and self.__creds.expired and self.__creds.refresh_token:
                self.__creds.refresh(Request())
            else:
                credentials_account_file = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file=credentials_account_file,
                                                                 scopes=list(scopes))
                self.__creds = flow.run_local_server(port=0)
            with open(f'data_endpoint/{self.__role}_token.json', 'w', encoding='utf-8') as token:
                token.write(self.__creds.to_json())

        # ___limitations___ #
        self.__limits: dict = dict()

        # ___ cache ___ #
        self.__cache: dict = dict()

        # ___classroom___#
        self.__classroom = build('classroom', 'v1', credentials=self.creds)

        try:
            if not os.path.exists('data_endpoint/gcc_cache.json'):
                with open('data_endpoint/gcc_cache.json', 'a', encoding='utf-8') as fh:
                    data: dict = dict()
                    json.dump(data, fh)
            else:
                with open('data_endpoint/gcc_cache.json', 'r', encoding='utf-8') as fh1:
                    data = json.load(fh1)
                    if isinstance(data, dict):
                        self.__cache = data
        except FileNotFoundError:
            self.__cache: dict = dict()

        if self.__workspace:
            check = self.__workspace
        else:
            check = self.__email

        self.__check = check

    @property
    def check(self):
        return self.__check

    @property
    def classroom(self):
        return self.__classroom

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

    @property
    def ref_cache_month(self):
        return self.__ref_cache_month

    @property
    def cache(self):
        return self.__cache

    @property
    def logger(self):
        return self.__logger

    def set_limits(self):
        self.__limits = ini_config.get_config(filename='conf/personal_config.ini', section='usage_limits')

    @gcc_validators.validate_params(str)
    def _accept_invitation(self, invitation_id: str) -> bool:
        """
        this func defines the accept_invitation method, Accepts an invitation.
        removing it and adding the invited user to the teachers or students (as appropriate) of the specified course.
        Only the invited user may accept an invitation.
        see https://developers.google.com/classroom/reference/rest/v1/courses.teachers/list
        for more info

        :param invitation_id: Identifier of the invitation to accept.
        :return: bool

        """
        try:
            self.classroom.courses().invitations().accept(id=invitation_id).execute()
            return True
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @staticmethod
    def save_cache(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            finally:
                with open('data_endpoint/gcc_cache.json', 'w', encoding='utf-8') as fh:
                    json.dump(args[0].cache, fh)

        return wrapper

    @save_cache
    def _update_cache(self):

        with open('data_endpoint/gcc_cache.json', 'r', encoding='utf-8') as fh:
            fh.read()
            results = self.classroom.courses().list(pageSize=100).execute()
            courses = results.get('courses', [])
            self.__cache[self.check] = courses
