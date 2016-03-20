__author__ = 'spec45as'
from MySql import MySqlManager

mysqlManager = MySqlManager()
from Item import Item
import json

print(mysqlManager.getAllUsers().container)
print(mysqlManager.addUser(666))
print(mysqlManager.getAllUsers().container)
print(mysqlManager.getUser(666))

for i in range(1,10):
    print(i)