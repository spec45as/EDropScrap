import hashlib
import json
import re
import random
from time import time

import unidecode

from Selenium import SeleniumLoader, NoItemsException, PageCouldntBeLoadedException
from Category import Category
from Item import Item
from MySql import MySqlManager
from StatCounter import printStats


def createIndexStringFromHashName(string):
    return re.sub(r'\W+', '-', unidecode.unidecode(string).lower())


class DataCollector():
    def __init__(self, isDota, range=5000):
        self.isDota = isDota
        sqlConfig = {}
        if self.isDota:
            # Just for tests, don't care guys
            sqlConfig['user'] = '046440198_dota'
            sqlConfig['password'] = '046440198_dota'
            sqlConfig['host'] = 'mysql.id222383009-0.myjino.ru'
            sqlConfig['database'] = 'id222383009-0_dota'
        else:
            # Just for tests, don't care guys
            sqlConfig['user'] = '046440198_easydr'
            sqlConfig['password'] = '046440198_easydr'
            sqlConfig['host'] = 'mysql.id222383009-0.myjino.ru'
            sqlConfig['database'] = 'id222383009-0_easydr'

        self.range = range
        self.mysqlManager = MySqlManager(sqlConfig)
        if self.isDota:
            self.baseURL = 'http://dota2.easydrop.ru'
        else:
            self.baseURL = 'http://easydrop.ru'
        self.seleniumLoader = SeleniumLoader(self.baseURL, self.isDota)
        self.allCategories = {}


    def getAllCategories(self, updateCategories=False):
        if updateCategories:
            print('Составление новых категорий дропов...')
        else:
            print('Загрузка категорий дропов...')

        if not updateCategories:
            self.allCategories = self.mysqlManager.getAllCategories()
            if (self.allCategories is None) or (self.allCategories == {}):
                raise Exception('Couldn\'t load item categories')
            else:
                print('Загрузка категорий дропов завершена')
                return True
        allSiteCategories = {}
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
            return False

        for currentCategory in allSiteCategories:
            try:
                indexName = currentCategory.get('href').split('/')
                indexName = createIndexStringFromHashName(indexName[len(indexName) - 1])
                price = int(currentCategory.findtext('span'))
                categoryObject = self.mysqlManager.getCategory(indexName)

                if categoryObject is None:
                    try:
                        newCategory = Category(currentCategory.findtext('strong'))
                        newCategory.marketIconURL = currentCategory.find_class('picture')[0].getchildren()[0].get('src')
                        newCategory.marketURL = currentCategory.get('href')
                        newCategory.price = price
                        newCategory.indexName = indexName
                        self.mysqlManager.addCategory(newCategory.indexName, newCategory.getJsonData())
                    except:
                        print('Error during creating of new Category')

            except:
                print('Error during category register')
                continue

        return self.getAllCategories(False)


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
                if allUsers.get(i, None) is None:
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

        for i in range(startPos, allUsersCount + 1):
            if self.mysqlManager.getUser(i):
                uncheckedUser = self.getUncheckedUser(allUsersCount - searchRange, allUsersCount)
                if not uncheckedUser is None:
                    self.getAllWins(uncheckedUser)
                    return 0
                else:
                    return 0
            t0 = time()
            try:
                print('\nProgress: ' + str(i) + '/' + str(allUsersCount), end="")

                webPage = self.seleniumLoader.loadUserInventoryURL(
                    self.baseURL + '/user/{user_id}'.format(user_id=i))
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
                print(' [No Items]', end="")
                self.mysqlManager.addUser(i)
                continue
            finally:
                t1 = time()
                print(' Загрузка страницы: {time}'.format(time=float("{0:.2f}".format(t1 - t0))) + ';', end="")

            try:
                self.mysqlManager.addUser(i)
            except:
                print("Ошибка добавления нового игрока")
                return 0

            t0 = time()
            for currentDrop in allDrops:
                try:
                    statusDiv = currentDrop.find_class('status')[0]
                    descDiv = currentDrop.find_class('descr')[0]
                    caseImage = currentDrop.find_class('case-image')[0]
                    if self.isDota:
                        name = descDiv.findtext('strong')
                    else:
                        name = descDiv.findtext('strong') + " | " + descDiv.findtext('span')
                    price = int(statusDiv.findall('span')[1].text)
                    caseIconURL = caseImage.get('src')
                    category = self.findCategory(caseIconURL)
                    owner = i

                    nameMD5 = hashlib.md5()
                    nameMD5.update(json.dumps(name).encode())
                    itemObject = self.mysqlManager.getItem(nameMD5.hexdigest(), i, category)
                    itemNameMD5 = self.mysqlManager.getItemName(nameMD5.hexdigest())
                    if itemNameMD5 is None:
                        self.mysqlManager.addItemName(name)

                    if itemObject is None:
                        try:
                            newItem = Item()
                            newItem.name = name
                            newItem.price = price
                            newItem.category = category
                            newItem.owner = owner
                            self.mysqlManager.addItem(newItem)
                        except:
                            print('Error during creating of new Item')
                    else:
                        itemObject.quantity = int(itemObject.quantity) + 1
                        if itemObject.price != price:
                            if int(itemObject.price) > int(price):
                                itemObject.price = price
                        self.mysqlManager.addItem(itemObject)
                except:
                    print('Item parsing error')
                    return 0
            t1 = time()
            print(' Обработка данных: {time}'.format(time=float("{0:.2f}".format(t1 - t0))), end="")


    def cleanup(self):
        self.mysqlManager.close()
        self.seleniumLoader.quit()


def start():
    while True:
        print('1 - Dota 2\n2 - CS:GO')
        isDota = True
        gameCommand = input("Введите число для дальнейших действий: ")
        if gameCommand == '1':
            isDota = True
        elif gameCommand == '2':
            isDota = False
        else:
            print('Неверная команда, попробуйте ещё раз')
            continue

        print(
            'Внимание! Перед началом необходимо получить доступ к базе данных!\n\n1 - Начать сбор данных\n2 - Вывести статистику\n3 - Обновить категории')
        command = input("Введите число для дальнейших действий: ")
        if command == '2':
            print('<<Вывод статистики>>')
            printStats(isDota)
        elif command == '1':
            print('<<Сбор статистики>>')
            startDataCollection(False, isDota)
        elif command == '3':
            print('<<Обновление категорий>>')
            startDataCollection(True, isDota)
        else:
            print('Неверная команда, попробуйте ещё раз')


def startDataCollection(categoryOnly=False, isDota=False):
    attempt = 0
    while True:
        attempt += 1
        print('Запуск сборщика данных, попытка: ' + str(attempt))
        try:
            dataLoader = DataCollector(isDota, 50000)

            if categoryOnly:
                result = dataLoader.getAllCategories(True)
                if result:
                    return
                else:
                    continue

            dataLoader.getAllCategories(False)
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
