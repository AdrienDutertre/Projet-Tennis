# -*- coding: utf-8 -*-

import sqlite3 
import pandas as pd

# Paramètres du script 
dbFilename = "../Data/database.db"
playersCsvFilePath = "../Data/playersInfo.csv"

# Connexion à la base et récupération d'un curseur 
conn = sqlite3.connect(dbFilename)
cursor = conn.cursor()

# Création de la table des joueurs
query = """CREATE TABLE IF NOT EXISTS players(
	id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	age TEXT,
	birthplace TEXT,
	residence TEXT,
	height TEXT, 
	weight TEXT,
	plays TEXT,
	turned_pro TEXT,
	coach TEXT,
	country TEXT,
	name TEXT)"""
cursor.execute(query)
conn.commit()

# Insertion des données
playersDF = pd.read_csv(playersCsvFilePath)
playersDF.drop(["Unnamed: 0", "link"], axis=1, inplace=True)
playersDF.fillna(" ", inplace=True)
playersDF["Turned Pro"] = playersDF["Turned Pro"].astype(str) 
playersList = playersDF.values
playersListTuple = [ tuple(x) for x in playersList ]
queryMany = """INSERT INTO players (age, birthplace, residence, height, weight, plays, turned_pro, coach, country, name) 
			   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
conn.executemany(queryMany, playersListTuple)

# Fermeture de la connexion à la base
conn.commit()
conn.close()
