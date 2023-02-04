from __future__ import print_function

import functools
import json

import os.path
from abc import ABC
import time
from datetime import timedelta, date

import gcc_exceptions
from conf import ini_config


from google.oauth2 import service_account

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from src import gcc_validators


class GccBase(ABC):
    # ___Main_EndPoints___ #
    __SERVICE_ENDPOINT: str = r'https://classroom.googleapis.com'

    # ___Scopes ___ #
    __ADMIN_SCOPES: dict[str, str] = {
        "courses": r"https://www.googleapis.com/auth/classroom.courses",
        "class_rosters": "https://www.googleapis.com/auth/classroom.rosters",
        "profile_emails": r"https://www.googleapis.com/auth/classroom.profile.emails",
        "profile_photos": r"https://www.googleapis.com/auth/classroom.profile.photos",
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

    def __init__(self, role: str, ref_cache_month: int = 12,
                 work_space: str = None, email: str = None):

        self.__creds = None

        if email != 'me':
            if not gcc_validators.is_email(email):
                raise gcc_exceptions.InvalidEmail()
            self.__email: str = email
        else:
            self.__email: None = None

        if work_space:
            if not gcc_validators.is_work_space_email(work_space):
                raise gcc_exceptions.InvalidWorkSpace()
            self.__workspace: str = work_space
        else:
            self.__workspace: None = None

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
            match self.__role:
                case 'student':
                    scopes = self.student_scopes
                case 'teacher':
                    scopes = self.teacher_scopes
                case 'admin':
                    scopes = self.admin_scopes


        self.__creds = None
        if os.path.exists(f'data/{self.__role}_token.json'):
            self.__creds = Credentials.from_authorized_user_file(f'data/{self.__role}_token.json',
                                                                 scopes=list(scopes))


        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.__creds.refresh(Request())
            else:
                credentials_account_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file=credentials_account_file,
                                                                 scopes=list(scopes))
                self.__creds = flow.run_local_server(port=0)

                # with open(r'C:\Users\liavt\PycharmProjects\google_classroom_cli\src\data\rosy-gantry-375713-a11bab60d294.json', 'r') as fh:
                #     key = json.load(fh)
                # self.__creds = service_account.Credentials.from_service_account_info(key, scopes=list(scopes))
            with open(f'data/{self.__role}_token.json', 'w', encoding='utf-8') as token:
                token.write(self.creds.to_json())


        # ___limitations___ #
        self.__limits: dict = dict()

        # ___ cache ___ #
        self.__cache: dict = dict()

        # ___classroom___#
        self.__classroom = build('classroom', 'v1', credentials=self.creds)

        try:
            if not os.path.exists('data/gcc_cache.json'):
                with open('data/gcc_cache.json', 'a', encoding='utf-8') as fh:
                    data: dict = dict()
                    json.dump(data, fh)
            else:
                with open('data/gcc_cache.json', 'r', encoding='utf-8') as fh1:
                    data = json.load(fh1)
                    if isinstance(data, dict):
                        self.__cache = data
        except FileNotFoundError:
            self.__cache: dict = dict()

    @property
    def classroom(self):
        return self.__classroom

    @property
    def creds(self):
        return self.__creds

    @property
    def email(self):
        return self.__email

    @property
    def workspace(self):
        return self.__workspace

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

    def set_limits(self):
        self.__limits = ini_config.get_config(filename='conf/personal_config.ini', section='usage_limits')

    @staticmethod
    def cacher(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]
            now = time.time()
            result = func(*args, **kwargs)
            course_id = result[0]
            if self.email not in self.__cache:
                self._update_cache(result, now)
            else:
                cache = self.__cache[self.email]
                if course_id in cache:
                    cache_time = cache[course_id]['cache_time']
                    age = (now - cache_time) / (60 * 60 * 24 * 30)
                    if age >= self.ref_cache_month:
                        cache.pop(course_id, None)
                        if not cache:
                            self.__cache.pop(self.email, None)
                    else:
                        cache[course_id]['cache_time'] = now
                else:
                    self._update_cache(result, now)
            return result
        return wrapper


    @staticmethod
    def save_cache(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            finally:
                with open('data/gcc_cache.json', 'w', encoding='utf-8') as fh:
                    json.dump(args[0].cache, fh)
        return wrapper


    @save_cache
    def _update_cache(self, result, now=None, add_teacher: bool = False, del_teacher: bool = False):
        course_id, course_name, teacher_email = result
        if self.email not in self.__cache:
            self.__cache[self.email] = {}
        if course_id not in self.__cache[self.email] and not del_teacher:
            self.__cache[self.email][course_id] = {
                'course_id': course_id,
                'course_name': course_name,
                'teachers': [teacher_email]
            }
        if add_teacher is True and teacher_email \
                not in self.__cache[self.email][course_id]['teachers']:

            self.__cache[self.email][course_id]['teachers'].append(teacher_email)
            self.__cache[self.email][course_id]['cache_time'] = now

        if del_teacher is True and str(course_id) in self.__cache[self.email]:
            self.__cache[self.email][course_id]['teachers'].remove(teacher_email)

            with open('data/gcc_cache.json', 'r', encoding='utf-8') as fh:
                gcc_cache = json.load(fh)

            if self.email in gcc_cache and course_id in gcc_cache[self.email]:
                gcc_cache[self.email][(str(course_id))]['teachers'] = list()





