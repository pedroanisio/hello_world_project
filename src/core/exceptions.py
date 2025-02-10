class PasswordTooWeakException(Exception):
    def __init__(self, message="Password does not meet complexity requirements"):
        self.message = message
        super().__init__(self.message)

class CustomAppException(Exception):
    def __init__(self, message="An application error occurred"):
        self.message = message
        super().__init__(self.message)
