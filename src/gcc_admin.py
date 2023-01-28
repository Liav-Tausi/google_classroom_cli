from gcc_base import GccBase
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow


class Admin(GccBase):

    def __init__(self):
        super().__init__()


    def create_course(self):
        classroom_service = build('classroom', 'v1', credentials=credentials)

        # Define the course details
        course = {
            'name': 'My Sample Course',
            'section': 'Sample Section',
            'descriptionHeading': 'This is a sample course created using the Google Classroom API',
            'enrollmentCode': 'abc123'
        }
        classroom_service.courses().create(body=course).execute()

