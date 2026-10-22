class CustomBaseException(Exception):
    def __init__(self, message: str):
        self.message = message

    def content(self):
        return {"status": "error", "message": self.message}


class IDParsingError(CustomBaseException):
    def __init__(self, message: str):
        super().__init__(message=message)
