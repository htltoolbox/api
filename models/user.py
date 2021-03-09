from ipaddress import IPv4Address
from typing import Optional
from pydantic import BaseModel, validator, IPvAnyAddress
from assets.database import openDBConnection
import re
from models.sessionkey import SessionKey


class preUser(BaseModel):
    EMAIL: Optional[str] = None
    PASSWORD: Optional[str] = None
    CLASS: Optional[str] = None


class User(BaseModel):
    ID: Optional[int] = None
    EMAIL: Optional[str] = None
    PASSWORD_HASH: Optional[str] = None
    NAME: Optional[str] = None
    LASTNAME: Optional[str] = None
    CLASS: Optional[str] = None
    PERMISSION_LEVEL: Optional[int] = None
    LAST_IP: Optional[str] = None
    ACTIVE: Optional[bool] = None
    TEMPHASH: Optional[str] = None

    @validator('ID')
    def is_positiv(cls, values):
        if values > 0:
            return values
        raise ValueError('ID <= 0 is not possible')

    @validator('EMAIL')
    def is_valid_email(cls, values):
        regex = r"^([A-z]+\.[A-z]+(\d\d)?@htl-salzburg.ac.at)$"
        if re.search(regex, values):
            return values
        else:
            raise ValueError('EMAIL not Valid')

    @validator('CLASS')
    def is_valid_class(cls, values):
        regex = r"^([1-8][A-I]([A-Z]{2,4})|(LEHRER))$"
        if re.search(regex, values):
            return values
        else:
            raise ValueError('CLASS in not Valid')

    @validator('LAST_IP')
    def  is_valid_ip(cls, values):
        regex = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        if re.search(regex, values):
            return values
        else:
            raise ValueError('IP in not Valid')
