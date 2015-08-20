# -*- coding: utf-8 -*-

import pandas as pd 
import numpy as np 
import random
import re
import sys

import extendedSysPath
from config import Config as conf


def concatenateAllYears(years) : 

	filePathes = [conf.dataDir+"/matches_data_file"+str(year)+".csv" for year in years]
	dataframes = [pd.read_csv(filepath) for filepath in filePathes]
	return pd.concat(dataframes, ignore_index=True)


def normalizePlayerName(row) :

	firstName = row["playerName"].split(",")[1]
	lastName = row["playerName"].split(",")[0]
	return firstName.lstrip() + " " + lastName


def readRankingsCsv(csvRankingsFilePath) :

	# Lecture des classement et petit munging 
	rankingsDF = pd.read_csv(csvRankingsFilePath, low_memory=False)
	rankingsDF.drop(["Unnamed: 0", "link"], axis=1, inplace=True)
	rankingsDF["playerName"] = rankingsDF.apply(normalizePlayerName, axis=1)
	rankingsDF.set_index("playerName", inplace=True)
	rankingsDF.columns = pd.to_datetime(rankingsDF.columns, format="%d.%m.%Y")
	oldColumnOrder = rankingsDF.columns
	newColumnsOrder = sorted(oldColumnOrder)
	rankingsDF = rankingsDF[newColumnsOrder]

	return rankingsDF


# Randomise la base : Remplacement de Winner et Loser par J0 et J1 et ajout d'une classe Winner qui vaudra 0 ou 1 
def randomizeDataFrame(dataframe) :

	# Création d'un vecteur valant aléatoirement 0 (qui signifiera victoire JA) ou 1 (victoire JB) 
	winnerPlayer = [ random.choice([0, 1]) for i in range(0, len(dataframe.index)) ]
	randomVector = [ bool(player) for player in winnerPlayer ]

	# Permutation de J0 et J1 quand random vector vaut True (=> winnerPlayer = 1 et donc on veut J1 gagne)
	columnsInInitialOrder =  [u'playerA', u'playerB', u'a_aces', u'a_double_faults', u'a_first_serve_hits', u'a_first_serve_total', u'a_first_serve_won', u'a_first_serve_played', u'a_second_serve_won', u'a_second_serve_played', u'a_break_points_saved', u'a_break_points_total', u'a_service_games', u'a_service_points_won', u'a_service_points_total', u'b_aces', u'b_double_faults', u'b_first_serve_hits', u'b_first_serve_total', u'b_first_serve_won', u'b_first_serve_played', u'b_second_serve_won', u'b_second_serve_played', u'b_break_points_saved', u'b_break_points_total', u'b_service_games', u'b_service_points_won', u'b_service_points_total']
	columnsInPermutedOrder = [u'playerB', u'playerA', u'b_aces', u'b_double_faults', u'b_first_serve_hits', u'b_first_serve_total', u'b_first_serve_won', u'b_first_serve_played', u'b_second_serve_won', u'b_second_serve_played', u'b_break_points_saved', u'b_break_points_total', u'b_service_games', u'b_service_points_won', u'b_service_points_total', u'a_aces', u'a_double_faults', u'a_first_serve_hits', u'a_first_serve_total', u'a_first_serve_won', u'a_first_serve_played', u'a_second_serve_won', u'a_second_serve_played', u'a_break_points_saved', u'a_break_points_total', u'a_service_games', u'a_service_points_won', u'a_service_points_total']
	dataframe.loc[randomVector, columnsInInitialOrder] = dataframe.loc[randomVector, columnsInPermutedOrder].values 

	# Enfin il ne reste plus qu'à ajouter une colonne indiquant le joueur gagnant qui sera winnerPlayer
	dataframe['winner'] = winnerPlayer

	return dataframe


