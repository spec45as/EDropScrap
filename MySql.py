import hashlib
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
                nameMD5 = hashlib.md5()
                nameMD5.update(json.dumps(item.name).encode())
                sql = "INSERT INTO `items_light` (`nameMD5`, `owner`, `category`, `price`, `quantity`)" \
                      " VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE `quantity` = %s, `price` = %s;"
                cursor.execute(sql, (
                    nameMD5.hexdigest(), item.owner, item.category, item.price, item.quantity,
                    item.quantity,
                    item.price))
            self.connection.commit()
            return True
        except Exception as error:
            print(error)
            return False

    def getItemName(self, nameMD5):
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT `itemName` FROM `item_names_light` WHERE `nameMD5`=%s"
                cursor.execute(sql, (nameMD5,))
                result = cursor.fetchone()

                if result is None:
                    return None
                return json.loads(result['itemName'])

        except Exception as error:
            print(error)
            return None

    def getAllItemNames(self):
        allNames = {}
        try:
            sql = "SELECT `nameMD5`, `itemName` FROM `item_names_light`"
            cursor = self.connection.cursor()
            cursor.execute(sql)
            for result in cursor:
                allNames[result['nameMD5']] = json.loads(result['itemName'])
            cursor.close()

            return allNames

        except Exception as error:
            print(error)
            return None

    def addItemName(self, itemName):
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO `item_names_light` (`nameMD5`, `itemName`) VALUES (%s, %s) ON DUPLICATE KEY UPDATE `itemName` = %s"
                jsonItemName = json.dumps(itemName)
                nameMD5 = hashlib.md5()
                nameMD5.update(jsonItemName.encode())
                cursor.execute(sql, (nameMD5.hexdigest(), jsonItemName, jsonItemName))
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
        allNames = self.getAllItemNames()
        try:
            sql = "SELECT `nameMD5`, `owner`, `category`, `price`, `quantity` FROM `items_light`"
            cursor = self.connection.cursor()
            cursor.execute(sql)
            for result in cursor:
                item = Item()
                item.name = allNames.get(result['nameMD5'], None)
                item.owner = result['owner']
                item.category = result['category']
                item.price = result['price']
                item.quantity = result['quantity']
                item.nameMD5 = result['nameMD5']
                allItems[str(result['owner']) + '_' + result['nameMD5']] = item

            cursor.close()

            return allItems

        except Exception as error:
            print(error)
            return None


    def getItem(self, nameMD5, owner, category):
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT `nameMD5`, `owner`, `category`, `price`, `quantity` FROM `items_light` WHERE `nameMD5`=%s AND `owner`=%s AND `category`=%s"
                cursor.execute(sql, (nameMD5, owner, category,))
                result = cursor.fetchone()
                if result is None:
                    return None

                item = Item()
                item.name = self.getItemName(result['nameMD5'])
                item.owner = result['owner']
                item.category = result['category']
                item.price = result['price']
                item.quantity = result['quantity']
                return item

        except Exception as error:
            print(error)
            return None

    def close(self):
        self.connection.close()