from gcc_base import GccBase
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

import gcc_validators
import gcc_exceptions


class Student(GccBase):

    def __init__(self, email: str, role='student'):
        super().__init__(role)
        if not gcc_validators.is_email:
            raise gcc_exceptions.InvalidEmail()
        self.__email: str = email