def getScoreColumns(row) :

	scoreText = str(row["score"])

	sets = { "a_set1":0, "a_set2":0, "a_set3":0, "a_set4":0, "a_set5":0,
			 "b_set1":0, "b_set2":0, "b_set3":0, "b_set4":0, "b_set5":0,
			 "a_tb_set1":0, "a_tb_set2":0, "a_tb_set3":0, "a_tb_set4":0, "a_tb_set5":0,
			 "b_tb_set1":0, "b_tb_set2":0, "b_tb_set3":0, "b_tb_set4":0, "b_tb_set5":0,
			 "comment": "Completed"  }

	# Cas W/O, Bye ou Ret dans le score 
	if "W/O" in scoreText :
		sets["comment"] = "W/O"
 
	if "N/A Bye" in row["playerB"] :
		sets["comment"] = "Bye"

	if "RET" in scoreText : 
		sets["comment"] = "RET"

	# Extraction des sets 
	setsRaw = scoreText.split(";")
	nbSets = len(setsRaw)
	
	if nbSets > 1 : 
		
		regex = r'([0-9]+)-([0-9]+)(\(([0-9]+)\))?'
		nbSetsWonByA = 0
		nbSetsForAVictory = row["num_of_sets"]

		for i in range(nbSets) :

			# Récupération des scores des 2 joueurs dans le set courant
			if "RET" not in setsRaw[i] :

				groups = re.match(regex, setsRaw[i].lstrip()).groups()
				sets["a_set"+str(i+1)] = int(groups[0])
				sets["b_set"+str(i+1)] = int(groups[1])
				if sets["a_set"+str(i+1)] > sets["b_set"+str(i+1)] : 
					nbSetsWonByA += 1
				
				# Gestion d'un tie-break...
				if groups[3] is not None : 
					# ...remporté par playerA
					if sets["a_set"+str(i+1)] == 7 :
						sets["a_tb_set"+str(i+1)] = 7 if int(groups[3]) <= 5 else int(groups[3]) + 2
						sets["b_tb_set"+str(i+1)] = int(groups[3]) 
					# ...remporté par playerB
					else : 
						sets["b_tb_set"+str(i+1)] = 7 if int(groups[3]) <= 5 else int(groups[3]) + 2
						sets["a_tb_set"+str(i+1)] = int(groups[3])

				else : 
					sets["a_tb_set"+str(i+1)] = 0 
					sets["b_tb_set"+str(i+1)] = 0

					# Test pour bien vérifier que le set est allé au bout 
					if not(abs(int(groups[0]) - int(groups[1])) >= 2 and max(int(groups[0]), int(groups[1])) >= 6) :
						comment = "RET"

		# Test pour vérifier que A a bien remporté suffisamment de set 
		if nbSetsWonByA < nbSetsForAVictory :
			comment = "RET"

	return pd.Series(sets)



def getCategory(row) :

	name = row["event_name"]

	# Premier cas : c'est un grand chelem 
	if "Grand Slams" in name : 
		return 1

	# Deuxième cas : c'est la master cup ou grand slam cup 
	if "Grand Slam Cup" in name or "Masters Cup" in name : 
		return 2
	
	# Troisième cas : c'est un masters series 
	if "Masters Series" in name or "Masters 1000" in name :
		return 3

	# Quatrième cas : c'est un atp 500 ou équivalent 
	if isAnAtp500(row, atp500Tournaments) : 
		return 4

	# Enfin dernier cas : si n'est aucun des précédents alors c'est que c'est un atp 250 
	return 5


