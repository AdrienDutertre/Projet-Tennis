# -*- coding: utf-8 -*-

"""

Created on Sun 1 mar 2015
    
@author: Ohayon

"""

from pandas import Series, DataFrame
import pandas as pd 
import numpy as np

def findLink(line):
	if pd.isnull(line['link_x']):
		return line['link_y']
	else:
		return line['link_x']



data = pd.read_csv("tempRank/playerRanking0.csv")
data.rename(columns={'Unnamed: 0':'playerName'},inplace=True)

for i in range(1,124):
	data2 = pd.read_csv("tempRank/playerRanking"+str(i)+".csv")
	data2.rename(columns={'Unnamed: 0':'playerName'},inplace=True)
	data = data.merge(data2,on='playerName',how='outer')
	data['link'] = data.apply(lambda x : findLink(x),axis=1)
	data.drop(['link_x','link_y'],inplace=True,axis=1)

data.to_csv('Data/playersRank.csv')