# -*- coding: utf-8 -*-

import os

class Config : 

	""" 
	Général 
	"""

	configDir = os.path.dirname(__file__)
	dataDir = os.path.join(configDir, "..", "Data")
	
	""" 
	Pré-processing 
	"""
	preProcessedMatchsFilename = "matchs.csv"
	preProcessedMatchsFilePath = os.path.join(dataDir, preProcessedMatchsFilename)
	preProcessedPlayersFilename = "players.csv"
	preProcessedPlayersFilePath = os.path.join(dataDir, preProcessedPlayersFilename)
	preProcessedRankingsFilename = "rankings.csv"
	preProcessedRankingsFilePath = os.path.join(dataDir, preProcessedRankingsFilename)
	atpUrl = "http://www.atpworldtour.com"
	atpRankingsUrl = "http://www.atpworldtour.com/Rankings/Singles.aspx"

	