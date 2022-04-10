from ..exceptions import ServerException


class LogAlreadyExists(ServerException):

    def __init__(self, log_id: str):
        super().__init__(400, f'Log: {log_id}, already exists.')
        self.log_id = log_id


class LogNotFound(ServerException):

    def __init__(self, log_id: str):
        super().__init__(404, f'Log: {log_id} not found.')
        self.log_id = log_id


class InvalidStatus(ServerException):

    def __init__(self, status: str):
        super().__init__(400, f'Invalid state: {status}.')
        self.status = status


class WhoisError(ServerException):

    def __init__(self):
        super().__init__(400, 'Name or Service not known.')
