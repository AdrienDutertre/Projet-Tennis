# -*- coding: utf-8 -*-

import requests
import html5lib
import unicodedata as uni
from bs4 import BeautifulSoup
import json
import re
from pandas import Series, DataFrame
import pandas as pd 
import numpy as np
import time
import extendedSysPath
from config import Config as conf

################################################################################################
# Some String manipulation functions

def normalize(string):
    return uni.normalize('NFKD',string).encode('ascii','ignore')


################################################################################################
# Returns a soup object from a given url

def getSoupFromUrl(url):
    result = requests.get(url)
    
    if result.status_code == 200:
        return BeautifulSoup(result.text,"html5lib")
    
    else:
        print 'Request failed', url
        return None


#################################################################################################
#                                                                                               #
"""                                      ATP World Tour                                       """
#                                                                                               #
#################################################################################################

##############################################################################################

# some int fields are completed with string "None" replace with 0
def atp_int(string):
	try:
		return int(string)
	except:
		return 0


def extractTournamentInfo(year):
	soup = getSoupFromUrl("http://www.atpworldtour.com/en/scores/archive/barclays-atp-world-tour-finals/605/"+str(year)+"/results")
	table = soup.find("div", id="scoresResultsContent")
	tableSplit = table.find_all("tbody")
	results = []
	cleaner = re.compile("[\n\t]")

	#get info for all matches
	for rounds in tableSplit: 
		for match in rounds.find_all("tr"):
			results.append(extractMatchInfo(match,year))


	# correct some mistake in the info
	correct_event_name = soup.find("td", class_="title-content").find("a").text + " " + cleaner.sub("", soup.find("td", class_="title-content").find_all("span")[0].text)
	
	time_tmp = time.strptime(cleaner.sub("", soup.find("td", class_="title-content").find_all("span")[1].text).split(" - ")[0], "%Y.%m.%d")
	correct_event_date = time.strftime("%Y-%m-%d %H:%M:%S.000",time_tmp)
	correct_results = []

	for match in results:

		match['event_name'] = correct_event_name
		match['event_time'] = correct_event_date
		if match['round'] == 'Finals' and year <= 2007: 
			match['num_of_sets'] = 3
		else: 
			match['num_of_sets'] = 2
		correct_results.append(match)

	return correct_results


