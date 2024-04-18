from fastapi import Depends, FastAPI
from pydantic import BaseModel, EmailStr, conint, constr
from database import DataBase
from datetime import date
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

app = FastAPI(
    title='MBT DataBase'
)
db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
db.connect_db()


class UserInfo(BaseModel):
    id: int
    telegram_id: str
    access: str | None
    data_reg: date | None
    status: str | None
    rating: int | None
    profit: int | None
    offers: int | None
    comment: str | None
    name: str | None
    sex: str | None
    born: date | None
    age: int | None
    residence: str | None
    education: str | None
    course: int | None
    profession: str | None
    salary: int | None
    hard_work: bool | None
    mid_work: bool | None
    art_work: bool | None
    other_work: str | None
    tools: str | None
    language: str | None
    phone: str | None
    email: str | None
    citizenship: str | None
    wallet: str | None
    is_driver: bool | None
    transport: str | None
    is_military: bool | None
    other_info: str | None


class UserAdd(BaseModel):
    telegram_id: str
    access: str | None
    data_reg: date | None
    status: str | None
    rating: int | None
    profit: int | None
    offers: int | None
    comment: str | None
    name: str | None
    sex: str | None
    born: date | None
    age: int | None
    residence: str | None
    education: str | None
    course: int | None
    profession: str | None
    salary: int | None
    hard_work: bool | None
    mid_work: bool | None
    art_work: bool | None
    other_work: str | None
    tools: str | None
    language: str | None
    phone: str | None
    email: str | None
    citizenship: str | None
    wallet: str | None
    is_driver: bool | None
    transport: str | None
    is_military: bool | None
    other_info: str | None


@app.get('/users/get_user_by_id')
async def get_user_id(id: int):
    usr_table = db.connect_table('users')
    user = usr_table.get_by_id(id)
    return user

@app.get('/users/get_user_by_telegram')
async def get_user_telegram(telegram_id: str):
    usr_table = db.connect_table('users')
    user = usr_table.get_by_param(param='telegram_id', value=telegram_id)
    return user

@app.post('/users/add_user')
async def add_user(user: UserAdd):
    usr_table = db.connect_table('users')
    user_dict = user.dict()
    usr_table.insert(**user_dict)
    user_info = usr_table.get_by_param(param='telegram_id', value=user_dict['telegram_id'])
    return user_info

@app.post('/users/update_info')
def update_user(user: UserInfo):
    usr_table = db.connect_table('users')
    user_dict = user.dict()
    usr_table.update_record(user_dict['id'], user_dict)
    user_info = usr_table.get_by_id(user_dict['id'])
    return user_info


