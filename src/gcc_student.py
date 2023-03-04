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
        this func defines the reclaim_submission, reclaims a student submission on behalf of the student that owns it.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions/reclaim
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param course_work_id: identifier of the course work. 'string'
        :param submission_id: identifier of the student submission. 'string'
        :return: bool
        """
        gcc_validators.are_params_in_cache(course_id, course_work_id, submission_id)
        gcc_validators.are_params_string(course_id, course_work_id, submission_id)
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


    def tern_in_submission(self, course_id: str, course_work_id: str, submission_id: str) -> bool:
        """
        this func defines the tern_in_submission, turns in a student submission.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions/turnIn
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param course_work_id: identifier of the course work. 'string'
        :param submission_id: identifier of the student submission. 'string'
        :return: bool
        """
        gcc_validators.are_params_in_cache(course_id, course_work_id, submission_id)
        gcc_validators.are_params_string(course_id, course_work_id, submission_id)
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
