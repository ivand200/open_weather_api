import time
from typing import Dict

import jwt
from settings import Settings

settings = Settings()

JWT_SECRET = settings.SECRET
JWT_ALGORITHM = settings.ALGORITHM


def token_response(token: str):
    return {"access_token": token}


def signJWT(user_id: str) -> Dict[str, str]:
    payload = {"user_id": user_id, "expires": time.time() + 600}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def decodeJWT(token: str):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else False
    except:
        return False


def transferJWT(user_id: str) -> str:
    payload = {"user_id": user_id, "expires": time.time() + 300}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token
