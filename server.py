from fastapi import FastAPI, HTTPException, Request, Depends, Query
from pydantic import BaseModel
from typing import Optional
from database import DataBase
from datetime import date, time
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, ACCESS_TOKEN
from psycopg2.errors import UniqueViolation
from database import RecordNotFound

app = FastAPI(
    title='MBT DataBase'
)


user_table = 'users'
customer_table = 'customers'
order_table = 'orders'
order_workers_table = 'order_workers'


class UserInfo(BaseModel):
    id: int
    access: str
    reg_date: date | None = None
    status: str | None = None
    rating: int | None = 0
    profit: int | None = 0
    orders: int | None = 0
    comment: str | None = None

    name: str
    sex: str
    born_date: date
    skills: str | None = None
    tools: str | None = None
    phone: str
    wallet: str | None = None
    transport: str | None = None
    other_info: str | None = None


class OrderInfo(BaseModel):
    id: int | None = None
    status: str
    reg_date: date
    manager_id: int
    customer_id: int | None = None
    order_date: date
    start_time: time | None = None
    finish_time: time | None = None
    transfer_type: str
    order_cost: int | None = None
    leave_place: str | None = None
    leave_time: time | None = None
    worker_price_hour: int | None = None
    need_foreman: bool
    payment_form: str | None = None
    break_duration: int | None = None
    count_workers: int | None = None
    order_place: str
    tasks: list[str]
    tools: list | None = None
    extra_info: str | None = None


class CustomerInfo(BaseModel):
    id: int | None = None
    name: str
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    phone: str
    telegram_id: Optional[int] = None
    comment: Optional[str] = None


async def verify_token(request: Request):
    headers = request.headers
    return
    access_token = headers.get('Authorization')
    if access_token is None:
        raise HTTPException(status_code=401, detail='Отсутствует токен доступа Authorization')
    if access_token != ACCESS_TOKEN:
        raise HTTPException(status_code=403, detail='Доступ запрещен')


@app.get('/api/users/')
async def get_users_all(token: str = Depends(verify_token)):
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
        users = db.get_all(user_table)
        return users
    except RecordNotFound as e:
        raise HTTPException(status_code=422, detail=f"{e}")
    finally:
        db.disconnect()


@app.get('/api/users/{user_id}', response_model=UserInfo)
async def get_user(user_id: int, token: str = Depends(verify_token)):
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        result = db.get_by_id(table_name=user_table, id=user_id)
        return result
    except RecordNotFound as e:
        raise HTTPException(status_code=404, detail=f"{e}")
    finally:
        db.disconnect()


@app.get('/api/users/name/')
async def get_users_by_name(pattern: str, token: str = Depends(verify_token)):
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
        result = db.get_by_pattern_str(table_name=user_table, param='name', pattern=pattern)
        return result
    except RecordNotFound:
        raise HTTPException(status_code=404, detail=f"Пользователи не найдены")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    finally:
        db.disconnect()


@app.get('/api/users/sex/')
async def get_users_by_name(sex: str, token: str = Depends(verify_token)):
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        result = db.get_by_pattern_str(table_name=user_table, param='sex', pattern=sex)
        return result
    except RecordNotFound:
        raise HTTPException(status_code=404, detail=f"Пользователи не найдены")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    finally:
        db.disconnect()


@app.get('/api/users/born_date/', description='Получить пользователей по дате рождения')
async def get_users_by_age(date_from: date, date_to: date, token: str = Depends(verify_token)):
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:

        result = db.get_by_size(table_name=user_table, param='born_date', min_value=date_from, max_value=date_to)
        return result
    except RecordNotFound:
        raise HTTPException(status_code=404, detail=f"Пользователи не найдены")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    finally:
        db.disconnect()


@app.get('/api/users/phone/')
async def get_users_by_phone(pattern: str, token: str = Depends(verify_token)):
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        result = db.get_by_pattern_str(table_name=user_table, param='phone', pattern=pattern)
        return result
    except RecordNotFound:
        raise HTTPException(status_code=404, detail=f"Пользователи не найдены")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    finally:
        db.disconnect()


@app.get('/api/users/{user_id}/orders/')
async def get_users_orders(user_id: int, token: str = Depends(verify_token)):
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        orders = db.get_by_param(table_name=order_workers_table, param='worker_id', value=user_id)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    finally:
        db.disconnect()


@app.post('/api/users/')
async def add_user(user: UserInfo, token: str = Depends(verify_token)) -> dict:
    user_dict = user.dict()
    if not user_dict['id']:
        user_dict.pop('id')
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        result = db.insert(table_name=user_table, **user_dict)
        return result
    except UniqueViolation:
        raise HTTPException(status_code=422, detail=f'Уже существует пользователь с таким id')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    finally:
        db.disconnect()


