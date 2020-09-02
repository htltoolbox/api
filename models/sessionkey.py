from typing import Optional
from pydantic import BaseModel, root_validator, ValidationError
from assets.database import openDBConnection


class SessionKey(BaseModel):
    key: str
    valid: Optional[bool] = False

    @root_validator
    def check_session_key(cls, values):
        db = openDBConnection()
        cursor = db.cursor()

        cursor.execute("SELECT SESSION_KEY FROM USERDATA WHERE SESSION_KEY = %s", (values['key'],))
        data = cursor.fetchone()

        if data[0] is not None:
            values['valid'] = True
            return values

        raise ValueError('SessionKey is not valid')
