import mysql.connector, yaml

with open('settings.yaml', encoding='utf8') as f:
    settings = yaml.safe_load(f)
    settings = settings['database']


def get_connection():
    connection = mysql.connector.connect(**settings, database='default', auth_plugin='mysql_native_password')
    return connection


def add_member(user_id, vk_name, id, name, position):
    connection = get_connection()
    cursor = connection.cursor()
    add = "INSERT INTO new_members (vk_id, vk_name, id, name, position) VALUES (%s, %s, %s, %s, %s)"
    data = (user_id, vk_name, id, name, position)
    cursor.execute(add, data)
    connection.commit()
    cursor.close()
    connection.close()
    return


def add_action(user_id, action, time):
    connection = get_connection()
    cursor = connection.cursor()
    add = "INSERT INTO reminders (Id, Action, Time) VALUES ( %s, %s, %s)"
    data = (user_id, action, time)
    cursor.execute(add, data)
    connection.commit()
    cursor.close()
    connection.close()
    return


def show_reminders(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    add = "SELECT Action, Time FROM reminders WHERE Id = %s ORDER BY Action"
    data = (user_id,)
    cursor.execute(add, data)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


def del_action(user_id, action, time):
    connection = get_connection()
    cursor = connection.cursor()
    add = "DELETE FROM reminders WHERE Id = %s AND Action = %s AND Time = %s"
    data = (user_id, action, time)
    cursor.execute(add, data)
    connection.commit()
    cursor.close()
    connection.close()
    return

def del_all(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    add = "DELETE FROM reminders WHERE Id = %s"
    data = (user_id,)
    cursor.execute(add, data)
    connection.commit()
    cursor.close()
    connection.close()
    return
