from datetime import timedelta


class ErrorMessages:
    IDEMPOTENCY_KEY_NOT_FOUND = "idempotency key not provided"
    DIFFERENT_PARAMS_WITH_SAME_IDEMPOTENCY_KEY = "idempotency key has been used on this endpoint already"
    
    
