# -*- coding: utf-8 -*-

import pandas as pd 
import numpy as np 
import random
import re


# Fonction retournant la concaténation de tous les matchs pour les années demandées 
def getAllMatchsForASpecificPeriod(years) : 

	listOfYearMatchs = []
	commonColumns = ['ATP', 'Location', 'Tournament', 'Date', 'Series', 'Court', 'Surface', 'Round', 'Best of', 'Winner', 'Loser', 'WRank', 'LRank', 'W1', 'L1', 'W2', 'L2', 'W3', 'L3', 'W4', 'L4', 'W5', 'L5', 'Wsets', 'Lsets', 'Comment']

	# Boucle sur toutes les années spécifiées en argument de la fonction 
	for year in years : 

		# Récupération des données brutes de l'année correspondante
		currentYearRawDf = pd.read_csv('Data/' + str(year) + '.csv')

		# On ne garde que les colonnes qui sont communes à tous les csv 
		listOfYearMatchs.append( currentYearRawDf[commonColumns] )

	# On retourne la concaténation de toutes ces données 
	return pd.concat(listOfYearMatchs, ignore_index=True)


# Uniformise les données
def standardizeDataFrame(dataframe) :

	# Liste des remplacements sur chaque colonne 
	standardizationDict = {'Surface': {'Carpet': 'Hard'},
						   'Series': {'International Gold': 'ATP500', 'International Series': 'ATP250', 'International': 'ATP250', 'Masters': 'Masters 1000' },
						   'Winner': {r'\s$': ''},
						   'Loser': {r'\s$': ''} }

	dataframe.replace(to_replace=standardizationDict, inplace=True, regex=True)
	
	return dataframe 


# Randomise la base : Remplacement de Winner et Loser par J0 et J1 et ajout d'une classe Winner qui vaudra 0 ou 1 
def randomizeDataFrame(dataframe) :

	# Création d'un vecteur valant aléatoirement 0 (qui signifiera victoire J0) ou 1 (victoire J1) 
	winnerPlayer = [ random.choice([0, 1]) for i in range(0, len(dataframe.index)) ]
	randomVector = [ bool(player) for player in winnerPlayer ]

	# Nouvelles colonnes (pour l'instant J0 remplace le winner et J1 le loser)
	newColumns = ['ATP', 'Location', 'Tournament', 'Date', 'Series', 'Court', 'Surface', 'Round', 'Best of', 'J0', 'J1', 'J0Rank', 'J1Rank', 'J0Set1', 'J1Set1', 'J0Set2', 'J1Set2', 'J0Set3', 'J1Set3', 'J0Set4', 'J1Set4', 'J0Set5', 'J1Set5', 'J0NbSets', 'J1NbSets', 'Comment']
	dataframe.columns = newColumns

	# Permutation de J0 et J1 quand random vector vaut True (=> winnerPlayer = 1 et donc on veut J1 gagne)
	columnsInInitialOrder = ['J0', 'J1', 'J0Rank', 'J1Rank', 'J0Set1', 'J1Set1', 'J0Set2', 'J1Set2', 'J0Set3', 'J1Set3', 'J0Set4', 'J1Set4', 'J0Set5', 'J1Set5', 'J0NbSets', 'J1NbSets']
	columnsInPermutedOrder = ['J1', 'J0', 'J1Rank', 'J0Rank', 'J1Set1', 'J0Set1', 'J1Set2', 'J0Set2', 'J1Set3', 'J0Set3', 'J1Set4', 'J0Set4', 'J1Set5', 'J0Set5', 'J1NbSets', 'J0NbSets']
	dataframe.loc[randomVector, columnsInInitialOrder] = dataframe.loc[randomVector, columnsInPermutedOrder].values 

	# Enfin il ne reste plus qu'à ajouter une colonne indiquant le joueur gagnant qui sera winnerPlayer
	dataframe['Winner'] = pd.Series(winnerPlayer)

	return dataframe

# Test : retourne un dataframe de features basiques 
def getBasicsFeatures(row) : 

	return row[ ['J0', 'J1'] ]
	

"""
	Test : retourne un dataframe de features basiques pour la régression logistique
 	Chaque ligne representera un match et contiendra les features suivantes :
 	[semaineAnnée, Surface, CatégorieTournoi, ClassementJ1, ClassementJ2, Nombre de sets gagnants]
	La classe a prédire sera donc Winner qui vaudra 0 si J0 a gagné et 1 sinon 
"""
def getBasicsFeaturesFromDataFrame(dataframe) : 

	basicFeatures = dataframe[ ['Date', 'Series', 'Round', 'Surface', 'Court', 'J0Rank', 'J1Rank', 'Best of', 'Winner'] ]
	basicFeatures.loc[:, 'Date'] = pd.Series( pd.to_datetime( basicFeatures.loc[:, 'Date'].values, dayfirst=True ) )
	basicFeatures.loc[:, 'Date'] = basicFeatures['Date'].apply( lambda x : x.to_datetime().isocalendar()[1] )

	return basicFeatures


startingYear = 2000
endingYear = 2014
normalizedMatchsFile = "Data/allData.csv"
normalizedAndRandomizedMatchsFile = "Data/allDataRandomized.csv"

print "\nConcaténation de tous les matchs de " + str(startingYear) + " à " + str(endingYear)
testData = getAllMatchsForASpecificPeriod( range(startingYear, endingYear+1) )

print "\nNormalisation des matchs"
testData = standardizeDataFrame(testData)

print "\nEcriture du fichier contenant tous les matchs de " + str(startingYear) + " à " + str(endingYear) + " : " + normalizedMatchsFile
testData.to_csv(normalizedMatchsFile)

print "\nRandomisation des matchs"
testData = randomizeDataFrame(testData)

print "\nEcriture du fichier contenant tous les matchs randomisés de " + str(startingYear) + " à " + str(endingYear) + " : " + normalizedAndRandomizedMatchsFile
testData.to_csv(normalizedAndRandomizedMatchsFile)

### TEST DES FEATURES BASIQUES : Développement en cours => Ne fonctionne pas encore...
#test = getBasicsFeaturesFromDataFrame(testData)
#print test
###
