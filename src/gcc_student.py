from gcc_base import GccBase
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

import gcc_validators
import gcc_exceptions


class Student(GccBase):

    def __init__(self, role: str = 'student', ref_cache_month: int = 12,
                 email: str = None, work_space: str = None):

        if role != 'student':
            raise gcc_exceptions.InvalidRole()
        super().__init__(role, ref_cache_month, work_space, email)
