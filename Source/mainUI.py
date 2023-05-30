import sys, time

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
#from PyQt5.QtChart import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import posdb as db
import computation as calc
#resource files
import teaIcons_rc, homeIcons_rc, sideIcons_rc, foodIcons_rc

class MainWindow(QMainWindow):
	def __init__(self):
		self.selectorDict = {"milkTeaSelector": "MilkTeaWindow",
						"frappeSelector": "FrappeWindow",
						"minterrificSelector" : "Minterrific",
						"chocolateSelector" : "Chocolate",
						"icedTeaSelector" : "IcedTea",
						"hotMilkTeaSelector" : "HotMilkTea",
						"matchaMuchoSelector" : "MatchaMucho",
						"yakultSelector" : "YakultWindow",
						"coffeeSelector" : "Coffee",
						"taroSelector" : "TaroWindow",
						"rocksaltSelector" : "RocksaltCheese",
						"sodaSelector" : "SodaSplashedWindow",
						}

		self.dbSelectorDict = {"milktea": "MilkTeaWindow",
						"frappe": "FrappeWindow",
						"minterrific" : "Minterrific",
						"chocolate" : "Chocolate",
						"icedTea" : "IcedTea",
						"hotMilkTea" : "HotMilkTea",
						"matchaMucho" : "MatchaMucho",
						"yakultMilkTea" : "YakultWindow",
						"coffee" : "Coffee",
						"taro" : "TaroWindow",
						"rocksaltCheese" : "RocksaltCheese",
						"sodaSplash" : "SodaSplashedWindow",
						"addOns":"AddOns",
						"foods":"FoodsGroup"
						}
		self.currentOrderText = ''
		self.currentOrderTally = []
		self.tempOrderTally = []
		self.currentBestFive = []
		self.inventoryChangesToBeMade = {"price": None ,"isAvailable":None, "category": None, 'productCode': None}

		super(MainWindow, self).__init__()
		uic.loadUi('mainCashier.ui',self)

		self.updateBestFive()
		self.mainStack.setCurrentIndex(0)
		self.milkTeaSelector.clicked.connect(lambda: self.showWindow("milkTeaSelector"))
		self.frappeSelector.clicked.connect(lambda: self.showWindow("frappeSelector"))
		self.minterrificSelector.clicked.connect(lambda: self.showWindow("minterrificSelector"))
		self.chocolateSelector.clicked.connect(lambda: self.showWindow("chocolateSelector"))
		self.icedTeaSelector.clicked.connect(lambda: self.showWindow("icedTeaSelector"))
		self.hotMilkTeaSelector.clicked.connect(lambda: self.showWindow("hotMilkTeaSelector"))
		self.matchaMuchoSelector.clicked.connect(lambda: self.showWindow("matchaMuchoSelector"))
		self.yakultSelector.clicked.connect(lambda: self.showWindow("yakultSelector"))
		self.coffeeSelector.clicked.connect(lambda: self.showWindow("coffeeSelector"))
		self.taroSelector.clicked.connect(lambda: self.showWindow("taroSelector"))
		self.rocksaltSelector.clicked.connect(lambda: self.showWindow("rocksaltSelector"))
		self.sodaSelector.clicked.connect(lambda: self.showWindow("sodaSelector"))
		self.button_checkout.clicked.connect(self.checkOut)
		self.input_cash.editingFinished.connect(self.cashInputValidate)
		self.top_checkout.clicked.connect(self.checkOut)
		self.deleteButton.clicked.connect(self.deleteDisplay)
		self.newOrder.clicked.connect(self.deleteDisplay)
		self.drinks_selector.clicked.connect(self.showDrinks)
		self.foods_selector.clicked.connect(self.showFoods)
		self.ramen_selector.clicked.connect(lambda: instanceFoodsGroup.viewFood('ramenGroup'))
		self.siomai_selector.clicked.connect(lambda: instanceFoodsGroup.viewFood('siomaiGroup'))
		self.bonito_selector.clicked.connect(lambda: instanceFoodsGroup.viewFood('bonitoGroup'))
		self.ramen_selector.clicked.connect(lambda: instanceFoodsGroup.viewFood('ramenGroup'))
		self.burger_selector.clicked.connect(lambda: instanceFoodsGroup.viewFood('burgerGroup'))
		self.fries_selector.clicked.connect(lambda: instanceFoodsGroup.viewFood('friesGroup'))
		self.shawarma_selector.clicked.connect(lambda: instanceFoodsGroup.viewFood('shawarmaGroup'))
		self.korDog_selector.clicked.connect(lambda: instanceFoodsGroup.viewFood('korDogGroup'))
		self.takoyaken_selector.clicked.connect(lambda: instanceFoodsGroup.viewFood('takoyakenGroup'))
		self.combo_selector.clicked.connect(lambda: instanceFoodsGroup.viewFood('comboGroup'))
		self.salesAnalysis_selector.clicked.connect(lambda: self.changeHomeView(2))
		self.inventory_selector.clicked.connect(lambda: self.changeHomeView(1))
		self.orderDisplayWidget.setColumnCount(2)
		self.orderDisplayWidget.setHorizontalHeaderLabels(['',''])
		self.inventoryTableWidget.setColumnCount(5)
		self.inventoryTableWidget.setHorizontalHeaderLabels(['category','Flavor name','Price','isAvailable','productCode'])
		self.dailyProfit_analysis.clicked.connect(self.dailyProfit)
		self.bestMonthly_analysis.clicked.connect(self.bestMonthlyFunc)
		self.bestAllTime_analysis.clicked.connect(self.bestAllTimeFunc)
		self.goHome_analysis.clicked.connect(lambda: self.changeHomeView(0))
		self.best1.clicked.connect(lambda: self.pickBest(0))
		self.best2.clicked.connect(lambda: self.pickBest(1))
		self.best3.clicked.connect(lambda: self.pickBest(2))
		self.best4.clicked.connect(lambda: self.pickBest(3))
		self.best5.clicked.connect(lambda: self.pickBest(4))
		self.goHomeButton.clicked.connect(lambda:self.changeHomeView(0))
		self.editButton.clicked.connect(self.inventoryEditButtonFunc)

		
		self.createInventoryTable()

		#chart creations
		self.figureDaily = plt.figure()
		self.canvasDaily = FigureCanvas(self.figureDaily)
		self.dailyProfitsLayout.addWidget(self.canvasDaily)

		self.figureMonthly = plt.figure()
		self.canvasMonthly = FigureCanvas(self.figureMonthly)
		self.monthlyLayout.addWidget(self.canvasMonthly)

		self.figureAllTime = plt.figure()
		self.canvasAllTime = FigureCanvas(self.figureAllTime)
		self.allTimeLayout.addWidget(self.canvasAllTime)

	def inventoryEditButtonFunc(self):
		selectedRow = self.inventoryTableWidget.currentRow()
		categorySelected = self.inventoryTableWidget.item(selectedRow,0).text()
		nameSelected = self.inventoryTableWidget.item(selectedRow,1).text()
		priceSelected = self.inventoryTableWidget.item(selectedRow,2).text()
		availabilitySelected = self.inventoryTableWidget.item(selectedRow,3).text()
		self.codeSelected = self.inventoryTableWidget.item(selectedRow,4).text()
		self.inventoryChangesToBeMade['category'] = categorySelected
		self.inventoryChangesToBeMade['productCode'] = self.codeSelected
		instanceInventoryEdit.priceInput.setText(priceSelected)
		instanceInventoryEdit.show()

	def editInventoryFunc(self):
		dbLink.updateAvailability(self.codeSelected, self.inventoryChangesToBeMade['isAvailable'])
		dbLink.updatePrice(self.codeSelected, self.inventoryChangesToBeMade['price'])
		eval(f"instance{self.dbSelectorDict[self.inventoryChangesToBeMade['category']]}.checkAvailability()")
		self.inventoryChangesToBeMade['price'] = None
		self.inventoryChangesToBeMade['isAvailable'] = None
		self.inventoryChangesToBeMade['productCode'] = None
		self.inventoryChangesToBeMade['category'] = None
		#self.inventoryTableWidget.clearContents()
		self.inventoryTableWidget.setRowCount(0)
		self.createInventoryTable()
		self.inventoryTableWidget.update()

	def createInventoryTable(self):
		horizontalHeader = self.inventoryTableWidget.horizontalHeader()
		horizontalHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
		horizontalHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
		horizontalHeader.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
		horizontalHeader.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
		horizontalHeader.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
		dbResult = dbLink.selectAllFrom('flavors')
		
		for n in dbResult:
			idNumber, category, flavorName, price, stock, productCode, isDefault = n
			rowPosition = self.inventoryTableWidget.rowCount()
			self.inventoryTableWidget.insertRow(rowPosition)
			self.inventoryTableWidget.setItem(rowPosition,0,QTableWidgetItem(str(category)))
			self.inventoryTableWidget.setItem(rowPosition,1,QTableWidgetItem(str(flavorName)))
			self.inventoryTableWidget.setItem(rowPosition,2,QTableWidgetItem(str(price)))
			self.inventoryTableWidget.setItem(rowPosition,3,QTableWidgetItem(str(bool(stock))))
			self.inventoryTableWidget.setItem(rowPosition,4,QTableWidgetItem(productCode))

	def updateBestFive(self):
		self.currentBestFive = calc.getBestFive()
		self.best1.setText(dbLink.findCode(self.currentBestFive[0])[2])
		self.best2.setText(dbLink.findCode(self.currentBestFive[1])[2])
		self.best3.setText(dbLink.findCode(self.currentBestFive[2])[2])
		self.best4.setText(dbLink.findCode(self.currentBestFive[3])[2])
		self.best5.setText(dbLink.findCode(self.currentBestFive[4])[2])

	def pickBest(self, numberOfBest):
		currentlyPicked = self.currentBestFive[numberOfBest]
		self.addTemp(currentlyPicked)
		addOns.show()

	def bestAllTimeFunc(self):
		self.analysisStack.setCurrentIndex(2)
		self.figureAllTime.clear()

		allTimeArray = calc.getBestAllTime()
		listOfTimes = []
		listOfFlavors = []
		for n in allTimeArray:
			listOfTimes.append(n['number'])
			listOfFlavors.append(n['flavorName'])
		fullFlavorNames = []
		for n in listOfFlavors:
			fullFlavorNames.append(dbLink.findCode(n)[2])

				# refresh canvas
		ax = self.figureAllTime.add_axes([0,0,1,1])
		ax.axis('equal')
		theme = plt.get_cmap('copper')
		ax.set_prop_cycle("color", [theme(1. * i / len(listOfTimes))
						for i in range(len(listOfTimes))])
		ax.pie(listOfTimes, labels = fullFlavorNames,autopct=make_autopct(listOfTimes), startangle=180)
		self.canvasAllTime.draw()

	def bestMonthlyFunc(self):
		self.analysisStack.setCurrentIndex(1)
		self.figureMonthly.clear()

		monthlyArray = calc.getBestMonth()
		listOfTimes = []
		listOfFlavors = []
		for n in monthlyArray:
			listOfTimes.append(n['number'])
			listOfFlavors.append(n['flavorName'])
		fullFlavorNames = []
		for n in listOfFlavors:
			fullFlavorNames.append(dbLink.findCode(n)[2])

		ax = self.figureMonthly.add_axes([0,0,1,1])

				# refresh canvas
		ax.axis('equal')
		theme = plt.get_cmap('Greens')
		ax.set_prop_cycle("color", [theme(1. * i / len(listOfTimes))
						for i in range(len(listOfTimes))])
		ax.pie(listOfTimes, labels = fullFlavorNames,autopct=make_autopct(listOfTimes),startangle=180)
		self.canvasMonthly.draw()

	def dailyProfit(self):

		self.analysisStack.setCurrentIndex(0)

		# clearing old figure
		self.figureDaily.clear()
		# create an axis
		ax = self.figureDaily.add_axes([0.05,0.05,.90,.90])
		listofDates, listOfProfits = calc.getDailyProfit()
		ax.bar(listofDates, listOfProfits, color = ['#81A969'])

		# refresh canvas
		self.canvasDaily.draw()


	def changeHomeView(self, index):
		if index == 2:
			self.dailyProfit()		
		self.mainStack.setCurrentIndex(index)

	def cashInputValidate(self):
		validationRule = QDoubleValidator(self.totalAmount, 999999, 2)
		isAcceptable = validationRule.validate(self.input_cash.text(),1)[0] == QValidator.Acceptable
		if isAcceptable:
			self.cashAmount = float(self.input_cash.text())
		else:
			self.input_cash.setText('')

	def showDrinks(self):
		self.mainView.setCurrentIndex(0)

	def showFoods(self):
		self.mainView.setCurrentIndex(1)

	def showWindow(self, window):
		eval(f"instance{self.selectorDict[window]}.show()")

	def addOrder(self, orderCode):
		if orderCode:
			if isinstance(orderCode,list):
				flavorName, price = findProduct(orderCode[0])
				price *= orderCode[1]
				pcs = str(orderCode[1])
				orderCode = orderCode[0]
				flavorName = f"{pcs} {flavorName}"

			elif orderCode[0:3] == "add":
				flavorName, price = findProduct(orderCode)
				flavorName = f'    {flavorName}'

			else:
				flavorName, price = findProduct(orderCode)
			rowPosition = self.orderDisplayWidget.rowCount()
			self.orderDisplayWidget.insertRow(rowPosition)
			self.orderDisplayWidget.setItem(rowPosition,0,QTableWidgetItem(flavorName))
			self.orderDisplayWidget.setItem(rowPosition,1,QTableWidgetItem(str(price)))

		self.currentOrderTally.append([orderCode, flavorName, price])
		self.tempOrderTally = []
		self.updateDisplay()

	def updateDisplay(self):
		self.totalAmount = calc.computeTally(self.currentOrderTally)
		self.beforeTax, self.taxVat = calc.tax(self.totalAmount) 
		self.output_tax.setText(str(round(self.taxVat,4)))
		self.output_subtotal.setText(str(round(self.beforeTax,4)))
		self.output_total.setText(str(self.totalAmount))

	def checkOut(self):
		try:
			self.changeAmount = self.cashAmount - self.totalAmount
			self.output_change.setText(str(self.changeAmount))
			dbLink.logTransactions(self.currentOrderTally, self.totalAmount, self.cashAmount, self.changeAmount, self.taxVat)
			self.resetDisplay()
			self.updateBestFive()

		except AttributeError:
			messageBox("Please input the amount received from the customer")

	def deleteDisplay(self):
		self.output_change.setText('')
		self.input_cash.setText('')
		self.resetDisplay()

	def resetDisplay(self):
		self.changeAmount = 0
		self.cashAmount = 0
		self.currentOrderText = ''
		self.currentOrderTally = []
		self.output_tax.setText('')
		self.output_subtotal.setText('')
		self.output_total.setText('')
		self.orderDisplayWidget.clearContents()
		self.orderDisplayWidget.setRowCount(0)

	def addTemp(self, order):
		self.tempOrderTally.append(order)

	def verifyOrder(self):
		for n in self.tempOrderTally:
			self.addOrder(n)

