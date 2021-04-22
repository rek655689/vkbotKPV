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
    if action is not None:
        add = 'INSERT reminders (Id, Action) VALUES(%s, %s)'
        data = (user_id, action)
    else:
        add = 'UPDATE reminders SET Time=%s WHERE Id = %s AND Time=""'
        data = (time, user_id)
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


def show_requests():
    connection = get_connection()
    cursor = connection.cursor()
    add = "SELECT * FROM intr ORDER BY name"
    cursor.execute(add)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


def del_requests(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    if user_id:
        add = "DELETE FROM intr WHERE vk_id = %s"
        data = (user_id,)
        cursor.execute(add, data)
    else:
        add = "DELETE FROM intr"
        cursor.execute(add)
    connection.commit()
    cursor.close()
    connection.close()
    return


def check_ids(action, time):
    connection = get_connection()
    cursor = connection.cursor()
    add = "SELECT Id FROM reminders WHERE Action = %s and Time = %s"
    data = (action, time)
    cursor.execute(add, data)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


################# ШАГИ #######################

def check_step(user_id, table):
    connection = get_connection()
    cursor = connection.cursor()
    add = f"SELECT step FROM {table} WHERE vk_id = %s"
    data = (user_id,)
    cursor.execute(add, data)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    if not result:
        return 0
    else:
        return result[0][0]


def add_step(user_id, step, table):
    connection = get_connection()
    cursor = connection.cursor()
    add = f"INSERT {table} (vk_id, step) VALUES(%s, %s) ON DUPLICATE KEY UPDATE step=VALUES(step)"
    data = (user_id, step)
    cursor.execute(add, data)
    connection.commit()
    cursor.close()
    connection.close()
    return


def del_step(user_id, table):
    connection = get_connection()
    cursor = connection.cursor()
    add = f"DELETE FROM {table} WHERE vk_id = %s"
    data = (user_id,)
    cursor.execute(add, data)
    connection.commit()
    cursor.close()
    connection.close()
    return


###################### ВСТУПЛЕНИЕ ########################

def add_inf(user_id, column, inf):
    connection = get_connection()
    cursor = connection.cursor()
    add = f"INSERT INTO intr (vk_id, {column}) VALUES(%s, %s) ON DUPLICATE KEY UPDATE {column}=VALUES({column})"
    data = (user_id, inf)
    cursor.execute(add, data)
    connection.commit()
    cursor.close()
    connection.close()
    return


def get_req(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    add = "SELECT id, name, last_name, position FROM intr WHERE vk_id = %s"
    data = (user_id, )
    cursor.execute(add, data)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


######################## УДАЛЕНИЕ НАПОМИНАНИЙ ######################


def del_add_action(user_id, action):
    connection = get_connection()
    cursor = connection.cursor()
    add = "INSERT del_reminders (vk_id, action) VALUES(%s, %s) ON DUPLICATE KEY UPDATE action=VALUES(action)"
    data = (user_id, action)
    cursor.execute(add, data)
    connection.commit()
    cursor.close()
    connection.close()
    return


def del_get_action(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    add = "SELECT action FROM del_reminders WHERE vk_id = %s"
    data = (user_id,)
    cursor.execute(add, data)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result[0][0]