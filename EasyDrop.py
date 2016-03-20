import re
import random

import unidecode

from FileLoader import FileLoader
from Selenium import SeleniumLoader, NoItemsException, PageCouldntBeLoadedException
from Category import Category
from Item import Item
from MySql import MySqlManager


mysqlManager = MySqlManager()

baseURL = 'http://www.easydrop.ru'

fileLoader = FileLoader(None)
allCategories = fileLoader.loadCategories()
seleniumLoader = SeleniumLoader()


def createIndexStringFromHashName(string):
    return re.sub(r'\W+', '-', unidecode.unidecode(string).lower())


def getAllCategories():
    try:
        webPage = seleniumLoader.loadCategories()
        if webPage is None:
            raise PageCouldntBeLoadedException()
        webPage.make_links_absolute(baseURL)
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
            categoryObject = allCategories.get(indexName, None)
            if categoryObject is None:
                try:
                    newCategory = Category(currentCategory.findtext('strong'))
                    newCategory.marketIconURL = currentCategory.find_class('picture')[0].getchildren()[0].get('src')
                    newCategory.marketURL = currentCategory.get('href')
                    newCategory.price = price
                    newCategory.indexName = indexName
                    newCategory.save()
                    newCategory.downloadIcon()

                    allCategories[indexName] = newCategory
                except:
                    print('Error during creating of new Category')
            else:
                if categoryObject.price != price:
                    categoryObject.price = price
                    categoryObject.save()
        except:
            print('Error during category register')
            continue


def getUserCount():
    try:
        htmlData = seleniumLoader.loadCountURL()
        if htmlData is None:
            raise PageCouldntBeLoadedException()
    except PageCouldntBeLoadedException as error:
        print('Can\'t load main URL')
        seleniumLoader.quit()
    else:
        return int(htmlData.find_class('stat')[0][1][0].text_content())


def findCategory(imageURL):
    for category in allCategories:
        if (allCategories[category].marketIconURL == imageURL):
            return allCategories[category].indexName
    return 'unknown'


def getUncheckedUser(rangeStart, rangeEnd):
    attempts = 3

    for attempt in range(1, attempts + 1):
        randomStartPos = rangeStart + int((rangeEnd - rangeStart) * random.random())
        if attempt != attempts:
            startPos = randomStartPos
        else:
            startPos = rangeStart

        for i in range(startPos, rangeEnd):
            allUsers = mysqlManager.getAllUsers()
            if allUsers.container.get(i, None) is None:
                return i

    return None


def getAllWins(startPos=0):
    allUsersCount = getUserCount()
    if allUsersCount is None:
        return -1

    searchRange = 3000
    randomStartPos = allUsersCount - searchRange + int(searchRange * random.random())

    if startPos == 0:
        startPos = randomStartPos

    for i in range(startPos, allUsersCount):
        allUsers = fileLoader.loadUsers()
        if mysqlManager.getUser(i) or (i == (allUsersCount - 1)):
            uncheckedUser = getUncheckedUser(allUsersCount - searchRange, allUsersCount)
            if not uncheckedUser is None:
                getAllWins(uncheckedUser)
                return 0
            else:
                return 0
        try:
            print('Progress: ' + str(i) + '/' + str(allUsersCount))
            webPage = seleniumLoader.loadUserInventoryURL('https://easydrop.ru/user/{user_id}'.format(user_id=i))
            if webPage is None:
                raise PageCouldntBeLoadedException()
            webPage.make_links_absolute(baseURL)
            allDrops = webPage.find_class('items-incase')[0].find_class('item-incase')
            if allDrops is None:
                raise PageCouldntBeLoadedException()
        except PageCouldntBeLoadedException as error:
            print('Can\'t load user page URL')
            continue
        except NoItemsException as error:
            print('No Items!')
            mysqlManager.addUser(i)
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
                categoryName = findCategory(caseIconURL)
                owner = str(i)

                itemObject = mysqlManager.getItem(owner + '_' + indexName + '_' + categoryName)

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
                        mysqlManager.addItem(newItem.getIndexName(), newItem.getJsonData())
                        # newItem.downloadIcon()

                    except:
                        print('Error during creating of new Item')
                else:
                    itemObject.quantity = int(itemObject.quantity) + 1
                    if itemObject.price != price:
                        if int(itemObject.price) > int(price):
                            itemObject.price = price
                    mysqlManager.updateItem(newItem.getIndexName(), newItem.getJsonData())
                    # itemObject.save()
                    # old file shit
            except:
                print('Item parsing error')

        mysqlManager.addUser(i)


    seleniumLoader.quit()


getAllCategories()
getAllWins()