class FrappeWindow(QWidget):
	def __init__(self):
		super(FrappeWindow, self).__init__()
		uic.loadUi('frappeSelected.ui',self)

		self.flavorList = ["frappe_matcha","frappe_mango","frappe_strawberry",
		"frappe_mixedBerries","frappe_chocoOreo","frappe_strawberryApollo",
		"frappe_cookiesCream","frappe_strawberryOreo","frappe_chocoMango",
		"frappe_coffeeJelly","frappe_mochaCoffee","frappe_almondCoffee",
		"frappe_tiramisuCoffee","frappe_hazelnutCoffee","frappe_caramelMacchiato",
		"frappe_specialBlend"]

		#Initializing the buttons
		self.frappe_matcha.clicked.connect(lambda: self.addOrder("frappe_matcha"))
		self.frappe_mango.clicked.connect(lambda: self.addOrder("frappe_mango"))
		self.frappe_strawberry.clicked.connect(lambda: self.addOrder("frappe_strawberry"))
		self.frappe_mixedBerries.clicked.connect(lambda: self.addOrder("frappe_mixedBerries"))
		self.frappe_chocoOreo.clicked.connect(lambda: self.addOrder("frappe_chocoOreo"))
		self.frappe_strawberryApollo.clicked.connect(lambda: self.addOrder("frappe_strawberryApollo"))
		self.frappe_cookiesCream.clicked.connect(lambda: self.addOrder("frappe_cookiesCream"))
		self.frappe_strawberryOreo.clicked.connect(lambda: self.addOrder("frappe_strawberryOreo"))
		self.frappe_chocoMango.clicked.connect(lambda: self.addOrder("frappe_chocoMango"))
		self.frappe_coffeeJelly.clicked.connect(lambda: self.addOrder("frappe_coffeeJelly"))
		self.frappe_mochaCoffee.clicked.connect(lambda: self.addOrder("frappe_mochaCoffee"))
		self.frappe_almondCoffee.clicked.connect(lambda: self.addOrder("frappe_almondCoffee"))
		self.frappe_tiramisuCoffee.clicked.connect(lambda: self.addOrder("frappe_tiramisuCoffee"))
		self.frappe_hazelnutCoffee.clicked.connect(lambda: self.addOrder("frappe_hazelnutCoffee"))
		self.frappe_caramelMacchiato.clicked.connect(lambda: self.addOrder("frappe_caramelMacchiato"))
		self.frappe_specialBlend.clicked.connect(lambda: self.addOrder("frappe_specialBlend"))
		
	def addOrder(self, order):
		mainWindowObj.addTemp(order)
		addOns.show()
		self.hide()

	def checkAvailability(self):
		for n in self.flavorList:
			availabilityBool = dbLink.checkAvailability(n)
			eval(f'self.{n}.setEnabled({availabilityBool})')

