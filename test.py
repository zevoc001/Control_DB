from DataBase import DataBase
import os
import psycopg2 as pg
import unittest
from dotenv import load_dotenv

load_dotenv('conf.env')

class DataBaseTest(unittest.TestCase):
    def setUp(self):
        self.db_name= os.getenv('DB_NAME')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        host= os.getenv('DB_HOST')
        port = os.getenv('DB_PORT')
        self.db = DataBase(self.db_name, user, password, host, port)
        self.conn = self.db.connect_db()
        self.assertIsNotNone(self.conn)

    def test_create_table(self):
        self.db.create_table('test_users_data', 'id SERIAL PRIMARY KEY, name VARCHAR(100), age INT')

    def test_connecting_table(self):
        self.table = self.db.connect_table('test_users_data')
    
    def test_drop_table(self):
        self.db.drop_table('test_users_data')
        self.table = self.db.connect_table('test_users_data')

    def tearDown(self):
        self.db.disconnect()
        status = self.db.status
        self.assertFalse(status)

if __name__ == '__main__':
    unittest.main()