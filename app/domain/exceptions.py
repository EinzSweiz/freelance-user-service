class UserServiceException(Exception):
    pass


class UserAlreadyExists(UserServiceException):
    def __init__(self, email: str) -> None:
        super().__init__(f"User with email {email} already exists.")
    
class UserNotExists(UserServiceException):
    def __init__(self, user_id: str) -> None:
        super().__init__(f"User with ID {user_id} does not exist.")

class InvalidCredentials(Exception):
    def __init__(self, message: str = "Invalid credentials"):
        self.message = message
        super().__init__(self.message)

class TokenRevoked(UserServiceException):
    def __init__(self) -> None:
        super().__init__("Token has been revoked.")

class UnauthorizedAction(UserServiceException):
    def __init__(self) -> None:
        super().__init__("You are not authorized to perform this action.")
    