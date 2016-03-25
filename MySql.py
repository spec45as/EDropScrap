import json

import pymysql.cursors

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
                sql = "INSERT INTO `categories_light` (`categoryIndex`, `jsonContent`) VALUES (%s, %s)"
                cursor.execute(sql, (categoryIndex, categoryJson))

            self.connection.commit()
            return True
        except Exception as error:
            print(error)
            return False

    def getCategory(self, categoryIndex):
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT `categoryIndex`, `jsonContent` FROM `categories_light` WHERE `categoryIndex`=%s"
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
            sql = "SELECT `categoryIndex`, `jsonContent` FROM `categories_light`"
            cursor = self.connection.cursor()
            cursor.execute(sql)
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

    def addItem(self, item):
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO `items_light` (`itemIndex`, `itemName`, `owner`, `category`, `price`, `quantity`)" \
                      " VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE `quantity` = %s, `price` = %s;"
                cursor.execute(sql, (
                    item.itemIndex, json.dumps(item.name), item.owner, item.category, item.price, item.quantity,
                    item.quantity,
                    item.price))
            self.connection.commit()
            return True
        except Exception as error:
            print(error)
            return False

    def addUser(self, userID):
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO `users_light` (`userID`) VALUES (%s)"
                cursor.execute(sql, (userID))
            self.connection.commit()
            return True
        except Exception as error:
            print(error)
            return False

    def getUser(self, userID):
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT `userID` FROM `users_light` WHERE `userID`=%s"
                cursor.execute(sql, (userID,))
                result = cursor.fetchone()

                if result is None:
                    return False
                return True

        except Exception as error:
            print(error)
            return None

    def getAllUsers(self):
        allUsersContainer = {}
        try:
            sql = "SELECT `userID` FROM `users_light`"
            cursor = self.connection.cursor()
            cursor.execute(sql)
            for result in cursor:
                allUsersContainer[result['userID']] = True
            cursor.close()

            return allUsersContainer

        except Exception as error:
            print(error)
            return None

    def getAllItems(self):
        allItems = {}
        try:
            sql = "SELECT `itemIndex`, `itemName`, `owner`, `category`, `price`, `quantity` FROM `items_light`"
            cursor = self.connection.cursor()
            cursor.execute(sql)
            for result in cursor:
                item = Item()
                item.name = json.loads(result['itemName'])
                item.owner = result['owner']
                item.category = result['category']
                item.price = result['price']
                item.itemIndex = result['itemIndex']
                item.quantity = result['quantity']

                allItems[result['itemIndex']] = item

            cursor.close()

            return allItems

        except Exception as error:
            print(error)
            return None


    def getItem(self, itemIndex):
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT `itemIndex`, `itemName`, `owner`, `category`, `price`, `quantity` FROM `items_light` WHERE `itemIndex`=%s"
                cursor.execute(sql, (itemIndex,))
                result = cursor.fetchone()

                if result is None:
                    return None

                item = Item()
                item.name = json.loads(result['itemName'])
                item.owner = result['owner']
                item.category = result['category']
                item.price = result['price']
                item.quantity = result['quantity']
                item.itemIndex = result['itemIndex']
                return item

        except Exception as error:
            print(error)
            return None

    def close(self):
        self.connection.close()