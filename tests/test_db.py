from database import DataBase
import os
import unittest
from dotenv import load_dotenv

load_dotenv('../.env')

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
        self.table = self.db.connect_table('users')

    def test_insert(self):
        self.table = self.db.connect_table('users')
        result = self.table.insert(name = 'John')
        self.assertTrue(result)

    def test_get_by_id(self):
        self.table = self.db.connect_table('users')
        user = self.table.get_by_id(1)
        self.assertTrue(user)

    def test_get_by_param_int(self):
        self.table = self.db.connect_table('users')
        user = self.table.get_by_param(param='telegram_id', value='1383046637')
        self.assertTrue(user)

    def test_get_by_param_int_wrong(self):
        self.table = self.db.connect_table('users')
        user = self.table.get_by_param(param='telegram_id', value='0')
        self.assertFalse(user)

    def test_get_by_param_str(self):
        self.table = self.db.connect_table('users')
        user = self.table.get_by_param(param='name', value='Бойко Иван Анатольевич')
        self.assertTrue(user)

    def test_get_by_param_str_wrong(self):
        self.table = self.db.connect_table('users')
        user = self.table.get_by_param(param='name', value='867п7е6пщгп7ека')
        self.assertFalse(user)

    def test_delete_by_id(self):
        self.table = self.db.connect_table('users')
        result = self.table.delete_by_id(5)
        self.assertTrue(result)

    def test_delete_by_param_str(self):
        self.table = self.db.connect_table('users')
        result = self.table.delete_by_param(param='name', value='John')
        self.assertTrue(result)

    def test_delete_by_param_str_wrong(self):
        self.table = self.db.connect_table('users')
        result = self.table.delete_by_param(param='', value='John')
        self.assertFalse(result)

    def test_delete_by_param_int(self):
        self.table = self.db.connect_table('users')
        result = self.table.delete_by_param(param='age', value=0)
        self.assertTrue(result)

    def test_delete_by_param_int_wrong(self):
        self.table = self.db.connect_table('users')
        result = self.table.delete_by_param(param='age', value='0')
        self.assertFalse(result)

    def test_update_record(self):
        self.table = self.db.connect_table('users')
        result = self.table.update_record(id=1, column_name='status', new_value='Test')
        self.assertTrue(result)

    def test_update_record_wrong_id(self):
        self.table = self.db.connect_table('users')
        result = self.table.update_record(id=0, column_name='status', new_value='Test')
        self.assertTrue(result)

    def test_update_record_wrong_column(self):
        self.table = self.db.connect_table('users')
        result = self.table.update_record(id=1, column_name='sta', new_value='Test')
        self.assertFalse(result)

    def test_update_record_wrong_value(self):
        self.table = self.db.connect_table('users')
        result = self.table.update_record(id=1, column_name='status', new_value=99)
        self.assertTrue(result)
    
    def test_drop_table(self):
        self.db.drop_table('test_users_data')
        self.table = self.db.connect_table('test_users_data')

    def tearDown(self):
        self.db.disconnect()
        status = self.db.status
        self.assertFalse(status)

if __name__ == '__main__':
    unittest.main()