import re
import random

import unidecode

from StatCounter import printStats

from FileLoader import FileLoader
from Selenium import SeleniumLoader, NoItemsException, PageCouldntBeLoadedException
from Category import Category
from Item import Item
from MySql import MySqlManager


def createIndexStringFromHashName(string):
    return re.sub(r'\W+', '-', unidecode.unidecode(string).lower())


class DataCollector():
    def __init__(self, range=5000):
        self.range = range
        self.mysqlManager = MySqlManager()
        self.fileLoader = FileLoader()
        self.baseURL = 'http://www.easydrop.ru'
        self.seleniumLoader = SeleniumLoader()
        self.allCategories = self.fileLoader.loadCategories()

    def getAllCategories(self):
        try:
            webPage = self.seleniumLoader.loadCategories()
            if webPage is None:
                raise PageCouldntBeLoadedException()
            webPage.make_links_absolute(self.baseURL)
            allSiteCategories = webPage.find_class('item')
            if allSiteCategories is None:
                raise PageCouldntBeLoadedException()
        except PageCouldntBeLoadedException as error:
            print('Can\'t load main Page with categories')

        for currentCategory in allSiteCategories:
            try:
                indexName = currentCategory.get('href').split('/')
                indexName = indexName[len(indexName) - 1]
                price = int(currentCategory.findtext('span'))
                categoryObject = self.allCategories.get(indexName, None)
                if categoryObject is None:
                    try:
                        newCategory = Category(currentCategory.findtext('strong'))
                        newCategory.marketIconURL = currentCategory.find_class('picture')[0].getchildren()[0].get('src')
                        newCategory.marketURL = currentCategory.get('href')
                        newCategory.price = price
                        newCategory.indexName = indexName
                        newCategory.save()
                        # newCategory.downloadIcon()

                        self.allCategories[indexName] = newCategory
                    except:
                        print('Error during creating of new Category')
                else:
                    if categoryObject.price != price:
                        categoryObject.price = price
                        categoryObject.save()
            except:
                print('Error during category register')
                continue


    def getUserCount(self):
        try:
            htmlData = self.seleniumLoader.loadCountURL()
            if htmlData is None:
                raise PageCouldntBeLoadedException()
        except PageCouldntBeLoadedException as error:
            print('Can\'t load main URL')
            self.seleniumLoader.quit()
        else:
            return int(htmlData.find_class('stat')[0][1][0].text_content())


    def findCategory(self, imageURL):
        for category in self.allCategories:
            if (self.allCategories[category].marketIconURL == imageURL):
                return self.allCategories[category].indexName
        return 'unknown'


    def getUncheckedUser(self, rangeStart, rangeEnd):
        attempts = 3

        for attempt in range(1, attempts + 1):
            randomStartPos = rangeStart + int((rangeEnd - rangeStart) * random.random())
            if attempt != attempts:
                startPos = randomStartPos
            else:
                startPos = rangeStart

            for i in range(startPos, rangeEnd):
                allUsers = self.mysqlManager.getAllUsers()
                if allUsers.container.get(i, None) is None:
                    return i

        return None


    def getAllWins(self, startPos=0):
        allUsersCount = self.getUserCount()
        if allUsersCount is None:
            return -1

        searchRange = self.range
        randomStartPos = allUsersCount - searchRange + int(searchRange * random.random())

        if startPos == 0:
            startPos = randomStartPos

        for i in range(startPos, allUsersCount):
            allUsers = self.fileLoader.loadUsers()
            if self.mysqlManager.getUser(i) or (i == (allUsersCount - 1)):
                uncheckedUser = self.getUncheckedUser(allUsersCount - searchRange, allUsersCount)
                if not uncheckedUser is None:
                    self.getAllWins(uncheckedUser)
                    return 0
                else:
                    return 0
            try:
                print('Progress: ' + str(i) + '/' + str(allUsersCount))
                webPage = self.seleniumLoader.loadUserInventoryURL(
                    'https://easydrop.ru/user/{user_id}'.format(user_id=i))
                if webPage is None:
                    raise PageCouldntBeLoadedException()
                webPage.make_links_absolute(self.baseURL)
                allDrops = webPage.find_class('items-incase')[0].find_class('item-incase')
                if allDrops is None:
                    raise PageCouldntBeLoadedException()
            except PageCouldntBeLoadedException as error:
                print('Can\'t load user page URL')
                continue
            except NoItemsException as error:
                print('No Items!')
                self.mysqlManager.addUser(i)
                continue

            for currentDrop in allDrops:
                try:
                    statusDiv = currentDrop.find_class('status')[0]
                    descDiv = currentDrop.find_class('descr')[0]
                    dropImage = currentDrop.find_class('drop-image')[0]
                    caseImage = currentDrop.find_class('case-image')[0]

                    name = descDiv.findtext('strong') + " | " + descDiv.findtext('span')
                    indexName = createIndexStringFromHashName(str(name))
                    price = int(statusDiv.findall('span')[1].text)
                    weaponIconURL = dropImage.get('src')
                    caseIconURL = caseImage.get('src')
                    categoryName = self.findCategory(caseIconURL)
                    owner = str(i)

                    itemObject = self.mysqlManager.getItem(owner + '_' + indexName + '_' + categoryName)

                    # itemObject = fileLoader.loadItem(owner + '_' + indexName + '_' + categoryName)
                    # old file shit

                    if itemObject is None:
                        try:
                            newItem = Item(name)
                            newItem.price = price
                            newItem.weaponIconURL = weaponIconURL
                            newItem.caseIconURL = caseIconURL
                            newItem.categoryName = categoryName
                            newItem.indexName = indexName + "_" + categoryName
                            newItem.owner = owner
                            # newItem.save()
                            # old file shit
                            self.mysqlManager.addItem(newItem.getIndexName(), newItem.getJsonData())
                            # newItem.downloadIcon()

                        except:
                            print('Error during creating of new Item')
                    else:
                        itemObject.quantity = int(itemObject.quantity) + 1
                        if itemObject.price != price:
                            if int(itemObject.price) > int(price):
                                itemObject.price = price
                        self.mysqlManager.updateItem(newItem.getIndexName(), newItem.getJsonData())
                        # itemObject.save()
                        # old file shit
                except:
                    print('Item parsing error')

            self.mysqlManager.addUser(i)

    def cleanup(self):
        self.mysqlManager.close()
        self.seleniumLoader.quit()


def start():
    while True:
        print(
            'Внимание! Перед началом необходимо получить доступ к базе данных!\n\n1 - Начать сбор данных')  # \n2 - Вывести статистику')
        command = input("Введите число для дальнейших действий: ")
        if command == '2':
            print('Вывод статистики:')
            printStats()
        elif command == '1':
            print('Сбор статистики')
            startDataCollection()
        else:
            print('Неверная команда, попробуйте ещё раз')


def startDataCollection():
    attempt = 1
    while True:
        print('Запуск сборщика данных, попытка: ' + str(attempt))
        try:
            dataLoader = DataCollector(50000)
            dataLoader.getAllCategories()
            dataLoader.getAllWins()
        except Exception as error:
            print(error)
        finally:
            try:
                dataLoader.cleanup()
            except Exception as error:
                print(error)


if __name__ == "__main__":
    start()