class MilkTeaWindow(QWidget):
	def __init__(self):
		super(MilkTeaWindow, self).__init__()
		uic.loadUi('milkTeaSelected.ui',self)

		self.flavorList = ["milktea_pearl","milktea_coffeeJelly","milktea_grassJelly",
		"milktea_banana","milktea_okinawa","milktea_strawberry","milktea_wintermelonPearl",
		"milktea_lychee","milktea_watermelonPearl","milktea_strawberryApollo","milktea_strawberryBanana",
		"milktea_tiramisu","milktea_almondCoffee","milktea_almondRedBeans","milktea_strawberryOreo",
		"milktea_wintermelonGrassJelly","milktea_cookiesCream"]

		#Initializing the buttons
		self.milktea_pearl.clicked.connect(lambda: self.addOrder("milktea_pearl"))
		self.milktea_coffeeJelly.clicked.connect(lambda: self.addOrder("milktea_coffeeJelly"))
		self.milktea_grassJelly.clicked.connect(lambda: self.addOrder("milktea_grassJelly"))
		self.milktea_banana.clicked.connect(lambda: self.addOrder("milktea_banana"))
		self.milktea_okinawa.clicked.connect(lambda: self.addOrder("milktea_okinawa"))
		self.milktea_strawberry.clicked.connect(lambda: self.addOrder("milktea_strawberry"))
		self.milktea_wintermelonPearl.clicked.connect(lambda: self.addOrder("milktea_wintermelonPearl"))
		self.milktea_lychee.clicked.connect(lambda: self.addOrder("milktea_lychee"))
		self.milktea_watermelonPearl.clicked.connect(lambda: self.addOrder("milktea_watermelonPearl"))
		self.milktea_strawberryApollo.clicked.connect(lambda: self.addOrder("milktea_strawberryApollo"))
		self.milktea_strawberryBanana.clicked.connect(lambda: self.addOrder("milktea_strawberryBanana"))
		self.milktea_tiramisu.clicked.connect(lambda: self.addOrder("milktea_tiramisu"))
		self.milktea_almondCoffee.clicked.connect(lambda: self.addOrder("milktea_almondCoffee"))
		self.milktea_almondRedBeans.clicked.connect(lambda: self.addOrder("milktea_almondRedBeans"))
		self.milktea_strawberryOreo.clicked.connect(lambda: self.addOrder("milktea_strawberryOreo"))
		self.milktea_wintermelonGrassJelly.clicked.connect(lambda: self.addOrder("milktea_wintermelonGrassJelly"))
		self.milktea_cookiesCream.clicked.connect(lambda: self.addOrder("milktea_cookiesCream"))
		

	def addOrder(self, order):
		mainWindowObj.addTemp(order)
		addOns.show()
		self.hide()

	def checkAvailability(self):
		for n in self.flavorList:
			availabilityBool = dbLink.checkAvailability(n)
			eval(f'self.{n}.setEnabled({availabilityBool})')

