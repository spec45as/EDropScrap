import re

import unidecode


__author__ = 'spec45as'


def createIndexStringFromHashName(string):
    return re.sub(r'\W+', '-', unidecode.unidecode(string).lower())


def generateIndexName(name, owner, category):
    return (str(owner) + '_' + createIndexStringFromHashName(name) + '_' + str(len(name)) + '_' + category)


class Item():
    def __init__(self, name='unknown'):
        self.name = name
        self.itemIndex = ''
        self.price = 0.0
        self.owner = 0
        self.category = ''
        self.quantity = 1

    def setIndexName(self):
        self.itemIndex = generateIndexName(self.name, self.owner, self.category)
        return self.itemIndex