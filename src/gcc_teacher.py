import datetime
import json
import pytz

from src.gcc_base import GccBase
from googleapiclient.errors import HttpError
from src import gcc_exceptions
from src import gcc_validators

__all__ = [
    'Teacher'
]


class Teacher(GccBase):

    def __init__(self, role: str = 'teacher', ref_cache_month: int = 12,
                 email: str = None, work_space: str = None):
        if role != 'teacher':
            raise gcc_exceptions.InvalidRole()
        super().__init__(role, ref_cache_month, work_space, email)

    def detailed_create_announcement(self, detailed_json: bool = False)-> dict or False:
        """
        this func defines the detailed_create_announcement method, creates a detailed announcement
        see https://developers.google.com/classroom/reference/rest/v1/courses.announcements/create
        for more info

        :return:
        """
        if not detailed_json:
            raise gcc_exceptions.AnnouncementJsonEmpty()

        with open("templates/detailed_announcement.json", 'r', encoding='utf-8') as fh:
            body = json.load(fh)
        try:
            response: dict = self.classroom.courses().announcements().create(**body).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str, dict, str, str)
    def quick_create_announcement(self, course_id: str, announcement_text: str, materials: dict, state: str,
                                  scheduled_time: str, update_time: str = None, assignee_mode: dict = None,
                                  students_options: list = None)-> dict or False:
        """
        this func defines the create_announcement method, create an announcement with the following params

        :param students_options: individual_students_options object
               https://developers.google.com/classroom/reference/rest/v1/IndividualStudentsOptions
               for object representation
               
        :param assignee_mode: Status of this announcement. If unspecified, the default state is DRAFT. 'string'
        :param update_time: Timestamp of the most recent change to this announcement. 'string'
        :param scheduled_time: 'string'
        :param state: announcement state
               https://developers.google.com/classroom/reference/rest/v1/courses.announcements#AnnouncementState
                    
        :param course_id: either identifier of the course or assigned alias. 'string'
        :param announcement_text: sting

        :param materials: materials object
               https://developers.google.com/classroom/reference/rest/v1/courses.announcements#Announcement
               for object representation

        :return: True
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        if state not in ['ANNOUNCEMENT_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
            raise gcc_exceptions.AnnouncementStateError()

        if assignee_mode not in ['ASSIGNEE_MODE_UNSPECIFIED', 'ALL_STUDENTS', 'INDIVIDUAL_STUDENTS']:
            raise gcc_exceptions.AssigneeModeError()

        announcement = {
            "text": announcement_text,
            "materials": [materials],
            "state": state,
            "updateTime": update_time,
            "scheduledTime": scheduled_time,
            "assigneeMode": assignee_mode,
            "individualStudentsOptions": {
                "studentIds": students_options
            },
            "creatorUserId": self.check
        }
        try:
            response: dict = self.classroom.courses().announcements().create(
                courseId=course_id,
                body=announcement
            ).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def delete_announcement(self, course_id: str, announcement_id: str) -> bool:
        """
        this func defines the delete_announcement method, delete an announcement with the following params
        see https://developers.google.com/classroom/reference/rest/v1/courses.announcements/delete
        for more info

        query-parameters = https://developers.google.com/classroom/reference/rest/v1/courses.announcements/delete#query-parameters

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param announcement_id: Announcement's id 'string'
        :return: True
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

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

    @gcc_validators.validate_params(str, str)
    def get_announcement(self, course_id: str, announcement_id: str):
        """
        this func defines the get_announcement method, get an announcement with the following params
        see https://developers.google.com/classroom/reference/rest/v1/courses.announcements/get
        for more info

        query-parameters = https://developers.google.com/classroom/reference/rest/v1/courses.announcements/get#query-parameters

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param announcement_id: announcement's id 'string'
        :return: response dict | False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        try:
            response: dict = self.classroom.courses().announcements().get(
                courseId=course_id,
                id=announcement_id
            )
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def list_announcements(self, states: str, page_size: int = 10, order_by: str = None,
                           page_token: str = None):
        """
        this func defines the list_announcement method, get a list with all the announcements with the following params
        see https://developers.google.com/classroom/reference/rest/v1/courses.announcements/list
        for more info

        query-parameters = https://developers.google.com/classroom/reference/rest/v1/courses.announcements/list#query-parameters

        :param states: https://developers.google.com/classroom/reference/rest/v1/courses.announcements#AnnouncementState
        :param page_size: Maximum number of items to return. Zero or unspecified indicates that the server may assign a maximum.
        :param order_by: Optional sort ordering for results
        :param page_token: https://developers.google.com/classroom/reference/rest/v1/courses.announcements/list#body.ListAnnouncementsResponse.FIELDS.next_page_token
        :return: response dict | False
        """
        query_params: dict = dict()

        if states:
            if states not in ['ANNOUNCEMENT_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
                raise gcc_exceptions.AnnouncementStateError()
            query_params['announcementStates'] = states

        if order_by:
            gcc_validators.are_params_string(order_by)
            query_params['orderBy'] = order_by

        if page_size:
            gcc_validators.are_params_int(page_size)
            if page_size >= 100:
                raise ValueError("Page size cannot be more than 100.")
            query_params['pageSize'] = page_size

        if page_token:
            gcc_validators.are_params_string(page_token)
            query_params['nextPageToken'] = page_token

        try:
            response = self.classroom.courses().announcements().list(**query_params)
            announcements = response.get("courses", [])
            next_page_token = response.get("nextPageToken", None)

            return {"announcements": announcements, "next_page_token": next_page_token}
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str, str)
    def modify_announcement_assignees(self, course_id: str, announcement_id: str, assignee_mode: str,
                                      add_student_ids: list[str] = None,
                                      remove_student_ids: list[str] = None) -> dict or False:
        """
        this func defines the modify_assignees method, modifies assignee mode and options of an announcement.
        see https://developers.google.com/classroom/reference/rest/v1/courses.announcements/modifyAssignees
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param announcement_id: Identifier of the announcement. 'string'
        :param assignee_mode: modes of assigning coursework/announcements. ['ASSIGNEE_MODE_UNSPECIFIED',
                                                                            'ALL_STUDENTS',
                                                                            'INDIVIDUAL_STUDENTS']
        :param add_student_ids: Set which students can view or cannot view the announcement.
        :param remove_student_ids: Set which students can view or cannot view the announcement.
        :return: response dict | False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        if assignee_mode not in ['ASSIGNEE_MODE_UNSPECIFIED', 'ALL_STUDENTS', 'INDIVIDUAL_STUDENTS']:
            raise gcc_exceptions.AssigneeModeError()

        body: dict = {
            "assigneeMode": assignee_mode,
            "modifyIndividualStudentsOptions": {
                "addStudentIds": add_student_ids,
                "removeStudentIds": remove_student_ids
            }
        }

        try:
            response: dict = self.classroom.courses().announcements().modify_assignment(
                courseId=course_id,
                id=announcement_id,
                body=body
            ).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def detailed_patch_announcement(self, detailed_json: bool = False) -> dict or False:
        """
        this func defines the detailed_patch_announcement method, modifies detailed options of an announcement.
        see https://developers.google.com/classroom/reference/rest/v1/courses.announcements/patch
        for more info

        param: detailed_json: flag for indication if json is full True if not False 'bool'
        :return: response dict | False
        """
        if not detailed_json:
            raise gcc_exceptions.AnnouncementJsonEmpty()

        with open('templates/detailed_announcement.json', 'r', encoding='utf-8') as fh:
            body = json.load(fh)
        try:
            response: dict = self.classroom.courses().announcements().create(**body).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def quick_patch_announcement(self, course_id: str, announcement_id: str, state: str = None,
                                 text: str = None, scheduled_time: str = None) -> dict or False:
        """
        this func defines the patch_announcement method, updates one or more fields of an announcement.
        see https://developers.google.com/classroom/reference/rest/v1/courses.announcements/patch
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param announcement_id: Identifier of the announcement. 'string'
        :param state: new announcement state ['ANNOUNCEMENT_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']
        :param text: new announcement text
        :param scheduled_time: new scheduled time
        :return: response dict | False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        body: dict = dict()

        if text:
            gcc_validators.are_params_string(state)
            body['text'] = text

        if state:
            if state not in ['ANNOUNCEMENT_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
                raise gcc_exceptions.AnnouncementStateError()
            body['state'] = state

        if scheduled_time:
            if isinstance(scheduled_time, datetime.datetime) and \
                    scheduled_time.tzinfo == pytz.utc:
                raise gcc_exceptions.TimeStampError()
            body['scheduledTime'] = scheduled_time

        update_mask: str = ','.join(body.keys())

        try:
            response: dict = self.classroom.courses().announcements().patch(
                courseId=course_id,
                id=announcement_id,
                updateMask=update_mask,
                body=body
            ).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def detailed_course_work_create(self, detailed_json: bool = False) -> dict or False:
        """
        this func defines the detailed_course_work_create method, creates course work..
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork/create
        for more info

        for detailed_course_work_create method the "detailed_course_work.json" stored at the data_endpoint directory should be filled!!
        for more info: https://developers.google.com/classroom/reference/rest/v1/courses.courseWork#CourseWork

        :param detailed_json: flag for indication if json is full True if not False 'bool'
        :return: response dict or False

        """
        if not detailed_json:
            raise gcc_exceptions.CourseWorkJsonEmpty()

        with open('templates/detailed_course_work.json', 'r', encoding='utf-8') as fh:
            body = json.load(fh)
        try:
            response: dict = self.classroom.courses().courseWork().create(**body).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str, str, list, str, str)
    def quick_course_work_create(self, course_id: str, title: str, description: str,
                                 material: dict, work_type: str, state: str) -> dict or False:
        """
        this func defines the quick_course_work_create method, creates course work..
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork/create
        for more info

        :param material: a list with a martial object see: https://developers.google.com/classroom/reference/rest/v1/Material
        :param state: the state of the course_work see: https://developers.google.com/classroom/reference/rest/v1/courses.courseWork#CourseWorkState
        :param work_type: type of the course_work see: https://developers.google.com/classroom/reference/rest/v1/CourseWorkType
        :param description: a course_work description 'string'
        :param title: a course_work title 'string'
        :param course_id: either identifier of the course or assigned alias. 'string'
        :return: response dict or False

        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        if state not in ['COURSE_WORK_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
            raise gcc_exceptions.CourseWorkStateError()

        if work_type not in ['COURSE_WORK_TYPE_UNSPECIFIED', 'ASSIGNMENT',
                             'SHORT_ANSWER_QUESTION', 'MULTIPLE_CHOICE_QUESTION']:
            raise gcc_exceptions.CourseWorkTypeError()

        body: dict = {
            'title': title,
            'description': description,
            'materials': [material],
            'workType': work_type,
            'state': state,
        }
        try:
            response: dict = self.classroom.courses().courseWork().create(
                courseId=course_id,
                body=body
            ).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def delete_course_work(self, course_id: str, course_work_id: str) -> bool:
        """
        this func defines the delete_course_work method, deletes course work..
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork/delete
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param course_work_id: identifier of the course work. 'string'
        :return: True or False 'bool'
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        try:
            self.classroom.courses().courseWork().delete(
                courseId=course_id,
                id=course_work_id
            ).execute()
            self._update_cache()
            return True
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def get_course_work(self, course_id: str, course_work_id: str) -> dict or False:
        """
        this func defines the get_course_work method, gets course work..
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork/get
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param course_work_id: identifier of the course work. 'string'
        :return: True or False 'bool'
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        try:
            response = self.classroom.courses().courseWork().get(
                courseId=course_id,
                id=course_work_id
            ).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str)
    def list_course_work(self, course_id: str, states: list[str] = None,
                         order_by: str = 'updateTime desc', page_size: int = 10,
                         page_token: str = None) -> tuple[list[dict], str] or False:
        """
        this func defines the get_course_work method, Returns a list of course work that the requester is permitted to view.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork/list
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'

        :param states: Restriction on the work status to return. Only courseWork that matches is returned.
                                   If unspecified, items with a work status of PUBLISHED is returned.

        :param page_size: Maximum number of items to return. Zero or unspecified indicates that the server may assign a maximum.
        :param order_by: Optional sort ordering for results
        :param page_token: Token identifying the next page of results to return. If empty, no further results are available 'string'
        :return: Tuple with a list of course work and nextPageToken value
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        query_params = {'courseId': course_id}

        if states:
            for state in states:
                if state not in ['COURSE_WORK_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
                    raise gcc_exceptions.CourseWorkStateError()
            query_params['courseWorkStates'] = states

        if order_by:
            gcc_validators.are_params_string(order_by)
            query_params['orderBy'] = order_by

        if page_size:
            gcc_validators.are_params_int(page_size)
            if page_size >= 100:
                raise ValueError("Page size cannot be more than 100.")
            query_params['pageSize'] = page_size

        if page_token:
            gcc_validators.are_params_string(page_token)
            query_params['nextPageToken'] = page_token

        try:
            response = self.classroom.courses().courseWork().list(**query_params)
            course_work_list = response.get("courseWork", [])
            next_page_token = response.get("nextPageToken", None)

            return {"course_work_list": course_work_list, "next_page_token": next_page_token}
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str, str)
    def modify_course_work_assignees(self, course_id: str, course_work_id: str, assignee_mode: str,
                                     add_student_ids: list[str] = None,
                                     remove_student_ids: list[str] = None) -> dict or False:
        """
        this func defines the modify_assignees method, Modifies assignee mode and options of a coursework.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork/modifyAssignees
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param course_work_id: Identifier of the course_work. 'string'
        :param assignee_mode: modes of assigning coursework/announcements. ['ASSIGNEE_MODE_UNSPECIFIED',
                                                                            'ALL_STUDENTS',
                                                                            'INDIVIDUAL_STUDENTS']
        :param add_student_ids: Set which students can view or cannot view the courseWork.
        :param remove_student_ids: Set which students can view or cannot view the courseWork.
        :return: response dict | False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        if assignee_mode not in ['ASSIGNEE_MODE_UNSPECIFIED', 'ALL_STUDENTS', 'INDIVIDUAL_STUDENTS']:
            raise gcc_exceptions.AssigneeModeError()

        body: dict = {
            "assigneeMode": assignee_mode,
            "modifyIndividualStudentsOptions": {
                "addStudentIds": add_student_ids,
                "removeStudentIds": remove_student_ids
            }
        }

        try:
            response: dict = self.classroom.courses().courseWork().modify_assignment(
                courseId=course_id,
                id=course_work_id,
                body=body
            ).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def detailed_patch_course_work(self, detailed_json: bool = False) -> dict or False:
        """
        this func defines the detailed_patch_course_work method, updates one or more fields of a course work.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork/patch
        for more info

        :param detailed_json: detailed course_json needs to be full
        :return: response dict or False
        """

        if not detailed_json:
            raise gcc_exceptions.CourseWorkJsonEmpty()

        with open('templates/detailed_course.json', 'r', encoding='utf-8') as fh:
            body = json.load(fh)

        update_mask = ','.join(body.keys())
        try:
            response: dict = self.classroom.courses().courseWork().patch(
                **body,
                updateMask=update_mask,
            ).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def quick_patch_course_work(self, course_id: str, course_work_id: str, title: str = None,
                                description: str = None, due_date: dict = None, due_time: dict = None,
                                scheduled_time: str = None, states: list[str] = None,
                                materials: dict = None) -> dict or False:
        """
        this func defines the quick_patch_course_work, updates one or more fields of a course work.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork/patch
        for more info

        :param scheduled_time: https://protobuf.dev/reference/protobuf/google.protobuf/#timestamp 'datetime.datetime'
        :param due_time: Optional date, in UTC, that submissions for this course work are due.

                         This must be specified if dueTime is specified.
        :param due_date: Optional time of day, in UTC, that submissions for this course work are due.
                         This must be specified if dueDate is specified.

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param course_work_id: either identifier of the course_work or assigned alias. 'string'
        :param title: Title of this course work. The title must be a valid UTF-8 string containing between 1 and 3000 characters. 'string'
        :param description: Optional description of this course work. If set,
                            the description must be a valid UTF-8 string containing no more than 30,000 characters. 'string'

        :param states: State of the course. If unspecified, the default state is PROVISIONED.
                      see https://developers.google.com/classroom/reference/rest/v1/courses#CourseState

        :param materials: Additional materials. Course must have no more than 20 material items. 'list[material]'
                         see https://developers.google.com/classroom/reference/rest/v1/Material
        :return: response dict or False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        body: dict = dict()

        if title:
            gcc_validators.are_params_string(title)
            body['title'] = title

        if description:
            gcc_validators.are_params_string(description)
            body['description'] = description

        if due_date:
            if isinstance(due_date, dict):
                raise TypeError()
            body['dueDate'] = due_date

        if due_time:
            if isinstance(due_time, dict):
                raise TypeError()
            body['dueTime'] = due_date

        if scheduled_time:
            if isinstance(scheduled_time, datetime.datetime) and \
                    scheduled_time.tzinfo == pytz.utc:
                raise gcc_exceptions.TimeStampError()
            body['scheduledTime'] = scheduled_time

        if states:
            for state in states:
                if state not in ['COURSE_WORK_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
                    raise gcc_exceptions.CourseWorkStateError()
            body['state'] = states

        if materials:
            if isinstance(materials, list):
                raise TypeError()
            body['materials'] = [materials]

        update_mask: str = ','.join(body.keys())

        try:
            response: dict = self.classroom.courses().courseWork().patch(
                courseId=course_id,
                id=course_work_id,
                updateMask=update_mask,
                body=body
            ).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str, str)
    def get_student_submissions(self, course_id: str, course_work_id: str, submission_id: str) -> dict or False:
        """
        this func defines the get_student_submissions, returns a student submission.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions/get
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param course_work_id: identifier of the course work. 'string'
        :param submission_id: identifier of the student submission. 'string'
        :return: response dict or False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        try:
            response = self.classroom.courses().courseWork().studentSubmissions().get(
                courseId=course_id,
                courseWorkId=course_work_id,
                id=submission_id
            ).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def list_student_submissions(self, course_id: str, course_work_id: str, user_id: str = None,
                                 page_size: int = 10, sub_states: list[str] = 'SUBMISSION_STATE_UNSPECIFIED',
                                 late: str = 'LATE_VALUES_UNSPECIFIED', page_token: str = None) -> dict or False:
        """
        this func defines the list_student_submissions, Returns a list of student submissions that the requester is permitted to view,
        factoring in the OAuth scopes of the response. - may be specified as the courseWorkId to include student submissions
        for multiple course work items.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions/list
        for more info

        :param page_token: nextPageToken value returned from a previous list call,
                          indicating that the subsequent page of results should be returned.
                          The list response must be otherwise identical to the one that resulted in this token.

        :param page_size: maximum number of items to return. Zero or unspecified indicates that the server may assign a maximum. 'int'

        :param late: requested lateness value. if specified, returned student submissions are restricted by the requested value.
                     if unspecified, submissions are returned regardless of late value.

        :param user_id: optional argument to restrict returned student work to those owned by the student with the specified identifier.
                        the identifier can be one of the following: {
                            the numeric identifier for the user,
                            the email address of the user ,
                            the string literal "me" indicating the requesting user
                        }
        :param sub_states: requested submission states. If specified, returned student submissions match one of the specified submission states.

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param course_work_id: identifier of the course work. 'string'
        :return: response dict or False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)


        query_params: dict = dict()

        if user_id:
            gcc_validators.are_params_string(user_id)
            query_params['userId'] = user_id

        if sub_states:
            for state in sub_states:
                if state not in ['SUBMISSION_STATE_UNSPECIFIED', 'NEW', 'CREATED',
                                 'TURNED_IN', 'RETURNED', 'RECLAIMED_BY_STUDENT']:
                    raise gcc_exceptions.SubmissionStateError()
            query_params['states'] = sub_states

        if late:
            gcc_validators.are_params_string(late)
            for late_value in late:
                if late_value not in ['LATE_VALUES_UNSPECIFIED', 'LATE_ONLY', 'NOT_LATE_ONLY']:
                    raise gcc_exceptions.SubmissionLateValueError()
            query_params['late'] = late

        if page_size:
            gcc_validators.are_params_int(page_size)
            if page_size >= 100:
                raise ValueError("Page size cannot be more than 100.")
            query_params['pageSize'] = page_size

        if page_token:
            gcc_validators.are_params_string(page_token)
            query_params['nextPageToken'] = page_token

        try:
            response = self.classroom.courses().studentSubmissions().list(
                courseId=course_id,
                courseWorkId=course_work_id,
                **query_params
            ).execute()
            student_submissions = response.get("studentSubmissions", [])
            next_page_token = response.get("nextPageToken", None)

            return {"student_submissions": student_submissions, "next_page_token": next_page_token}
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str, str, dict)
    def modify_submissions_attachments(self, course_id: str, course_work_id: str, submission_id: str,
                                       materials: dict) -> dict or False:
        """
        this func defines the modify_submissions_attachments, modifies attachments of student submission..
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions/modifyAttachments
        for more info

        :param materials: attachments to add. A student submission may not have more than 20 attachments.
                          Form attachments are not supported.
                          see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions#Attachment

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param course_work_id: identifier of the course work. 'string'
        :param submission_id: identifier of the student submission. 'string'
        :return: response dict or False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        body: dict = {
            "addAttachments": [
                materials
            ]
        }
        try:
            response = self.classroom.courses().courseWork().studentSubmissions().modifyAttachments(
                courseId=course_id,
                courseWorkId=course_work_id,
                id=submission_id,
                body=body
            ).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def detailed_patch_student_submissions(self, detailed_json: bool = False) -> dict or False:
        """
        this func defines the detailed_patch_student_submissions, updates one or more fields of a student submission.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions/patch
        for more info

        :param detailed_json: flag for indication if json is full True if not False 'bool'
        :return: response dict or False
        """
        if not detailed_json:
            raise gcc_exceptions.StudentsSubmissionsJsonEmpty()

        with open('templates/detailed_students_submissions.json', 'r', encoding='utf-8') as fh:
            body = json.load(fh)

        update_mask = ','.join(body.keys())

        try:
            response: dict = self.classroom.courses().courseWork().studentSubmissions().patch(
                **body,
                updateMask=update_mask,
            ).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str, str)
    def quick_patch_student_submissions(self, course_id: str, course_work_id: str, submission_id: str,
                                        sub_states: list[str] = None, assigned_grade: int = None,
                                        short_answer: str = None, alternate_link: str = None,
                                        assignment_submission: dict = None) -> dict or False:
        """
        this func defines the quick_patch_student_submissions, updates one or more fields of a student submission.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions/patch
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param course_work_id: identifier of the course work. 'string'
        :param submission_id: identifier of the student submission. 'string'

        :param sub_states: requested submission states.
                          if specified, returned student submissions match one of the specified submission states.

        :param assigned_grade: optional grade. if unset, no grade was set. This value must be non-negative.
                               decimal (that is, non-integer) values are allowed, but are rounded to two decimal places.

        :param short_answer: submission content when courseWorkType is SHORT_ANSWER_QUESTION.
                             see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions#ShortAnswerSubmission

        :param alternate_link: absolute link to the submission in the Classroom web UI.

        :param assignment_submission: submission content when courseWorkType is ASSIGNMENT.
                                      see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions#AssignmentSubmission
        :return: response dict or False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        body: dict = dict()

        if sub_states:
            gcc_validators.are_params_string(sub_states)
            for state in sub_states:
                if state not in ['SUBMISSION_STATE_UNSPECIFIED', 'NEW', 'CREATED',
                                 'TURNED_IN', 'RETURNED', 'RECLAIMED_BY_STUDENT']:
                    raise gcc_exceptions.SubmissionStateError()
            body['state'] = sub_states

        if assigned_grade:
            gcc_validators.are_params_int(assigned_grade)
            body['assignedGrade'] = assigned_grade

        if short_answer:
            gcc_validators.are_params_string(short_answer)
            body['shortAnswerSubmission'] = {"answer": short_answer}

        if alternate_link:
            gcc_validators.are_params_string(alternate_link)
            body['alternateLink'] = alternate_link

        if assignment_submission:
            body['assignmentSubmission'] = {"attachments": [{assignment_submission}]}

        update_mask: str = ','.join(body.keys())

        try:
            response: dict = self.classroom.courses().courseWork().studentSubmissions().patch(
                courseId=course_id,
                courseWorkId=course_work_id,
                id=submission_id,
                updateMask=update_mask,
                body=body
            ).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str, str)
    def return_student_submissions(self, course_id: str, course_work_id: str, submission_id: str) -> dict or False:
        """
        this func defines the return_student_submissions, returns a student submission.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions/return
        for more info

         :param course_id: either identifier of the course or assigned alias. 'string'
        :param course_work_id: identifier of the course work. 'string'
        :param submission_id: identifier of the student submission. 'string'
        :return: response dict or False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        try:
            response = self.classroom.courses().courseWork().studentSubmissions().return_(
                courseId=course_id,
                courseWorkId=course_work_id,
                id=submission_id
            ).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def detailed_create_course_work_materials(self, detailed_json: bool = False) -> dict or False:
        """
        this func defines the detailed_create_course_work_materials, creates a course work material.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWorkMaterials/create
        for more info

        :param detailed_json: flag for indication if json is full True if not False 'bool'
        :return: response dict or False

        """
        if not detailed_json:
            raise gcc_exceptions.CourseWorkMaterialJsonEmpty()
        try:
            with open('templates/detailed_course_work_material.json', 'r', encoding='utf-8') as fh:
                body = json.load(fh)

            response = self.classroom.courses().courseWorkMaterials().create(**body).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str, str, list)
    def quick_create_course_work_materials(self, course_id: str, title: str, description: str,
                                           materials: dict) -> dict or False:
        """
        this func defines the quick_create_course_work_materials, creates a course work material.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWorkMaterials/create
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'

        :param title: title of this course work material. The title must be a valid UTF-8 string
                      containing between 1 and 3000 characters.

        :param description: optional description of this course work material.
                            The text must be a valid UTF-8 string containing no more than 30,000 characters.

        :param materials: additional materials.
                         a course work material must have no more than 20 material items.
                         see https://developers.google.com/classroom/reference/rest/v1/Material

        :return: response dict or False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        body: dict = {
            "title": title,
            "description": description,
            "materials": [materials]
        }
        try:
            response = self.classroom.courses().courseWorkMaterials().create(
                courseId=course_id,
                body=body
            ).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def delete_course_work_materials(self, course_id: str, c_w_m_id: str) -> bool:
        """
        this func defines the delete_course_work_materials, deletes a course work material.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWorkMaterials/delete
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param c_w_m_id: identifier of the course work material to delete. 'string'
        :return: bool
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        try:
            self.classroom.courses().courseWorkMaterials().delete(
                courseId=course_id,
                id=c_w_m_id
            ).execute()
            self._update_cache()
            return True
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def get_course_work_materials(self, course_id: str, c_w_m_id: str) -> dict or False:
        """
        this func defines the get_course_work_materials, returns a course work material.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWorkMaterials/get
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param c_w_m_id: identifier of the course work material to get. 'string'
        :return: response dict or False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        try:
            response = self.classroom.courses().courseWorkMatirials().get(
                courseId=course_id,
                id=c_w_m_id
            ).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str)
    def list_course_work_materials(self, course_id: str, c_w_m_states: list[str] = None, page_size: int = 10,
                                   page_token: str = None, order_by: str = None, material_link: str = None,
                                   material_drive_id: str = None) -> dict or False:
        """
        this func defines the list_course_work_materials, returns a list of course work material that the
        requester is permitted to view.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWorkMaterials/get
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'

        :param c_w_m_states: status of this course work material. If unspecified, the default state is DRAFT.
                            see https://developers.google.com/classroom/reference/rest/v1/courses.courseWorkMaterials#CourseWorkMaterialState

        :param page_size: maximum number of items to return. Zero or unspecified indicates that the server may assign a maximum.

        :param page_token: nextPageToken value returned from a previous list call, indicating that the subsequent page of results should be returned.

        :param order_by: optional sort ordering for results. a comma-separated list of fields with an optional sort direction keyword.
                         supported field is updateTime. Supported direction keywords are asc and desc.
                         if not specified, updateTime desc is the default behavior. Examples: updateTime asc, updateTime

        :param material_link: optional filtering for course work material with at least one link material whose URL partially matches the provided string.

        :param material_drive_id: optional filtering for course work material with at least one Drive material whose ID matches the provided string.
                                  if materialLink is also specified, course work material must have materials matching both filters.

        :return: response dict or False

        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        query_params: dict = dict()

        if c_w_m_states:
            for state in c_w_m_states:
                if state not in ['COURSEWORK_MATERIAL_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
                    raise gcc_exceptions.CourseWorkMaterialStateError()
            query_params['state'] = c_w_m_states

        if page_size:
            gcc_validators.are_params_int(page_size)
            if page_size >= 100:
                raise ValueError("Page size cannot be more than 100.")
            query_params['pageSize'] = page_size

        if page_token:
            gcc_validators.are_params_string(page_token)
            query_params['nextPageToken'] = page_token

        if order_by:
            gcc_validators.are_params_int(order_by)
            query_params['orderBy'] = order_by

        if material_link:
            gcc_validators.are_params_string(material_link)
            query_params['materialLink'] = material_link

        if material_drive_id:
            gcc_validators.are_params_string(material_drive_id)
            query_params['materialDriveId'] = material_drive_id

        try:
            response = self.classroom.courses().courseWorkMatirials().list(
                courseId=course_id,
                **query_params
            ).execute()
            course_work_material = response.get("courseWorkMaterial", [])
            next_page_token = response.get("nextPageToken", None)

            return {"course_work_material": course_work_material, "next_page_token": next_page_token}
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def detailed_patch_course_work_material(self, detailed_json: bool = False) -> dict or False:
        """
        this func defines the detailed_patch_course_work_material, updates one or more fields of a course work material.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWorkMaterials/patch
        for more info

        :param detailed_json: flag for indication if json is full True if not False 'bool'
        :return: bool

        """
        if not detailed_json:
            raise gcc_exceptions.CourseWorkMaterialJsonEmpty()

        with open('templates/detailed_course_work_material.json', 'r', encoding='utf-8') as fh:
            body = json.load(fh)
        try:
            response = self.classroom.courses().courseWorkMatirials().patch(**body).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def quick_patch_course_work_material(self, course_id: str, c_w_m_id: str, title: str = None, material: dict = None,
                                         description: str = None, scheduled_time: str = None, states: list[str] = None,
                                         individual_students_options: list[str] = None) -> dict or False:
        """
        this func defines the quick_patch_course_work_material, updates one or more fields of a course work material.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWorkMaterials/patch
        for more info

        :param states: status of this course work material. If unspecified, the default state is DRAFT.
                            see https://developers.google.com/classroom/reference/rest/v1/courses.courseWorkMaterials#CourseWorkMaterialState

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param c_w_m_id: identifier of the course work material to patch. 'string'

        :param title: title of this course work material. The title must be a valid UTF-8 string
                      containing between 1 and 3000 characters.

        :param description: optional description of this course work material.
                            The text must be a valid UTF-8 string containing no more than 30,000 characters.

        :param material: additional materials.
                         a course work material must have no more than 20 material items.
                         see https://developers.google.com/classroom/reference/rest/v1/Material

        :param scheduled_time: optional timestamp when this course work material is scheduled to be published.
                               a timestamp in RFC3339 UTC "Zulu" format, with nanosecond resolution and up to nine fractional digits.
                               examples: "2014-10-02T15:01:23Z" and "2014-10-02T15:01:23.045123456Z".
                               see https://protobuf.dev/reference/protobuf/google.protobuf/#google.protobuf.Timestamp

        :param individual_students_options: Identifiers of students with access to the course work material.
                                            This field is set only if assigneeMode is INDIVIDUAL_STUDENTS.
                                            If the assigneeMode is INDIVIDUAL_STUDENTS,
                                            then only students specified in this field can see the course work material.
                                            see https://developers.google.com/classroom/reference/rest/v1/IndividualStudentsOptions

        :return: response dict or False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        body: dict = dict()

        if states:
            for state in states:
                if state not in ['COURSEWORK_MATERIAL_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
                    raise gcc_exceptions.CourseWorkMaterialStateError()
            body['state'] = states

        if title:
            gcc_validators.are_params_string(title)
            body['title'] = title

        if description:
            gcc_validators.are_params_string(description)
            body['description'] = description

        if material:
            if isinstance(material, dict):
                raise TypeError()
            body['materials'] = [material]

        if scheduled_time:
            gcc_validators.are_params_string(scheduled_time)
            body['scheduledTime'] = scheduled_time

        if individual_students_options:
            if isinstance(material, list):
                raise TypeError()
            body['IndividualStudentsOptions'] = {"studentIds": individual_students_options}

        update_mask: str = ','.join(body.keys())

        try:
            response: dict = self.classroom.courses().courseWorkMatirials().patch(
                courseId=course_id,
                id=c_w_m_id,
                updateMask=update_mask,
                body=body
            ).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str, str)
    def quick_add_student(self, course_id: str, enrollment_code: str, user_id: str) -> dict or False:
        """
        this func defines the quick_add_student, adds a user as a student of a course.
        see https://developers.google.com/classroom/reference/rest/v1/courses.students/create
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param enrollment_code: Enrollment code of the course to create the student in.
                                This code is required if userId corresponds to the requesting user;
                                it may be omitted if the requesting user has administrative permissions to create students for any user.

        :param user_id: optional argument to restrict returned student work to those owned by the student with the specified identifier.
                        the identifier can be one of the following: {
                            the numeric identifier for the user,
                            the email address of the user ,
                            the string literal "me" indicating the requesting user
                        }
        :return: response dict | bool
        """
        # validation
        gcc_validators.are_params_in_cache(course_id, enrollment_code)

        body: dict = {
            "userId": user_id,
        }
        try:
            response = self.classroom.courses().students().create(
                courseId=course_id,
                enrollmentCode=enrollment_code,
                body=body
            ).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def detailed_add_student(self, detailed_json: bool = False) -> dict or False:
        """
        this func defines the detailed_add_student, adds a user as a student of a course.
        see https://developers.google.com/classroom/reference/rest/v1/courses.students/create
        for more info

        :param detailed_json: detailed course_json needs to be full
        :return: response dict | bool
        """
        if not detailed_json:
            raise gcc_exceptions.DetailedStudentJsonEmpty()

        with open(r'templates\derailed_student.json', 'r') as fh:
            body = json.load(fh)

        try:
            response = self.classroom.courses().students().create(**body).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def delete_student(self, course_id: str, user_id: str) -> bool:
        """
        this func defines the delete_student, deletes a user as a student of a course.
        see https://developers.google.com/classroom/reference/rest/v1/courses.students/delete
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param user_id: optional argument to restrict returned student work to those owned by the student with the specified identifier.
                        the identifier can be one of the following: {
                            the numeric identifier for the user,
                            the email address of the user ,
                            the string literal "me" indicating the requesting user
                        }
        :return: bool
        """
        gcc_validators.are_params_in_cache(course_id)

        try:
            self.classroom.courses().students().delete(
                courseId=course_id,
                id=user_id
            ).execute()
            self._update_cache()
            return True
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def get_student(self, course_id: str, user_id: str) -> dict or False:
        """
        this func defines the get_student, return a user as a student of a course.
        see https://developers.google.com/classroom/reference/rest/v1/courses.students/get
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param user_id: optional argument to restrict returned student work to those owned by the student with the specified identifier.
                        the identifier can be one of the following:
                            the numeric identifier for the user,
                            the email address of the user ,
                            the string literal "me" indicating the requesting user

        :return: response dict or False
        """
        gcc_validators.are_params_in_cache(course_id)

        try:
            response = self.classroom.courses().students().get(
                courseId=course_id,
                id=user_id
            ).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str)
    def list_students(self, course_id: str, page_size: int = 10, page_token: str = None) -> dict or False:
        """
        this func defines the list_students, returns a list of students of this course that the requester is permitted to view.
        see https://developers.google.com/classroom/reference/rest/v1/courses.students/list
        for more info
        
        :param course_id: either identifier of the course or assigned alias. 'string'
        :param page_size: Maximum number of items to return. The default is 30 if unspecified or 0.
                          The server may return fewer than the specified number of results.
        :param page_token: nextPageToken value returned from a previous list call,
                           indicating that the subsequent page of results should be returned.
                           The list request must be otherwise identical to the one that resulted in this token.

        :return: response dict or false
        """
        gcc_validators.are_params_in_cache(course_id)

        query_params: dict = dict()

        if page_size:
            gcc_validators.are_params_int(page_size)
            if page_size >= 100:
                raise ValueError("Page size cannot be more than 100.")
            query_params["pageSize"] = page_size

        if page_token:
            gcc_validators.are_params_string(page_token)
            query_params["pageToken"] = page_token

        try:
            response = self.classroom.courses().students().list(
                courseId=course_id,
                **query_params
            ).execute()

            students = response.get("students", [])
            next_page_token = response.get("nextPageToken", None)

            return {"students": students, "nextPageToken": next_page_token}
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def create_topic(self, course_id: str, topic_name: str) -> dict or False:
        """
        this func defines the create_topic, creates a topic.
        see https://developers.google.com/classroom/reference/rest/v1/courses.topics/create
        for more info

        :param topic_name: The name of the topic, generated by the user. Leading and trailing whitespaces, if any,
                          are trimmed. Also, multiple consecutive whitespaces are collapsed into one inside the name.
                          The result must be a non-empty string. Topic names are case-sensitive, and must be no longer than 100 characters.
        :param course_id: either identifier of the course or assigned alias. 'string'
        :return: response dict or False
        """
        gcc_validators.are_params_in_cache(course_id)

        body: dict = {
            "name": topic_name,
        }

        try:
            response = self.classroom.courses().topics().create(
                coutseId=course_id,
                body=body
            ).execute()
            self._update_cache()

            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def delete_topic(self, course_id: str, topic_id: str) -> dict or False:
        """
        this func defines the delete_topic, deletes a topic.
        see https://developers.google.com/classroom/reference/rest/v1/courses.topics/delete
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param topic_id: identifier of the topic.
        :return: bool
        """
        gcc_validators.are_params_in_cache(course_id)

        try:
            self.classroom.courses().topics().delete(
                courseId=course_id,
                id=topic_id
            ).execute()
            return True
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def get_topic(self, course_id: str, topic_id: str) -> dict or False:
        """
        this func defines the get_topic, returns a topic.
        see https://developers.google.com/classroom/reference/rest/v1/courses.topics/delete
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param topic_id: identifier of the topic.
        :return: response dict or False
        """
        gcc_validators.are_params_in_cache(course_id)

        try:
            response = self.classroom.courses().topics().delete(
                courseId=course_id,
                id=topic_id
            ).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str)
    def list_topics(self, course_id: str, page_size: int = 10, page_token: str = None) -> dict or False:
        """
        this func defines the list_topics, returns the list of topics that the requester is permitted to view.
        see https://developers.google.com/classroom/reference/rest/v1/courses.topics/delete
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param page_size: Maximum number of items to return. Zero or unspecified indicates that the server may assign a maximum.
                          The server may return fewer than the specified number of results.
        :param page_token: nextPageToken value returned from a previous list call, indicating that the subsequent
                          page of results should be returned. The list request must be otherwise identical to the one that resulted in this token.
        :return: response dict or False

        """
        gcc_validators.are_params_string(course_id)

        query_params: dict = dict()

        if page_size:
            gcc_validators.are_params_int(page_size)
            if page_size >= 100:
                raise ValueError("Page size cannot be more than 100.")
            query_params["pageSize"] = page_size

        if page_token:
            gcc_validators.are_params_string(page_token)
            query_params["pageToken"] = page_token

        try:
            response = self.classroom.courses().topics().list(
                courseId=course_id,
                **query_params
            ).execute()

            topics = response.get("topics", [])
            next_page_token = response.get("nextPageToken", None)
            return {"topics": topics, "nextPageToken": next_page_token}
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str, str)
    def patch_topic(self, course_id: str, topic_id: str, topic_name: str)-> dict or False:
        """
        this func defines the patch_topic, updates one or more fields of a topic.
        see https://developers.google.com/classroom/reference/rest/v1/courses.topics/patch
        for more info

        :param topic_name: The name of the topic, generated by the user. Leading and trailing whitespaces,
        if any, are trimmed. Also, multiple consecutive whitespaces are collapsed into one inside the name.
        The result must be a non-empty string. Topic names are case-sensitive, and must be no longer than 100 characters.

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param topic_id: identifier of the topic
        :return: response dict or False
        """
        gcc_validators.are_params_in_cache(course_id)

        try:
            response: dict = self.classroom.courses().topics().patch(
                courseId=course_id,
                id=topic_id,
                updateMask='name',
                body={'name': topic_name}
            ).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def accept_invitation(self, invitation_id: str):
        return self._accept_invitation(invitation_id=invitation_id)