class SodaSplashedWindow(QWidget):
	def __init__(self):
		super(SodaSplashedWindow, self).__init__()
		uic.loadUi('sodaSplashSelected.ui',self)

		self.flavorList = ["soda_mangoGreen","soda_mangoLychee","soda_honeyLemon",
		"soda_strawberryPassion","soda_strawberryApple"]

		#Initializing the buttons
		self.soda_mangoGreen.clicked.connect(lambda: self.addOrder("soda_mangoGreen"))
		self.soda_mangoLychee.clicked.connect(lambda: self.addOrder("soda_mangoLychee"))
		self.soda_honeyLemon.clicked.connect(lambda: self.addOrder("soda_honeyLemon"))
		self.soda_strawberryPassion.clicked.connect(lambda: self.addOrder("soda_strawberryPassion"))
		self.soda_strawberryApple.clicked.connect(lambda: self.addOrder("soda_strawberryApple"))
		

	def addOrder(self, order):
		mainWindowObj.addTemp(order)
		addOns.show()
		self.hide()

	def checkAvailability(self):
		for n in self.flavorList:
			availabilityBool = dbLink.checkAvailability(n)
			eval(f'self.{n}.setEnabled({availabilityBool})')

class TaroWindow(QWidget):
	def __init__(self):
		super(TaroWindow, self).__init__()
		uic.loadUi('taroSelected.ui',self)

		self.flavorList = ["taro_pearl","taro_pudding","taro_redBeans"]

		#Initializing the buttons
		self.taro_pearl.clicked.connect(lambda: self.addOrder("taro_pearl"))
		self.taro_pudding.clicked.connect(lambda: self.addOrder("taro_pudding"))
		self.taro_redBeans.clicked.connect(lambda: self.addOrder("taro_redBeans"))
		

	def addOrder(self, order):
		mainWindowObj.addTemp(order)
		addOns.show()
		self.hide()

	def checkAvailability(self):
		for n in self.flavorList:
			availabilityBool = dbLink.checkAvailability(n)
			eval(f'self.{n}.setEnabled({availabilityBool})')

class YakultWindow(QWidget):
	def __init__(self):
		super(YakultWindow, self).__init__()
		uic.loadUi('yakultMilkTea.ui',self)

		self.flavorList = ["yakult_grape","yakult_passionFruit","yakult_blueberry",
		"yakult_lychee","yakult_strawberry","yakult_mango","yakult_greenApple"]

		#Initializing the buttons
		self.yakult_grape.clicked.connect(lambda: self.addOrder("yakult_grape"))
		self.yakult_passionFruit.clicked.connect(lambda: self.addOrder("yakult_passionFruit"))
		self.yakult_blueberry.clicked.connect(lambda: self.addOrder("yakult_blueberry"))
		self.yakult_lychee.clicked.connect(lambda: self.addOrder("yakult_lychee"))
		self.yakult_strawberry.clicked.connect(lambda: self.addOrder("yakult_strawberry"))
		self.yakult_mango.clicked.connect(lambda: self.addOrder("yakult_mango"))
		self.yakult_greenApple.clicked.connect(lambda: self.addOrder("yakult_greenApple"))


	def addOrder(self, order):
		mainWindowObj.addTemp(order)
		addOns.show()
		self.hide()

	def checkAvailability(self):
		for n in self.flavorList:
			availabilityBool = dbLink.checkAvailability(n)
			eval(f'self.{n}.setEnabled({availabilityBool})')

class Chocolate(QWidget):
	def __init__(self):
		super(Chocolate, self).__init__()
		uic.loadUi('chocolateSelected.ui',self)

		self.flavorList = ["choco_Pearl","choco_banana","choco_mango","choco_oreo",
		"choco_almond","choco_caramel"]

		#Initializing the buttons
		self.choco_Pearl.clicked.connect(lambda: self.addOrder("choco_Pearl"))
		self.choco_banana.clicked.connect(lambda: self.addOrder("choco_banana"))
		self.choco_mango.clicked.connect(lambda: self.addOrder("choco_mango"))
		self.choco_oreo.clicked.connect(lambda: self.addOrder("choco_oreo"))
		self.choco_almond.clicked.connect(lambda: self.addOrder("choco_almond"))
		self.choco_caramel.clicked.connect(lambda: self.addOrder("choco_caramel"))


	def addOrder(self, order):
		mainWindowObj.addTemp(order)
		addOns.show()
		self.hide()

	def checkAvailability(self):
		for n in self.flavorList:
			availabilityBool = dbLink.checkAvailability(n)
			eval(f'self.{n}.setEnabled({availabilityBool})')

