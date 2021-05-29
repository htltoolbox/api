from typing import Optional

from pydantic import BaseModel, HttpUrl, PositiveInt


class TempClickboard(BaseModel):
    NAME: str
    AUTHOR_ID: PositiveInt
    SHORT_DESCRIPTION: Optional[str] = None
    IMG_URL: Optional[HttpUrl] = None
    DOK_URL: Optional[HttpUrl] = None
    SCH_URL: Optional[HttpUrl] = None
    BRD_URL: Optional[HttpUrl] = None
    STP_URL: Optional[HttpUrl] = None


class Clickboard(BaseModel):
    ID: PositiveInt
    NAME: str
    AUTHOR_ID: PositiveInt
    AUTHOR: Optional[str] = None
    SHORT_DESCRIPTION: Optional[str] = None
    IMG_URL: Optional[HttpUrl] = None
    DOK_URL: Optional[HttpUrl] = None
    SCH_URL: Optional[HttpUrl] = None
    BRD_URL: Optional[HttpUrl] = None
    STP_URL: Optional[HttpUrl] = None
