# -*- coding: utf-8 -*-

import pandas as pd 
import numpy as np 
import random
import re

def getPlayerRanking(player, dateAsked, rankingsDF) : 

	# Cas où le joueur n'est pas dans le csv ==> return None
	if player not in rankingsDF.index : 
		return None

	# Récupération de la série correspondant aux classements antérieurs du joueur
	playerRankings = rankingsDF.ix[player]
	playerRankings.dropna(inplace=True)
	priorRankings = playerRankings[ playerRankings.index <= dateAsked ]

	# Cas où il n'y a pas de classement antérieur ==> return None
	if len(priorRankings) < 1 : 
		return None

	# Enfin on garde la plus récente 
	lastRankAndPoints = priorRankings[-1].split("::")
	lastRank = int(lastRankAndPoints[0])
	lastPoints = int( lastRankAndPoints[1].replace(",", "") )
	lastDate = priorRankings.index[-1]

	# Calcul de la précision de l'info : nb de jours dont date l'info
	accuracy = (dateAsked - lastDate).days

	return pd.Series({"rank": lastRank, "points": lastPoints, "delay": accuracy})


def normalizePlayerName(row) :

	firstName = row["playerName"].split(",")[1]
	lastName = row["playerName"].split(",")[0]
	return firstName.lstrip() + " " + lastName


# Paramètres du programme 
rankingsCsvFilePath = "Data/playersRank.csv"
player = "Federer, Roger"
dateAsked = pd.to_datetime("2011-08-01")

# Lecture des classement et petit munging 
rankingsDF = pd.read_csv(rankingsCsvFilePath)
rankingsDF.drop(["Unnamed: 0", "link"], axis=1, inplace=True)
rankingsDF["playerName"] = rankingsDF.apply(normalizePlayerName, axis=1)
rankingsDF.set_index("playerName", inplace=True)
rankingsDF.columns = pd.to_datetime(rankingsDF.columns, format="%d.%m.%Y")
oldColumnOrder = rankingsDF.columns
newColumnsOrder = sorted(oldColumnOrder)
rankingsDF = rankingsDF[newColumnsOrder]

# Test sur Roger pour voir si cela fonctionne
infos = getPlayerRanking(player, dateAsked, rankingsDF)


tmp = test.apply(lambda x : getPlayerRanking(x["playerA"], pd.to_datetime(x["event_time"], format="%Y-%m-%d %H:%M:%S.%f"), rankingsDF), axis=1)
