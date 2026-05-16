class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)

    @property
    def error_type(self) -> str:
        return self.__class__.__name__


class ValidationException(AppException):
    def __init__(self, message: str = "Invalid request data") -> None:
        super().__init__(message=message, status_code=400)


class DatabaseException(AppException):
    def __init__(self, message: str = "Database operation failed") -> None:
        super().__init__(message=message, status_code=500)


class AuthenticationException(AppException):
    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message=message, status_code=401)
