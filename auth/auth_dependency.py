from fastapi import HTTPException
from fastapi import Header

from auth.jwt_handler import verify_access_token


async def authenticate_user(

    authorization: str = Header(None)

):

    # ===================================
    # CHECK HEADER EXISTS
    # ===================================

    if authorization is None:

        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    # ===================================
    # CHECK BEARER PREFIX
    # ===================================

    if not authorization.startswith("Bearer "):

        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header"
        )

    # ===================================
    # EXTRACT TOKEN
    # ===================================

    token = authorization.replace(
        "Bearer ",
        ""
    )

    # ===================================
    # VERIFY TOKEN
    # ===================================

    payload = verify_access_token(token)

    if payload is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return payload