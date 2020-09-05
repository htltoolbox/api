from typing import Optional

from pydantic import BaseModel


class TokenData(BaseModel):
    EMAIL: Optional[str] = None