def isAnAtp500(row, atp500Tournaments) :

	# Extraction de l'année du tournoi en gérant le cas où les premiers jours du tournoi sont sur l'année d'avant
	date = row["event_time"]
	year = int(date.split('-')[0])
	month = int(date.split('-')[1])
	day = int(date.split('-')[2].split(' ')[0])

	if month == 12 and day > 20 : 
		year+=1

	# Récupération des atp500 de l'année correspondante
	atp500 = atp500Tournaments[year]

	# Cas particulier du tournoi du Queens en 1998-2000
	if year in range(1998, 2001) and "Queen's" in row["event_name"] :
		return False
		
	# Si un des at500 de l'année matche on renvoit True
	for tournament in atp500 : 

		if tournament in row["event_name"] : 
			return True

	# Sinon c'est False
	return False


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
	lastRank = int(lastRankAndPoints[0].replace(",", ""))
	lastPoints = int( lastRankAndPoints[1].replace(",", "") )
	lastDate = priorRankings.index[-1]

	# Calcul de la précision de l'info : nb de jours dont date l'info
	accuracy = (dateAsked - lastDate).days

	return pd.Series({"rank": lastRank, "points": lastPoints, "delay": accuracy})


# Paramètres du programme
dates = range(1991, 2015)
csvOutputFilePath = conf.preProcessedMatchsFilePath
csvRankingsFilePath = conf.preProcessedRankingsFilePath

atp500Tournaments = {
1991: ["Philadelphia","Barcelona","Tokyo Outdoor","Stuttgart Outdoor","Washington","Indianapolis","New Haven","Brussels","Sydney Indoor","Tokyo Indoor","Stuttgart Indoor","Memphis"],
1992: ["Philadelphia","Barcelona","Tokyo Outdoor","Stuttgart Outdoor","Washington","Indianapolis","New Haven","Brussels","Sydney Indoor","Tokyo Indoor","Stuttgart Indoor","Memphis"],
1993: ["Milan","Memphis","Philadelphia","Stuttgart Indoor","Barcelona","Tokyo Outdoor","Stuttgart Outdoor","Washington","Indianapolis","New Haven","Sydney Indoor","Tokyo Indoor"],
1994: ["Milan","Memphis","Philadelphia","Stuttgart Indoor","Barcelona","Tokyo Outdoor","Stuttgart Outdoor","Washington","Indianapolis","New Haven","Sydney Indoor","Tokyo Indoor"],
1995: ["Milan","Memphis","Philadelphia","Stuttgart Indoor","Barcelona","Tokyo Outdoor","Stuttgart Outdoor","Washington","Indianapolis","New Haven","Tokyo Indoor"],
1996: ["Antwerp","Memphis","Philadelphia","Milan","Barcelona","Tokyo","Stuttgart","Washington","Indianapolis","New Haven","Vienna"],
1997: ["Antwerp","Memphis","Philadelphia","Milan","Barcelona","Tokyo","Stuttgart","Washington","Indianapolis","New Haven","Singapore","Vienna"],
1998: ["Antwerp","Memphis","Philadelphia","London","Barcelona","Tokyo","Stuttgart","Washington","Indianapolis","New Haven","Singapore","Vienna"],
1999: ["Memphis","Rotterdam","London","Barcelona","Tokyo","Stuttgart","Kitzbuhel","Washington","Indianapolis","Singapore","Vienna"],
2000: ["Memphis","Rotterdam","London","Mexico","Barcelona","Stuttgart","Kitzbuhel","Washington","Indianapolis","Vienna","Tokyo"],
2001: ["Memphis","Rotterdam","Dubai","Acapulco","Barcelona","Stuttgart","Kitzbuhel","Washington","Indianapolis","Vienna","Tokyo"],
2002: ["Memphis","Rotterdam","Dubai","Acapulco","Barcelona","Kitzbuhel","Washington","Indianapolis","Vienna","Tokyo"],
2003: ["Memphis","Rotterdam","Dubai","Acapulco","Barcelona","Stuttgart","Kitzbuhel","Vienna","Tokyo"],
2004: ["Memphis","Rotterdam","Dubai","Acapulco","Barcelona","Stuttgart","Kitzbuhel","Vienna","Tokyo"],
2005: ["Memphis","Rotterdam","Dubai","Acapulco","Barcelona","Stuttgart","Kitzbuhel","Vienna","Tokyo"],
2006: ["Memphis","Rotterdam","Dubai","Acapulco","Barcelona","Stuttgart","Kitzbuhel","Vienna","Tokyo"],
2007: ["Memphis","Rotterdam","Dubai","Acapulco","Barcelona","Stuttgart","Kitzbuhel","Vienna","Tokyo"],
2008: ["Memphis","Rotterdam","Dubai","Acapulco","Barcelona","Stuttgart","Kitzbuhel","Vienna","Tokyo"],
2009: ["Memphis","Rotterdam","Dubai","Acapulco","Barcelona","Hamburg","Washington","Beijing","Tokyo", "Basel", "Valencia"],
2010: ["Memphis","Rotterdam","Dubai","Acapulco","Barcelona","Hamburg","Washington","Beijing","Tokyo", "Basel", "Valencia"],
2011: ["Memphis","Rotterdam","Dubai","Acapulco","Barcelona","Hamburg","Washington","Beijing","Tokyo", "Basel", "Valencia"],
2012: ["Memphis","Rotterdam","Dubai","Acapulco","Barcelona","Hamburg","Washington","Beijing","Tokyo", "Basel", "Valencia"],
2013: ["Memphis","Rotterdam","Dubai","Acapulco","Barcelona","Hamburg","Washington","Beijing","Tokyo", "Basel", "Valencia"],
2014: ["Rio de Janeiro","Rotterdam","Dubai","Acapulco","Barcelona","Hamburg","Washington","Beijing","Tokyo", "Basel", "Valencia"],
2015: ["Rio de Janeiro","Rotterdam","Dubai","Acapulco","Barcelona","Halle","London","Hamburg","Washington","Beijing","Tokyo", "Basel", "Valencia"]
}


