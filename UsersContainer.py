__author__ = 'spec45as'
import json


class UsersContainer():
    def __init__(self):
        self.container = {}

    def saveUser(self, userID):
        self.container[userID] = True
        self.save()

    def isUserChecked(self, userID):
        return self.container.get(str(userID), False)

    def save(self):
        data = {}
        data['container'] = self.container
        jsonDump = json.dumps(data)

        try:
            saveFile = open('users/{indexName}.txt'.format(indexName='users'), 'w')
            saveFile.write(jsonDump)
            saveFile.close()
            return True
        except:
            print('[UsersContainer Class] Error during saving {indexName}!'.format(indexName='users'))
            return False

    def load(self, jsonData):
        try:
            self.container = jsonData['container']
            return True
        except:
            print('[UsersContainer Class] Error during loading {indexName}!'.format(indexName='users'))
            return False