class RocksaltCheese(QWidget):
	def __init__(self):
		super(RocksaltCheese, self).__init__()
		uic.loadUi('rocksaltCheeseSelected.ui',self)

		self.flavorList = ["rocksalt_wintermelon","rocksalt_chocolate","rocksalt_mango",
		"rocksalt_strawberry","rocksalt_blueberry","rocksalt_tiramisu"]

		#Initializing the buttons
		self.rocksalt_wintermelon.clicked.connect(lambda: self.addOrder("rocksalt_wintermelon"))
		self.rocksalt_chocolate.clicked.connect(lambda: self.addOrder("rocksalt_chocolate"))
		self.rocksalt_mango.clicked.connect(lambda: self.addOrder("rocksalt_mango"))
		self.rocksalt_strawberry.clicked.connect(lambda: self.addOrder("rocksalt_strawberry"))
		self.rocksalt_blueberry.clicked.connect(lambda: self.addOrder("rocksalt_blueberry"))
		self.rocksalt_tiramisu.clicked.connect(lambda: self.addOrder("rocksalt_tiramisu"))


	def addOrder(self, order):
		mainWindowObj.addTemp(order)
		addOns.show()
		self.hide()

	def checkAvailability(self):
		for n in self.flavorList:
			availabilityBool = dbLink.checkAvailability(n)
			eval(f'self.{n}.setEnabled({availabilityBool})')

class Coffee(QWidget):
	def __init__(self):
		super(Coffee, self).__init__()
		uic.loadUi('coffeeSelected.ui',self)

		self.flavorList = ["coffee_iced","coffee_special","coffee_hazelnut","coffee_mocha",
		"coffee_caramel","coffee_tiramisu"]

		#Initializing the buttons
		self.coffee_iced.clicked.connect(lambda: self.addOrder("coffee_iced"))
		self.coffee_special.clicked.connect(lambda: self.addOrder("coffee_special"))
		self.coffee_hazelnut.clicked.connect(lambda: self.addOrder("coffee_hazelnut"))
		self.coffee_mocha.clicked.connect(lambda: self.addOrder("coffee_mocha"))
		self.coffee_caramel.clicked.connect(lambda: self.addOrder("coffee_caramel"))
		self.coffee_tiramisu.clicked.connect(lambda: self.addOrder("coffee_tiramisu"))


	def addOrder(self, order):
		mainWindowObj.addTemp(order)
		addOns.show()
		self.hide()

	def checkAvailability(self):
		for n in self.flavorList:
			availabilityBool = dbLink.checkAvailability(n)
			eval(f'self.{n}.setEnabled({availabilityBool})')

class IcedTea(QWidget):
	def __init__(self):
		super(IcedTea, self).__init__()
		uic.loadUi('icedTeaSelected.ui',self)

		self.flavorList = ["iced_greenApple","iced_passionFruit","iced_lychee","iced_wintermelon",
		"iced_strawberry","iced_mango","iced_blueberry","iced_grape","iced_lemongrass",
		"iced_flavoredNata","iced_flavoredCheese"]

		#Initializing the buttons
		self.iced_greenApple.clicked.connect(lambda: self.addOrder("iced_greenApple"))
		self.iced_passionFruit.clicked.connect(lambda: self.addOrder("iced_passionFruit"))
		self.iced_lychee.clicked.connect(lambda: self.addOrder("iced_lychee"))
		self.iced_wintermelon.clicked.connect(lambda: self.addOrder("iced_wintermelon"))
		self.iced_strawberry.clicked.connect(lambda: self.addOrder("iced_strawberry"))
		self.iced_mango.clicked.connect(lambda: self.addOrder("iced_mango"))
		self.iced_blueberry.clicked.connect(lambda: self.addOrder("iced_blueberry"))
		self.iced_grape.clicked.connect(lambda: self.addOrder("iced_grape"))
		self.iced_lemongrass.clicked.connect(lambda: self.addOrder("iced_lemongrass"))
		self.iced_flavoredNata.clicked.connect(lambda: self.addOrder("iced_flavoredNata"))
		self.iced_flavoredCheese.clicked.connect(lambda: self.addOrder("iced_flavoredCheese"))


	def addOrder(self, order):
		mainWindowObj.addTemp(order)
		addOns.show()
		self.hide()

	def checkAvailability(self):
		for n in self.flavorList:
			availabilityBool = dbLink.checkAvailability(n)
			eval(f'self.{n}.setEnabled({availabilityBool})')

class MatchaMucho(QWidget):
	def __init__(self):
		super(MatchaMucho, self).__init__()
		uic.loadUi('matchaMuchoSelected.ui',self)

		self.flavorList = ["matcha_matchoco","matcha_matchberry","matcha_redBean","matcha_cheese"]

		#Initializing the buttons
		self.matcha_matchoco.clicked.connect(lambda: self.addOrder("matcha_matchoco"))
		self.matcha_matchberry.clicked.connect(lambda: self.addOrder("matcha_matchberry"))
		self.matcha_redBean.clicked.connect(lambda: self.addOrder("matcha_redBean"))
		self.matcha_cheese.clicked.connect(lambda: self.addOrder("matcha_cheese"))


	def addOrder(self, order):
		mainWindowObj.addTemp(order)
		addOns.show()
		self.hide()

	def checkAvailability(self):
		for n in self.flavorList:
			availabilityBool = dbLink.checkAvailability(n)
			eval(f'self.{n}.setEnabled({availabilityBool})')