def extractMatchInfo(match,year):
	
	result = {}
	
	cleaner = re.compile("[\n\t]")

	# find the names and id for stats
	names = match.find_all("td", class_="day-table-name")
	result["playerA"] = cleaner.sub("",names[0].text)
	winnerUrl = names[0].find('a')['href']
	result["playerB"] = cleaner.sub("",names[1].text)

	idFinder = re.compile(r"/([a-zA-Z0-9]{4})/")
	loserId = idFinder.findall(names[1].find('a')['href'])[0]
	result["winner"] = result["playerA"]

	# find the score and format it
	tmp = cleaner.sub("",match.find("td", class_="day-table-score").text).split()
	for i in range(len(tmp)):
		if len(tmp[i]) == 3:
			tmp[i] = tmp[i][0] + "-" + tmp[i][1] +"(" + tmp[i][2] + ")"
		elif len(tmp[i]) == 2:
			tmp[i] = tmp[i][0] + "-" + tmp[i][1]
	result["score"] = "; ".join(tmp)


	# get the url for stats
	stats = getSoupFromUrl("http://www.atpworldtour.com"+ winnerUrl + "/match-stats/605/"+str(year)+"/"+loserId+"/match-stats")
	
	result['event_name'] = cleaner.sub("",stats.find("h3",class_="section-title").text)
	
	result['surface'] = cleaner.sub("",stats.find("div",class_="modal-scores-header-info").find_all("div")[1].find('span',class_="score-value").text).upper()
	
	result['event_time'] = cleaner.sub("",stats.find("div",class_="modal-scores-header-info").find_all("div")[3].text)
	
	result['round'] = cleaner.sub("",stats.find("td", class_="title-area").text)
	
	# load a json of all the stats coded in hard inside the page
	
	try:
		data = json.loads(cleaner.sub("",stats.find("script", id="matchStatsData").text))

		timesplit = data[0]['playerStats']['Time'].split(":")

		result['duration_minutes'] = atp_int(timesplit[0])*60 + atp_int(timesplit[1])

		result['a_aces'] = atp_int(data[0]['playerStats']['Aces'])

		result['a_double_faults'] = atp_int(data[0]['playerStats']['DoubleFaults'])

		result['a_first_serve_won'] = atp_int(data[0]['playerStats']['FirstServePointsWon'])

		result['a_first_serve_played'] = atp_int(data[0]['playerStats']['FirstServePointsPlayed'])

		result['a_first_serve_hits'] = atp_int(data[0]['playerStats']['FirstServePointsPlayed'])

		result['a_second_serve_won'] = atp_int(data[0]['playerStats']['SecondServePointsWon'])

		result['a_second_serve_played'] = atp_int(data[0]['playerStats']['SecondServePointsPlayed'])

		result['a_first_serve_total'] = atp_int(data[0]['playerStats']['TotalServicePointsWonPercentageDivisor'])

		result['a_break_points_saved'] = atp_int(data[0]['playerStats']['BreakPointsSavedPercentageDividend'])

		result['a_break_points_total'] = atp_int(data[0]['playerStats']['BreakPointsFacedServing'])

		result['a_service_games'] = atp_int(data[0]['playerStats']['ServiceGamesPlayed'])

		result['a_service_points_won'] = atp_int(data[0]['playerStats']['TotalServicePointsWonPercentageDividend'])

		result['a_service_points_total'] = atp_int(data[0]['playerStats']['TotalServicePointsWonPercentageDivisor'])

		result['b_aces'] = atp_int(data[0]['opponentStats']['Aces'])

		result['b_double_faults'] = atp_int(data[0]['opponentStats']['DoubleFaults'])

		result['b_first_serve_won'] = atp_int(data[0]['opponentStats']['FirstServePointsWon'])

		result['b_first_serve_played'] = atp_int(data[0]['opponentStats']['FirstServePointsPlayed'])

		result['b_first_serve_hits'] = atp_int(data[0]['opponentStats']['FirstServePointsPlayed'])

		result['b_second_serve_won'] = atp_int(data[0]['opponentStats']['SecondServePointsWon'])

		result['b_second_serve_played'] = atp_int(data[0]['opponentStats']['SecondServePointsPlayed'])

		result['b_first_serve_total'] = atp_int(data[0]['opponentStats']['TotalServicePointsWonPercentageDivisor'])

		result['b_break_points_saved'] = atp_int(data[0]['opponentStats']['BreakPointsSavedPercentageDividend'])

		result['b_break_points_total'] = atp_int(data[0]['opponentStats']['BreakPointsFacedServing'])

		result['b_service_games'] = atp_int(data[0]['opponentStats']['ServiceGamesPlayed'])

		result['b_service_points_won'] = atp_int(data[0]['opponentStats']['TotalServicePointsWonPercentageDividend'])

		result['b_service_points_total'] = atp_int(data[0]['opponentStats']['TotalServicePointsWonPercentageDivisor'])

		#print "match crawled"

	except:

		print "fatal error in json format in : http://www.atpworldtour.com"+ winnerUrl + "/match-stats/605/"+str(year)+"/"+loserId+"/match-stats"

	return result


if __name__ == '__main__':

	for year in range(1991,2015):

		print "crawling year " + str(year)

		#extract the data
		results = extractTournamentInfo(year)
		data = pd.read_csv(conf.dataDir + "/matches_data_file"+str(year)+".csv")

		#format it
		add = pd.DataFrame(results)
		add = add.reindex(index=add.index[::-1]).reset_index(drop=True)
		add.index = add.index + data.shape[0]

		#merge and save
		newData = pd.concat([data,add])
		# SAVE IN A COMPLETED VERSION DO NOT OVERWRITE ORIGINAL DATA
		newData.to_csv(conf.dataDir + "/matches_data_file"+str(year)+"completed.csv",index=False)



