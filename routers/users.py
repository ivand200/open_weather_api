import logging
import sys

from fastapi import APIRouter, Body, Depends, HTTPException, Header, Body, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import Optional

from schemas.users import (
    UserCreate,
    UserPublic,
    UserPublic,
    ItemBase,
    ItemCreate,
    ItemPublic,
    UserItems,
)
from models.users import Blacklist, User, Item
from routers.auth import signJWT, decodeJWT, transferJWT
from db import get_db
from settings import Settings

settings = Settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

router = APIRouter()

api_key_header = APIKeyHeader(name="Token")


def blacklist_check(token: str, db: Session = Depends(get_db)):
    """
    Check token in blacklist
    """
    check = db.query(Blacklist).filter(Blacklist.token == token).first()
    if check:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def check_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Check user in db
    """
    try:
        user_db = db.query(User).filter(User.login == user.login).first()
        varify_password = pwd_context.verify(user.password, user_db.password)
        if user_db and varify_password:
            return True
        return False
    except:
        False


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user
    """
    logger.info(f"SignUp a new user: {user.login}")
    user_db = db.query(User).filter(User.login == user.login).first()
    if user_db:
        raise HTTPException(status_code=400, detail="Login already exists.")
    hashed_password = pwd_context.hash(user.password)
    new_user = User(login=user.login, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return signJWT(new_user.login)


@router.post("/login", status_code=status.HTTP_200_OK)
async def user_login(user: UserCreate, db: Session = Depends(get_db)):
    """
    User login
    """
    logging.info(f"Login user: {user.login}")
    if check_user(user, db):
        return signJWT(user.login)
    raise HTTPException(status_code=403, detail="Unauthorized")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def exit_user(
    db: Session = Depends(get_db),
    token: str = Depends(api_key_header),
):
    """
    User logout
    """
    token_jwt = decodeJWT(token)
    if not token_jwt:
        raise HTTPException(status_code=401, detail="Access denied")
    token_blacklist = Blacklist(token=token)
    logger.info(f"User logout: {token_jwt['user_id']}")
    db.add(token_blacklist)
    db.commit()
    return True


@router.post(
    "/items/new", response_model=ItemPublic, status_code=status.HTTP_201_CREATED
)
async def create_item(
    item: ItemBase,
    db: Session = Depends(get_db),
    token: str = Depends(api_key_header),
):
    """
    Create a item
    """
    blacklist = blacklist_check(token, db)
    token_jwt = decodeJWT(token)
    if not token_jwt:
        raise HTTPException(status_code=401, detail="Access denied")
    logging.info(f"Create a item: {item}")
    user_db = db.query(User).filter(User.login == token_jwt["user_id"]).first()
    new_item = Item(title=item.title, user_id=user_db.id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.delete("/items/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    id: int,
    db: Session = Depends(get_db),
    token: str = Depends(api_key_header),
):
    """
    Delete users item by id
    """
    logger.info(f"Delete item: {id}")
    token = decodeJWT(token)
    if not token:
        raise HTTPException(status_code=401, detail="Access denied")
    item = db.query(Item).filter(Item.id == id).first()
    user = db.query(User).filter(User.login == token["user_id"]).first()
    if item.user_id != user.id:
        raise HTTPException(status_code=400, detail=f"Cant find item id: {id}")
    logger.info(f"Delete item id: {id} user_id: {item.user_id}")
    db.delete(item)
    db.commit()
    return True


@router.get("/items", response_model=UserItems, status_code=status.HTTP_200_OK)
async def get_items(
    db: Session = Depends(get_db),
    token: str = Depends(api_key_header),
):

    """
    Get all user items
    """
    token = decodeJWT(token)
    if not token:
        raise HTTPException(status_code=401, detail="Access denied")
    logger.info(f"Users items for {token['user_id']}")
    user = db.query(User).filter(User.login == token["user_id"]).first()
    items = db.query(Item).filter(Item.user_id == user.id).all()
    logging.info(f"Get all items, user: {user.login}, items: {len(items)}")
    result = UserItems(user=user, items=items)
    return result


@router.post("/send", status_code=status.HTTP_201_CREATED)
async def send_item(
    user_login: str = Body(...),
    item_id: int = Body(...),
    db: Session = Depends(get_db),
    token: str = Depends(api_key_header),
):
    """
    Send users item to other user
    """
    token = decodeJWT(token)
    if not token:
        raise HTTPException(status_code=401, detail="Access denied")
    user = db.query(User).filter(User.login == token["user_id"]).first()
    item = db.query(Item).filter(Item.id == item_id).first()
    if item.user_id != user.id:
        raise HTTPException(status_code=400, detail=f"Cant find item id: {item_id}")
    logging.info(f"Item transfer from user: {user.login}, item: {item.id}")
    user_login_jwt = transferJWT(user_login)
    user_token = user_login_jwt.decode("utf-8")
    url = f"{settings.BACKEND_URL}/{user_token}/{item_id}"
    return url


@router.get("/{user_token}/{item_id}", status_code=status.HTTP_200_OK)
async def get_transfer(
    user_token: str,
    item_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(api_key_header),
):
    """
    Get item transfer
    """
    token = decodeJWT(token)
    if not token:
        raise HTTPException(status_code=401, detail="Access denied")
    logging.info(f"Get item transfer, item: {item_id}, user: {token['user_id']}")
    user = db.query(User).filter(User.login == token["user_id"]).first()
    check_user_token = decodeJWT(user_token)
    if not user or check_user_token["user_id"] != user.login:
        raise HTTPException(status_code=400, detail="Something wrong!")
    item = db.query(Item).filter(Item.id == item_id).first()
    item.user_id = user.id
    db.commit()
    return {"status": "ok"}