class HotMilkTea(QWidget):
	def __init__(self):
		super(HotMilkTea, self).__init__()
		uic.loadUi('hotMilkTea.ui',self)

		self.flavorList = ["hot_milkTea","hot_goat","hot_brownSugar","hot_greenTea"]

		#Initializing the buttons
		self.hot_milkTea.clicked.connect(lambda: self.addOrder("hot_milkTea"))
		self.hot_goat.clicked.connect(lambda: self.addOrder("hot_goat"))
		self.hot_brownSugar.clicked.connect(lambda: self.addOrder("hot_brownSugar"))
		self.hot_greenTea.clicked.connect(lambda: self.addOrder("hot_greenTea"))

	def addOrder(self, order):
		mainWindowObj.addTemp(order)
		addOns.show()
		self.hide()

	def checkAvailability(self):
		for n in self.flavorList:
			availabilityBool = dbLink.checkAvailability(n)
			eval(f'self.{n}.setEnabled({availabilityBool})')

class Minterrific(QWidget):
	def __init__(self):
		super(Minterrific, self).__init__()
		uic.loadUi('minterrificSelected.ui',self)

		self.flavorList = ["dyna_milkTea","dyna_choco","dyna_oreo"]

		#Initializing the buttons
		self.dyna_milkTea.clicked.connect(lambda: self.addOrder("dyna_milkTea"))
		self.dyna_choco.clicked.connect(lambda: self.addOrder("dyna_choco"))
		self.dyna_oreo.clicked.connect(lambda: self.addOrder("dyna_oreo"))

	def addOrder(self, order):
		mainWindowObj.addTemp(order)
		addOns.show()
		self.hide()

	def checkAvailability(self):
		for n in self.flavorList:
			availabilityBool = dbLink.checkAvailability(n)
			eval(f'self.{n}.setEnabled({availabilityBool})')

class AddOns(QWidget):
	def __init__(self):
		super(AddOns, self).__init__()
		uic.loadUi('addOns.ui',self)

		self.flavorList = ["add_pearl","add_pudding","add_oreo","add_redBeans","add_nata",
		"add_poppingBoba","add_grassJelly","add_coffeeJelly","add_rocksaltCheese"]

		#Initializing the buttons
		#Used "dummyFunc()" to enable the addOns window to accept multiple addOns
		self.add_pearl.clicked.connect(lambda: self.dummyFunc())
		self.add_pudding.clicked.connect(lambda: self.dummyFunc())
		self.add_oreo.clicked.connect(lambda: self.dummyFunc())
		self.add_redBeans.clicked.connect(lambda: self.dummyFunc())
		self.add_nata.clicked.connect(lambda: self.dummyFunc())
		self.add_poppingBoba.clicked.connect(lambda: self.dummyFunc())
		self.add_grassJelly.clicked.connect(lambda: self.dummyFunc())
		self.add_coffeeJelly.clicked.connect(lambda: self.dummyFunc())
		self.add_rocksaltCheese.clicked.connect(lambda: self.dummyFunc())
		self.cancel_addOns.clicked.connect(lambda: self.close())
		self.accept_addOns.clicked.connect(lambda: self.verifyOrder(True))


	def dummyFunc(self):
		pass

	def verifyOrder(self, accept = False):
		if accept:
			if self.add_pearl.isChecked():
				mainWindowObj.addTemp("add_pearl")

			if self.add_pudding.isChecked():
				mainWindowObj.addTemp("add_pudding")

			if self.add_oreo.isChecked():
				mainWindowObj.addTemp("add_oreo")

			if self.add_redBeans.isChecked():
				mainWindowObj.addTemp("add_redBeans")

			if self.add_nata.isChecked():
				mainWindowObj.addTemp("add_nata")

			if self.add_poppingBoba.isChecked():
				mainWindowObj.addTemp("add_poppingBoba")

			if self.add_grassJelly.isChecked():
				mainWindowObj.addTemp("add_grassJelly")

			if self.add_coffeeJelly.isChecked():
				mainWindowObj.addTemp("add_coffeeJelly")

			if self.add_rocksaltCheese.isChecked():
				mainWindowObj.addTemp("add_rocksaltCheese")

			mainWindowObj.verifyOrder()
			self.resetOrder()

	def closeEvent(self, event):
		reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
				QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

		if reply == QMessageBox.Yes:
			event.accept()
			self.resetOrder()

		else:
			event.ignore()

	def resetOrder(self):
		mainWindowObj.tempOrderTally = []
		self.add_pearl.setChecked(False)
		self.add_pudding.setChecked(False)
		self.add_oreo.setChecked(False)
		self.add_redBeans.setChecked(False)
		self.add_nata.setChecked(False)
		self.add_poppingBoba.setChecked(False)
		self.add_grassJelly.setChecked(False)
		self.add_coffeeJelly.setChecked(False)
		self.add_rocksaltCheese.setChecked(False)
		self.hide()

	def showEvent(self,QShowEvent):
		self.addOnVisible = True

	def hideEvent(self,QHideEvent):
		self.addOnVisible = False

class LogInWindow(QWidget):
	def __init__(self):
		super(LogInWindow, self).__init__()
		uic.loadUi('login.ui',self)

		self.passMistakes = 0
		self.loginStackedWidget.setCurrentIndex(0)

		self.input_username.returnPressed.connect(lambda: self.focusNextPrevChild(True))
		self.input_password.returnPressed.connect(self.checkLogin)
		self.usernameInput.returnPressed.connect(lambda: self.focusNextPrevChild(True))
		self.passwordInput.returnPressed.connect(lambda: self.focusNextPrevChild(True))
		self.confirmPassword.returnPressed.connect(self.checkRegistration)
		self.registerSubmit.clicked.connect(self.checkRegistration)
		self.loginButton.clicked.connect(self.checkLogin)
		self.registerButton.clicked.connect(lambda: self.changeStackView(1))
		self.cancelButton.clicked.connect(lambda: self.changeStackView(0))

		self.show()

	def checkLogin(self):
		username = self.input_username.text()
		password = self.input_password.text()
		sha256Data = calc.hash256(f"{username}password{password}")
		if dbLink.checkLogin(sha256Data):
			mainWindowObj.show()
			self.close()
		else:
			self.passMistakes += 1
			if self.passMistakes > 3:
				self.close()
			self.input_username.setText('')
			self.input_username.setFocus()
			self.input_password.setText('')

	def checkRegistration(self):
		username = self.usernameInput.text()
		password = self.passwordInput.text()
		confirmPassword = self.confirmPassword.text()
		if (password == confirmPassword) and (password != ''):
			dbLink.registerUser(username, password, calc.hash256(f"{username}password{password}"))
			self.loginStackedWidget.setCurrentIndex(0)
			messageBox("User has been created, please login")
		else:
			messageBox("Please check the Password and Confirm Password")

	def changeStackView(self, index):
		self.loginStackedWidget.setCurrentIndex(index)
		
