# Import relevant packages
import base64
import requests
import pandas as pd
import numpy as np
import json
from pandas import json_normalize
import schedule
import time
import datetime
from datetime import date
import os

# store today's date in a variable for the api pull url
todayDate = date.today().strftime('%Y%m%d')
# concat today's date into api pull url
concateURL = str("https://api.mysportsfeeds.com/v2.1/pull/nhl/2021-2022-regular/date/"+todayDate+"/player_gamelogs.json")
# store private authentication key from environment files
key = str(os.environ.get('fantasyPoolApiKey'))

# we want our stats to live update every ~1 minute but the cumulative stats only update once per day
# to work around that we will load todays stats as well as the cumulative stats and add them together 

# function to pull today's stats updated every ~1 minute
# function to pull today's stats updated every ~1 minute
def todayRequest():
    try:
        response = requests.get(
            # api url for todays game logs
            url = concateURL,
            # specifc data to pull
            params={
                'stats':'points',
                # all teams are being pulled
                "team":{'tor,col,flo,dal,wsh,pit,car,bos,edm,tbl,min,nsh,nyr,cgy,lak,stl'}
            },
            # authentication using stored key variable
            headers={
                "Authorization": "Basic " + base64.b64encode('{}:{}'.format(key,"MYSPORTSFEEDS").encode('utf-8')).decode('ascii')
            }
        )
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    return response.content

# function to call api pull functions and format the pulled data
def formatStats():
    # call today's data and load the json into a dict format
    todayPullData = todayRequest()
    todayPullData = json.loads(todayPullData)

    # empty list to append desired today's data into
    todayList = []

    # loop to grab and append desired data from each gamelog since there are more stats avaialble than we actually want
    # there is a gamelog for each player who has participated in a game that has started
    # desired stats are: team, player id, player first name, player last name, player points
    for i in range(0, len(todayPullData['gamelogs'])):
        gameID = todayPullData['gamelogs'][i]['game']['id']
        playerTeam = todayPullData['gamelogs'][i]['team']['abbreviation']
        playerID = todayPullData['gamelogs'][i]['player']['id']
        playerFirstName = todayPullData['gamelogs'][i]['player']['firstName']
        playerLastName = todayPullData['gamelogs'][i]['player']['lastName'] 
        playerPoints = int(todayPullData['gamelogs'][i]['stats']['scoring']['points'])
        todayList.append([gameID, playerTeam, playerID, playerFirstName, playerLastName, playerPoints])
        
    # build dataframe from the desired today's data
    # set dataframe column names
    todayColumns = ['GameID','Team','ID', 'FirstName', 'LastName', 'TodayPoints']
    # create dataframe from set columns and appended list
    rawTodayStatsDF = pd.DataFrame(data = todayList, columns = todayColumns)
    # since there are multiple gamelogs for a single player (from multiple games) the points must be summed tog et the total points
    sendTodayStatDF = rawTodayStatsDF.groupby(['GameID','Team','ID','FirstName','LastName'], as_index = False).sum()
    # temp dataframe to count the number of gamelogs belonging to each player to calculate the games played
    countTodayStatDF = rawTodayStatsDF.groupby(['GameID','Team','ID','FirstName','LastName'], as_index = False).count()
    # insert games played into the points dataframe
    sendTodayStatDF.insert(loc = 5,column = 'TodayGamesPlayed', value = countTodayStatDF['TodayPoints'])

    # fill NaN values created from outter join with 0, players on an off day had 0 points today
    sendTodayStatDF.fillna(0, inplace = True)
    sendTodayStatDF = sendTodayStatDF.rename(columns = {'TodayGamesPlayed':'GamesPlayed'})
    sendTodayStatDF = sendTodayStatDF.rename(columns = {'TodayPoints':'Points'})
    # changing the team abbreviations for florida and winnipeg
    sendTodayStatDF['Team'].replace({'FLO':'FLA'}, inplace = True)
    # drop the Sam Bennet entry for calgary that hasn't been removed from the API
    # sendStatDF = sendStatDF.drop(sendStatDF[(sendStatDF['Team'] == 'CGY') & (sendStatDF['ID'] == 5415)].index)

    if os.path.exists('playerStatsTotal.csv') == True:
        sendStatDF = pd.read_csv('playerStatsTotal.csv')
        sendStatDF = pd.concat([sendStatDF,sendTodayStatDF])
        sendStatDF = sendStatDF.drop_duplicates(subset = ['GameID','ID'], keep = 'last')
    else:
        sendStatDF = sendTodayStatDF.copy()
        
    sendStatDF.to_csv(
        'playerStatsTotal.csv', 
        index = False)
    
    return sendStatDF

def buildAgg():
    totalStats = formatStats()
    
    aggStats = totalStats.copy()
    aggStats = aggStats.drop(columns = 'GameID', axis  = 1)
    aggStats = aggStats.groupby(['Team','ID','FirstName','LastName'], as_index = False).sum()
    # save the fully formatted dataframe to a .csv
    aggStats.to_csv(
        'playerStatsAgg.csv', 
        index = False)

    return aggStats, totalStats

#aggStats, totalStats = buildAgg()

# call buildAgg function every 60 seconds
schedule.every(60).seconds.do(buildAgg)

while 1:
    schedule.run_pending()
    time.sleep(1)