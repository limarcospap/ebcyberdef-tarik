

class ServerException(Exception):

    def __init__(self, status_code: int, msg: str, errors: dict = None):
        self.msg = msg
        self.errors = errors
        self.status_code = status_code


class InvalidInputs(ServerException):

    def __init__(self):
        super().__init__(400, 'Invalid inputs.')


class Unauthorized(ServerException):

    def __init__(self):
        super().__init__(403, 'Unauthorized access.')
