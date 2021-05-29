from typing import Optional

from pydantic import BaseModel


class App(BaseModel):
    ID: int = 0
    NAME: Optional[str] = None
    REDIR_URL: Optional[str] = None
    API_KEY: Optional[str] = None
    LOGO_URL: Optional[str] = None
