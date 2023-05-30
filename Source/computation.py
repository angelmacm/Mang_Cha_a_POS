from datetime import datetime, timedelta
import hashlib
import numpy as np
import matplotlib.pyplot as plt
import posdb as db

def tax(amount):
	taxVat = amount*.12
	return amount-taxVat, taxVat

def change(amount, money):
	return (amount-money) * -1

def computeTally(tallylist):
	computedTally = 0
	for n in tallylist:
		computedTally += n[2]
	return computedTally

def hash256(text):
	h = hashlib.new('sha256')
	h.update(bytearray(text,'utf-8'))
	return h.hexdigest()


def getDailyProfit():
	timeRange = 7
	initialDate = datetime.now()
	formatSQL = '%m/%d/%y'
	#print(dateToday,dateStart)
	listOfProfits = []
	for q in range(timeRange+1):
		dateToCheck = initialDate - timedelta(days = int(timeRange-q))
		dateToCheck = str(dateToCheck.strftime('%Y-%m-%d'))
		saveTemplate = {'Date': '',
						'Amount': 0}
		dbResult = dbLink.rangeData(dateToCheck, dateToCheck, 'transactionlogs')
		totalAmount = 0
		for n in dbResult:
			transactionId, itemsBought, amount, money, change, tax, date = n
			totalAmount += amount
		saveTemplate['Date'] = dateToCheck
		saveTemplate['Amount'] = totalAmount
		listOfProfits.append(saveTemplate)
	listOfDates = []
	listOfAmounts = []
	for n in listOfProfits:
		listOfDates.append(n['Date'])
		listOfAmounts.append(n['Amount'])
	return listOfDates,listOfAmounts

def getBestAllTime():
	dbResult = dbLink.selectAllFrom('transactionlogs')
	listOfOrders = []
	listOfFlavors = []
	#print(dbResult)
	for n in dbResult:
		idNumber, itemsBought, itemAmount, customerMoney, customerChange, valueTax, date = n
		listOfOrders = itemsBought.replace('[','').replace(']','').replace("'","").replace(" ","").split(',')
		for q in listOfOrders:
			foundInList = False
			if "_" in q:
				if 'add_' in q:
					continue
				for w in listOfFlavors:
					if q == w['flavorName']:
						w['number'] += 1
						foundInList = True

				if not foundInList:
					template = {'flavorName': q,
								'number': 1}
					listOfFlavors.append(template)
			
	lengthOfList = len(listOfFlavors)
	maxIndex = lengthOfList-1

	for eachIndex in range(1,lengthOfList):
		if listOfFlavors[eachIndex]['number'] < listOfFlavors[eachIndex-1]['number']:
			for eachNum in range(eachIndex, 0, -1):
				if listOfFlavors[eachNum]['number'] < listOfFlavors[eachNum-1]['number']:
					tempHolder = listOfFlavors[eachNum]
					listOfFlavors[eachNum] = listOfFlavors[eachNum-1]
					listOfFlavors[eachNum-1] = tempHolder

	#listOfFlavors = listOfFlavors[::-1]
	return listOfFlavors

def getBestMonth():
	initialDate = datetime.now()
	formatSQL = '%m/%d/%y'
	dateStart = initialDate - timedelta(days = 30)
	dateStart = str(dateStart.strftime('%Y-%m-0'))
	dateEnd = str(initialDate.strftime('%Y-%m-%d'))
	#print(dateToday,dateStart)
	dbResult = dbLink.rangeData(dateStart, dateEnd, 'transactionlogs')
	listOfOrders = []
	listOfFlavors = []
	#print(dbResult)
	for n in dbResult:
		idNumber, itemsBought, itemAmount, customerMoney, customerChange, valueTax, date = n
		listOfOrders = itemsBought.replace('[','').replace(']','').replace("'","").replace(" ","").split(',')
		for q in listOfOrders:
			foundInList = False
			if "_" in q:
				if 'add_' in q:
					continue
				for w in listOfFlavors:
					if q == w['flavorName']:
						w['number'] += 1
						foundInList = True

				if not foundInList:
					template = {'flavorName': q,
								'number': 1}
					listOfFlavors.append(template)
			
	lengthOfList = len(listOfFlavors)
	maxIndex = lengthOfList-1

	for eachIndex in range(1,lengthOfList):
		if listOfFlavors[eachIndex]['number'] < listOfFlavors[eachIndex-1]['number']:
			for eachNum in range(eachIndex, 0, -1):
				if listOfFlavors[eachNum]['number'] < listOfFlavors[eachNum-1]['number']:
					tempHolder = listOfFlavors[eachNum]
					listOfFlavors[eachNum] = listOfFlavors[eachNum-1]
					listOfFlavors[eachNum-1] = tempHolder

	#listOfFlavors = listOfFlavors[::-1]
	return listOfFlavors

def getBestFive():
	results = getBestAllTime()
	topFlavors = []
	for n in results:
		topFlavors.append(n['flavorName'])
	topFlavors = topFlavors[::-1]
	return topFlavors[0:5]



dbLink = db.localDBLink