class FoodsGroup(QWidget):
	def __init__(self):
		super(FoodsGroup, self).__init__()
		uic.loadUi('foods.ui',self)

		#initializing variables
		self.tempOrderTally = []
		self.lastViewedIndex = 0
		self.flavorList = ["ramen_jr","ramen_big","siomai_chicken","siomai_pork","siomai_beef",
		"bonito_large","bonito_medium","burger_classic","burger_cheese","burger_egg",
		"burger_overload","burger_hamCheese","fries_regular","fries_medium","fries_large",
		"addFries_cheese","addFries_barbecue","addFries_sourCream","addFries_plain",
		"shaw_original","shaw_spicy","korDog_classic","korDog_frenchfry","korDog_cheese",
		"korDog_mozza","addKorDog_mayo","addKorDog_catsup","addKorDog_mustard","addKorDog_hotSauce",
		"tako_select_single","tako_select_barkada","singTako_cheese","singTako_crab",
		"singTako_dblCheese","singTako_chickenMelt","singTako_octoBits","singTako_bacon",
		"singTako_tunaMelt","barTako_cheese","barTako_crab","barTako_dblCheese","barTako_chickenMelt",
		"barTako_octoBits","barTako_bacon","barTako_tunaMelt","combo1","combo2","combo3","combo4"]

		#initializing buttons
		self.acceptButton.clicked.connect(self.acceptOrder)
		self.cancelButton.clicked.connect(self.cancelOrder)

		#ramen group
		self.ramen_jr.clicked.connect(lambda: self.toggleClick('ramen_jr'))
		self.ramen_big.clicked.connect(lambda: self.toggleClick('ramen_big'))

		#siomai group
		self.siomai_chicken.clicked.connect(lambda: self.toggleClick('siomai_chicken'))
		self.siomai_pork.clicked.connect(lambda: self.toggleClick('siomai_pork'))
		self.siomai_beef.clicked.connect(lambda: self.toggleClick('siomai_beef'))

		#bonito group
		self.bonito_large.clicked.connect(lambda: self.toggleClick('bonito_large'))
		self.bonito_medium.clicked.connect(lambda: self.toggleClick('bonito_medium'))

		#burger group
		self.burger_classic.clicked.connect(lambda: self.toggleClick('burger_classic'))
		self.burger_cheese.clicked.connect(lambda: self.toggleClick('burger_cheese'))
		self.burger_egg.clicked.connect(lambda: self.toggleClick('burger_egg'))
		self.burger_overload.clicked.connect(lambda: self.toggleClick('burger_overload'))
		self.burger_hamCheese.clicked.connect(lambda: self.toggleClick('burger_hamCheese'))

		#fries group
		self.fries_regular.clicked.connect(lambda: self.toggleClick('fries_regular'))
		self.fries_medium.clicked.connect(lambda: self.toggleClick('fries_medium'))
		self.fries_large.clicked.connect(lambda: self.toggleClick('fries_large'))
		self.addFries_cheese.clicked.connect(lambda: self.toggleClick('addFries_cheese'))
		self.addFries_barbecue.clicked.connect(lambda: self.toggleClick('addFries_barbecue'))
		self.addFries_sourCream.clicked.connect(lambda: self.toggleClick('addFries_sourCream'))
		self.addFries_plain.clicked.connect(lambda: self.toggleClick('addFries_plain'))

		#shawarma group
		self.shaw_original.clicked.connect(lambda: self.toggleClick('shaw_original'))
		self.shaw_spicy.clicked.connect(lambda: self.toggleClick('shaw_spicy'))

		#korean corndog group
		self.korDog_classic.clicked.connect(lambda: self.toggleClick('korDog_classic'))
		self.korDog_frenchfry.clicked.connect(lambda: self.toggleClick('korDog_frenchfry'))
		self.korDog_cheese.clicked.connect(lambda: self.toggleClick('korDog_cheese'))
		self.korDog_mozza.clicked.connect(lambda: self.toggleClick('korDog_mozza'))
		self.addKorDog_mayo.clicked.connect(lambda: self.toggleClick('addKorDog_mayo'))
		self.addKorDog_catsup.clicked.connect(lambda: self.toggleClick('addKorDog_catsup'))
		self.addKorDog_mustard.clicked.connect(lambda: self.toggleClick('addKorDog_mustard'))
		self.addKorDog_hotSauce.clicked.connect(lambda: self.toggleClick('addKorDog_hotSauce'))

		#takoyaken selector
		self.tako_select_single.clicked.connect(lambda: self.toggleClick('tako_select_single'))
		self.tako_select_barkada.clicked.connect(lambda: self.toggleClick('tako_select_barkada'))

		#takoyaken single package
		self.singTako_cheese.clicked.connect(lambda: self.toggleClick('singTako_cheese'))
		self.singTako_crab.clicked.connect(lambda: self.toggleClick('singTako_crab'))
		self.singTako_dblCheese.clicked.connect(lambda: self.toggleClick('singTako_dblCheese'))
		self.singTako_chickenMelt.clicked.connect(lambda: self.toggleClick('singTako_chickenMelt'))
		self.singTako_octoBits.clicked.connect(lambda: self.toggleClick('singTako_octoBits'))
		self.singTako_bacon.clicked.connect(lambda: self.toggleClick('singTako_bacon'))
		self.singTako_tunaMelt.clicked.connect(lambda: self.toggleClick('singTako_tunaMelt'))

		#takoyaken barkada package
		self.barTako_cheese.clicked.connect(lambda: self.toggleClick('barTako_cheese'))
		self.barTako_crab.clicked.connect(lambda: self.toggleClick('barTako_crab'))
		self.barTako_dblCheese.clicked.connect(lambda: self.toggleClick('barTako_dblCheese'))
		self.barTako_chickenMelt.clicked.connect(lambda: self.toggleClick('barTako_chickenMelt'))
		self.barTako_octoBits.clicked.connect(lambda: self.toggleClick('barTako_octoBits'))
		self.barTako_bacon.clicked.connect(lambda: self.toggleClick('barTako_bacon'))
		self.barTako_tunaMelt.clicked.connect(lambda: self.toggleClick('barTako_tunaMelt'))

		#combo group
		self.combo1.clicked.connect(lambda: self.toggleClick('combo1'))
		self.combo2.clicked.connect(lambda: self.toggleClick('combo2'))
		self.combo3.clicked.connect(lambda: self.toggleClick('combo3'))
		self.combo4.clicked.connect(lambda: self.toggleClick('combo4'))

	def toggleClick(self, productCode):
		if productCode in self.tempOrderTally:
			self.tempOrderTally.remove(productCode)
		else:
			if 'siomai' in productCode:
				self.siomaiIncrement(productCode)
			else:
				self.tempOrderTally.append(productCode)

	def siomaiIncrement(self, productCode):
		self.mainView.setCurrentIndex(11)
		self.lastViewedIndex = 11
		self.siomaiFlavor = productCode

	def cancelOrder(self):
		self.resetButtons()
		self.close()

	def acceptOrder(self, productCode = False):
		if self.lastViewedIndex == 11:
			self.siomaiNumber = self.siomaiQty.value()
			self.tempOrderTally.append([self.siomaiFlavor,self.siomaiNumber])

		mainWindowObj.tempOrderTally = self.tempOrderTally
		mainWindowObj.verifyOrder()
		addOns.resetOrder()
		self.resetButtons()
		self.close()
		

	def addOrder(self, productCode):
		self.tempOrderTally.append(productCode)

	def dummyFunc(self):
		pass

	def viewFood(self, selector):
		self.selectorDict = {	'ramenGroup': 0,
								'siomaiGroup': 1,
								'bonitoGroup': 2,
								'burgerGroup': 3,
								'friesGroup': 4,
								'shawarmaGroup': 5,
								'korDogGroup': 6,
								'takoyakenGroup': 7,
								'takoyakenSingleGroup': 8,
								'takoyakenBarkadaGroup': 9,
								'comboGroup': 10,
							}
		self.lastViewedIndex = self.selectorDict[selector]
		self.mainView.setCurrentIndex(self.lastViewedIndex)
		self.show()

	def resetButtons(self):
		for n in self.tempOrderTally:
			if isinstance(n, list):
				n = n[0]
			eval(f'self.{n}.setChecked(False)')
		self.tempOrderTally = []

