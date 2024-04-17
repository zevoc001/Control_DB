from typing import Dict, Any
from datetime import date
import psycopg2 as pg
from psycopg2.extras import DictCursor
from config import DB_NAME, DB_PORT, DB_USER, DB_HOST, DB_PASSWORD


class DataBase():
    '''
    Класс DataBase предназначен для управления подключением к базе данных PostgreSQL. 
    Этот класс позволяет выполнять подключение к базе данных, создание и удаление таблиц, а также управление транзакциями и сессиями.

    db_name: имя базы данных к которой необходимо подключиться.
    user: имя пользователя для доступа к базе данных.
    password: пароль пользователя для доступа к базе данных.
    host: адрес сервера базы данных.
    port: порт сервера базы данных (по умолчанию 5432).

    Исключения
    В случае ошибок подключения к базе данных метод connect_db() выбрасывает исключение ConnectionError.
    При ошибках выполнения операций с базой данных будет выброшено исключение pg.Error.
    '''

    def __init__(self, db_name:str, user:str, password:str, host:str, port= 5432):
        self.db_name = db_name
        self.user = user
        self.password = password 
        self.host= host
        self.port = port
        self.status = False

    def connect_db(self) -> object: # Подключение к БД PostgreeSQL
        '''
        Подключается к базе данных PostgreSQL. В случае успешного подключения возвращает объект conn для выполнения операций с базой данных. 
        В случае неудачи выбрасывает исключение ConnectionError. 
        '''
        step_conn = 0 
        def connecting(step_conn): # Попытка подключения
            conn_string = "dbname='{0}' user='{1}' password='{2}' host='{3}' port='{4}'".format(self.db_name, self.user, self.password, self.host, self.port) # Строка запроса
            try:
                self.conn = pg.connect(conn_string)
                self.status = True
            except pg.OperationalError:
                step_conn += 1
                if step_conn < 5:
                    connecting(step_conn)

        connecting(step_conn)
        if self.status == True:
            return self.conn
        else:
            raise ConnectionError
        
    def connect_table(self, table_name: str):
        '''
        
        Подключает к таблице БД. В качестве аргумента принимает название таблицы.
        Перед подключение к таблице необходимо подключиться к БД
        Возвращает объект Table.
        '''
        table = Table(self, table_name)
        return table
    
    def create_table(self, table_name: str, table_schema: str):
        '''
        Создаёт и возвращает объект класса Table, связанный с указанной таблицей в базе данных. Этот метод позволяет работать с таблицами через высокоуровневый интерфейс.

        table_name: название таблицы в базе данных.
        create_table(table_name: str, table_schema: str)
        Создаёт новую таблицу в базе данных с указанной схемой. Если таблица с таким именем уже существует, действие не выполняется.

        Схема пишется в стиле SQL описания таблицы, например:
        'id SERIAL PRIMARY KEY, name VARCHAR(100), age INT'.
        '''
        with self.conn.cursor() as cursor:
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({table_schema})")
            self.conn.commit()

    def drop_table(self, table_name: str):
        '''
        Удаляет таблицу из базы данных. Если таблица не существует, операция игнорируется.
        table_name: название удаляемой таблицы.
        В случае ошибки возвращает pg.Error
        '''
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                self.conn.commit()
        except:
            self.conn.rollback()
            raise pg.Error
        
    def disconnect(self):
        '''
        Отключает текущее соединение с базой данных и освобождает ресурсы. 
        После вызова этого метода дальнейшее взаимодействие с базой данных через текущий экземпляр класса DataBase становится невозможным.
        '''
        self.conn.close()
        self.status = False


class Table(): # Таблица данных пользователей
    '''
    Класс Table предназначен для взаимодействия с конкретной таблицей в базе данных PostgreSQL. 
    Он предоставляет методы для выполнения основных операций с данными: выборка (SELECT), вставка (INSERT), удаление (DELETE) и обновление (UPDATE) записей.
    '''
    def __init__(self, db, table_name):
        self.db_name = db.db_name
        self.conn = db.conn
        self.table_name = table_name

    def get_by_id(self, id: int) -> list:
        """
        Выполняет выборку данных из таблицы. Может использоваться для выборки всех записей или записей, удовлетворяющих условию where.
        """
        select_query = f'SELECT * FROM {self.table_name} WHERE "id" = CAST(%s AS INTEGER);'
        with self.conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(select_query, (id,))
            records = cursor.fetchall()
            records_dict = [dict(record) for record in records]
            return records_dict  # Возвращается список кортежей

    def get_by_param(self, param: str, value: str|int) -> list:
        """
        Выполняет выборку данных из таблицы. Может использоваться для выборки всех записей или записей, удовлетворяющих условию where.
        """
        if type(value) == str:
            select_query = f'SELECT * FROM {self.table_name} WHERE "{param}" = CAST(%s AS VARCHAR)'
        else:
            select_query = f'SELECT * FROM {self.table_name} WHERE "{param}" = CAST(%s AS INTEGER)'
        with self.conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(select_query, (value,))
            records = cursor.fetchall()
            try:
                user = [dict(record) for record in records]
                user['data_reg'] = user['data_reg'].strftime("%Y-%m-%d")
                user['born'] = user['born'].strftime("%Y-%m-%d")
                return records  # Возвращается список кортежей
            except IndexError:
                return []


    def insert(self, **kwargs): # Добавление нового кортежа
        '''
        Добавляет новую запись в таблицу. Аргументы передаются в виде именованных параметров, где ключи соответствуют именам столбцов.
        Данные передаются следующим образом:
        id = 1, name = 'John'...'''
        keys = ', '.join(kwargs.keys())
        values = tuple(kwargs.values())
        placeholders = ', '.join(['%s'] * len(kwargs))

        insert_query = f"INSERT INTO {self.table_name} ({keys}) VALUES ({placeholders})"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(insert_query, values)
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            raise e
            return False

    def delete_by_id(self, id: int): # Удаление кортежа
        '''
        Удаляет записи из таблицы, удовлетворяющие условию where.
        where: строка условия для удаления (например, "id = 4")
        '''
        delete_query = f"DELETE FROM {self.table_name} WHERE id = CAST(%s AS INTEGER)"

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(delete_query, (id, ))
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            return False

    def delete_by_param(self, param: str, value: int|str):
        '''
        Удаляет записи из таблицы, удовлетворяющие условию where.
        where: строка условия для удаления (например, "id = 4")
        '''
        if type(value) == int:
            delete_query = f"DELETE FROM {self.table_name} WHERE {param} = CAST(%s AS INTEGER)"
        else:
            delete_query = f"DELETE FROM {self.table_name} WHERE {param} = CAST(%s AS VARCHAR)"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(delete_query, (value, ))
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            return False

    def update_record(self, id: int, column_name: str, new_value: int|str):
        """
        Обновляет один параметр записи в указанной таблице.

        id: идентификатор записи, которую нужно обновить.
        column_name: название столбца, значение которого нужно обновить.
        new_value: новое значение для указанного столбца.
        Если запись нет возвращается True
        Если значение неверное возвращается True
        """
        query = f"UPDATE {self.table_name} SET {column_name} = %s WHERE id = %s"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (new_value, id))
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            return False