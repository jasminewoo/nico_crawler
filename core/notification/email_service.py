from abc import abstractmethod


class EmailError(Exception):
    pass


class Email:
    def __init__(self, credentials=None):
        self.credentials = credentials

    @abstractmethod
    def send(self, subject, body):
        pass
