import pymysql.cursors
import json

#Just for tests, don't care guys
user = '046440198_easydr'
password = '046440198_easydr'
host = 'mysql.id222383009-0.myjino.ru'
database = 'id222383009-0_easydr'

# Connect to the database
connection = pymysql.connect(host=host,
                             user=user,
                             password=password,
                             db=database,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        # Create a new record
        dic = {'office': {'component_office': ['Word2010SP0', 'PowerPoint2010SP0']}}
        sql = "INSERT INTO `test` (`ip_address`, `soft_data`) VALUES (%s, %s)"
        cursor.execute(sql, ('python.org', json.dumps(dic)))

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()

    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT `ip_address`, `soft_data` FROM `test` WHERE `ip_address`=%s"
        cursor.execute(sql, ('python.org',))
        result = cursor.fetchone()
        print(result)
finally:
    connection.close()