# -*- coding: utf-8 -*-

import sqlite3 
import pandas as pd
import re
import numpy as np

def cleanWeightOrHeight(x) : 
	
	weightOrHeight = re.compile(r".*\(([0-9]{1,3})")
	return np.nan if pd.isnull(x) else int(weightOrHeight.match(x).group(1))

def getDob(x) : 

	dob = re.compile(r".*\((.*)\)")
	return np.nan if pd.isnull(x) else dob.match(x).group(1).replace(".", "/")

def createPlayersTable(playersFilePath, sqlConn) :
	
	# Récupération des infos sur les joueurs 
	playersDF = pd.read_csv(playersFilePath)
	playersDF = playersDF.drop(["Unnamed: 0", "link"], axis=1)

	# Standardisation des colonnes : minuscule et espace = _
	playersDF.columns = [x.replace(" ", "_").lower() for x in playersDF.columns]

	# Nettoyage de certains champs 
	playersDF.loc[playersDF.plays == " Unknown", "plays"] = np.nan
	playersDF.weight = playersDF.weight.apply(cleanWeightOrHeight)
	playersDF.height = playersDF.height.apply(cleanWeightOrHeight)
	playersDF.age = playersDF.age.apply(getDob)
	playersDF = playersDF.rename(columns={"age": "dob"})
	playersDF["playername"] = playersDF.playername.apply(lambda x : (x.split(",")[1] + " " + x.split(",")[0]).strip())

	# Mise dans la table players de ce df 
	playersDF.to_sql('players', conn, if_exists="replace")
	return playersDF

def createRankingsTable(playersDF, rankingsFilePath, sqlConn) : 

	# Récupération des classements en DF 
	rankingsDF = pd.read_csv(rankingsFilePath, low_memory=False)
	rankingsDF = rankingsDF.drop(["Unnamed: 0", "link"], axis=1).set_index("playerName")

	# Mise sous forme database : nom,date,classement
	rankingsDF = rankingsDF.stack().reset_index()
	rankingsDF = rankingsDF.rename(columns={"level_1":"date", 0:"rAndP"})

	# Séparation rank, points et traitement date
	rankingsDF.date = rankingsDF.date.str.replace(".", "/")
	rankingsDF["rank"] = rankingsDF.rAndP.apply(lambda x :x.split("::")[0])
	rankingsDF["points"] = rankingsDF.rAndP.apply(lambda x :x.split("::")[1])
	rankingsDF = rankingsDF.drop("rAndP", axis=1)
	
	# Merge avec playersDF pour avoir les id
	playersDF["playerId"] = playersDF.index
	rankingsDF["playerName"] = rankingsDF.playerName.apply(lambda x : (x.split(",")[1] + " " + x.split(",")[0]).strip())
	idDF = playersDF[["playername", "playerId"]].rename(columns={"playername":"playerName"})
	rankingsDF = rankingsDF.merge(idDF).drop("playerName", axis=1)

	# Mise dans la table rankings de ce df 
	rankingsDF.to_sql('rankings', conn, if_exists="replace")
	return rankingsDF

def createMatchAndTournamentTables(matchesFilepath, playersDF, conn) :

	# Récupération des matches en DF
	matchsDF = pd.read_csv(matchesFilepath)

	# Travail sur la date pour la mettre au même format que les dob des players
	matchsDF.event_time = matchsDF.event_time.apply(lambda x : x.split(" ")[0])
	matchsDF.event_time = pd.to_datetime(matchsDF.event_time).apply(lambda x : x.strftime("%d/%m/%Y"))

	# Récupération des tournois en sql
	tournamentsDF = matchsDF[["event_time", "event_name", "surface"]].drop_duplicates()
	tournamentsDF.index = range(len(tournamentsDF))
	tournamentsDF.to_sql("tournaments", conn, if_exists="replace")

	# Jointure sur les tournois (pour les joueurs le nom fait office de jointure)
	tournamentsDF["idTournoi"] = tournamentsDF.index
	matchsDF = pd.merge(matchsDF, tournamentsDF)

	# Jointure sur les players
	playersDF["idPlayerA"] = playersDF.index
	playersDF = playersDF[["idPlayerA", "playername"]].rename(columns={"playername": "playerA"})
	matchsDF = pd.merge(matchsDF, playersDF, how="left")
	playersDF = playersDF.rename(columns={"idPlayerA":"idPlayerB", "playerA":"playerB"})
	matchsDF = pd.merge(matchsDF, playersDF, how="left")

	# Suppression des champs tournois et player devenus redondants et écriture de la table
	matchsDF.drop(["playerA", "playerB", "Unnamed: 0", "event_time", "event_name", "surface"], axis=1, inplace=True)
	matchsDF.to_sql("matchs", conn, if_exists="replace")

	return matchsDF, tournamentsDF


# Paramètres 
dbFilePath = "../Data/database.db"
playersInfoFilePath = "../Data/players_infos.csv"
rankingsFilePath = "../Data/rankings.csv"
matchesFilepath = "../Data/matchs.csv"

# Connexion à la base 
conn = sqlite3.connect(dbFilePath)
conn.text_factory = str

# Création des tables
playersDF = createPlayersTable(playersInfoFilePath, conn)
rankingsDF = createRankingsTable(playersDF, rankingsFilePath, conn)
matchesDF, tournamentsDF = createMatchAndTournamentTables(matchesFilepath, playersDF, conn)
