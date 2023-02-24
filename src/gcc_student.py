from googleapiclient.errors import HttpError

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


    def reclaim_submission(self, course_id: str, course_work_id: str, submission_id: str) -> bool:
        """

        :param course_id:
        :param course_work_id:
        :param submission_id:
        :return:
        """
        try:
            self.classroom.courses().courseWork().studentSubmissions().reclaim(
                courseId=course_id,
                courseWorkId=course_work_id,
                id=submission_id
            ).execute()
            return True
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False


    def tern_in_submission(self, c, course_id: str, course_work_id: str, submission_id: str) -> bool:
        """

        :param c:
        :param course_id:
        :param course_work_id:
        :param submission_id:
        :return:
        """
        try:
            self.classroom.courses().courseWork().studentSubmissions().ternIn(
                courseId=course_id,
                courseWorkId=course_work_id,
                id=submission_id
            ).execute()
            return True
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False
