import pymysql.cursors

# Just for tests, don't care guys
user = '046440198_easydr'
password = '046440198_easydr'
host = 'mysql.id222383009-0.myjino.ru'
database = 'id222383009-0_easydr'


class MySqlManager():
    def __init__(self):
        # Connect to the database
        self.connection = pymysql.connect(host=host,
                                          user=user,
                                          password=password,
                                          db=database,
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

    def addItem(self, itemIndex, itemJson):

        try:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `items` (`itemIndex`, `jsonContent`) VALUES (%s, %s)"
                cursor.execute(sql, (itemIndex, itemJson))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()
            return True
        except Exception as error:
            print(error)
            return False

    def getItem(self, itemIndex):
        try:
            with self.connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT `itemIndex`, `jsonContent` FROM `items` WHERE `itemIndex`=%s"
                cursor.execute(sql, (itemIndex,))
                result = cursor.fetchone()
                return result
        except Exception as error:
            print(error)
            return None

    def close(self):
        self.connection.close()