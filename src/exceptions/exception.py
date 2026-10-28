class CustomBaseException(Exception):
    def __init__(self, message: str | None = None):
        self.message = message

    def content(self):
        if self.message:
            return {"status": "error", "message": self.message}


class IDParsingError(CustomBaseException):
    def __init__(self, message: str | None):
        super().__init__(message=message)
