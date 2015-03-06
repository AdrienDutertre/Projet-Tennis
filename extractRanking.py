# -*- coding: utf-8 -*-

"""

Created on Sun 1 mar 2015
    
@author: Ohayon

"""

import requests
import html5lib
import unicodedata as uni
from bs4 import BeautifulSoup
import json
import re
from pandas import Series, DataFrame
import pandas as pd 

################################################################################################
# Some String manipulation functions

def normalize(string):
    return uni.normalize('NFKD',string).encode('ascii','ignore')


################################################################################################
# Returns a soup object from a given url

def getSoupFromUrl(url):
    result = requests.get(url)
    
    if result.status_code == 200:
        return BeautifulSoup(result.text,"html5lib")
    
    else:
        print 'Request failed', url
        return None


#################################################################################################
#                                                                                               #
"""                                       ATP Ranking                                         """
#                                                                                               #
#################################################################################################

##############################################################################################
# Find Date

def getDateForRanking():
	soup = getSoupFromUrl("http://www.atpworldtour.com/Rankings/Singles.aspx")
	dateBalise = soup.find_all("div", class_="playerBioFilterItem")[0].find_all("option")[0:1287]
	dateList = map(lambda x:normalize(x.text),dateBalise)
	return dateList


##############################################################################################
# Find Date

def getRankingForDate(date,linkData):
	rankingData={}
	for i in range (0,10):
		rankNumber = i*100+1
		soup = getSoupFromUrl("http://www.atpworldtour.com/Rankings/Singles.aspx?d="+date+"&r="+str(rankNumber)+"&c=#")
		table = soup.find("tbody")
		lines = table.find_all("tr")
		#print i
		for i in range(1,len(lines)):
			playerLine = lines[i].find_all("td")
			playerName = normalize(playerLine[0].find("a").text)
			playerUrl = playerLine[0].find("a").attrs["href"]
			ranking = normalize(playerLine[0].find("span").text)
			point = normalize(playerLine[1].find("a").text)
			rankingData[playerName]=str(ranking)+"::"+str(point)
			if (playerName not in linkData):
				linkData[playerName]=playerUrl
	return rankingData,linkData

def getRankingFromDateList(dateList):
	dataDict={}
	linkData={}
	for date in dateList:
		print "Fetching ranking for " + date
		dataDict[date],linkData=getRankingForDate(date,linkData)
	return dataDict,linkData

dateList = getDateForRanking()
print "Date found"
for i in range(0,124):
	RankData,linkData = getRankingFromDateList(dateList[10*i:10*(i+1)])
	RankData['link']=linkData
	Data = pd.DataFrame(RankData)
	Data.to_csv("tempRank/playerRanking"+str(i)+".csv")
	print "CSV " + str(i) + " file done"
#rankingData,linkData = getRankingForDate("16.02.2015")

