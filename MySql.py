import json

import pymysql.cursors

from UsersContainer import UsersContainer
from Item import Item


# Just for tests, don't care guys
user = '046440198_easydr'
password = '046440198_easydr'
host = 'mysql.id222383009-0.myjino.ru'
database = 'id222383009-0_easydr'


class MySqlManager():
    def __init__(self):
        print('[Mysql] Загрузка...')
        self.connection = pymysql.connect(host=host,
                                          user=user,
                                          password=password,
                                          db=database,
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)


    def addItem(self, itemIndex, itemJson):
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO `items` (`itemIndex`, `jsonContent`) VALUES (%s, %s)"
                cursor.execute(sql, (itemIndex, itemJson))

            self.connection.commit()
            return True
        except Exception as error:
            print(error)
            return False

    def updateItem(self, itemIndex, itemJson):
        try:
            with self.connection.cursor() as cursor:
                sql = "UPDATE `items` SET jsonContent=%s WHERE itemIndex=%s"
                cursor.execute(sql, (itemJson, itemIndex))
            self.connection.commit()
            return True
        except Exception as error:
            print(error)
            return False

    def addUser(self, userID):
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO `users` (`userID`) VALUES (%s)"
                cursor.execute(sql, (userID))

            self.connection.commit()
            return True
        except Exception as error:
            print(error)
            return False

    def getUser(self, userID):
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT `userID` FROM `users` WHERE `userID`=%s"
                cursor.execute(sql, (userID,))
                result = cursor.fetchone()

                if result is None:
                    return False

                return True

        except Exception as error:
            print(error)
            return None

    def getAllUsers(self):
        allUsersContainer = UsersContainer()
        allUsers = {}
        try:
            sql = "SELECT `userID` FROM `users`"
            cursor = self.connection.cursor()
            cursor.execute(sql)
            # print cur.description
            # r = cur.fetchall()
            # print r
            # ...or...
            for result in cursor:
                allUsers[result['userID']] = True
            cursor.close()

            allUsersContainer.container = allUsers
            return allUsersContainer

        except Exception as error:
            print(error)
            return None

    def getAllItems(self):
        allItems = {}
        try:
            sql = "SELECT `itemIndex`, `jsonContent` FROM `items`"
            cursor = self.connection.cursor()
            cursor.execute(sql)
            # print cur.description
            # r = cur.fetchall()
            # print r
            # ...or...
            for result in cursor:
                jsonData = json.loads(result['jsonContent'])
                item = Item()
                item.load(jsonData)
                allItems[result['itemIndex']] = item

            cursor.close()

            return allItems

        except Exception as error:
            print(error)
            return None


    def getItem(self, itemIndex):
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT `itemIndex`, `jsonContent` FROM `items` WHERE `itemIndex`=%s"
                cursor.execute(sql, (itemIndex,))
                result = cursor.fetchone()

                if result is None:
                    return None

                jsonData = json.loads(result['jsonContent'])
                item = Item()
                item.load(jsonData)

                return item

        except Exception as error:
            print(error)
            return None

    def close(self):
        self.connection.close()