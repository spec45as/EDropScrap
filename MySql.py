import json

import pymysql.cursors

from UsersContainer import UsersContainer
from Category import Category
from Item import Item

class MySqlManager():
    def __init__(self, sqlConfig):
        print('[Mysql] Загрузка...')
        self.connection = pymysql.connect(host=sqlConfig['host'],
                                          user=sqlConfig['user'],
                                          password=sqlConfig['password'],
                                          db=sqlConfig['database'],
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

    def addCategory(self, categoryIndex, categoryJson):
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO `categories` (`categoryIndex`, `jsonContent`) VALUES (%s, %s)"
                cursor.execute(sql, (categoryIndex, categoryJson))

            self.connection.commit()
            return True
        except Exception as error:
            print(error)
            return False

    def getCategory(self, categoryIndex):
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT `categoryIndex`, `jsonContent` FROM `categories` WHERE `categoryIndex`=%s"
                cursor.execute(sql, (categoryIndex,))
                result = cursor.fetchone()

                if result is None:
                    return None

                jsonData = json.loads(result['jsonContent'])
                category = Category()
                category.load(jsonData)

                return category

        except Exception as error:
            print(error)
            return None

    def getAllCategories(self):
        allCategories = {}
        try:
            sql = "SELECT `categoryIndex`, `jsonContent` FROM `categories`"
            cursor = self.connection.cursor()
            cursor.execute(sql)
            # print cur.description
            # r = cur.fetchall()
            # print r
            # ...or...
            for result in cursor:
                jsonData = json.loads(result['jsonContent'])
                category = Category()
                category.load(jsonData)
                allCategories[result['categoryIndex']] = category

            cursor.close()

            return allCategories

        except Exception as error:
            print(error)
            return None

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