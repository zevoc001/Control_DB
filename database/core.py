from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine.url import URL
from dotenv import load_dotenv
import os


load_dotenv('/Control_DB/.env')

database = {
    'drivername': 'postgres',
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'username': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),

}
engine = create_engine(
    url=URL(**database),
    echo=True,
    pool_size=5,
    max_overflow=10
)

with engine.connect() as conn:
    res = conn.execute(text('SELECT VERSION()'))
    print(f'{res=}')
