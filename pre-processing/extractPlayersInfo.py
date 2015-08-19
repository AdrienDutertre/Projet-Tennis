# -*- coding: utf-8 -*-

import requests
import html5lib
import unicodedata as uni
from bs4 import BeautifulSoup
import json
import re
from pandas import Series, DataFrame
import pandas as pd 
import numpy as np

import extendedSysPath
from config import Config as conf

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

def getPlayerInfo(partUrl):
	soup = getSoupFromUrl(conf.atpUrl+partUrl)
	playerInfoCard = soup.find("div",id="playerBioInfoCardMain")
	playerInfoList = playerInfoCard.find("ul",id="playerBioInfoList").find_all("li")
	playerInfoListNormalized={}
	print partUrl
	for playerInfo in playerInfoList:
		playerInfoListNormalized[normalize(playerInfo.text).split(":")[0]]=normalize(playerInfo.text).split(":")[1]
	playerCountry = normalize(playerInfoCard.find("div",id="playerBioInfoFlag").find("p").text)
	playerInfoListNormalized['Country']=playerCountry

	InfoList = ['Age','Birthplace', 'Residence','Height','Weight','Plays','Turned Pro','Coach','Country']
	res = []
	for info in InfoList:
		if info in playerInfoListNormalized:
			res.append(playerInfoListNormalized[info])
		else: 
			res.append(np.nan)
	print res
	return res

InfoList = ['Age','Birthplace', 'Residence','Height','Weight','Plays','Turned Pro','Coach','Country']
df = pd.read_csv(conf.preProcessedRankingsFilePath)
df[InfoList] = df.apply(lambda x : getPlayerInfo(x['link']),axis=1)
df.to_csv(conf.preProcessedPlayersFilePath)