# Lecture de toutes les années 
print "\nConcaténation de toutes les années de " + str(dates[0]) + " à " + str(dates[len(dates)-1])
sys.stdout.flush()
totalDF = concatenateAllYears(dates)

# Et de tous les classements
print "Lecture de tous les classements" 
sys.stdout.flush()
rankingsDF = readRankingsCsv(csvRankingsFilePath)

# On extraie les catégories de chaque tournoi
print "Extraction des catégories"
sys.stdout.flush() 
totalDF["category"] = totalDF.apply(getCategory, axis=1)

# Extraction du score 
print "Extraction du score : "
sys.stdout.flush() 
scoreColumns = totalDF.apply(getScoreColumns, axis=1)
totalDF = pd.concat([totalDF, scoreColumns], axis=1)

# L'étape de randomization à présent
print "Randomization de la base"
sys.stdout.flush() 
totalDF = randomizeDataFrame(totalDF)

# Obtention des rankings pour chaque joueur et chaque match
print "Obtention des rankings pour chaque match"
sys.stdout.flush()
rankingsPlayerAColumns = totalDF.apply(lambda x : getPlayerRanking(x["playerA"], pd.to_datetime(x["event_time"], format="%Y-%m-%d %H:%M:%S.%f"), rankingsDF), axis=1)
rankingsPlayerAColumns.rename(columns={"delay": "a_delay", "rank": "a_rank", "points": "a_points"}, inplace=True)
rankingsPlayerBColumns = totalDF.apply(lambda x : getPlayerRanking(x["playerB"], pd.to_datetime(x["event_time"], format="%Y-%m-%d %H:%M:%S.%f"), rankingsDF), axis=1)
rankingsPlayerBColumns.rename(columns={"delay": "b_delay", "rank": "b_rank", "points": "b_points"}, inplace=True)
totalDF = pd.concat([totalDF, rankingsPlayerAColumns, rankingsPlayerBColumns], axis=1)

# Sauvegarde du Df 
print "Ecriture : " + str(csvOutputFilePath)	
sys.stdout.flush()
totalDF.to_csv(csvOutputFilePath)

