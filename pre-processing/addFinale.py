# -*- coding: utf-8 -*-

"""

Created on Sun 1 mar 2015
    
@author: Ohayon

"""
import numpy as np
from pandas import Series, DataFrame
import pandas as pd 
import math

def arrangeData(df,df2):
	tempDf = df
	tempDf[u'event_name'] = tempDf.apply(lambda x: x['Location'] + x['Tournament'],axis=1)
	tempDf[u'event_time'] = tempDf['Date']
	tempDf[u'surface'] = tempDf['Surface']
	tempDf[u'num_of_sets'] = tempDf.apply(lambda x: int(x['Best of'])/2+1,axis=1)
	tempDf[u'playerA'] = tempDf.apply(lambda x:convertPlayerName(x["Winner"],df2),axis=1)
	tempDf[u'playerB'] = tempDf.apply(lambda x:convertPlayerName(x["Loser"],df2),axis=1)
	tempDf[u'winner'] = tempDf['playerA']
	tempDf[u'score'] = tempDf.apply(lambda x: convertScore(x),axis=1)
	tempDf[u'round'] = tempDf['Round']
	listOfEmpty = [u'duration_minutes', u'a_aces', u'a_double_faults', u'a_first_serve_hits', u'a_first_serve_total', u'a_first_serve_won', u'a_first_serve_played', u'a_second_serve_won', u'a_second_serve_played', u'a_break_points_saved', u'a_break_points_total', u'a_service_games', u'a_service_points_won', u'a_service_points_total', u'b_aces', u'b_double_faults', u'b_first_serve_hits', u'b_first_serve_total', u'b_first_serve_won', u'b_first_serve_played', u'b_second_serve_won', u'b_second_serve_played', u'b_break_points_saved', u'b_break_points_total', u'b_service_games', u'b_service_points_won', u'b_service_points_total']
	tempDf[listOfEmpty] = DataFrame(0,index=tempDf.index,columns=listOfEmpty)
	return tempDf[df2.columns]

def convertScore(line):
	score=""
	for i in range(1,6):
		if not math.isnan(float(line['W'+str(i)])): 
			score=score+str(int(line['W'+str(i)]))+"-"+str(int(line['L'+str(i)]))+"; "
	if line['Comment'] == "Completed":
		score = score[0:-2]
	else:
		score = score[0:-2] + " RET"
	return score

def convertPlayerName(name,df2):
	rName = name.split(" ")[0]
	if rName == "Del":
		rName= "Del Potro"
	if rName == "Ferrer":
		rName="David Ferrer"
	if rName == "Simon":
		rName="Gilles Simon"
	if rName == "Johansson":
		rName="Thomas Johansson"
	broadcast = [rName in pName for pName in df2['playerA']]
	realNames = df2[broadcast]['playerA'].unique()
	if len(realNames) == 1:
		realName = realNames[0]
	else:
		print ">>>>>>>>>>>ERROR   :    " + rName
	return realName

def addMastersCup():
	for year in range(2000,2015):
		#load Data
		data = pd.read_csv('Data/'+str(year)+'.csv')
		matchesData = pd.read_csv('Data/matches_data_file'+str(year)+'.csv')
		
		#find MasterCup
		mastersCup = data[data['Tournament']=='Masters Cup']

		#extract data
		matchesMastersCup = arrangeData(mastersCup,matchesData)
		n,p=matchesData.shape
		matchesMastersCup.reset_index(inplace=True)
		matchesMastersCup.drop('index',axis=1,inplace=True)
		matchesMastersCup.reset_index(inplace=True)
		matchesMastersCup['index'] = matchesMastersCup['index'] + n
		matchesMastersCup.set_index('index',inplace=True)

		matchesDataComplete = pd.concat([matchesData,matchesMastersCup])
		matchesDataComplete.to_csv('Data/matches_data_file'+str(year)+'c.csv')


