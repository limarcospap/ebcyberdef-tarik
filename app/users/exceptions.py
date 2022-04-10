from ..exceptions import ServerException


class UserAlreadyExists(ServerException):

    def __init__(self, username: str):
        super().__init__(400, f'Username: {username}, already exists.')
        self.username = username


class UserNotFound(ServerException):

    def __init__(self, username: str):
        super().__init__(404, f'Username: {username}, not found.')
        self.username = username


class InvalidPassword(ServerException):

    def __init__(self):
        super().__init__(400, f'Invalid password.')


class InvalidToken(ServerException):

    def __init__(self):
        super().__init__(400, f'Invalid token.')
