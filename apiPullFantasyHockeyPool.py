import base64
import requests
import pandas as pd
import numpy as np
import json
from pandas import json_normalize
import schedule
import time
from datetime import date

todayDate = date.today().strftime('%Y%m%d')
concateURL = str("https://api.mysportsfeeds.com/v2.1/pull/nhl/current/date/"+todayDate+"/player_gamelogs.json")
keyLoc = open('C:/Users/fortn/Documents/DataScience/Projects/fantasyHockeyPool/fantasyHockeyPool/key.txt','r')
key = str(keyLoc.readline())

def todayRequest():
    try:
        response = requests.get(
            url=concateURL,
            params={
                'stats':'points',
                'team':{'29,30,11,15,3,19,23,20,22,27,16,24,4,28,25,14,7,18,8,20,9,13,6,10,26,17,1,12,21,142,2,5'}
            },
            headers={
                "Authorization": "Basic " + base64.b64encode('{}:{}'.format(key,"MYSPORTSFEEDS").encode('utf-8')).decode('ascii')
            }
        )
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    return response.content

def pastRequest():
    try:
        response = requests.get(
            url="https://api.mysportsfeeds.com/v2.1/pull/nhl/current/player_gamelogs.json",
            params={
                'date':'since-20210419',
                'stats':'points',
                'team':{'29,30,11,15,3,19,23,20,22,27,16,24,4,28,25,14,7,18,8,20,9,13,6,10,26,17,1,12,21,142,2,5'}
            },
            headers={
                "Authorization": "Basic " + base64.b64encode('{}:{}'.format(key,"MYSPORTSFEEDS").encode('utf-8')).decode('ascii')
            }
        )
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    return response.content

def formatStats():
    pastPullData = pastRequest()
    pastPullData = json.loads(pastPullData)

    todayPullData = todayRequest()
    todayPullData = json.loads(todayPullData)

    pastList = []

    for i in range(0, len(pastPullData['gamelogs'])):
        playerTeam = pastPullData['gamelogs'][i]['team']['abbreviation']
        playerID = pastPullData['gamelogs'][i]['player']['id']
        playerFirstName = pastPullData['gamelogs'][i]['player']['firstName']
        playerLastName = pastPullData['gamelogs'][i]['player']['lastName']
        playerPoints = int(pastPullData['gamelogs'][i]['stats']['scoring']['points'])
        pastList.append([playerTeam, playerID, playerFirstName, playerLastName, playerPoints])

    pastColumns = ['Team','ID', 'FirstName', 'LastName', 'PastPoints']
    rawPastStatsDF = pd.DataFrame(data = pastList, columns = pastColumns)
    sendPastStatDF = rawPastStatsDF.groupby(['Team','ID','FirstName','LastName'], as_index = False).sum()
    countPastStatDF = rawPastStatsDF.groupby(['ID','FirstName','LastName'], as_index = False).count()
    sendPastStatDF.insert(loc = 4,column = 'PastGamesPlayed', value = countPastStatDF['PastPoints'])

    todayList = []

    for i in range(0, len(todayPullData['gamelogs'])):
        playerTeam = todayPullData['gamelogs'][i]['team']['abbreviation']
        playerID = todayPullData['gamelogs'][i]['player']['id']
        playerFirstName = todayPullData['gamelogs'][i]['player']['firstName']
        playerLastName = todayPullData['gamelogs'][i]['player']['lastName']
        playerPoints = int(todayPullData['gamelogs'][i]['stats']['scoring']['points'])
        todayList.append([playerTeam, playerID, playerFirstName, playerLastName, playerPoints])
        
    todayColumns = ['Team','ID', 'FirstName', 'LastName', 'TodayPoints']
    rawTodayStatsDF = pd.DataFrame(data = todayList, columns = todayColumns)
    sendTodayStatDF = rawTodayStatsDF.groupby(['Team','ID','FirstName','LastName'], as_index = False).sum()
    countTodayStatDF = rawTodayStatsDF.groupby(['ID','FirstName','LastName'], as_index = False).count()
    sendTodayStatDF.insert(loc = 4,column = 'TodayGamesPlayed', value = countTodayStatDF['TodayPoints'])

    sendStatDF = sendTodayStatDF.merge(sendPastStatDF, how = 'outer', on = ['Team','ID','FirstName','LastName'])
    sendStatDF.fillna(0, inplace = True)
    sendStatDF['GamesPlayed'] = sendStatDF.loc[:,['TodayGamesPlayed', 'PastGamesPlayed']].sum(axis=1)
    sendStatDF.drop(['TodayGamesPlayed', 'PastGamesPlayed'], axis = 1, inplace = True)
    sendStatDF['Points'] = sendStatDF.loc[:,['TodayPoints', 'PastPoints']].sum(axis=1)
    sendStatDF.drop(['TodayPoints', 'PastPoints'], axis = 1, inplace = True)

    sendStatDF.to_csv(
        r'C:\Users\fortn\Documents\Fantasy Hockey\2020-2021\Playoffs\playerStats.csv', 
        index = False)

schedule.every(60).seconds.do(formatStats)

while 1:
    schedule.run_pending()
    time.sleep(1)

