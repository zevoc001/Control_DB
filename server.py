from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from database import DataBase
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

app = FastAPI(
    title='MBT DataBase'
)
db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
db.connect_db()


@app.get('/users/get_user')
async def get_user(tg_id: int):
    usr_table = db.connect_table('users_data')
    user_data = usr_table.get_user(tg_id)
    return user_data
