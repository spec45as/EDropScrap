from FileLoader import FileLoader
from MySql import MySqlManager


def printStats():
    fileLoader = FileLoader()
    allCategories = fileLoader.loadCategories()

    mysqlManager = MySqlManager()
    allItems = mysqlManager.getAllItems()
    allUsers = mysqlManager.getAllUsers()

    allCategoriesInfo = {}

    overallCompanyProfit = 0
    overallQuantity = 0

    for category in allCategories:
        categoryPrice = allCategories[category].price
        overallPrice = 0
        averagePrice = 0
        quantity = 0
        companyProfit = 0
        chance = 0.0
        profitable = 0.0
        looses = 0
        wins = 0
        items = {}
        for item in allItems:
            if allItems[item].categoryName == category:
                if allItems[item].price >= categoryPrice:
                    wins += allItems[item].quantity
                else:
                    looses += allItems[item].quantity

                quantity = quantity + allItems[item].quantity

                items[allItems[item].owner + '_' + allItems[item].indexName] = allItems[item]
                overallPrice = overallPrice + allItems[item].price * allItems[item].quantity

        groupedItems = {}
        for curItem in items:
            currentIndex = items[curItem].indexName
            if groupedItems.get(currentIndex, None) is None:
                groupedItems[currentIndex] = items[curItem]
            else:
                groupedItems[currentIndex].quantity = groupedItems[currentIndex].quantity + items[curItem].quantity
                groupedItems[currentIndex].price = groupedItems[currentIndex].price + items[curItem].price

        for curItem in groupedItems:
            currentIndex = groupedItems[curItem].indexName
            groupedItems[currentIndex].price = float(
                "{0:.1f}".format(float(groupedItems[currentIndex].price / groupedItems[currentIndex].quantity)))

        if quantity != 0:
            averagePrice = float("{0:.2f}".format(float(overallPrice / quantity)))
            companyProfit = categoryPrice * quantity - overallPrice
            profitable = float("{0:.2f}".format(float(averagePrice / categoryPrice * 100.0)))
            chance = float("{0:.2f}".format(float(wins / quantity * 100.0)))
            overallCompanyProfit = companyProfit + overallCompanyProfit
            overallQuantity = quantity + overallQuantity

            values = {}
            values['name'] = allCategories[category].categoryName
            values['categoryPrice'] = categoryPrice
            values['quantity'] = quantity
            values['looses'] = looses
            values['wins'] = wins
            values['averagePrice'] = averagePrice
            values['overallPrice'] = overallPrice
            values['companyProfit'] = companyProfit
            values['profitable'] = profitable
            values['chance'] = chance
            values['items'] = groupedItems

            allCategoriesInfo[allCategories[category].indexName] = values

    sortedAllCategoriesInfo = sorted(allCategoriesInfo, key=lambda dict: allCategoriesInfo[dict]['profitable'],
                                     reverse=True)


    def printOverallData():
        print('\nИтоговая прибыль компании easydrop.ru составила ' + str(overallCompanyProfit) + ' руб')
        print('Всего в базе ' + str(len(allUsers.container)) + ' игроков')
        print('Общее количество посчитанных дропов ' + str(overallQuantity) + ' штук\n')


    print('\n===================Начало вывода статистики===================\n')

    printOverallData()

    for currentCategory in sortedAllCategoriesInfo:
        currentCategoryDict = allCategoriesInfo[currentCategory]
        print(currentCategoryDict['name'] + ' - Цена открытия: ' + str(currentCategoryDict['categoryPrice']) + ' руб.')
        print("Подробная информация о кейсе:")
        print('Этот кейс открыли как минимум ' + str(currentCategoryDict['quantity']) + ' раз')
        print('Из них выиграло ' + str(currentCategoryDict['wins']) + ' раз')
        print('Проиграло ' + str(currentCategoryDict['looses']) + ' раз')
        print('Выпавшие вещи в этом кейсе стоят в среднем ' + str(currentCategoryDict['averagePrice']) + ' руб.')
        print('В сумме вещей в этом кейсе выпало на ' + str(currentCategoryDict['overallPrice']) + ' руб.')
        print('В сумме easydrop заработал на этом кейсе ' + str(currentCategoryDict['companyProfit']) + ' руб.')
        print('Окупаемость в этом кейсе: ' + str(currentCategoryDict['profitable']) + '%')
        print('Шанс на выпадение окупаемой вещи в этом кейсе: ' + str(currentCategoryDict['chance']) + '%')

        print('\nПодробная статистика:\n')
        print('{name: <50}   {count}     {price}      {chance}'.format(name='Название', count='Кол-во', price='Цена',
                                                                       chance='Шанс'))
        print('================================================================================')
        for itemIndex in currentCategoryDict['items']:
            curItem = currentCategoryDict['items'][itemIndex]
            try:  # баги с кодировкой
                print('{name: <50} {count: >4} шт {price: >8} руб   {chance: >5}%'.format(name=curItem.name,
                                                                                          count=curItem.quantity,
                                                                                          price=curItem.price,
                                                                                          chance=float(
                                                                                              "{0:.2f}".format(float(
                                                                                                  curItem.quantity /
                                                                                                  currentCategoryDict[
                                                                                                      'quantity'] * 100.0)))))
            except:
                print('# Current Line Error #')
        print('================================================================================\n\n\n')

    printOverallData()
    print('\n===================Конец вывода статистики===================\n')


