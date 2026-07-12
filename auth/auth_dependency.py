from fastapi import Depends
from fastapi import HTTPException

from auth.jwt_handler import verify_access_token
from auth.oauth2 import oauth2_scheme


async def authenticate_user(

    token: str = Depends(oauth2_scheme)

):

    payload = verify_access_token(token)

    if payload is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid or Expired Token"
        )

    return payload