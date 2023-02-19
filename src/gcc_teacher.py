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

    def detailed_create_announcement(self, course_id: str, announcement_json: bool = False) -> dict | False:
        """
        this func defines the detailed_create_announcement method, creates a detailed announcement
        see https://developers.google.com/classroom/reference/rest/v1/courses.announcements/create
        for more info


        :return:
        """
        if not announcement_json:
            raise gcc_exceptions.AnnouncementJsonEmpty()

        with open("templates/detailed_announcement.json", 'r') as fh:
            body = json.load(fh)
        try:
            request: dict = self.classroom.courses().announcements().create(
                courseId=course_id,
                body=body
            ).execute()
            self._update_cache()
            return request
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False


    def quick_create_announcement(self, course_id: str, announcement_text: str, materials: dict, state: dict,
                                  scheduled_time: str, update_time: datetime.datetime = None, assignee_mode: dict = None,
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
            request: dict = self.classroom.courses().announcements().create(
                courseId=course_id,
                body=announcement
            ).execute()
            self._update_cache()
            return request
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
        :return: request dict | False
        """
        # validation
        gcc_validators.are_params_string(course_id, announcement_id)

        try:
            request: dict = self.classroom.courses().announcements().get(
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
        :return: request dict | False
        """
        # validation
        gcc_validators.are_params_string(ann_states, page_token, order_by)
        gcc_validators.are_params_int(page_size)

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
            request = self.classroom.courses().announcements().list(**query_params)
            if page_token:
                gcc_validators.are_params_string(page_token)
                request.pageToken = page_token
            request.execute()
            announcements = request.get("courses", [])
            next_page_token = request.get("nextPageToken", None)
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
        :return: request dict | False
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
            request: dict = self.classroom.courses().announcements().modify_assignment(
                courseId=course_id,
                id=announcement_id,
                body=body
            ).execute()
            self._update_cache()
            return request
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def detailed_patch_announcement(self, course_id: str) -> dict | False:
        """
        this func defines the detailed_patch_announcement method, modifies detailed options of an announcement.
        see https://developers.google.com/classroom/reference/rest/v1/courses.announcements/patch
        for more info

        param: course_id: either identifier of the course or assigned alias. 'string'
        :return: request dict | False
        """
        with open('templates/detailed_announcement.json', 'r') as fh:
            body = json.load(fh)
        try:
            request: dict = self.classroom.courses().announcements().create(
                courseId=course_id,
                body=body
            ).execute()
            self._update_cache()
            return request
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
        :return: request dict | False
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
        update_mask = update_mask.rstrip(',')

        try:
            request: dict = self.classroom.courses().announcements().patch(
                courseId=course_id,
                id=announcement_id,
                updateMask=update_mask,
                body=body
            ).execute()
            self._update_cache()
            return request
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def detailed_course_work_create(self, course_id: str, course_work_json: bool = False) -> dict | False:
        """
        this func defines the detailed_course_work_create method, creates course work..
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork/create
        for more info

        for detailed_course_work_create method the "detailed_course_work.json" stored at the data_endpoint directory should be filled!!
        for more info: https://developers.google.com/classroom/reference/rest/v1/courses.courseWork#CourseWork

        :param course_work_json: flag for indication if json is full True if not False 'bool'
        :param course_id: either identifier of the course or assigned alias. 'string'
        :return: request dict or False

        """
        if not course_work_json:
            raise gcc_exceptions.CourseWorkJsonEmpty()

        with open('templates/detailed_course_work.json', 'r') as fh:
            body = json.load(fh)
        try:
            request: dict = self.classroom.courses().courseWork().create(
                courseId=course_id,
                body=body
            ).execute()
            self._update_cache()
            return request
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
        :return: request dict or False

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
            request: dict = self.classroom.courses().courseWork().create(
                courseId=course_id,
                body=body
            ).execute()
            self._update_cache()
            return request
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
        this func defines the get_course_work method, Returns a list of course work that the requester is permitted to view.
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
        if course_work_states is not None:
            for state in course_work_states:
                if state not in ['COURSE_WORK_STATE_UNSPECIFIED', 'PUBLISHED', 'DRAFT', 'DELETED']:
                    raise gcc_exceptions.CourseWorkStateError()

        gcc_validators.are_params_int(page_size)

        query_params = {'courseId': course_id}
        if course_work_states:
            query_params['courseWorkStates'] = course_work_states
        if order_by:
            query_params['orderBy'] = order_by
        if page_size:
            query_params['pageSize'] = page_size
        if page_token:
            query_params['pageToken'] = page_token

        try:
            request= self.classroom.courses().courseWork().list(**query_params)
            if page_token:
                gcc_validators.are_params_string(page_token)
                request.pageToken = page_token
            request.execute()
            course_work_list = request.get("courseWork", [])
            next_page_token = request.get("nextPageToken", None)

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
        :return: request dict | False
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
            request: dict = self.classroom.courses().courseWork().modify_assignment(
                courseId=course_id,
                id=course_work_id,
                body=body
            ).execute()
            self._update_cache()
            return request
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def detailed_patch_course_work(self, course_id: str, course_work_id: str, course_work_json: bool = False):
        """
        this func defines the detailed_patch_course_work method, updates one or more fields of a course work.
        see https://developers.google.com/classroom/reference/rest/v1/courses.courseWork/patch
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param course_work_id: either identifier of the course_work or assigned alias. 'string'
        :param course_work_json: detailed course_json needs to be full
        :return:
        """
        if not course_work_json:
            raise gcc_exceptions.CourseWorkJsonEmpty()

        with open('templates/detailed_course.json', 'r') as fh:
            body = json.load(fh)

        update_mask = ','.join(body.keys())
        try:
            request: dict = self.classroom.courses().courseWork().patch(
                courseId=course_id,
                id=course_work_id,
                updateMask=update_mask,
                body=body
            ).execute()
            self._update_cache()
            return request
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def quick_patch_course_work(self, course_id: str, course_work_id: str, title: str = None,
                                description: str = None, due_date: dict = None, due_time: dict = None,
                                scheduled_time: datetime.datetime = None, state: str = None,
                                materials: list = None) -> dict | False:
        """
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
        :return: request dict or False
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
        update_mask = update_mask.rstrip(',')

        try:
            request: dict = self.classroom.courses().courseWork().patch(
                courseId=course_id,
                id=course_work_id,
                updateMask=update_mask,
                body=body
            ).execute()
            self._update_cache()
            return request
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False


if __name__ == '__main__':
    gcc = Teacher(role='teacher', email='liavt242@gmail.com')
