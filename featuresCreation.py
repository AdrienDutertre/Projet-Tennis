# -*- coding: utf-8 -*-

import pandas as pd 
import numpy as np 
import random
import re
import datetime


"""
	Test : retourne un dataframe de features basiques pour la régression logistique
 	Chaque ligne representera un match et contiendra les features suivantes :
 	[semaineAnnée, Extérieur, Surface, CatégorieTournoi, Nb sets gagnants, round, Classements J1 et J2, Vainqueur]
	La classe a prédire sera donc Winner qui vaudra 0 si J0 a gagné et 1 sinon 
"""
def getBasicsFeaturesFromDataFrame(dataframe) : 

	basicFeatures = dataframe[ ['Tournament', 'Location', 'Date', 'Series', 'Round', 'Surface', 'Court', 'J0Rank', 'J1Rank', 'Best of', 'Winner'] ].copy()
	
	# Petit travail sur les dates : on rajoute l'année du tournoi pour pouvoir les distinguer 
	basicFeatures.loc[:, 'Date'] = pd.Series( pd.to_datetime( basicFeatures.loc[:, 'Date'].values, dayfirst=True ) )
	basicFeatures['TournamentYear'] = basicFeatures['Date'].apply( lambda x : (x.to_datetime() + datetime.timedelta(days=15)).isocalendar()[0])
	
	# Feature 1 : La semaine du match
	basicFeatures.loc[:, 'Week'] = basicFeatures['Date'].apply( lambda x : x.to_datetime().isocalendar()[1] )

	# Features 2, 3 et 4 : Extérieur ou intérieur, rapidité de la surface et prestige du tournoi
	replaceDictionary = {   'Court': {'Indoor': '0', 'Outdoor': '1'},
							'Surface': {'Clay':'1', 'Hard':'2', 'Grass': '3'},
							'Series': {'ATP250': 1, 'ATP500': 2, 'Masters 1000': '3', 'Masters Cup': '4', 'Grand Slam': '5'}
						}

	basicFeatures.replace(to_replace=replaceDictionary, inplace=True, regex=True)

	# Feature 6 : Le nombre de tours restants à disputer pour remporter le titre 
	roundsSerie = basicFeatures.groupby(['Tournament', 'TournamentYear']).apply(getRemainingRounds)
	basicFeatures['RemainingRoundsToWinTournament'] = pd.concat( [roundsSerie.values[i] for i in range(len(roundsSerie.values))] )
	
	# Les features restantes sont déjà présentes telles quelles dans le dataframe initial
	columns = ['Week', 'Court', 'Surface', 'Series', 'Best of', 'RemainingRoundsToWinTournament', 'J0Rank', 'J1Rank', 'Winner']

	return basicFeatures[columns].astype(int)


# Prend en argument un groupe représentant les matchs pour un tournoi et retourne une série des tours restants
def getRemainingRounds(x) : 

	# On récupère la serie des rounds du groupe courant 
	roundsSerie = x['Round']

	# On sait déja q'une finale = 1 match a gagner pour remporter le titre, une demie 2 et un quart 3 
	replaceDictionary = {'The Final': '1', 'Semifinals': '2', 'Quarterfinals': '3', 'Round Robin': '3'}

	# Nombre de tours du tournoi 
	nbRounds = len(x['Round'].unique())

	# Si le tournoi fait moins de 3 rounds ou plus de 7 c'est q'il y a un pb...
	if( nbRounds < 3 or nbRounds > 7 ) : 
		print "Error " + str(nbRounds) + "rounds : " + str(x['Tournament'].tolist()[0]) + " " + str(x['TournamentYear'].tolist()[0])

	else :
		replaceDictionary['1st Round'] = str(nbRounds)
		replaceDictionary['2nd Round'] = str(nbRounds-1) 
		replaceDictionary['3rd Round'] = str(nbRounds-2)
		replaceDictionary['4th Round'] = str(nbRounds-3)

	roundsSerie.replace(to_replace=replaceDictionary, inplace=True)
	return roundsSerie.astype(int)


# Fonction permettant de transformer un string en int (utile pour éviter les warnings pandas sur read_csv mixed types)
def parseStringToInt(x) :

	x = x.replace('.0', '')
	x = re.sub(r'\D', '', x)
	if x :
		return int(x)
	else :
		return 0



rawDataFilePath = 'Data/allDataRandomized.csv'
featuresFilePath = 'basicFeatures.csv'

# Récupération des données brutes
print '\nRécupération des données brutes contenues dans : ' + rawDataFilePath
dtypes = {'J0Set1': np.int32, 'J1Set1': np.int32, 'J0Set2': np.int32, 'J1Set2': np.int32, 
		  'J0Set3': np.int32, 'J1Set3': np.int32, 'J0Set4': np.int32, 'J1Set4': np.int32,
		  'J0Set5': np.int32, 'J1Set5': np.int32, 'J0NbSets': np.int32, 'J1NbSets': np.int32} 
converters = {'J0Set1': parseStringToInt, 'J1Set1': parseStringToInt, 'J0Set2': parseStringToInt, 'J1Set2': parseStringToInt, 
		  'J0Set3': parseStringToInt, 'J1Set3': parseStringToInt, 'J0Set4': parseStringToInt, 'J1Set4': parseStringToInt,
		  'J0Set5': parseStringToInt, 'J1Set5': parseStringToInt, 'J0NbSets': parseStringToInt, 'J1NbSets': parseStringToInt} 
rawDataframe = pd.read_csv(rawDataFilePath, dtype=dtypes, converters=converters)

# Récupération des features basiques 
print '\nCalcul des features basiques pour tous les matchs'
featuresDataframe = getBasicsFeaturesFromDataFrame(rawDataframe)

# Ecriture du fichier contenant les features basiques
print '\nEcritures des features dans : ' + featuresFilePath
featuresDataframe.to_csv(featuresFilePath)


