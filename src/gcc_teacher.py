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


    def create_announcement(self, course_id: str, announcement_text: str, materials: dict,
                            state: dict, scheduled_time: str, alternate_link: str = None,
                            creation_time: str = None, update_time: str = None, assignee_mode: dict = None,
                            individual_students_options: dict = None):
        """
        this func defines the create_announcement method, create an announcement with the following params

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
        :param announcement_text: sting

        :param materials: materials object
               https://developers.google.com/classroom/reference/rest/v1/courses.announcements#Announcement
               for object representation

        :return:
        """
        if state not in ['ANNOUNCEMENT_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
            raise gcc_exceptions.AnnouncementStateError()

        if not all(isinstance(param, str) for param in (announcement_text, course_id, creation_time,
                                                        assignee_mode, update_time, scheduled_time)):
            raise TypeError()

        announcement = {
            "text": announcement_text,
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
            self.classroom.courses().announcements().create(
                courseId=course_id,
                body=announcement
            ).execute()
            self._update_cache()
            return True
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False


    def delete_announcement(self, course_id: str, announcement_id: str) -> bool:
        """
        this func defines the delete_announcement method, delete an announcement with the following params
        see https://developers.google.com/classroom/reference/rest/v1/courses.announcements/delete
        for more info

        query-parameters = https://developers.google.com/classroom/reference/rest/v1/courses.announcements/delete#query-parameters

        :param course_id: course's id string
        :param announcement_id: announcement's id string
        :return:
        """
        if not all(isinstance(param, str) for param in (course_id, announcement_id)):
            raise TypeError()

        try:
            self.classroom.courses().announcements().delete(
                courseId=course_id,
                id=announcement_id
            )
            self._update_cache()
            return True
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False


    def get_announcement(self, course_id: str, announcement_id: str) -> dict | False:
        """
        this func defines the get_announcement method, get an announcement with the following params
        see https://developers.google.com/classroom/reference/rest/v1/courses.announcements/get
        for more info

        query-parameters = https://developers.google.com/classroom/reference/rest/v1/courses.announcements/get#query-parameters

        :param course_id: course's id string
        :param announcement_id: announcement's id string
        :return:
        """
        if not all(isinstance(param, str) for param in (course_id, announcement_id)):
            raise TypeError()
        try:
            request = self.classroom.courses().announcements().get(
                courseId=course_id,
                id=announcement_id
            )
            self._update_cache()
            return request
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False


    def list_announcements(self, ann_states: str, page_size: int = 10, order_by: str = None,
                           page_token: str = None) -> tuple | False:
        """
        this func defines the list_announcement method, get a list with all the announcements with the following params
        see https://developers.google.com/classroom/reference/rest/v1/courses.announcements/list
        for more info

        query-parameters = https://developers.google.com/classroom/reference/rest/v1/courses.announcements/list#query-parameters

        :param ann_states: https://developers.google.com/classroom/reference/rest/v1/courses.announcements#AnnouncementState
        :param page_size: Maximum number of items to return. Zero or unspecified indicates that the server may assign a maximum.
        :param order_by: Optional sort ordering for results
        :param page_token: https://developers.google.com/classroom/reference/rest/v1/courses.announcements/list#body.ListAnnouncementsResponse.FIELDS.next_page_token
        :return:
        """

        if not all(isinstance(param, str) for param in (ann_states, page_token, order_by)):
            raise TypeError()

        if ann_states not in ['ANNOUNCEMENT_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
            raise gcc_exceptions.AnnouncementStateError()

        query_params: dict = {}
        if ann_states:
            query_params['announcementStates'] = ann_states
        if order_by:
            query_params['orderBy'] = order_by
        if page_size:
            query_params['pageSize'] = str(page_size)
        if page_token:
            query_params['pageToken'] = page_token
        try:
            request = self.classroom.courses().announcements().list(**query_params).execute()
            announcements = request.get("courses", [])
            next_page_token = request.get("nextPageToken", None)
            self._update_cache()
            return announcements, next_page_token
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False


    def modify_assignees(self, course_id: str, announcement_id: str, assignee_mode: str,
                         add_student_ids: list[str], remove_student_ids: list[str]) -> dict | False:

        if not all(isinstance(param, str) for param in (course_id, announcement_id, assignee_mode)):
            raise TypeError()

        if assignee_mode not in ['ASSIGNEE_MODE_UNSPECIFIED', 'ALL_STUDENTS', 'INDIVIDUAL_STUDENTS']:
            raise gcc_exceptions.AssigneeModeError()

        announcement = {
            "assigneeMode": assignee_mode,
            "modifyIndividualStudentsOptions": {
                "addStudentIds": add_student_ids,
                "removeStudentIds": remove_student_ids
            }
        }

        try:
            request = self.classroom.courses().announcements().modify_assignment(
                courseId=course_id,
                id=announcement_id,
                body=announcement
            ).execute()

            return request

        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def patch_announcement(self, course_id: str, announcement_id: str, new_state: str = None,
                           new_text: str = None, new_scheduled_time: str = None):

        if not all(isinstance(param, str) for param in (course_id, announcement_id)):
            raise TypeError()

        announcement: dict = {}
        update_mask = ''

        if new_text:
            if not isinstance(new_state, str):
                raise TypeError()
            announcement['text'] = new_text
            update_mask += 'text,'

        if new_state:
            if new_state not in ['ANNOUNCEMENT_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
                raise gcc_exceptions.AnnouncementStateError()
            announcement['state'] = new_state
            update_mask += 'state,'

        if new_scheduled_time:
            if not isinstance(new_scheduled_time, str):
                raise TypeError()
            announcement['scheduledTime'] = new_scheduled_time
            update_mask += 'scheduledTime,'

        update_mask = update_mask.rstrip(',')

        try:
            request = self.classroom.courses().announcements().patch(
                courseId=course_id,
                id=announcement_id,
                updateMask=update_mask,
                body=announcement
            ).execute()
            return request
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False


if __name__ == '__main__':
    gcc = Teacher(role='teacher', email='liavt242@gmail.com')
