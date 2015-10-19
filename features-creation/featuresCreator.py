# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

import extendedSysPath
from config import Config as conf

class featuresExtractor():

	# def __init__()

	def readData(self):
		self.dataDF = pd.read_csv(conf.preProcessedMatchsFilePath)
		return self

	def createBasicFeatures(self):
		
		# clean rounds
		self.dataDF['round'] = self.dataDF['round'].replace(['Round Robin','Semi-Finals','Finals'],['Q','S','F'])
		self.dataDF['round'] = self.dataDF['round'].replace(['R128','R64','R32','R16','Q','S','F'],np.arange(7,0,-1))

		# convert to timestamps
		self.dataDF['event_time'] = pd.to_datetime(self.dataDF['event_time'])

		# create week
		self.dataDF['event_week'] = self.dataDF['event_time'].apply(lambda x : x.week)

		# create year
		self.dataDF['event_year'] = self.dataDF['event_time'].apply(lambda x : x.year)


		# for player a and b
		for prefix in ['a','b']:

			# create age 
			self.dataDF[prefix + '_age'] = self.dataDF[prefix + '_age'].apply(lambda x: x[-11:-1] if not pd.isnull(x) else x)
			self.dataDF[prefix + '_age'] =  pd.to_datetime(self.dataDF[prefix + '_age'],format='%d.%m.%Y')
			self.dataDF[prefix + '_age'] = (self.dataDF['event_time'] - self.dataDF[prefix + '_age']).astype('timedelta64[Y]') 


			# create imc 
			self.dataDF[prefix + '_imc'] = self.dataDF[prefix + '_weight'].astype(float) / (self.dataDF[prefix + '_height'].astype(float)/100)**2

			# clean hand
			self.dataDF[prefix + '_plays'] = self.dataDF[prefix + '_plays'].fillna(' Unknown')

			# turned pro
			self.dataDF[prefix + '_turned pro'] = self.dataDF[prefix + '_turned pro'].replace(0,np.nan)
			self.dataDF[prefix + '_turnedpro'] = self.dataDF['event_year'] - self.dataDF[prefix + '_turned pro']
			self.dataDF.drop([prefix + '_turned pro'],inplace=True,axis=1)
			self.dataDF[prefix + '_turnedpro'][self.dataDF[prefix + '_turnedpro'] < 1] = 0
		return self


	def createStatisticalFeatures(self):
		return self



	def getAllFeatures(self):
		return self.dataDF

	def getBasicFeatures(self):
		basicPlayerFeatures = []
		for prefix in ['a','b']:
			for feat in ['age','height','weight','plays','rank','turnedpro','imc']:
				basicPlayerFeatures.append(prefix+'_'+feat)

		basicEventFeatures = ['surface','category','num_of_sets','round','event_week','event_year']

		features = np.r_[basicPlayerFeatures,basicEventFeatures]
		return self.dataDF[features]

	def getLabel(self):
		return self.dataDF['winner']



if __name__ == '__main__':

	features =  featuresExtractor()
	features.readData()
	features.createBasicFeatures()
	featuresDF = features.getFeatures()




