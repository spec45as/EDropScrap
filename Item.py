__author__ = 'spec45as'
import time
import json
import os.path

import requests


class Item():
    def __init__(self, itemName='unknown'):
        self.name = itemName
        self.indexName = ''
        self.price = 0.0
        self.owner = '0'
        self.weaponIconURL = ''
        self.caseIconURL = ''
        self.categoryName = ''
        self.quantity = 1

        # UNIX дата последнего обновления цен
        self.lastUpdate = time.time()

    def updatePrices(self):
        self.lastUpdate = time.time()

    def downloadIcon(self):
        imagePath = 'item_icons/{imageName}.png'.format(imageName=self.indexName)

        if not os.path.isfile(imagePath):
            imageSource = requests.get(self.weaponIconURL)

            imageFile = open(imagePath, 'wb')
            imageFile.write(imageSource.content)
            imageFile.close()

    def getIndexName(self):
        return self.owner + '_' + self.indexName

    def getJsonData(self):
        itemData = {}

        itemData['name'] = self.name
        itemData['indexName'] = self.indexName
        itemData['quantity'] = self.quantity
        itemData['categoryName'] = self.categoryName
        itemData['price'] = self.price
        itemData['owner'] = self.owner
        itemData['caseIconURL'] = self.caseIconURL
        # itemData['weaponIconURL'] = self.weaponIconURL
        #itemData['lastUpdate'] = self.lastUpdate
        jsonDump = json.dumps(itemData)
        return jsonDump


    def save(self):
        jsonDump = self.getJsonData()

        try:
            saveFile = open('items/{name}.txt'.format(name=self.getIndexName()), 'w')
            saveFile.write(jsonDump)
            saveFile.close()
            return True
        except:
            print('[Item Class] Error during saving {name}!'.format(name=self.getIndexName()))
            return False

    def load(self, jsonData):
        try:
            self.name = jsonData['name']
            self.indexName = jsonData['indexName']
            self.quantity = jsonData['quantity']
            self.categoryName = jsonData['categoryName']
            self.price = jsonData['price']
            self.caseIconURL = jsonData['caseIconURL']
            # self.weaponIconURL = jsonData['weaponIconURL']
            #self.lastUpdate = jsonData['lastUpdate']
            self.owner = jsonData['owner']

            return True
        except:
            print('[Item Class] Error during loading {name}!'.format(name=self.getIndexName()))
            return False