__author__ = 'spec45as'
import os
from glob import glob
import json
import time

# import portalocker  убрано для совместимости

from Category import Category
from Item import Item
from UsersContainer import UsersContainer


class FileLoader():
    def __init__(self, mainApp):
        self.mainApp = mainApp
        # print("[File Loader] Init")

    def loadFile(self, fileName, attempt=0):
        try:
            if not os.path.isfile(fileName):
                raise FileNotFoundError
            file = open(fileName)
            fileContent = file.read()
            # portalocker.lock(file, portalocker.LOCK_EX) убрано для совместимости
            file.close()
            return fileContent
        except FileNotFoundError:
            print("[FileLoader] File not found error: " + fileName)
            return None
        except Exception as error:
            if attempt != 3:
                time.sleep(3)
                self.loadFile(fileName, attempt=attempt + 1)
            elif attempt == 3:
                print("[FileLoader] Unknown error: " + fileName)
                return None

    def loadCategories(self):
        allCategories = {}
        result = [y for x in os.walk('categories/') for y in glob(os.path.join(x[0], '*.txt'))]
        for k in result:
            newCategory = Category()
            if newCategory.load(json.loads(self.loadFile(k))):
                allCategories[newCategory.indexName] = newCategory
        return allCategories

    def loadItems(self):
        allItems = {}
        result = [y for x in os.walk('items/') for y in glob(os.path.join(x[0], '*.txt'))]
        for k in result:
            newItem = Item()
            if newItem.load(json.loads(self.loadFile(k))):
                allItems[newItem.indexName] = newItem
        return allItems

    def loadItem(self, indexName):
        item = None
        itemPath = 'items/{indexName}.txt'.format(indexName=indexName)

        if not os.path.isfile(itemPath):
            return None

        result = self.loadFile(itemPath)
        if result != "":
            item = Item()
            if item.load(json.loads(result)):
                return item
        return None


    def loadUsers(self, attempt=0):
        try:
            allUsers = UsersContainer()
            result = [y for x in os.walk('users/') for y in glob(os.path.join(x[0], '*.txt'))]
            for k in result:
                usersContainer = UsersContainer()
                if usersContainer.load(json.loads(self.loadFile(k))):
                    allUsers = usersContainer
                    break
            return allUsers
        except Exception as error:
            if attempt != 3:
                time.sleep(1)
                self.loadUsers(attempt=attempt + 1)
            elif attempt == 3:
                raise error