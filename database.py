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