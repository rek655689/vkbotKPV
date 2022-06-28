import mysql.connector
from typing import List, Tuple, Dict, Set
from functools import wraps


def connect(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        with mysql.connector.connect(**self.database_config) as connection:
            cursor = connection.cursor()
            result = func(self, cursor, *args, **kwargs)
            connection.commit()
            cursor.close()
            connection.close()
        return result
    return inner


class Database:

    def __init__(self, database_config):
        self.database_config = database_config

    @connect
    def get_one(self, cursor, table: str, key: str, value: any, column: str = None, extra='') -> tuple or None:
        """
        Получение одной строки данных из базы данных

        :param cursor: курсор БД
        :param table: таблица, в которой происходит поиск
        :param key: ключ, по которому осуществляется поиск
        :param value: значение ключа
        :param column: необязательный параметр, обзначает столбец
        :param extra: дополнительные условия для запроса
        :return: кортеж с данными строки или None
        """

        if column is None:
            cursor.execute(f"SELECT * FROM {table} WHERE {key} = '{value}'{extra}")
        else:
            cursor.execute(f"SELECT {column} FROM {table} WHERE {key} = '{value}'{extra}")
        result = cursor.fetchone()
        return result

    @connect
    def get_all(self, cursor, table: str, key: str = None, value: any = None, column: str = None, extra: str = '') -> List[tuple] or List[None]:
        """
        Получение нескольких строк из базы данных
        :param cursor: курсор БД
        :param table: таблица, в которой происходит поиск
        :param key: ключ, по которому осуществляется поиск
        :param value: значение ключа
        :param column: необязательный параметр, обозначает столбец
        :param extra: дополнительные условия для запроса
        :return: список строк, представленных кортежами, или список None
        """

        if key is None and column is None:
            cursor.execute(f"SELECT * FROM {table}{extra}")
        elif key is None and column is not None:
            cursor.execute(f"SELECT {column} FROM {table}{extra}")
        elif column is None:
            cursor.execute(f"SELECT * FROM {table} WHERE {key} = '{value}'{extra}")
        else:
            cursor.execute(f"SELECT {column} FROM {table} WHERE {key} = '{value}'{extra}")
        result = cursor.fetchall()
        return result

    @connect
    def set(self, cursor, table: str, key: str, value: any, column: str, column_value: any):
        """
        Добавление значения в базу данных
        :param cursor: курсор БД
        :param table: таблица, в которую добавляется значение
        :param key: ключ, по которому добавляется значение
        :param value: значение ключа
        :param column: столбец, к которому добавляется значение
        :param column_value: значение столбца
        """

        cursor.execute(
            f"INSERT {table} ({key}, {column}) VALUES({value}, {column_value})")

    @connect
    def upd(self, cursor, table: str, key: any, value: any, column: str, column_value: any):
        """
        Обновление значения в базе данных
        :param cursor: курсор БД
        :param table: таблица, в которую добавляется значение
        :param key: ключ, по которому добавляется значение
        :param value: значение ключа
        :param column: столбец, к которому добавляется значение
        :param column_value: значение столбца
        """

        stmt = f"UPDATE {table} SET {column}=%s WHERE {key}=%s"
        cursor.execute(stmt, [column_value, value])

    @connect
    def delete(self, cursor, table: str, key: any, value: any, extra: str = ''):
        """
        Удаление строки таблицы

        :param cursor: курсор БД
        :param table: таблица, из которой удаляется строка
        :param key: ключ
        :param value: значение ключа
        :param extra: дополнительные условия для запроса
        """
        cursor.execute(f"DELETE FROM {table} WHERE {key} = '{value}'{extra}")

    @connect
    def add_row(self, cursor, table: str, columns: list, values: list):
        """
        Добавление целой строки данных

        :param cursor: курсор БД
        :param table: таблица, к которой добавляется строка
        :param columns: столбцы
        :param values: значения столбцов
        """

        stmt = f"INSERT {table} ({', '.join(columns)}) VALUES ({str('%s, ' * len(columns))[:-2]})"
        cursor.execute(stmt, tuple(values))

    # @connect
    # def intr(self, cursor, vk_id: int, func: str, column: str = None, value: int or str = None) -> List[tuple] or List[None]:
    #     """
    #     Получение данных/обновление таблицы с вступающими в группу пользователями
    #
    #     :param cursor: курсор БД
    #     vk_id: id пользователя ВКонтакте
    #     func: что необходимо сделать: get - получить данные, set - добавить, del - удалить
    #     column: столбец с которым нужно работать, при значении all возвращает всё
    #     value: значение, которое нужно вставить в таблицу"""
    #
    #     if func == 'get':
    #         if column == 'all':
    #             cursor.execute(f"SELECT * FROM intr WHERE vk_id = {vk_id}")
    #         else:
    #             cursor.execute(f"SELECT {column} FROM intr WHERE vk_id = {vk_id}")
    #         result = cursor.fetchall()
    #         return result
    #     if func == 'set':
    #         cursor.execute(
    #             f"INSERT intr (vk_id, {column}) VALUES({vk_id}, '{value}') ON DUPLICATE KEY UPDATE {column}=VALUES({column})")
    #     if func == 'del':
    #         cursor.execute(f"DELETE FROM intr WHERE vk_id = {vk_id}")
    #
    # @connect
    # def req_manager(self, connection, cursor, vk_id: int, func: str, column: str = None, value: int or str = None) -> List[tuple] or List[
    #     None]:
    #     """Получение данных/обновление таблицы с вступающими в группу пользователями
    #
    #     vk_id: id пользователя ВКонтакте
    #     func: что необходимо сделать: get - получить данные, set - добавить, del - удалить
    #     column: столбец с которым нужно работать, при значении all возвращает всё
    #     value: значение, которое нужно вставить в таблицу"""
    #
    #     if func == 'get':
    #         if column == 'all':
    #             cursor.execute(f"SELECT * FROM req_manager WHERE vk_id = {vk_id}")
    #         else:
    #             cursor.execute(f"SELECT {column} FROM req_manager WHERE vk_id = {vk_id}")
    #         result = cursor.fetchall()
    #         return result
    #     if func == 'set':
    #         cursor.execute(
    #             f"INSERT req_manager (vk_id, {column}) VALUES({vk_id}, '{value}') ON DUPLICATE KEY UPDATE {column}=VALUES({column})")
    #     if func == 'del':
    #         cursor.execute(f"DELETE FROM req_manager WHERE vk_id = {vk_id}")


#
#
# def add_member(user_id, vk_name, id, name, position):
#     connection = get_connection()
#     cursor = connection.cursor()
#     add = "INSERT INTO new_members (vk_id, vk_name, id, name, position) VALUES (%s, %s, %s, %s, %s)"
#     data = (user_id, vk_name, id, name, position)
#     cursor.execute(add, data)
#     connection.commit()
#     cursor.close()
#     connection.close()
#     return
#
#
# def add_action(user_id, action, time, section):
#     connection = get_connection()
#     cursor = connection.cursor()
#     if action is not None:
#         add = 'INSERT reminders (id, action) VALUES(%s, %s)'
#         data = (user_id, action)
#     else:
#         if time is not None:
#             add = 'UPDATE reminders SET time=%s WHERE id = %s AND time="0"'
#             data = (time, user_id)
#         else:
#             add = 'UPDATE reminders SET section=%s WHERE id = %s AND section="0"'
#             data = (section, user_id)
#     cursor.execute(add, data)
#     connection.commit()
#     cursor.close()
#     connection.close()
#     return
#
#
# def show_reminders(user_id):
#     connection = get_connection()
#     cursor = connection.cursor()
#     add = "SELECT action, time, section FROM reminders WHERE id = %s ORDER BY time"
#     data = (user_id,)
#     cursor.execute(add, data)
#     result = cursor.fetchall()
#     cursor.close()
#     connection.close()
#     return result
#
#
# def del_action(user_id, action, time):
#     connection = get_connection()
#     cursor = connection.cursor()
#     add = "DELETE FROM reminders WHERE id = %s AND action = %s AND time = %s"
#     data = (user_id, action, time)
#     cursor.execute(add, data)
#     connection.commit()
#     cursor.close()
#     connection.close()
#     return
#
#
# def del_all(user_id, time):
#     connection = get_connection()
#     cursor = connection.cursor()
#     if time:
#         add = "DELETE FROM reminders WHERE id = %s"
#     else:
#         add = "DELETE FROM reminders WHERE id = %s AND time = '0'"
#     data = (user_id,)
#     cursor.execute(add, data)
#     connection.commit()
#     cursor.close()
#     connection.close()
#     return
#
#
# def show_request(user_id):
#     connection = get_connection()
#     cursor = connection.cursor()
#     add = "SELECT * FROM intr WHERE vk_id = %s"
#     data = (user_id,)
#     cursor.execute(add, data)
#     result = cursor.fetchall()
#     cursor.close()
#     connection.close()
#     return result
#
#
# def del_requests(user_id):
#     connection = get_connection()
#     cursor = connection.cursor()
#     add = "DELETE FROM intr WHERE vk_id = %s"
#     data = (user_id,)
#     cursor.execute(add, data)
#     connection.commit()
#     cursor.close()
#     connection.close()
#     return
#
#
# def check_ids(action, time, section):
#     connection = get_connection()
#     cursor = connection.cursor()
#     add = "SELECT id FROM reminders WHERE action = %s and time = %s and section = %s"
#     data = (action, time, section)
#     cursor.execute(add, data)
#     result = cursor.fetchall()
#     cursor.close()
#     connection.close()
#     return result
#
#
# ################# ШАГИ #######################
#
# def check_step(user_id, table):
#     connection = get_connection()
#     cursor = connection.cursor()
#     add = f"SELECT step FROM {table} WHERE vk_id = %s"
#     data = (user_id,)
#     cursor.execute(add, data)
#     result = cursor.fetchall()
#     cursor.close()
#     connection.close()
#     if not result:
#         return 0
#     else:
#         return result[0][0]
#
#
# def add_step(user_id, step, table):
#     connection = get_connection()
#     cursor = connection.cursor()
#     add = f"INSERT {table} (vk_id, step) VALUES(%s, %s) ON DUPLICATE KEY UPDATE step=VALUES(step)"
#     data = (user_id, step)
#     cursor.execute(add, data)
#     connection.commit()
#     cursor.close()
#     connection.close()
#     return
#
#
# def del_step(user_id, table):
#     connection = get_connection()
#     cursor = connection.cursor()
#     add = f"DELETE FROM {table} WHERE vk_id = %s"
#     data = (user_id,)
#     cursor.execute(add, data)
#     connection.commit()
#     cursor.close()
#     connection.close()
#     return
#
#
# ###################### ВСТУПЛЕНИЕ ########################
#
# def add_inf(user_id, column, inf):
#     connection = get_connection()
#     cursor = connection.cursor()
#     add = f"INSERT INTO intr (vk_id, {column}) VALUES(%s, %s) ON DUPLICATE KEY UPDATE {column}=VALUES({column})"
#     data = (user_id, inf)
#     cursor.execute(add, data)
#     connection.commit()
#     cursor.close()
#     connection.close()
#     return
#
#
# def get_req(user_id):
#     connection = get_connection()
#     cursor = connection.cursor()
#     add = "SELECT id, name, last_name, position FROM intr WHERE vk_id = %s"
#     data = (user_id, )
#     cursor.execute(add, data)
#     result = cursor.fetchall()
#     cursor.close()
#     connection.close()
#     return result
#
#
# def add_ids(message_id, last_manager_id, user_id):
#     connection = get_connection()
#     cursor = connection.cursor()
#     add = "INSERT INTO req_manager (message_id, manager_id, vk_id) VALUES(%s, %s, %s)"
#     data = (message_id, last_manager_id, user_id)
#     cursor.execute(add, data)
#     connection.commit()
#     cursor.close()
#     connection.close()
#     return
#
#
# def delete_ids(user_id):
#     connection = get_connection()
#     cursor = connection.cursor()
#     add = "DELETE FROM req_manager WHERE vk_id = %s"
#     data = (user_id,)
#     cursor.execute(add, data)
#     connection.commit()
#     cursor.close()
#     connection.close()
#     return
#
#
# def select_managers(user_id):
#     connection = get_connection()
#     cursor = connection.cursor()
#     add = "SELECT message_id, manager_id FROM req_manager WHERE vk_id = %s"
#     data = (user_id,)
#     cursor.execute(add, data)
#     result = cursor.fetchall()
#     cursor.close()
#     connection.close()
#     return result
#
#
#
# ######################## УДАЛЕНИЕ НАПОМИНАНИЙ ######################
#
#
# def del_add_action(user_id, action):
#     connection = get_connection()
#     cursor = connection.cursor()
#     add = "INSERT del_reminders (vk_id, action) VALUES(%s, %s) ON DUPLICATE KEY UPDATE action=VALUES(action)"
#     data = (user_id, action)
#     cursor.execute(add, data)
#     connection.commit()
#     cursor.close()
#     connection.close()
#     return
#
#
# def del_get_action(user_id):
#     connection = get_connection()
#     cursor = connection.cursor()
#     add = "SELECT action FROM del_reminders WHERE vk_id = %s"
#     data = (user_id,)
#     cursor.execute(add, data)
#     result = cursor.fetchall()
#     cursor.close()
#     connection.close()
#     return result[0][0]
