import json
from gcc_base import GccBase
import gcc_exceptions
import gcc_validators
from googleapiclient.errors import HttpError

__all__ = [
    'Admin'
]


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

    def detailed_create_course(self, detailed_json: bool = False) -> tuple:
        """
        This method reads in a detailed JSON representation of a course from a file and creates the course.
        course object! https://developers.google.com/classroom/reference/rest/v1/courses#Course
        see detailed_course.json
        :return: tuple

        """
        if not detailed_json:
            raise gcc_exceptions.CourseJsonEmpty()

        with open('templates/detailed_course.json', 'r') as fh:
            course_json = json.load(fh)
        try:
            response: dict = self.classroom.courses().create(body=course_json).execute()
            print(f"""
                   Created course: {response["name"]}
                   Course id: {response["id"]}
                   Enrollment code: {response["enrollmentCode"]}
                   """)
            self._update_cache()
            return response['id'], response["name"]
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)

    @gcc_validators.validate_params(str, str, str, str, str, str)
    def quick_create_course(self, name: str, section: str, description: str, room: str, owner_id='me',
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
        # validation
        if course_state.upper() not in ['COURSE_STATE_UNSPECIFIED', 'PROVISIONED',
                                        'ACTIVE', 'ARCHIVED', 'DECLINED', 'SUSPENDED']:
            raise gcc_exceptions.CourseStateError()

        body: dict = {
            'name': name,
            'section': section,
            'descriptionHeading': description,
            'room': room,
            'ownerId': owner_id,
            'courseState': course_state.upper()
        }
        try:
            response: dict = self.classroom.courses().create(body=body).execute()
            print(f"""
                   Created course: {response["name"]}
                   Course id: {response["id"]}
                   Enrollment code: {response["enrollmentCode"]}
                   """)
            self._update_cache()
            return int(response['id']), response["name"], self.check
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)

    @gcc_validators.validate_params(str)
    def delete_course(self, course_id: str) -> bool:
        """
        this func defines the delete_course method, deletes a course.
        see https://developers.google.com/classroom/reference/rest/v1/courses/delete
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :return: True | False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

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

    def detailed_patch_course(self, detailed_json: bool = False) -> dict or bool:
        """
        this func defines the detailed_patch_course method, modifies assignee mode and options of an announcement.
        see https://developers.google.com/classroom/reference/rest/v1/courses/patch
        for more info

        :param detailed_json:
        :return:
        """
        if not detailed_json:
            raise gcc_exceptions.CourseJsonEmpty()

        with open('templates/detailed_course.json', 'r') as fh:
            body = json.load(fh)
        try:
            response: dict = self.classroom.courses().patch(**body).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str)
    def quick_patch_course(self, course_id: str, name: str = None, state: str = None,
                           description: str = None, description_heading: str = None,
                           materials: dict = None) -> bool:
        """
        this func defines the patch_course method, modifies assignee mode and options of an announcement.
        see https://developers.google.com/classroom/reference/rest/v1/courses/delete
        for more info

        :param materials: Additional materials. CourseWork must have no more than 20 material items. 'list[material]'
                         https://developers.google.com/classroom/reference/rest/v1/Material

        :param description_heading: Optional heading for the description. For example, "Welcome to 10th Grade Biology."
                                    If set, this field must be a valid UTF-8 string and no longer than 3600 characters. 'string'

        :param description: Optional description. For example, "We'll be learning about the structure of
                            living creatures from a combination of textbooks, guest lectures, and lab work. Expect to be excited!"
                            If set, this field must be a valid UTF-8 string and no longer than 30,000 characters. 'string'

        :param state: State of the course. If unspecified, the default state is PROVISIONED.

        :param name: Name of the course. For example, "10th Grade Biology". The name is required.
                     It must be between 1 and 750 characters and a valid UTF-8 string. 'string'

        :param course_id: either identifier of the course or assigned alias. 'string'
        :return: True | False
        """
        body: dict = dict()

        if name:
            gcc_validators.are_params_string(name)
            body['name'] = name

        if description:
            gcc_validators.are_params_string(description)
            body['description'] = description

        if description_heading:
            gcc_validators.are_params_string(description_heading)
            body['descriptionHeading'] = description_heading

        if state:
            if state not in ['COURSE_STATE_UNSPECIFIED', 'PROVISIONED',
                             'ACTIVE', 'ARCHIVED', 'DECLINED', 'SUSPENDED']:
                raise gcc_exceptions.CourseStateError()
            body['courseState'] = state

        if materials:
            if isinstance(materials, list):
                raise TypeError()
            body['materials'] = [materials]

        update_mask = ','.join(body.keys())

        try:
            self.classroom.courses().patch(
                id=course_id,
                updateMask=update_mask,
                body=body
            ).execute()
            self._update_cache()
            return True
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def update_course(self, detailed_json: bool = False) -> dict or bool:
        """
        this func defines the detailed_patch_course method, modifies assignee mode and options of an announcement.
        see https://developers.google.com/classroom/reference/rest/v1/courses/patch
        for more info

        :param detailed_json:
        :return:
        """
        if not detailed_json:
            raise gcc_exceptions.CourseJsonEmpty()

        with open('templates/detailed_course.json', 'r') as fh:
            body = json.load(fh)
        try:
            response: dict = self.classroom.courses().update(**body).execute()
            self._update_cache()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str)
    def get_course(self, course_id: str) -> dict | bool:
        """
        this func defines the get_course method, returns a course..
        see https://developers.google.com/classroom/reference/rest/v1/courses/get
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :return: request | False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        try:
            response: dict = self.classroom.courses().get(courseId=str(course_id)).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def list_courses(self, student_id: str = 'me', teacher_id: str = 'me', states: list[str] = None,
                     page_size: int = 10, page_token: str = None) -> tuple[str, str] | bool:
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

        :param states: https://developers.google.com/classroom/reference/rest/v1/courses#CourseState
        :param page_size: Maximum number of items to return. Zero or unspecified indicates that the server may assign a maximum.
        :param page_token: Token identifying the next page of results to return. If empty, no further results are available
        :return tuple[the courses, the next page token] | False
        """
        # validation

        query_params: dict = dict()

        if student_id:
            gcc_validators.are_params_string(student_id)
            query_params['studentId'] = student_id

        if teacher_id:
            gcc_validators.are_params_string(teacher_id)
            query_params['teacherId'] = teacher_id

        if states:
            for state in states:
                if state not in ['COURSE_STATE_UNSPECIFIED', 'ACTIVE', 'ARCHIVED',
                                 'PROVISIONED', 'DECLINED', 'SUSPENDED']:
                    raise gcc_exceptions.CourseStateError()
            query_params['courseStates'] = states

        if page_size:
            gcc_validators.are_params_int(page_size)
            query_params['pageSize'] = page_size

        if page_token:
            gcc_validators.are_params_string(page_token)
            query_params['pageToken'] = page_token
        try:
            request: dict = self.classroom.courses().list(**query_params).execute()
            courses = request.get("courses", [])
            next_page_token = request.get("nextPageToken", None)
            return courses, next_page_token
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def create_alias(self, course_id: str, alias: str) -> dict | bool:
        """
        this func defines the create_alias method, creates an alias for a course.
        see https://developers.google.com/classroom/reference/rest/v1/courses.aliases/create
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param alias: alias 'string'
        :return: request dict | False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        body: dict = {
            "alias": alias
        }
        try:
            response: dict = self.classroom.courses().aliases().create(courseId=course_id, body=body).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def delete_alias(self, course_id: str, alias: str) -> bool:
        """
        this func defines the delete_alias method, deletes an alias of a course.
        see https://developers.google.com/classroom/reference/rest/v1/courses.aliases/delete
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param alias: alias 'string'
        :return: True | False
        """
        gcc_validators.are_params_in_cache(course_id)

        try:
            self.classroom.courses().aliases().delete(courseId=course_id,
                                                      aliasId=alias).execute()
            return True
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str)
    def list_alias(self, course_id: str, page_size: int = 10, page_token: str = None) -> tuple | bool:
        """
        this func defines the list_alias method, returns a list of aliases for a course..
        see https://developers.google.com/classroom/reference/rest/v1/courses.aliases/list
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param page_size: Page size 'int'
        :param page_token: Next page token 'string'
        :return: request | False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)
        gcc_validators.are_params_int(page_size)

        try:
            response = self.classroom.courses().aliases().list(courseId=course_id,
                                                               pageSize=page_size)
            if page_token:
                gcc_validators.are_params_string(page_token)
                response.pageToken = page_token
            teacher = response.execute()
            next_page_token = teacher.get("nextPageToken", None)

            return response, next_page_token
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def add_teacher(self, course_id: str, teacher_email: str = 'me') -> bool:
        """
        this func defines the add_teacher method, creates a teacher of a course..
        see https://developers.google.com/classroom/reference/rest/v1/courses.teachers/create
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param teacher_email: Teacher's email or 'me'
        :return: True | False
        """
        # validation
        gcc_validators.are_params_in_cache(course_id)
        gcc_validators.is_email(teacher_email)

        data: dict = {
            "userId": teacher_email,
        }
        try:
            request: dict = self.classroom.courses().teachers().create(courseId=course_id,
                                                                       body=data).execute()

            print('User %s was added as a teacher to the course with ID %s'
                  % (request.get('profile').get('name').get('fullName'),
                     course_id))
            self._update_cache()
            return True
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def delete_teacher(self, course_id: str, teacher_email: str) -> tuple[str, str] | bool:
        """
        this func defines the delete_teacher method, removes the specified teacher from the specified course.
        see https://developers.google.com/classroom/reference/rest/v1/courses.teachers/delete
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param teacher_email: Teacher's email
        :return: tuple[str, str] | False

        """
        # validation
        gcc_validators.are_params_in_cache(course_id)
        gcc_validators.is_email(teacher_email)

        try:
            self.classroom.courses().teachers().delete(courseId=course_id,
                                                       userId=teacher_email).execute()
            self._update_cache()
            print(f'User {teacher_email} was deleted from course with ID {course_id}')
            return teacher_email, course_id
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def get_teacher(self, course_id: str, teacher_email: str) -> dict | bool:
        """
        this func defines the delete_teacher method, removes the specified teacher from the specified course.
        see https://developers.google.com/classroom/reference/rest/v1/courses.teachers/get
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param teacher_email: Teacher's email
        :return: request dict | False

        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        if not gcc_validators.is_email(teacher_email):
            raise gcc_exceptions.InvalidEmail()
        try:
            response: dict = self.classroom.courses().teachers().get(courseId=course_id,
                                                                     userId=teacher_email).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str)
    def list_teachers(self, course_id: str, page_size: int = 10, page_token: str = None) -> tuple[dict, str] | bool:
        """
        this func defines the list_teachers method, returns a list of teachers of this course that the requester is permitted to view.
        see https://developers.google.com/classroom/reference/rest/v1/courses.teachers/list
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param page_size: page size 'int'
        :param page_token: next page token 'string'
        :return: tuple[dict, str]

        """
        # validation
        gcc_validators.are_params_in_cache(course_id)

        query_params: dict = dict()

        if page_size:
            gcc_validators.are_params_int(page_size)
            if page_size >= 100:
                raise ValueError("Page size cannot be more than 100.")
            query_params['pageSize'] = page_size

        if page_token:
            gcc_validators.are_params_string(page_token)
            query_params['nextPageToken'] = page_token

        try:
            response = self.classroom.courses().teachers().list(courseId=course_id,
                                                                pageSize=page_size)
            if page_token:
                gcc_validators.are_params_string(page_token)
                response.pageToken = page_token
            response.execute()
            teacher = response.get("teachers", [])
            next_page_token = teacher.get("nextPageToken", None)

            return teacher, next_page_token
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    def accept_invitation(self, invitation_id: str):
        return self._accept_invitation(invitation_id=invitation_id)

    @gcc_validators.validate_params(str, str, str)
    def create_invitation(self, course_id: str, user_id: str, role: str) -> dict | bool:
        """
        this func defines the create_invitation, creates an invitation. only one invitation for a user and course may exist at a time.
        delete and re-create an invitation to make changes
        see https://developers.google.com/classroom/reference/rest/v1/invitations/create
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param user_id: optional argument to restrict returned student work to those owned by the student with the specified identifier.
                        the identifier can be one of the following:
                            the numeric identifier for the user,
                            the email address of the user ,
                            the string literal "me" indicating the requesting user

        :param role: role to invite the user to have. Must not be COURSE_ROLE_UNSPECIFIED.
                     COURSE_ROLE_UNSPECIFIED, STUDENT, TEACHER, OWNER
        :return: response dict or False

        """
        gcc_validators.are_params_in_cache(course_id)

        if role not in ["STUDENT", "TEACHER", "OWNER"]:
            raise gcc_exceptions.RoleError()

        body: dict = {
            "userId": user_id,
            "courseId": course_id,
            "role": role
        }
        try:
            response = self.classroom.courses().invitations().create(body=body).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str)
    def delete_invitation(self, invitation_id: str) -> bool:
        """
        this func defines the delete_invitation method, deletes an invitation.
        see https://developers.google.com/classroom/reference/rest/v1/invitations/delete
        for more info

        :param invitation_id: identifier of the invitation to delete.
        :return: bool

        """
        try:
            self.classroom.courses().invitations().delete(id=invitation_id).execute()
            return True
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str)
    def get_invitation(self, invitation_id: str) -> dict | bool:
        """
        this func defines the get_invitation method, gets an invitation.
        see https://developers.google.com/classroom/reference/rest/v1/invitations/get
        for more info

        :param invitation_id: identifier of the invitation to delete.
        :return: bool

        """
        try:
            response = self.classroom.courses().invitations().get(id=invitation_id).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    @gcc_validators.validate_params(str, str)
    def list_invitation(self, course_id: str, user_id: str, page_size: int = 10,
                        page_token: str = None) -> dict:
        """
        this func defines the get_invitation method, gets an invitation.
        see https://developers.google.com/classroom/reference/rest/v1/invitations/get
        for more info

        :param course_id: either identifier of the course or assigned alias. 'string'
        :param user_id: optional argument to restrict returned student work to those owned by the student with the specified identifier.
                        the identifier can be one of the following:
                            the numeric identifier for the user,
                            the email address of the user ,
                            the string literal "me" indicating the requesting user
        :param page_size: Maximum number of items to return. Zero or unspecified indicates that the server may assign a maximum.
                          The server may return fewer than the specified number of results.
        :param page_token: nextPageToken value returned from a previous list call, indicating that the subsequent
                          page of results should be returned. The list request must be otherwise identical to the one that resulted in this token.
        :return: response dict | False
        """
        gcc_validators.are_params_in_cache(course_id)

        query_params: dict = dict()

        if page_size:
            gcc_validators.are_params_int(page_size)
            if page_size >= 100:
                raise ValueError("Page size cannot be more than 100.")
            query_params['pageSize'] = page_size

        if page_token:
            gcc_validators.are_params_string(page_token)
            query_params['nextPageToken'] = page_token

        try:
            response = self.classroom.courses().invitations().list(
                courseId=course_id,
                id=user_id,
                **query_params
            ).execute()

            invitations = response.get("invitations", [])
            next_page_token = response.get("nextPageToken", None)
            return {"invitations": invitations, "nextPageToken": next_page_token}
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False

    # def create_registration(self, course_id: str, cloud_pubsub_topic: str, feed_url: str) -> dict | bool:
    #     """
    #     Creates a Google Classroom registration for a feed URL and a Cloud Pub/Sub topic.
    #
    #     :param course_id: either identifier of the course or assigned alias. 'string'
    #     :param cloud_pubsub_topic: The Cloud Pub/Sub topic to which notifications will be sent.
    #     :param feed_url: The URL of the feed to monitor for changes.
    #     :return: A dictionary representing the newly created registration, or False if an error occurs.
    #     """
    #     try:
    #         topic_name = f'projects/{self.project_id}/topics/{cloud_pubsub_topic}'
    #         cloud_pubsub_topic = {'topicName': topic_name}
    #
    #
    #         body = {
    #             'feed': {
    #                 'feedType': 'COURSE_WORK_CHANGES',
    #                 'courseWorkChangesInfo': {'courseId': course_id}
    #             },
    #             'cloudPubsubTopic': cloud_pubsub_topic,
    #             'feedUrl': feed_url
    #         }
    #
    #         response = self.classroom.registrations().create(body=body).execute()
    #         return response
    #     except HttpError as error:
    #         self.logger.error('An error occurred: %s' % error)
    #         return False

    @gcc_validators.validate_params(str)
    def get_user(self, user_id: str) -> dict | bool:
        """
        this func defines the get_user method, returns a user profile.
        see https://developers.google.com/classroom/reference/rest/v1/userProfiles/get
        for more info

        :param user_id: identifier of the profile to return. The identifier can be one of the following:
                        the numeric identifier for the user
                        the email address of the user
                        the string literal "me", indicating the requesting user
        :return: response dict or False
        """
        try:
            response = self.classroom.userProfiles().get(userId=user_id).execute()
            return response
        except HttpError as error:
            self.logger.error('An error occurred: %s' % error)
            return False


if __name__ == '__main__':
    gcc = Admin(email='liavt242@gmail.com')
    liav = gcc.get_user('me')
