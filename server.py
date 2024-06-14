from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional
from database import DataBase
from datetime import date, time
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, ACCESS_TOKEN


app = FastAPI(
    title='MBT DataBase'
)
db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
db.connect_db()


class UserInfo(BaseModel):
    id: int
    access: Optional[str] = 'user'
    reg_date: Optional[date] = None
    status: Optional[str] = None
    rating: Optional[int] = None
    profit: Optional[int] = None
    offers: Optional[int] = None
    comment: Optional[str] = None
    name: Optional[str] = None
    sex: Optional[str] = None
    born_date: Optional[date] = None
    residence: Optional[str] = None
    education: Optional[str] = None
    course: Optional[int] = None
    profession: Optional[str] = None
    salary: Optional[int] = None
    hard_work: Optional[bool] = None
    mid_work: Optional[bool] = None
    art_work: Optional[bool] = None
    other_work: Optional[str] = None
    tools: Optional[str] = None
    language: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    citizenship: Optional[str] = None
    wallet: Optional[str] = None
    is_driver: Optional[bool] = None
    transport: Optional[str] = None
    is_military: Optional[bool] = None
    other_info: Optional[str] = None
    photo_link: Optional[int] = None


class OrderInfo(BaseModel):
    status: Optional[str] = 'Active'
    reg_date: Optional[date] = date.today()
    manager_id: Optional[int] = None
    employer_id: Optional[int] = None
    order_date: Optional[date] = None
    tasks: Optional[str] = None
    place: Optional[str] = None
    work_form: Optional[str] = None
    price_full: Optional[float] = None
    price_hour: Optional[float] = None
    payment_form: Optional[str] = None
    need_workers: Optional[int] = None
    tools: Optional[str] = None
    transfer_type: Optional[str] = None
    leave_time: Optional[time] = None
    start_time: Optional[time] = None
    finish_time: Optional[time] = None
    back_time: Optional[time] = None
    break_time: Optional[time] = None
    is_feed: Optional[bool] = None
    clothes: Optional[str] = 'Рабочая одежда'
    add_info: Optional[str] = None
    break_duration: Optional[int] = 60
    taskmaster_id: Optional[int] = None
    worker_telegram_id_1: Optional[int] = None
    worker_telegram_id_2: Optional[int] = None
    worker_telegram_id_3: Optional[int] = None
    worker_telegram_id_4: Optional[int] = None
    worker_telegram_id_5: Optional[int] = None
    worker_telegram_id_6: Optional[int] = None
    worker_telegram_id_7: Optional[int] = None
    worker_telegram_id_8: Optional[int] = None
    worker_telegram_id_9: Optional[int] = None
    worker_telegram_id_10: Optional[int] = None


class EmployerInfo(BaseModel):
    name: str
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    phone: str
    telegram_id: Optional[int] = None
    comment: Optional[str] = None


async def verify_token(request: Request):
    pass
    headers = request.headers
    access_token = headers.get('Authorization')
    if access_token is None:
        raise HTTPException(status_code=401, detail='Отсутствует токен доступа Authorization')
    if access_token != ACCESS_TOKEN:
        raise HTTPException(status_code=403, detail='Доступ запрещен')


@app.get('/api/users/')
async def get_users_all(token: str = Depends(verify_token)):
    usr_table = db.connect_table('users')
    users = usr_table.get_all()
    response = users
    return response


@app.get('/api/users/{user_id}', response_model=UserInfo)
async def get_user(user_id: int, token: str = Depends(verify_token)):
    usr_table = db.connect_table('users')
    response = usr_table.get_by_id(user_id)
    if response:
        return response
    else:
        raise HTTPException(status_code=404, detail="Пользователь не найден")


@app.get('/api/users/name/')
async def get_users_by_name(pattern: str, token: str = Depends(verify_token)):
    user_table = db.connect_table('users')
    result = user_table.get_by_pattern_str(param='name', pattern=pattern)
    return result


@app.post('/api/users/')
async def add_user(user: UserInfo, token: str = Depends(verify_token)) -> dict:
    usr_table = db.connect_table('users')
    user_dict = user.dict()
    result = usr_table.insert(**user_dict)
    if result:
        response = usr_table.get_by_id(id=user_dict['id'])
        return {'id': response}
    else:
        raise HTTPException(status_code=422, detail="Ошибка сохранения данных")


@app.put('/api/users/')
async def update_user(user: UserInfo, token: str = Depends(verify_token)) -> dict:
    usr_table = db.connect_table('users')
    user_dict = user.dict()
    result = usr_table.update_record(id=user_dict['id'], updates=user_dict)
    if result:
        response = usr_table.get_by_id(id=user_dict['id'])
        return response
    else:
        raise HTTPException(status_code=422, detail='Ошибка изменения данных')


