from typing import Optional

from pydantic import BaseModel, PositiveInt

from db import models


class JWTTokensResponse(BaseModel):
    """Response schema with access and refresh tokens and tokens type"""

    access_token: str
    refresh_token: Optional[str]
    token_type: Optional[str]
    access_lifetime: PositiveInt
    refresh_lifetime: PositiveInt


class JWTTokenPayload(BaseModel):
    """JWT token payload"""

    pk: str
    type: models.JWTType
