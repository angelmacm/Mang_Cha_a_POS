import datetime, random, sqlite3

class LocalConnection:
    def __init__(self, dbFile):
        """ create a database connection to a SQLite database """
        self.connectSql = None
        try:
            self.connectSql = sqlite3.connect(dbFile)
            self.localCursor = self.connectSql.cursor()
        except Exception as e:
            print(e)
        self.existsResults = []
        
        self.connectSql.commit()

    def checkLocaltables(self):
        for tableNames in self.tableNamesList:
            sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tableNames}'"
            self.localCursor.execute(sql)
            isExists = self.localCursor.fetchall()
            self.existsResults.append(bool(isExists))

    def registerUser(self, user, password, sha256, idNumber = 0, syncOnly= False):
        if not syncOnly:
            sql = 'INSERT INTO users (user, pass, sha256) VALUES (?,?,?)'
            val = (user, password, sha256)
        else:
            sql = 'INSERT INTO users (id, user, pass, sha256) VALUES (?,?,?,?)'
            val = (idNumber, user, password, sha256)
        self.localCursor.execute(sql, val)

    def addFlavor(self, category, floatNumber, price, isAvailable, productCode,idNumber = 0, syncOnly= False, isDefault = 0):
        if not syncOnly:
            sql = "INSERT INTO flavors (category, float, price, isAvailable, productCode, isDefault) VALUES (?, ?, ?, ?, ?, ?)"
            val = (category, floatNumber, price, isAvailable, productCode)
        else:
            sql = "INSERT INTO flavors (id, category, float, price, isAvailable, productCode, isDefault) VALUES (?, ?, ?, ?, ?, ?, ?)"
            val = (idNumber, category, floatNumber, price, isAvailable, productCode, isDefault)
        self.localCursor.execute(sql,val)

    def logTransactions(self, itemsBought, amount, money, change, tax, dateCol = '', idNumber = 0, syncOnly = False):
        if not syncOnly:
            filteredItemsBought = []
            for n in itemsBought:
                filteredItemsBought.append(n[0])
            sql = 'INSERT INTO transactionlogs (itemsBought, amount, moneyCol, changeAmount, tax) VALUES (?, ?, ?, ?, ?)'
            val = (str(filteredItemsBought), amount, money, change, tax)
        else:
            sql = 'INSERT INTO transactionlogs (id, itemsBought, amount, moneyCol, changeAmount, tax, dateCol) VALUES (?, ?, ?, ?, ?, ?, ?)'
            val = (idNumber, itemsBought, amount, money, change, tax, dateCol)
        self.localCursor.execute(sql,val)

    def logMessage(self, message, idNumber = 0, dateCol = '', syncOnly=False):
        if not syncOnly:
            sql = 'INSERT INTO systemlogs (message) VALUES (?)'
            val = (message,)
        else:
            sql = 'INSERT INTO systemlogs (id, message, dateCol) VALUES (?,?,?)'
            val = (idNumber, message,  dateCol)
        self.localCursor.execute(sql,val)

    def todayData(self, tableName):
        startTime = "00:00:00"
        endTime = "23:59:59"
        todayDate = datetime.date.today()
        sql = "SELECT * FROM "+ tableName +" WHERE `dateCol` BETWEEN ? and ?"
        startDate = f"{todayDate} {startTime}"
        endDate = f"{todayDate} {endTime}"
        val = (startDate, endDate)
        self.localCursor.execute(sql, val)
        todayData = self.localCursor.fetchall()

        return todayData

    def selectAllFrom(self, tableName):
        sql = "SELECT * FROM "+ tableName
        self.localCursor.execute(sql)
        todayData = self.localCursor.fetchall()
        return todayData

    def rangeData(self, rangeStart, rangeEnd, tableName):
        startTime = "00:00:00"
        endTime = "23:59:59"
        todayDate = datetime.date.today()
        sql = "SELECT * FROM "+ tableName +" WHERE `dateCol` BETWEEN ? and ?"
        startDate = f"{rangeStart} {startTime}"
        endDate = f"{rangeEnd} {endTime}"
        val = (startDate, endDate)
        self.localCursor.execute(sql, val)
        todayData = self.localCursor.fetchall()
        return todayData

    def addInventory(self, flavor, price, stock, productCode, category = 'misc'):
        sql = 'INSERT INTO flavors (category,flavor,price,stock,productCode) VALUES (?,?,?,?,?)'
        val = (category, flavor, price, stock,productCode)
        self.localCursor.execute(sql,val)

    def findCode(self, productCode):
        sql = "SELECT * FROM `flavors` WHERE `productCode` = ?"
        val = (productCode,)
        self.localCursor.execute(sql,val)
        productDetails = self.localCursor.fetchall()
        idNumber, category, flavorName, price, stock, productCode, isDefault = productDetails[0]
        return idNumber, category, flavorName, price, stock, productCode, isDefault

    def checkLogin(self, sha256Data):
        sql = "SELECT * FROM `users` WHERE `sha256` = ?"
        val = (sha256Data,)
        self.localCursor.execute(sql,val)
        productDetails = self.localCursor.fetchall()
        return bool(productDetails)

    def checkAvailability(self, productCode):
        sql = "SELECT * FROM `flavors` WHERE `productCode` = ?"
        val = (productCode,)
        self.localCursor.execute(sql,val)
        productDetails = self.localCursor.fetchall()
        return bool(productDetails[0][4])

    def updateAvailability(self, productCode, isAvailable):
        sql = "UPDATE `flavors` SET `isAvailable` = ? WHERE `flavors`.`productCode` = ?"
        val = (int(bool(isAvailable)), productCode)
        self.localCursor.execute(sql,val)
        self.connectSql.commit()

    def updatePrice(self, productCode, price):
        sql = "UPDATE `flavors` SET `price` = ? WHERE `flavors`.`productCode` = ?"
        val = (float(price), productCode)
        self.localCursor.execute(sql,val)
        self.connectSql.commit()

    def exportDatabase(self):
        pass



localDBLink = LocalConnection("pos_system.db")

