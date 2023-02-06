from gcc_base import GccBase
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

import re
from googleapiclient.errors import HttpError
import gcc_exceptions
import gcc_validators


class Teacher(GccBase):

    def __init__(self, role: str = 'teacher', ref_cache_month: int = 12,
                 email: str = None, work_space: str = None):
        if role != 'teacher':
            raise gcc_exceptions.InvalidRole()
        super().__init__(role, ref_cache_month, work_space, email)

    def create_announcement(self, course_id: str, announce_text: str, materials: object,
                            state: object, scheduled_time: str, alternate_link: str,
                            creation_time: str, update_time: str, assignee_mode: object,
                            individual_students_options: object):
        """
        :param individual_students_options: individual_students_options object
               https://developers.google.com/classroom/reference/rest/v1/IndividualStudentsOptions
               for object representation
               
        :param assignee_mode: 'string'
        :param update_time: 'string'
        :param creation_time: 'string'
        :param alternate_link: 'string'
        :param scheduled_time: 'string'
        :param state: announcement state 
               https://developers.google.com/classroom/reference/rest/v1/courses.announcements#AnnouncementState
                    
        :param course_id: string
        :param announce_text: sting

        :param materials: materials object
               https://developers.google.com/classroom/reference/rest/v1/courses.announcements#Announcement
               for object representation

        :return:
        """
        if state not in ['ANNOUNCEMENT_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
            raise gcc_exceptions.AnnouncementStateError()

        if not all(isinstance(param, str) for param in (announce_text, course_id, creation_time,
                                                        assignee_mode, update_time, scheduled_time)):
            raise TypeError()

        announcement = {
            "text": announce_text,
            "materials": [materials],
            "state": state,
            "alternateLink": alternate_link,
            "creationTime": creation_time,
            "updateTime": update_time,
            "scheduledTime": scheduled_time,
            "assigneeMode": assignee_mode,
            "individualStudentsOptions": {individual_students_options},
            "creatorUserId": self.check
        }
        try:
            request = self.classroom.courses().announcements().create(
                courseId=course_id,
                body=announcement
            ).execute()
            self._update_cache()
            return request
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)





if __name__ == '__main__':
    gcc = Teacher(role='teacher', email='liavt242@gmail.com')
