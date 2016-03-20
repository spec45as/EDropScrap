__author__ = 'spec45as'
import json
import time
import os.path

import requests


class Category():
    def __init__(self, categoryName='unknown'):
        self.categoryName = categoryName
        self.indexName = ''
        self.price = 0.0
        self.marketURL = ''
        self.marketIconURL = ''

        # UNIX дата последнего обновления цен
        self.lastUpdate = time.time()

    def updatePrices(self):
        self.lastUpdate = time.time()

    def downloadIcon(self):
        imagePath = 'category_icons/{imageName}.png'.format(imageName=self.categoryName)

        if not os.path.isfile(imagePath):
            imageSource = requests.get(self.marketIconURL)

            imageFile = open(imagePath, 'wb')
            imageFile.write(imageSource.content)
            imageFile.close()

    def save(self):
        itemData = {}
        itemData['categoryName'] = self.categoryName
        itemData['indexName'] = self.indexName
        itemData['price'] = self.price
        itemData['marketURL'] = self.marketURL
        itemData['marketIconURL'] = self.marketIconURL
        itemData['lastUpdate'] = self.lastUpdate
        jsonDump = json.dumps(itemData)

        try:
            saveFile = open('categories/{indexName}.txt'.format(indexName=self.indexName), 'w')
            saveFile.write(jsonDump)
            saveFile.close()
            return True
        except:
            print('[Category Class] Error during saving {indexName}!'.format(indexName=self.indexName))
            return False

    def load(self, jsonData):
        try:
            self.categoryName = jsonData['categoryName']
            self.indexName = jsonData['indexName']
            self.price = jsonData['price']
            self.marketURL = jsonData['marketURL']
            self.marketIconURL = jsonData['marketIconURL']
            self.lastUpdate = jsonData['lastUpdate']
            return True
        except:
            print('[Category Class] Error during loading {indexName}!'.format(indexName=self.indexName))
            return False