@app.put('/api/users/')
async def update_user(user: UserInfo, token: str = Depends(verify_token)) -> dict:
    user_dict = user.dict()
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        result = db.update_record(table_name=user_table, id=user_dict['id'], updates=user_dict)
        return result
    except TypeError:
        raise HTTPException(status_code=422, detail='Пользователь не существует')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    finally:
        db.disconnect()


@app.delete('/api/users/{user_id}')
async def delete_user(user_id: int, token: str = Depends(verify_token)) -> dict:
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        result = db.delete_by_id(table_name=user_table, id=user_id)
        if result:
            return result
        else:
            raise HTTPException(status_code=422, detail='Ошибка удаления пользователя')
    finally:
        db.disconnect()


@app.get('/api/customers/')
async def get_customers_all(token: str = Depends(verify_token)):
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        result = db.get_all(table_name=customer_table)
        return result
    except RecordNotFound:
        raise HTTPException(status_code=404, detail=f"Пользователи не найдены")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    finally:
        db.disconnect()


@app.get('/api/customers/{customer_id}')
async def get_customer(customer_id: int, token: str = Depends(verify_token)):
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        result = db.get_by_id(table_name=customer_table, id=customer_id)
        return result
    except RecordNotFound:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    finally:
        db.disconnect()


@app.get('/api/customers/name/')
async def get_customers_by_name(pattern: str, token: str = Depends(verify_token)):
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        result = db.get_by_pattern_str(table_name=customer_table, param='name', pattern=pattern)
        return result
    except RecordNotFound:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    finally:
        db.disconnect()


@app.post('/api/customers/')
async def add_customer(customer: CustomerInfo, token: str = Depends(verify_token)):
    customer_dict = customer.dict()
    if not customer_dict['id']:
        customer_dict.pop('id')
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        result = db.insert(table_name=customer_table, **customer_dict)
        return result
    except UniqueViolation:
        raise HTTPException(status_code=422, detail='Пользователь с таким id уже существует')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'{e}')
    finally:
        db.disconnect()


@app.put('/api/customers/')
async def update_customer(customer_id: int, customer: CustomerInfo, token: str = Depends(verify_token)) -> dict:
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        customer_dict = customer.dict()
        result = db.update_record(table_name=customer_table, id=customer_id, updates=customer_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'{e}')
    finally:
        db.disconnect()


@app.delete('/api/customers/{customer_id}')
async def delete_customer(customer_id: int, token: str = Depends(verify_token)) -> dict:
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        result = db.delete_by_id(table_name=customer_table, id=customer_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'{e}')
    finally:
        db.disconnect()


@app.get('/api/orders/')
async def get_orders_all(token: str = Depends(verify_token)):
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        orders = db.get_all(table_name=order_table)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'{e}')
    finally:
        db.disconnect()


@app.get('/api/orders/{order_id}')
async def get_order(order_id: int, token: str = Depends(verify_token)):
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        order = db.get_by_id(table_name=order_table, id=order_id)
        return order
    except RecordNotFound:
        raise HTTPException(status_code=404, detail='Заказ не найден')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'{e}')
    finally:
        db.disconnect()


@app.get('/api/orders/{order_id}/workers/')
async def get_workers_id(order_id: int, token: str = Depends(verify_token)):
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        result = db.get_by_param(table_name=order_workers_table, param='order_id', value=order_id)
        return [worker['worker_id'] for worker in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'{e}')
    finally:
        db.disconnect()


@app.post('/api/orders/{order_id}/workers/')
async def add_worker(order_id: int, worker_id: int, token: str = Depends(verify_token)):
    data = {
        'order_id': order_id,
        'worker_id': worker_id
    }
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        result = db.insert(table_name=order_workers_table, **data)
        return result
    except Exception as e:
        return HTTPException(status_code=500, detail=e)
    finally:
        db.disconnect()


@app.post('/api/orders/')
async def add_order(order: OrderInfo, token: str = Depends(verify_token)):
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        order_dict = dict(order)
        if not order_dict['id']:
            order_dict.pop('id')
        result = db.insert(table_name=order_table, **order_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    finally:
        db.disconnect()


@app.put('/api/orders/{order_id}', response_model=OrderInfo)
async def update_order(order_id: int, order: OrderInfo, token: str = Depends(verify_token)):
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        order_dict = dict(order)
        if not order_dict['id']:
            order_dict.pop('id')
        result = db.update_record(table_name=order_table, id=order_id, updates=order_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    finally:
        db.disconnect()


@app.delete('/api/orders/{order_id}')
async def delete_order(order_id: int, token: str = Depends(verify_token)) -> dict:
    db = DataBase(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    try:
        result = db.delete_by_id(table_name=order_table, id=order_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'{e}')
    finally:
        db.disconnect()
