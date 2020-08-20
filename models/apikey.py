from typing import Optional
from pydantic import BaseModel, root_validator
from assets.database import openDBConnection


class apikey(BaseModel):
    ID: Optional[int]
    NAME: Optional[str]
    APIKEY: str
    PERMISSION: Optional[int]
    DATE_GENERATED: Optional[str]

    @root_validator
    def validate_key(cls, values):
        db = openDBConnection()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM APIKEYS WHERE APIKEY = %s", (values['APIKEY'],))

        data = cursor.fetchone()

        te1 = data[2]
        te2 = values['APIKEY']
        res = (te1 == te2)

        if res:
            values['ID'] = data[0]
            values['NAME'] = data[1]
            values['PERMISSION'] = data[3]
            values['DATE_GENERATED'] = data[4]

            return values

        raise ValueError('API key is not Valid')
