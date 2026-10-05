# Did this to be able to handle exceptions raised in middlewares.
# By default, http exceptions raised in the middlewares aren't caught by starlette's ExceptionMiddleware
# which handles exceptions like HTTPException because the middleware is processed before it is defined.
# ServerErrorMiddleware -> Where we are(##user_middleware##)-> ExceptionMiddleware -> User Business Logic.
# By doing this, we allow our exceptions raised in middleware to be caught by the ServerErrorMiddleWare
# Which only catches exceptions with the status code 500 or the Exception class directly by default

class CustomBaseException(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        
    def content(self):
        return {"error":self.message}
        
class IdempotencyException(CustomBaseException):
    def __init__(self, message: str, status_code: int):
        super().__init__(message, status_code)
