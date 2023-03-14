class TeacherCli:
    def __init__(self, **kwargs):
        self.__service = kwargs["service"]
        self.__method = kwargs["method"]


teacher = """
                detailed_json: bool, course_id: str, announcement_text: str, announcement_id: str, materials: dict,
                state: str, states: str, scheduled_time: str, update_time: str = None, assignee_mode: dict = None,
                students_options: list = None, page_size: int = 10, order_by: str = None, page_token: str = None,
                add_student_ids: list[str] = None, remove_student_ids: list[str] = None, title: str = None,
                description: str = None, work_type: str = None, course_work_id: str = None, due_date: dict = None,
                due_time: dict = None, user_id: str = None, sub_states: list[str] = None, late: str = None,
                assigned_grade: int = None, short_answer: str = None, alternate_link: str = None,
                assignment_submission: dict = None, c_w_m_id: str = None, material_link: str = None, material_drive_id: str = None,
                individual_students_options: list = None, enrollment_code: str = None, topic_name: str = None, topic_id: str = None,
                invitation_id: str = None
         """
