import os
from dotenv import load_dotenv


load_dotenv('.env')

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_TABLE = os.getenv('DB_TABLE')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
