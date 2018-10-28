import base64
from email.mime.text import MIMEText

from core.google_utils import create_service
from core.notification.email_service import Email

SCOPES = 'https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.metadata'


class Gmail(Email):
    def __init__(self, credentials=None, logger=None):
        Email.__init__(self, credentials)
        self.service = None
        self.logger = logger

    def send(self, subject, body):
        self.initialize_service()
        to = self.get_my_email_address()
        msg = _create_message(to=to, subject=subject, message_text=body)
        _send_message(self.service, 'me', msg)

    def initialize_service(self):
        if not self.service:
            self.service = create_service('gmail', 'v1', SCOPES)

    def get_my_email_address(self):
        json = self.service.users().getProfile(userId='me').execute()
        return json['emailAddress']


def _create_message(to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = 'me'
    message['subject'] = subject
    b64_bytes = base64.urlsafe_b64encode(str.encode(message.as_string()))
    return {'raw': bytes.decode(b64_bytes)}


def _send_message(service, user_id, message):
    service.users().messages().send(userId=user_id, body=message).execute()
