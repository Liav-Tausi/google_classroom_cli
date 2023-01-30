from gcc_base import GccBase
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

import re

import gcc_exceptions
import gcc_validators


class Student(GccBase):

    def __init__(self, email: str, path_to_creds: str, role: str = 'teacher'):
        if role != 'teacher':
            raise gcc_exceptions.InvalidRole()
        super().__init__(role, path_to_creds)
        if not gcc_validators.is_email(email):
            raise gcc_exceptions.InvalidEmail()
        self.__email: str = email
