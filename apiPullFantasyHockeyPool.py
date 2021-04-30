# Import relevant packages
import base64
import requests
import pandas as pd
import numpy as np
import json
from pandas import json_normalize
import schedule
import time
from datetime import date

# store today's date in a variable for the api pull url
todayDate = date.today().strftime('%Y%m%d')
# concat today's date into api pull url
concateURL = str("https://api.mysportsfeeds.com/v2.1/pull/nhl/current/date/"+todayDate+"/player_gamelogs.json")
# store private authentication key from local .txt
keyLoc = open('C:/Users/fortn/Documents/DataScience/Projects/fantasyHockeyPool/fantasyHockeyPool/key.txt','r')
key = str(keyLoc.readline())

# we want our stats to live update every ~1 minute but the cumulative stats only update once per day
# to work around that we will load todays stats as well as the cumulative stats and add them together 

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
                'team':{'29,30,11,15,3,19,23,20,22,27,16,24,4,28,25,14,7,18,8,20,9,13,6,10,26,17,1,12,21,142,2,5'}
            },
            # authentication using stored key variable
            headers={
                "Authorization": "Basic " + base64.b64encode('{}:{}'.format(key,"MYSPORTSFEEDS").encode('utf-8')).decode('ascii')
            }
        )
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    return response.content

# function to pull cumulative stats updated once a day at ~10pm PST
def pastRequest():
    try:
        response = requests.get(
            # api url for cumulative game logs
            url="https://api.mysportsfeeds.com/v2.1/pull/nhl/current/player_gamelogs.json",
            # specific data to pull
            params={
                # start date of the pool (can be a date range or an entire season if required)
                'date':'since-20210419',
                'stats':'points',
                # all teams are being pulled
                'team':{'29,30,11,15,3,19,23,20,22,27,16,24,4,28,25,14,7,18,8,20,9,13,6,10,26,17,1,12,21,142,2,5'}
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
    # call cumulative data and load the json into a dict format
    pastPullData = pastRequest()
    pastPullData = json.loads(pastPullData)

    # call today's data and load the json into a dict format
    todayPullData = todayRequest()
    todayPullData = json.loads(todayPullData)

    # empty list to append desired cumulative data into
    pastList = []

    # loop to grab and append desired data from each gamelog since there are more stats avaialble than we actually want
    # there is a gamelog for each player for each game within the date range specified in the api pull
    # desired stats are: team, player id, player first name, player last name, player points
    for i in range(0, len(pastPullData['gamelogs'])):
        playerTeam = pastPullData['gamelogs'][i]['team']['abbreviation']
        playerID = pastPullData['gamelogs'][i]['player']['id']        
        playerFirstName = pastPullData['gamelogs'][i]['player']['firstName']
        playerLastName = pastPullData['gamelogs'][i]['player']['lastName']
        playerPoints = int(pastPullData['gamelogs'][i]['stats']['scoring']['points'])
        pastList.append([playerTeam, playerID, playerFirstName, playerLastName, playerPoints])

    # build dataframe from the desired cumulative data
    # set dataframe column names
    pastColumns = ['Team','ID', 'FirstName', 'LastName', 'PastPoints']
    # create dataframe from set columns and appended list
    rawPastStatsDF = pd.DataFrame(data = pastList, columns = pastColumns)
    # since there are multiple gamelogs for a single player (from multiple games) the points must be summed tog et the total points
    sendPastStatDF = rawPastStatsDF.groupby(['Team','ID','FirstName','LastName'], as_index = False).sum()
    # temp dataframe to count the number of gamelogs belonging to each player to calculate the games played
    countPastStatDF = rawPastStatsDF.groupby(['ID','FirstName','LastName'], as_index = False).count()
    # insert games played into the points dataframe
    sendPastStatDF.insert(loc = 4,column = 'PastGamesPlayed', value = countPastStatDF['PastPoints'])

    # empty list to append desired today's data into
    todayList = []

    # loop to grab and append desired data from each gamelog since there are more stats avaialble than we actually want
    # there is a gamelog for each player who has participated in a game that has started
    # desired stats are: team, player id, player first name, player last name, player points
    for i in range(0, len(todayPullData['gamelogs'])):
        playerTeam = todayPullData['gamelogs'][i]['team']['abbreviation']
        playerID = todayPullData['gamelogs'][i]['player']['id']
        playerFirstName = todayPullData['gamelogs'][i]['player']['firstName']
        playerLastName = todayPullData['gamelogs'][i]['player']['lastName']
        playerPoints = int(todayPullData['gamelogs'][i]['stats']['scoring']['points'])
        todayList.append([playerTeam, playerID, playerFirstName, playerLastName, playerPoints])
        
    # build dataframe from the desired today's data
    # set dataframe column names
    todayColumns = ['Team','ID', 'FirstName', 'LastName', 'TodayPoints']
    # create dataframe from set columns and appended list
    rawTodayStatsDF = pd.DataFrame(data = todayList, columns = todayColumns)
    # since there are multiple gamelogs for a single player (from multiple games) the points must be summed tog et the total points
    sendTodayStatDF = rawTodayStatsDF.groupby(['Team','ID','FirstName','LastName'], as_index = False).sum()
    # temp dataframe to count the number of gamelogs belonging to each player to calculate the games played
    countTodayStatDF = rawTodayStatsDF.groupby(['ID','FirstName','LastName'], as_index = False).count()
    # insert games played into the points dataframe
    sendTodayStatDF.insert(loc = 4,column = 'TodayGamesPlayed', value = countTodayStatDF['TodayPoints'])

    # merge our cumulative and today dataframes into a final dataframe
    # outer join is used since the today dataframe does not contain players who had an off day
    sendStatDF = sendTodayStatDF.merge(sendPastStatDF, how = 'outer', on = ['Team','ID','FirstName','LastName'])
    # fill NaN values created from outter join with 0, players on an off day had 0 points today
    sendStatDF.fillna(0, inplace = True)
    # creating a new column for total games played and dropping the individual games played columns
    sendStatDF['GamesPlayed'] = sendStatDF.loc[:,['TodayGamesPlayed', 'PastGamesPlayed']].sum(axis=1)
    sendStatDF.drop(['TodayGamesPlayed', 'PastGamesPlayed'], axis = 1, inplace = True)
    # creating new column for total points and dropping the individual points columns
    sendStatDF['Points'] = sendStatDF.loc[:,['TodayPoints', 'PastPoints']].sum(axis=1)
    sendStatDF.drop(['TodayPoints', 'PastPoints'], axis = 1, inplace = True)
    # changing the team abbreviations for florida and winnipeg
    sendStatDF['Team'].replace({'FLO':'FLA', 'WPJ':'WPG'}, inplace = True)

    # save the fully formatted dataframe to a .csv
    sendStatDF.to_csv(
        r'C:\Users\fortn\Documents\Fantasy Hockey\2020-2021\Playoffs\playerStats.csv', 
        index = False)

# call formatStats function every 60 seconds
schedule.every(60).seconds.do(formatStats)

while 1:
    schedule.run_pending()
    time.sleep(1)

