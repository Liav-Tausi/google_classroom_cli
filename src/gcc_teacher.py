import datetime
import json
import pytz

from gcc_base import GccBase
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.errors import HttpError
import gcc_exceptions
import gcc_validators


class Teacher(GccBase):

    def __init__(self, role: str = 'teacher', ref_cache_month: int = 12,
                 email: str = None, work_space: str = None):
        if role != 'teacher':
            raise gcc_exceptions.InvalidRole()
        super().__init__(role, ref_cache_month, work_space, email)

    def detailed_create_announcement(self, announcement_json: bool = False) -> dict | False:
        """
        this func defines the detailed_create_announcement method, creates a detailed announcement
        see https://developers.google.com/classroom/reference/rest/v1/courses.announcements/create
        for more info


        :return:
        """
        if not announcement_json:
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

    def quick_create_announcement(self, course_id: str, announcement_text: str, materials: dict, state: dict,
                                  scheduled_time: str, update_time: str = None,
                                  assignee_mode: dict = None,
                                  students_options: list = None) -> dict | False:
        """
        this func defines the create_announcement method, create an announcement with the following params

        :param students_options: individual_students_options object
               https://developers.google.com/classroom/reference/rest/v1/IndividualStudentsOptions
               for object representation
               
        :param assignee_mode: Status of this announcement. If unspecified, the default state is DRAFT. 'string'
        :param update_time: Timestamp of the most recent change to this announcement. 'string'
        :param alternate_link: 'string'
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
        gcc_validators.are_params_string(announcement_text, course_id, assignee_mode, update_time, scheduled_time)

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
        gcc_validators.are_params_string(course_id, announcement_id)

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

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param announcement_id: announcement's id 'string'
        :return: response dict | False
        """
        # validation
        gcc_validators.are_params_string(course_id, announcement_id)

        try:
            response: dict = self.classroom.courses().announcements().get(
                courseId=course_id,
                id=announcement_id
            )
            self._update_cache()
            return response
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
        :return: response dict | False
        """
        query_params: dict = dict()

        if ann_states:
            if ann_states not in ['ANNOUNCEMENT_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
                raise gcc_exceptions.AnnouncementStateError()
            query_params['announcementStates'] = ann_states

        if order_by:
            gcc_validators.are_params_string(order_by)
            query_params['orderBy'] = order_by

        if page_size:
            gcc_validators.are_params_int(page_size)
            query_params['pageSize'] = page_size

        if page_token:
            gcc_validators.are_params_string(page_token)
            query_params['nextPageToken'] = page_token

        try:
            response = self.classroom.courses().announcements().list(**query_params)
            announcements = response.get("courses", [])
            next_page_token = response.get("nextPageToken", None)
            self._update_cache()
            return announcements, next_page_token
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def modify_announcement_assignees(self, course_id: str, announcement_id: str, assignee_mode: str,
                                      add_student_ids: list[str] = None,
                                      remove_student_ids: list[str] = None) -> dict | False:
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
        gcc_validators.are_params_string(course_id, announcement_id, assignee_mode)

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

    def detailed_patch_announcement(self, detailed_announcement_json: bool = False) -> dict | False:
        """
        this func defines the detailed_patch_announcement method, modifies detailed options of an announcement.
        see https://developers.google.com/classroom/reference/rest/v1/courses.announcements/patch
        for more info

        param: detailed_announcement_json: flag for indication if json is full True if not False 'bool'
        :return: response dict | False
        """
        if not detailed_announcement_json:
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

    def quick_patch_announcement(self, course_id: str, announcement_id: str, state: str = None,
                                 text: str = None, scheduled_time: str = None) -> dict | False:
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
        gcc_validators.are_params_string(course_id, announcement_id)

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

        update_mask = ','.join(body.keys())

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

    def detailed_course_work_create(self, course_work_json: bool = False) -> dict | False:
        """
        this func defines the detailed_course_work_create method, creates course work..
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork/create
        for more info

        for detailed_course_work_create method the "detailed_course_work.json" stored at the data_endpoint directory should be filled!!
        for more info: https://developers.google.com/classroom/reference/rest/v1/courses.courseWork#CourseWork

        :param course_work_json: flag for indication if json is full True if not False 'bool'
        :return: response dict or False

        """
        if not course_work_json:
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

    def quick_course_work_create(self, course_id: str, title: str, description: str,
                                 material: list, work_type: str, state: str) -> dict | False:
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
        gcc_validators.are_params_string(course_id, title, description, work_type, state)

        if state not in ['COURSE_WORK_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
            raise gcc_exceptions.CourseWorkStateError()

        if work_type not in ['COURSE_WORK_TYPE_UNSPECIFIED', 'ASSIGNMENT',
                             'SHORT_ANSWER_QUESTION', 'MULTIPLE_CHOICE_QUESTION']:
            raise gcc_exceptions.CourseWorkTypeError()

        if isinstance(material, list):
            raise TypeError()

        body: dict = {
            'title': title,
            'description': description,
            'materials': material,
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

    def delete_course_work(self, course_id: str, course_work_id: str) -> bool:
        """
        this func defines the delete_course_work method, deletes course work..
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork/delete
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param course_work_id: identifier of the course work. 'string'
        :return: True or False 'bool'
        """
        gcc_validators.are_params_string(course_id, course_work_id)
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

    def get_course_work(self, course_id: str, course_work_id: str) -> bool:
        """
        this func defines the get_course_work method, gets course work..
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork/get
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param course_work_id: identifier of the course work. 'string'
        :return: True or False 'bool'
        """
        gcc_validators.are_params_string(course_id, course_work_id)
        try:
            self.classroom.courses().courseWork().get(
                courseId=course_id,
                id=course_work_id
            ).execute()
            self._update_cache()
            return True
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def list_course_work(self, course_id: str, course_work_states: list[str] = None,
                         order_by: str = 'updateTime desc', page_size: int = 10,
                         page_token: str = None) -> tuple[list[dict], str] | False:
        """
        this func defines the get_course_work method, Returns a list of course work that the responseer is permitted to view.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork/list
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'

        :param course_work_states: Restriction on the work status to return. Only courseWork that matches is returned.
                                   If unspecified, items with a work status of PUBLISHED is returned.

        :param page_size: Maximum number of items to return. Zero or unspecified indicates that the server may assign a maximum.
        :param order_by: Optional sort ordering for results
        :param page_token: Token identifying the next page of results to return. If empty, no further results are available 'string'
        :return: Tuple with a list of course work and nextPageToken value
        """
        gcc_validators.are_params_string(course_id)
        gcc_validators.are_params_int(page_size)

        query_params = {'courseId': course_id}

        if course_work_states:
            for state in course_work_states:
                if state not in ['COURSE_WORK_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
                    raise gcc_exceptions.CourseWorkStateError()
            query_params['courseWorkStates'] = course_work_states

        if order_by:
            gcc_validators.are_params_string(order_by)
            query_params['orderBy'] = order_by

        if page_size:
            gcc_validators.are_params_int(page_size)
            query_params['pageSize'] = page_size

        if page_token:
            gcc_validators.are_params_string(page_token)
            query_params['nextPageToken'] = page_token

        try:
            response = self.classroom.courses().courseWork().list(**query_params)
            course_work_list = response.get("courseWork", [])
            next_page_token = response.get("nextPageToken", None)

            self._update_cache()
            return course_work_list, next_page_token
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def modify_course_work_assignees(self, course_id: str, course_work_id: str, assignee_mode: str,
                                     add_student_ids: list[str] = None,
                                     remove_student_ids: list[str] = None) -> dict | False:
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
        gcc_validators.are_params_string(course_id, course_work_id, assignee_mode)

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

    def detailed_patch_course_work(self, course_work_json: bool = False) -> dict | False:
        """
        this func defines the detailed_patch_course_work method, updates one or more fields of a course work.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork/patch
        for more info

        :param course_work_json: detailed course_json needs to be full
        :return: response dict or False
        """

        if not course_work_json:
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

    def quick_patch_course_work(self, course_id: str, course_work_id: str, title: str = None,
                                description: str = None, due_date: dict = None, due_time: dict = None,
                                scheduled_time: datetime.datetime = None, state: list[str] = None,
                                materials: list = None) -> dict | False:
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

        :param state: State of the course. If unspecified, the default state is PROVISIONED.
                      see https://developers.google.com/classroom/reference/rest/v1/courses#CourseState

        :param materials: Additional materials. Course must have no more than 20 material items. 'list[material]'
                         see https://developers.google.com/classroom/reference/rest/v1/Material
        :return: response dict or False
        """

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

        if state:
            if state not in ['COURSE_WORK_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
                raise gcc_exceptions.CourseWorkStateError()
            body['state'] = description

        if materials:
            if isinstance(materials, list):
                raise TypeError()
            body['materials'] = materials

        update_mask = ','.join(body.keys())

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

    def get_student_submissions(self, course_id: str, course_work_id: str, submission_id: str) -> dict | False:
        """
        this func defines the get_student_submissions, returns a student submission.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions/get
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param course_work_id: identifier of the course work. 'string'
        :param submission_id: identifier of the student submission. 'string'
        :return: response dict or False
        """
        gcc_validators.are_params_string(course_id, course_work_id, submission_id)
        try:
            response = self.classroom.courses().courseWork().studentSubmissions().get(
                courseId=course_id,
                courseWorkId=course_work_id,
                id=submission_id
            ).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def list_student_submissions(self, course_id: str, course_work_id: str, user_id: str,
                                 page_size: int = 10, sub_states: list[str] = 'SUBMISSION_STATE_UNSPECIFIED',
                                 late: str = 'LATE_VALUES_UNSPECIFIED', page_token: str = None) -> dict | False:
        """
        this func defines the list_student_submissions, Returns a list of student submissions that the requester is permitted to view,
        factoring in the OAuth scopes of the request. - may be specified as the courseWorkId to include student submissions
        for multiple course work items.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions/list
        for more info

        :param page_token: nextPageToken value returned from a previous list call,
                          indicating that the subsequent page of results should be returned.
                          The list request must be otherwise identical to the one that resulted in this token.

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
        gcc_validators.are_params_string(course_id, course_work_id)

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

            self._update_cache()
            return student_submissions, next_page_token
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def modify_submissions_attachments(self, course_id: str, course_work_id: str, submission_id: str,
                                       materials: dict) -> dict | False:
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
        gcc_validators.are_params_string(course_id, course_work_id, submission_id)
        if not isinstance(materials, dict):
            raise TypeError()

        body: dict = {
            "addAttachments": [
                {materials}
            ]
        }
        try:
            response = self.classroom.courses().courseWork().studentSubmissions().modifyAttachments(
                courseId=course_id,
                courseWorkId=course_work_id,
                id=submission_id,
                body=body
            ).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def detailed_patch_student_submissions(self, students_submissions_json: bool = False) -> dict | False:
        """
        this func defines the detailed_patch_student_submissions, updates one or more fields of a student submission.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions/patch
        for more info

        :param students_submissions_json: flag for indication if json is full True if not False 'bool'
        :return: response dict or False
        """
        if not students_submissions_json:
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

    def quick_patch_student_submissions(self, course_id: str, course_work_id: str, submission_id: str,
                                        sub_states: list[str] = None, assigned_grade: int = None,
                                        short_answer: str = None, alternate_link: str = None,
                                        assignment_submission: dict = None) -> dict | False:
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

        update_mask = ','.join(body.keys())

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

    def return_student_submissions(self, course_id: str, course_work_id: str, submission_id: str) -> dict | False:
        """
        this func defines the return_student_submissions, returns a student submission.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions/return
        for more info

         :param course_id: either identifier of the course or assigned alias. 'string'
        :param course_work_id: identifier of the course work. 'string'
        :param submission_id: identifier of the student submission. 'string'
        :return: response dict or False
        """
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

    def detailed_create_course_work_materials(self, detailed_course_work_material_json: bool = False):
        """

        :param detailed_course_work_material_json:
        :return:
        """
        if not detailed_course_work_material_json:
            raise gcc_exceptions.CourseWorkMaterialJsonEmpty()
        try:
            with open('templates/detailed_course_work_material.json', 'r', encoding='utf-8') as fh:
                body = json.load(fh)

            response = self.classroom.courses().courseWorkMaterials().create(**body).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def quick_create_course_work_materials(self, course_id: str, title: str, description: str, materials: list):
        """

        :param course_id:
        :param title:
        :param description:
        :param materials:
        :return:
        """
        body: dict = {
            "title": title,
            "description": description,
            "materials": materials
        }
        try:
            response = self.classroom.courses().courseWorkMaterials().create(
                courseId=course_id,
                body=body
            ).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def delete_course_work_materials(self, course_id: str, c_w_m_id: str):
        """

        :param course_id:
        :param c_w_m_id:
        :return:
        """
        try:
            response = self.classroom.courses().courseWorkMaterials().delete(
                courseId=course_id,
                id=c_w_m_id
            ).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False


    def get_course_work_materials(self, course_id: str, c_w_m_id: str) -> dict | False:
        """

        :param course_id:
        :param c_w_m_id:
        :return:
        """
        try:
            response = self.classroom.courses().courseWorkMatirials().get(
                courseId=course_id,
                id=c_w_m_id
            ).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def list_course_work_materials(self, course_id: str, c_w_m_state: list[str] = None, page_size: int = 10,
                                   page_token: str = None, order_by: str = None, material_link: str = None,
                                   material_drive_id: str = None):
        """

        :param course_id:
        :param c_w_m_state:
        :param page_size:
        :param page_token:
        :param order_by:
        :param material_link:
        :param material_drive_id:
        :return:
        """
        query_params: dict = dict()

        if c_w_m_state:
            for state in c_w_m_state:
                if state not in ['COURSEWORK_MATERIAL_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
                    raise gcc_exceptions.CourseWorkMaterialStateError()
            query_params['state'] = c_w_m_state

        if page_size:
            gcc_validators.are_params_int(page_size)
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

            self._update_cache()
            return course_work_material, next_page_token
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def detailed_patch_course_work_material(self, detailed_course_work_material_json: bool = False) -> dict | False:
        """

        :param detailed_course_work_material_json:
        :return:
        """
        if not detailed_course_work_material_json:
            raise gcc_exceptions.CourseWorkMaterialJsonEmpty()

        with open('templates/detailed_course_work_material.json', 'r', encoding='utf-8') as fh:
            body = json.load(fh)

        try:
            response = self.classroom.courses().courseWorkMatirials().patch(**body).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def quick_patch_course_work_material(self, course_id: str, c_w_m_id: str, title: str = None,  material: list = None,
                                         description: str = None, scheduled_time: str = None, c_w_m_state: str = None,
                                         individual_students_options: list[str] = None) -> dict | False:
        """

        :param c_w_m_state:
        :param course_id:
        :param c_w_m_id:
        :param title:
        :param material:
        :param description:
        :param scheduled_time:
        :param individual_students_options:
        :return:
        """
        body: dict = dict()

        if c_w_m_state:
            for state in c_w_m_state:
                if state not in ['COURSEWORK_MATERIAL_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
                    raise gcc_exceptions.CourseWorkMaterialStateError()
            body['state'] = c_w_m_state

        if title:
            gcc_validators.are_params_string(title)
            body['title'] = title

        if description:
            gcc_validators.are_params_string(description)
            body['description'] = description

        if material:
            if isinstance(material, list):
                raise TypeError()
            body['materials'] = material

        if scheduled_time:
            gcc_validators.are_params_string(scheduled_time)
            body['scheduledTime'] = scheduled_time

        if individual_students_options:
            if isinstance(material, list):
                raise TypeError()
            body['IndividualStudentsOptions'] = {"studentIds": individual_students_options}


        update_mask = ','.join(body.keys())

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




if __name__ == '__main__':
    gcc = Teacher(role='teacher', email='liavt242@gmail.com')
