import datetime
import json
from typing import Tuple, Any

from gcc_base import GccBase
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import gcc_exceptions
import gcc_validators

from googleapiclient.errors import HttpError


class Admin(GccBase):

    def __init__(self, role: str = 'admin', email: str = None,
                 work_space: str = None, ref_cache_month: int = 12):

        if role != 'admin':
            raise gcc_exceptions.InvalidRole()
        super().__init__(role, ref_cache_month, work_space, email)

        if self.workspace:
            check = self.workspace
        else:
            check = self.email

        self.__check = check

    @property
    def check(self):
        return self.__check

    def detailed_create_course(self) -> tuple:
        """
        This method reads in a detailed JSON representation of a course from a file and creates the course.
        course object! https://developers.google.com/classroom/reference/rest/v1/courses#Course
        see detailed_create_course.json
        :return: tuple

        """
        with open('data/detailed_create_course.json', 'r') as fh:
            course_json = json.load(fh)
        try:
            request = self.classroom.courses().create(body=course_json).execute()
            print(f"""
            Created course: {request["name"]}
            Course id: {request["id"]}
            """)
            self._update_cache()
            return request['id'], request["name"]
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)

    def create_course(self, name: str, section: str, description: str, room: str, owner_id='me',
                      course_state: str = 'PROVISIONED') -> tuple:
        """
        This method creates a course with the given name, section, description, room, owner_id, and course_state.
        see https://developers.google.com/classroom/reference/rest/v1/courses/create
        for more info

        :param name: Name of course 'string'
        :param section: Section of course 'string'
        :param description: Description of course 'string'
        :param room: Room of course 'string'
        :param owner_id: Owner's id or 'me' 'string'
        :param course_state: Course state ['PROVISIONED', 'ACTIVE', 'ARCHIVED', 'DECLINED', 'SUSPENDED'] 'string'
        :return: tuple of course info
        """
        gcc_validators.are_params_string(name, section, description, room, owner_id, course_state)

        if course_state.upper() not in ['PROVISIONED', 'ACTIVE', 'ARCHIVED', 'DECLINED', 'SUSPENDED']:
            raise gcc_exceptions.CourseStateError()

        course: dict = {
            'name': name,
            'section': section,
            'descriptionHeading': description,
            'room': room,
            'ownerId': owner_id,
            'courseState': course_state.upper()
        }
        try:
            request = self.classroom.courses().create(body=course).execute()
            print(f"""
                   Created course: {request["name"]}
                   Course id: {request["id"]}
                   """)
            self._update_cache()
            return int(request['id']), request["name"], self.check
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)

    def delete_course(self, course_id: str) -> bool:
        """
        this func defines the delete_course method, deletes a course.
        see https://developers.google.com/classroom/reference/rest/v1/courses/delete
        for more info

        :param course_id: Identifier of the course to delete
        :return: True | False
        """
        gcc_validators.are_params_string(course_id)

        if course_id not in self.cache[self.check]:
            raise gcc_exceptions.NotInCache()
        try:
            request = self.classroom.courses().delete(id=course_id).execute()
            print(f"""
                       Deleted course: {request["name"]}
                       Course id: {request["id"]}
            """)
            self._update_cache()
            return True
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def patch_course(self, course_id: str, update_mask: str, course_data: dict) -> bool:
        """
        this func defines the patch_course method, modifies assignee mode and options of an announcement.
        see https://developers.google.com/classroom/reference/rest/v1/courses/delete
        for more info

        :param course_id: Identifier of the course to patch string
        :param update_mask: Mask that identifies which fields on the course to update ex: "user.displayName,photo".
        :param course_data: course object! https://developers.google.com/classroom/reference/rest/v1/courses#Course
        :return: True | False
        """
        gcc_validators.are_params_string(course_id, update_mask)

        if not isinstance(course_data, dict):
            raise TypeError()

        course = {
            'name': course_data.get('name'),
            'section': course_data.get('section'),
            'descriptionHeading': course_data.get('descriptionHeading'),
            'description': course_data.get('description'),
            'room': course_data.get('room'),
            'courseState': course_data.get('courseState'),
            'ownerId': course_data.get('ownerId')
        }
        try:
            self.classroom.courses().patch(
                id=course_id,
                updateMask=update_mask,
                body=course
            ).execute()
            self._update_cache()
            return True
        except HttpError as error:
            self.logger.error(f'An error occurred: {error}')
            return False

    def update_course(self, course_id: str, course_data: dict) -> bool:
        """
        this func defines the update_course method, updates a course.
        see https://developers.google.com/classroom/reference/rest/v1/courses/update
        for more info

        :param course_id: Identifier of the course to patch string
        :param course_data: Course object! https://developers.google.com/classroom/reference/rest/v1/courses#Course
        :return: True | False
        """
        if not isinstance(course_id, str) and not isinstance(course_data, dict):
            raise TypeError()

        course = {
            'name': course_data.get('name'),
            'section': course_data.get('section'),
            'descriptionHeading': course_data.get('descriptionHeading'),
            'description': course_data.get('description'),
            'room': course_data.get('room'),
            'courseState': course_data.get('courseState'),
            'ownerId': course_data.get('ownerId')
        }
        try:
            self.classroom.courses().update(courseId=course_id).execute()
            self._update_cache()
            return True
        except HttpError as error:
            self.logger.error(f'An error occurred: {error}')
            return False

    def get_course(self, course_id: str) -> dict | False:
        """
        this func defines the get_course method, returns a course..
        see https://developers.google.com/classroom/reference/rest/v1/courses/get
        for more info

        :param course_id: Identifier of the course to patch string
        :return: request | False
        """
        gcc_validators.are_params_string(course_id)

        try:
            request = self.classroom.courses().get(courseId=str(course_id)).execute()
            return request
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def list_courses(self, student_id: str = 'me', teacher_id: str = 'me', course_states: list[str] = None,
                     page_size: int = 10, page_token: str = None) -> tuple[str, str] | False:
        """
        this func defines the list_courses method, returns a list of courses that the requesting user is permitted to view,
        restricted to those that match the request. Returned courses are ordered by creation time,
        with the most recently created coming first.
        see https://developers.google.com/classroom/reference/rest/v1/courses/list
        for more info

        :param student_id: Restricts returned courses to those having a student with the specified identifier.
        (the numeric identifier for the user *or*
        the email address of the user "or"
        the string literal "me" "or"
        indicating the requesting user)

        :param teacher_id: Restricts returned courses to those having a teacher with the specified identifier.
        (the numeric identifier for the user *or*
        the email address of the user "or"
        the string literal "me" "or"
        indicating the requesting user)

        :param course_states: https://developers.google.com/classroom/reference/rest/v1/courses#CourseState
        :param page_size: Maximum number of items to return. Zero or unspecified indicates that the server may assign a maximum.
        :param page_token: Token identifying the next page of results to return. If empty, no further results are available
        :return tuple[the courses, the next page token] | False
        """
        gcc_validators.are_params_string(student_id, teacher_id, page_token)
        gcc_validators.are_params_int(page_size)

        if course_states not in ['COURSE_STATE_UNSPECIFIED', 'ACTIVE', 'ARCHIVED',
                                 'PROVISIONED', 'DECLINED', 'SUSPENDED']:
            raise gcc_exceptions.CourseStateError()

        query_params = {}
        if student_id:
            query_params['studentId'] = student_id
        if teacher_id:
            query_params['teacherId'] = teacher_id
        if course_states:
            query_params['courseStates'] = course_states
        if page_size:
            query_params['pageSize'] = page_size
        if page_token:
            query_params['pageToken'] = page_token
        try:
            request = self.classroom.courses().list(**query_params).execute()
            courses = request.get("courses", [])
            next_page_token = request.get("nextPageToken", None)
            return courses, next_page_token
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def create_alias(self, course_id: str, alias: str) -> dict | False:
        """
        this func defines the create_alias method, creates an alias for a course.
        see https://developers.google.com/classroom/reference/rest/v1/courses.aliases/create
        for more info

        :param course_id: Identifier of the course. 'string'
        :param alias: alias 'string'
        :return: request dict | False
        """
        gcc_validators.are_params_string(course_id)

        body: dict = {
            "alias": alias
        }
        try:
            request = self.classroom.courses().aliases().create(courseId=course_id, body=body).execute()
            return request
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def delete_alias(self, course_id: str, alias: str) -> bool:
        """
        this func defines the delete_alias method, deletes an alias of a course.
        see https://developers.google.com/classroom/reference/rest/v1/courses.aliases/delete
        for more info

        :param course_id: Identifier of the course. 'string'
        :param alias: alias 'string'
        :return: True | False
        """
        gcc_validators.are_params_string(course_id, alias)

        try:
            self.classroom.courses().aliases().delete(courseId=course_id,
                                                      aliasId=alias).execute()
            return True
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def list_alias(self, course_id: str, page_size: int = 10, page_token: str = None) -> tuple | False:
        """
        this func defines the list_alias method, returns a list of aliases for a course..
        see https://developers.google.com/classroom/reference/rest/v1/courses.aliases/list
        for more info

        :param course_id: Identifier of the course. 'string'
        :param page_size: Page size 'int'
        :param page_token: Next page token 'string'
        :return: request | False
        """

        gcc_validators.are_params_string(course_id)
        gcc_validators.are_params_int(page_size)

        try:
            request = self.classroom.courses().aliases().list(courseId=course_id,
                                                              pageSize=page_size)
            if page_token:
                gcc_validators.are_params_string(page_token)
                request.pageToken = page_token
            teacher = request.execute()
            next_page_token = teacher.get("nextPageToken", None)

            return request, next_page_token
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def add_teacher(self, course_id: str, teacher_email: str = 'me') -> bool:
        """
        this func defines the add_teacher method, creates a teacher of a course..
        see https://developers.google.com/classroom/reference/rest/v1/courses.teachers/create
        for more info

        :param course_id: Identifier of the course. string
        :param teacher_email: Teacher's email or 'me'
        :return: True | False
        """
        gcc_validators.are_params_string(course_id, teacher_email)

        if not gcc_validators.is_email(teacher_email) and teacher_email != 'me':
            raise gcc_exceptions.InvalidEmail()
        data: dict = {
            "userId": teacher_email,
        }
        try:
            request = self.classroom.courses().teachers().create(courseId=course_id,
                                                                 body=data).execute()

            print('User %s was added as a teacher to the course with ID %s'
                  % (request.get('profile').get('name').get('fullName'),
                     course_id))
            self._update_cache()
            return True
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def delete_teacher(self, course_id: str, teacher_email: str) -> tuple[str, str] | False:
        """
        this func defines the delete_teacher method, removes the specified teacher from the specified course.
        see https://developers.google.com/classroom/reference/rest/v1/courses.teachers/delete
        for more info

        :param course_id: Identifier of the course. string
        :param teacher_email: Teacher's email
        :return: tuple[str, str] | False

        """
        gcc_validators.are_params_string(course_id, teacher_email)

        if teacher_email not in self.cache[self.check][course_id]['teachers']:
            raise gcc_exceptions.TeacherNotInCourse()
        if not gcc_validators.is_email(teacher_email):
            raise gcc_exceptions.InvalidEmail()
        try:
            self.classroom.courses().teachers().delete(courseId=course_id,
                                                       userId=teacher_email).execute()
            self._update_cache()
            print(f'User {teacher_email} was deleted from course with ID {course_id}')
            return teacher_email, course_id
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def get_teacher(self, course_id: str, teacher_email: str) -> dict | False:
        """
        this func defines the delete_teacher method, removes the specified teacher from the specified course.
        see https://developers.google.com/classroom/reference/rest/v1/courses.teachers/get
        for more info

        :param course_id: Identifier of the course. string
        :param teacher_email: Teacher's email
        :return: request dict | False

        """
        gcc_validators.are_params_string(course_id, teacher_email)

        if not gcc_validators.is_email(teacher_email):
            raise gcc_exceptions.InvalidEmail()
        try:
            request = self.classroom.courses().teachers().get(courseId=course_id,
                                                              userId=teacher_email).execute()
            return request
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def list_teachers(self, course_id: str, page_size: int = 10, page_token: str = None):
        """
        this func defines the list_teachers method, returns a list of teachers of this course that the requester is permitted to view.
        see https://developers.google.com/classroom/reference/rest/v1/courses.teachers/list
        for more info

        :param course_id: Identifier of the course. string
        :param page_size: page size 'int'
        :param page_token: next page token 'string'
        :return:
        """
        gcc_validators.are_params_string(course_id, page_token)
        gcc_validators.are_params_int(page_size)

        if page_size > 100:
            raise ValueError("Page size cannot be more than 100.")
        try:
            request = self.classroom.courses().teachers().list(courseId=course_id,
                                                               pageSize=page_size)
            if page_token:
                request.pageToken = page_token
            teacher = request.execute()
            next_page_token = teacher.get("nextPageToken", None)

            return teacher, next_page_token
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False


if __name__ == '__main__':
    gcc = Admin(email='liavt242@gmail.com')
    liav = gcc.create_course(name='daniel', section='liav', description='liav', room='fee')
    # # gcc.add_teacher(course_id=liav[0])
    # # gcc.delete_teacher(course_id=542178731078, teacher_email='liavt242@gmail.com')
    # gcc.delete_course(course_id=588714514132)
    # print(gcc.get_teacher(course_id=588714514132, teacher_email='liavt242@gmail.com'))
    # print(gcc.list_teachers(course_id=588714514132))
    # print(gcc.list_courses(teacher_id='liavt242@gmail.com'))
