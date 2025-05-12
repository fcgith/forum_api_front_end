from fastapi import HTTPException

not_authorized = HTTPException(status_code=403, detail="Not authorized")
not_found = HTTPException(status_code=404, detail="Not found")
internal_error = HTTPException(status_code=500, detail="Internal server error")