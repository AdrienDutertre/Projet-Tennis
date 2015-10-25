# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

import extendedSysPath
from config import Config as conf


class featuresExtractor():

	def __init__(self) : 

		self.basicPlayerFeatures = ['age','height','weight','plays','rank','turnedpro','imc']
		self.basicEventFeatures = ['surface','category','num_of_sets','round','event_week','event_year']


	def readData(self):
		
		self.dataDF = pd.read_csv(conf.preProcessedMatchsFilePath)
		return self

	
	def createBasicFeatures(self):
		
		# Uniformisation des rounds puis codage sous forme du nombre de matchs à remporter pour gagner le titre
		self.dataDF['round'] = self.dataDF['round'].replace(['Round Robin','Semi-Finals','Finals'],['Q','S','F'])
		self.dataDF['round'] = self.dataDF['round'].replace(['R128','R64','R32','R16','Q','S','F'],np.arange(7,0,-1))

		# Obtention du contexte temporel des matchs : année et semaine dans l'année
		self.dataDF['event_time'] = pd.to_datetime(self.dataDF['event_time'])
		self.dataDF['event_week'] = self.dataDF['event_time'].apply(lambda x : x.week)
		self.dataDF['event_year'] = self.dataDF['event_time'].apply(lambda x : x.year)

		# Features concernant les joueurs indépendamment l'un de l'autre
		for prefix in ['a','b']:

			# Age des joueurs au moment des matchs (en années)
			self.dataDF[prefix + '_age'] = self.dataDF[prefix + '_age'].apply(lambda x: x[-11:-1] if not pd.isnull(x) else x)
			self.dataDF[prefix + '_age'] =  pd.to_datetime(self.dataDF[prefix + '_age'],format='%d.%m.%Y')
			self.dataDF[prefix + '_age'] = (self.dataDF['event_time'] - self.dataDF[prefix + '_age']).astype('timedelta64[Y]') 

			# IMC des joueurs à partir de leur taille et poids
			self.dataDF[prefix + '_imc'] = self.dataDF[prefix + '_weight'].astype(float) / (self.dataDF[prefix + '_height'].astype(float)/100)**2

			# Main du joueur (droitier/gaucher/ambidextre/inconnu)
			self.dataDF[prefix + '_plays'] = self.dataDF[prefix + '_plays'].fillna(' Unknown')

			# Nombre d'années passées sur le circuit pro au moment des matchs
			self.dataDF[prefix + '_turned pro'] = self.dataDF[prefix + '_turned pro'].replace(0,np.nan)
			self.dataDF[prefix + '_turnedpro'] = self.dataDF['event_year'] - self.dataDF[prefix + '_turned pro']
			self.dataDF.drop([prefix + '_turned pro'],inplace=True,axis=1)

			# Cas des joueurs amateurs au moment du match mais devenus pro ensuite => 0 année d'ancienneté
			self.dataDF.loc[ self.dataDF[prefix + '_turnedpro'] < 1, prefix + '_turnedpro'] = 0
		
		return self


	def createStatisticalFeatures(self):
		return self

	
	def getAllFeatures(self):
		return self.dataDF

	
	def getBasicFeatures(self):
		
		basicPlayerFeatures = []
		for prefix in ['a','b']:
			for feature in self.basicPlayerFeatures :
				basicPlayerFeatures.append(prefix+'_'+feature)

		features = np.r_[basicPlayerFeatures,self.basicEventFeatures]
		return self.dataDF[features]

	
	def getLabel(self):
		return self.dataDF['winner']



if __name__ == '__main__':

	features =  featuresExtractor()
	features.readData()
	features.createBasicFeatures()
	featuresDF = features.getAllFeatures()
