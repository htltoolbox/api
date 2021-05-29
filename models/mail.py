import re
from typing import Optional

from pydantic import BaseModel, validator

from assets.mail import sendMail


class Mail(BaseModel):
    to: str
    subject: str
    message: str
    html: Optional[bool] = False

    @validator('to')
    def is_valid_email(cls, email):
        regex = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
        if re.search(regex, email):
            return email
        else:
            raise ValueError('EMAIL not Valid')

    def send(self):
        return sendMail(to=self.to, subject=self.subject, message=self.message, html=self.html)
