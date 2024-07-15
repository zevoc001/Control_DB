import psycopg2
from datetime import date
from psycopg2.extras import DictCursor
from psycopg2.errors import UniqueViolation, ConnectionException


class RecordNotFound(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'RecordNotFound, {self.message}'
        else:
            return 'RecordNotFound'


class DataBase:
    """
    Class DataBase:
    Класс DataBase предназначен для управления подключением к базе данных PostgreSQL.
    Этот класс позволяет выполнять подключение к базе данных, создание и удаление таблиц, а также управление транзакциями и сессиями.

    Attributes:
        db_name (str): Имя базы данных к которой необходимо подключиться.
        user (str): Имя пользователя для доступа к базе данных.
        password (str): Пароль пользователя для доступа к базе данных.
        host (str): Адрес сервера базы данных.
        port (int): Порт сервера базы данных (по умолчанию 5432).
        status (bool): Статус подключения к базе данных.

    Methods:
        connect_db() -> object:
            Подключается к базе данных PostgreSQL. В случае успешного подключения возвращает объект conn для выполнения операций с базой данных.
            В случае неудачи выбрасывает исключение ConnectionError.

        connect_table(table_name: str):
            Подключает к таблице БД. В качестве аргумента принимает название таблицы.
            Перед подключением к таблице необходимо подключиться к БД.
            Возвращает объект Table.

        create_table(table_name: str, table_schema: str):
            Создаёт и возвращает объект класса Table, связанный с указанной таблицей в базе данных.
            Этот метод позволяет работать с таблицами через высокоуровневый интерфейс.
            Создаёт новую таблицу в базе данных с указанной схемой. Если таблица с таким именем уже существует, действие не выполняется.
            Схема пишется в стиле SQL описания таблицы, например: 'id SERIAL PRIMARY KEY, name VARCHAR(100), age INT'.

        drop_table(table_name: str):
            Удаляет таблицу из базы данных. Если таблица не существует, операция игнорируется.
            В случае ошибки возвращает pg.Error.

        disconnect():
            Отключает текущее соединение с базой данных и освобождает ресурсы.
            После вызова этого метода дальнейшее взаимодействие с базой данных через текущий экземпляр класса DataBase становится невозможным.
"""

    def __init__(self, db_name: str, user: str, password: str, host: str, port=5432):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = psycopg2.connect(database=db_name, user=user, password=password, host=host, port=port,
                                           cursor_factory=DictCursor)
        self.cursor = self.connection.cursor()

    def get_by_id(self, table_name: str, id: int) -> dict:
        """
        Выполняет выборку данных из таблицы.
        Если найдено несколько записей с указанным id, то возвращает первую найденную.
        Args:
            table_name: название таблицы
            id: уникальный номер записи

        Returns:
            Возвращает словарь с данными в их типе.
            Если запись не найдена возвращает ошибку RecordNotFound.
        """

        select_query = f'SELECT * FROM "{table_name}" WHERE "id" = %s;'
        try:
            self.cursor.execute(select_query, (id,))
            records = self.cursor.fetchall()
            self.connection.commit()
            records_list = [dict(record) for record in records]
            if records_list:
                record = records_list[0]
                return record
            else:
                raise RecordNotFound()
        except Exception as e:
            self.connection.rollback()
            raise e

    def get_by_param(self, table_name: str, param: str, value: str | int) -> list[dict]:
        """
        Выполняет выборку записей из таблицы на основе значения столбца.
        В качестве условия поиска использует название столбца (param) и его значение (числовое или строковое)
        Args:
            table_name: название таблицы
            param: наименование столбца
            value: значение столбца

        Returns:
        Возвращает список с найденными записями d виде словаря в их типе.
        Если записей нет, то возвращает пустой список
        """

        if type(value) == str:
            select_query = f'SELECT * FROM "{table_name}" WHERE "{param}" = CAST(%s AS VARCHAR)'
        else:
            select_query = f'SELECT * FROM "{table_name}" WHERE "{param}" = CAST(%s AS INTEGER)'

        try:
            self.cursor.execute(select_query, (value,))
            records = self.cursor.fetchall()
            records_list = [dict(record) for record in records]
            return records_list
        except Exception as e:
            raise e
        finally:
            self.connection.rollback()

    def get_by_pattern_str(self, table_name: str, param: str, pattern: str | int) -> list[dict]:
        """
        Выполняет выборку записей на основе шаблона. Поиск производится без учета регистра.

        Args:
            table_name: название таблицы
            param: наименование столбца
            pattern: шаблон

        Returns:
        Возвращает список с найдеными записями.
        """

        select_query = f'SELECT * FROM "{table_name}" WHERE {param} ILIKE %s'
        value = f'%{pattern}%'
        try:
            self.cursor.execute(select_query, (value,))
            records = self.cursor.fetchall()
            records_list = [dict(record) for record in records]
            return records_list
        except Exception as e:
            raise e
        finally:
            self.connection.rollback()

    def get_by_size(self, table_name: str, param: str, max_value: int | date, min_value: int | date) -> list:
        """
        Выполняет выборку записей на основе вхождения значения в диапазон.
        Указывается максимальное и минимальное значение. Поиск происходит с учетом граничных значений
        В случае с датой необходимо передать объект типа date

        Args:
            table_name: название таблицы
            param: столбец
            max_value: нижняя граница (Включительно)
            min_value: верхняя граница (Включительно)

        Returns:
            Возвращает список совпавших кортежей
        """

        select_query = f'SELECT * FROM "{table_name}" WHERE {param} BETWEEN %s AND %s'
        max_value = f'%{max_value}%'
        min_value = f'%{min_value}%'
        try:
            self.cursor.execute(select_query, (min_value, max_value))
            records = self.cursor.fetchall()
            records_list = [dict(record) for record in records]
            return records_list
        except Exception as e:
            raise e
        finally:
            self.connection.rollback()

    def get_all(self, table_name: str) -> list:
        """
        Возвращает все записи из таблицы.
        Args:
            table_name: название атблицы

        Returns:
            Возвращает список со значениями
        """

        select_query = f'SELECT * FROM "{table_name}"'
        try:
            self.cursor.execute(select_query)
            records = self.cursor.fetchall()
            records_list = [dict(record) for record in records]
            return records_list
        except Exception as e:
            raise e
        finally:
            self.connection.rollback()

    def insert(self, table_name: str, **kwargs):  # Добавление нового кортежа
        """
        Добавляет запись в таблицу.
        Если значение id является автозаполняемым, то оно может не указываться.
        Args:
            table_name: название таблицы
            **kwargs: именованные значения столбцов

        Returns:
            Возвращает данные вставленной записи.
        """

        keys = ', '.join(kwargs.keys())
        values = tuple(kwargs.values())
        placeholders = ', '.join(['%s'] * len(kwargs))

        insert_query = f'INSERT INTO "{table_name}" ({keys}) VALUES ({placeholders}) RETURNING *'
        try:
            self.cursor.execute(insert_query, values)
            record = self.cursor.fetchone()
            result = dict(record)
            self.connection.commit()
            return result
        except UniqueViolation as e:
            self.connection.rollback()
            raise e
        except Exception as e:
            self.connection.rollback()
            raise e

    def delete_by_id(self, table_name: str, id: int):  # Удаление кортежа
        """
        Удаляет записи из таблицы по значению id.

        Args:
            table_name: название таблицы
            id: id записи

        Returns:
            Возвращает данные удаленной записи
        """

        delete_query = f'DELETE FROM "{table_name}" WHERE id = %s RETURNING *'

        try:
            self.cursor.execute(delete_query, (id,))
            record = self.cursor.fetchone()
            result = dict(record)
            self.connection.commit()
            return result
        except Exception as e:
            self.connection.rollback()
            raise e

    def delete_by_param(self, table_name: str, param: str, value: int | str):
        """
        Удаляет записи из таблицы на основе значения столбца.

        Args:
            table_name: название таблицы
            param: название столбца
            value: значение для фильтрации

        Returns:
            Возвращает данные удаленной записи
        """

        if type(value) == int:
            delete_query = (f'DELETE FROM "{table_name}" WHERE {param} = CAST(%s AS INTEGER)'
                            f'RETURNING *')
        else:
            delete_query = (f'DELETE FROM "{table_name}" WHERE {param} = CAST(%s AS VARCHAR)'
                            f'RETURNING *')

        try:
            self.cursor.execute(delete_query, (value,))
            records = self.cursor.fetchall()
            result = [dict(record) for record in records]
            self.connection.commit()
            return result
        except Exception as e:
            self.connection.rollback()
            raise e

    def update_record(self, table_name: str, id: int, updates: dict) -> dict:
        """
        Обновляет запись в таблице.

        Args:
            table_name: название таблицы
            id: уникальный идентификатор записи
            updates: словарь с новыми данными записи

        Returns:
            Возвращает словарь с данные вставленной записи
        """

        # Собираем части запроса для каждого ключа в словаре updates
        set_clause = ', '.join([f"{key} = %s" for key in updates.keys()])
        values = list(updates.values())
        values.append(id)  # добавляем id в конец списка параметров

        query = f'UPDATE "{table_name}" SET {set_clause} WHERE id = %s RETURNING *'
        self.cursor.execute(query, values)
        try:
            record = self.cursor.fetchone()
            result = dict(record)
            self.connection.commit()
            return result
        except TypeError as e:
            self.connection.rollback()
            raise TypeError(f'Запись не обновлена, {e}')