class InventoryEdit(QWidget):
	def __init__(self):
		super(InventoryEdit, self).__init__()
		uic.loadUi('inventoryEditOption.ui',self)
		self.acceptPressed = False
		self.priceInput.editingFinished.connect(self.cashInputValidate)
		self.acceptButton.clicked.connect(self.acceptButtonFunc)
		self.cancelButton.clicked.connect(self.resetInputs)

	def cashInputValidate(self):
		validationRule = QDoubleValidator(0, 999999, 2)
		isAcceptable = validationRule.validate(self.priceInput.text(),1)[0] == QValidator.Acceptable
		if isAcceptable:
			self.cashAmount = float(self.priceInput.text())
		else:
			self.priceInput.setText('')

	def acceptButtonFunc(self):
		self.acceptPressed = True
		isAvailable = self.trueFalseChoices.currentText()
		priceChange = self.priceInput.text()
		if isAvailable == 'False':
			isAvailable = False
		elif isAvailable == 'True':
			isAvailable = True
		if isAvailable == ' ':
			mainWindowObj.inventoryChangesToBeMade['isAvailable'] = None
		else:
			mainWindowObj.inventoryChangesToBeMade['isAvailable'] = isAvailable

		if priceChange == None:
			mainWindowObj.inventoryChangesToBeMade['price'] = None
		else:
			mainWindowObj.inventoryChangesToBeMade['price'] = float(priceChange)
		self.resetInputs()

	def resetInputs(self):
		self.trueFalseChoices.setCurrentIndex(0)
		self.priceInput.setText('')
		
		self.close()

	def closeEvent(self, event):
		if self.acceptPressed:
			reply = QMessageBox.Yes
			self.acceptPressed = False
		else:
			reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
					QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

		if reply == QMessageBox.Yes:
			mainWindowObj.editInventoryFunc()
			event.accept()

			#print('Window closed')
		else:
			event.ignore()





def findProduct(productCode):
	productInfo = dbLink.findCode(productCode)
	flavorName, price = productInfo[2:4]
	return flavorName, price

def make_autopct(values):
	def my_autopct(pct):
		total = sum(values)
		val = int(round(pct*total/100.0))
		return '{v:d}'.format(v=val)
	return my_autopct

def messageBox(message):
	dialogBox = QMessageBox()
	dialogBox.setText(message)
	dialogBox.setWindowTitle("Alert!")
	dialogBox.exec_()

print('Starting pyqt')
app = QApplication(sys.argv)

instanceInventoryEdit = InventoryEdit()

print('Starting database')
dbLink = db.localDBLink
  
print('starting instanceFoodsGroup')
instanceFoodsGroup = FoodsGroup()

print('starting instanceMilkTeaWindow')
instanceMilkTeaWindow = MilkTeaWindow()

print('starting instanceFrappeWindow')
instanceFrappeWindow = FrappeWindow()

print('starting instanceMinterrific')
instanceMinterrific = Minterrific()

print('starting instanceChocolate')
instanceChocolate = Chocolate()

print('starting instanceIcedTea')
instanceIcedTea = IcedTea()

print('starting instanceHotMilkTea')
instanceHotMilkTea = HotMilkTea()

print('starting instanceMatchaMucho')
instanceMatchaMucho = MatchaMucho()

print('starting instanceYakultWindow')
instanceYakultWindow = YakultWindow()

print('starting instanceCoffee')
instanceCoffee = Coffee()

print('starting instanceTaroWindow')
instanceTaroWindow = TaroWindow()

print('starting instanceRocksaltCheese')
instanceRocksaltCheese = RocksaltCheese()

print('starting instanceSodaSplashedWindow')
instanceSodaSplashedWindow = SodaSplashedWindow()

print('starting addOns')
addOns = AddOns()

print('starting mainWindowObj')
mainWindowObj = MainWindow()

print('starting instancelogInWindow')
instancelogInWindow = LogInWindow()

try:
	sys.exit(app.exec_())
except:
	dbLink.connectSql.commit()
	#dbLink.synchDatabases()
	#dbLink.connectSql.commit()
	print("Exiting")
