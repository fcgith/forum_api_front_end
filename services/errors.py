from fastapi import HTTPException

class ForumError(HTTPException):
    def __init__(self, code=400, detail="Bad request"):
        self._status_code = code
        super().__init__(status_code=code, detail=detail)  # Pass message to base class

    def __str__(self):
        return f"{super().__str__()} (Error Code: {self._status_code})"



not_authorized = ForumError(code=403, detail="Not authorized")
not_found = ForumError(code=404, detail="Not found")
internal_error = ForumError(code=500, detail="Internal server error")