@app.delete('/api/users/{user_id}')
async def delete_user(user_id: int, token: str = Depends(verify_token)) -> dict:
    usr_table = db.connect_table('users')
    result = usr_table.delete_by_id(id=user_id)
    if result:
        return {'user_id': user_id, 'status': 'deleted'}
    else:
        raise HTTPException(status_code=422, detail='Ошибка удаления пользователя')


@app.get('/api/employers/')
async def get_employers_all(token: str = Depends(verify_token)):
    emp_table = db.connect_table('employers')
    result = emp_table.get_all()
    return result


@app.get('/api/employers/{employer_id}')
async def get_employer(employer_id: int, token: str = Depends(verify_token)):
    emp_table = db.connect_table('employers')
    result = emp_table.get_by_id(employer_id)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Пользователь не найден")


@app.get('/api/employers/name/')
async def get_employers_by_name(pattern: str, token: str = Depends(verify_token)):
    emp_table = db.connect_table('employers')
    result = emp_table.get_by_pattern_str(param='name', pattern=pattern)
    return result


@app.post('/api/employers/')
async def add_employer(employer: EmployerInfo, token: str = Depends(verify_token)):
    emp_table = db.connect_table('employers')
    employer = employer.dict()
    result = emp_table.insert(**employer)
    if result:
        return {'id': result}
    else:
        return HTTPException(status_code=422, detail='Ошибка сохранения')


@app.put('/api/employers/')
async def update_employer(employer_id: int, employer: EmployerInfo, token: str = Depends(verify_token)) -> dict:
    emp_table = db.connect_table('employers')
    employer_dict = employer.dict()
    result = emp_table.update_record(id=employer_id, updates=employer_dict)
    if result:
        response = emp_table.get_by_id(id=employer_id)
        return response
    else:
        raise HTTPException(status_code=422, detail='Ошибка изменения данных')


@app.delete('/api/employers/{employer_id}')
async def delete_employer(employer_id: int, token: str = Depends(verify_token)) -> dict:
    emp_table = db.connect_table('employers')
    result = emp_table.delete_by_id(id=employer_id)
    if result:
        return {'employer_id': employer_id, 'status': 'deleted'}
    else:
        raise HTTPException(status_code=422, detail='Ошибка удаления пользователя')


@app.get('/api/orders/')
async def get_orders_all(token: str = Depends(verify_token)):
    order_table = db.connect_table('orders')
    orders = order_table.get_all()
    return orders


@app.get('/api/orders/{order_id}')
async def get_order(order_id: int, token: str = Depends(verify_token)):
    order_table = db.connect_table('orders')
    order = order_table.get_by_id(order_id)
    if order:
        return order
    else:
        raise HTTPException(status_code=404, detail='Заказ не найден')


@app.post('/api/orders/')
async def add_order(order: OrderInfo, token: str = Depends(verify_token)):
    orders_table = db.connect_table('orders')
    order = dict(order)
    result = orders_table.insert(**order)
    if result:
        return {'id': result}
    else:
        raise HTTPException(status_code=422, detail="Ошибка сохранения данных")


@app.put('/api/orders/{order_id}')
async def update_order(order_id: int, order_data: dict, token: str = Depends(verify_token)):
    order_table = db.connect_table('orders')
    new_order = dict(order_data)
    result = order_table.update_record(order_id, new_order)
    if result:
        return {'id': order_id, 'status': 'updated'}
    else:
        raise HTTPException(status_code=422, detail="Ошибка обновления")


@app.delete('/api/orders/{order_id}')
async def delete_order(order_id: int, token: str = Depends(verify_token)) -> dict:
    emp_table = db.connect_table('orders')
    result = emp_table.delete_by_id(id=order_id)
    if result:
        return {'order_id': order_id, 'status': 'deleted'}
    else:
        raise HTTPException(status_code=422, detail='Ошибка удаления пользователя')


@app.get('/api/orders/worker/')
async def get_users_orders(user_id: int, token: str = Depends(verify_token)) -> list:
    emp_table = db.connect_table('orders')
    columns = ['worker_telegram_id_1',
               'worker_telegram_id_2',
               'worker_telegram_id_3',
               'worker_telegram_id_4',
               'worker_telegram_id_5',
               'worker_telegram_id_6',
               'worker_telegram_id_7',
               'worker_telegram_id_8',
               'worker_telegram_id_9',
               'worker_telegram_id_10',
               ]
    orders = emp_table.search_in_table(columns, user_id)
    return orders


@app.put('/api/orders/status/')
async def finish_order(order_id: int, token: str = Depends(verify_token)):
    order_table = db.connect_table('orders')
    try:
        value = {'status': 'Finished'}
        order_table.update_record(order_id, value)
        return {'status': 'Success'}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
