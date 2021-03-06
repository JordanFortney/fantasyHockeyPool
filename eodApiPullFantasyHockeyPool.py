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
import os

# store private authentication key from environment files
key = str(os.environ.get('fantasyPoolApiKey'))

# once the cumulative stats ''finally'' update at ~10pm PST today's stats are no longer needed
# in fact they are being double counted so an End Of Day update needs to be run once

# function to pull cumulative stats updated once a day at ~10pm PST
def pastRequest():
    try:
        response = requests.get(
            # api url for cumulative game logs
            url="https://api.mysportsfeeds.com/v2.1/pull/nhl/2021-playoff/player_gamelogs.json",
            # specific data to pull
            params={
                # start date of the pool (can be a date range or an entire season if required)
                # the data parameter (line 29) should be deleted once the NHL playoffs officially begin
                #'date':'from-20210419-to-today',
                #'date':'until-20210706',
                "stats":"points",
                # all teams are being pulled
                "team":{'tor,col,flo,vgk,wsh,pit,car,bos,edm,tbl,min,nsh,nyi,mtl,wpj,stl'}
            },
            # authentication using stored key variable
            headers={
                "Authorization": "Basic " + base64.b64encode('{}:{}'.format(key,"MYSPORTSFEEDS").encode('utf-8')).decode('ascii')
            }
        )
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    return response.content

def formatStats():
    # call cumulative data and load the json into a dict format
    eodPullData = pastRequest()
    eodPullData = json.loads(eodPullData)
    # empty list to append desired cumulative data into
    eodList = []

    # loop to grab and append desired data from each gamelog since there are more stats available than we actually want
    # there is a gamelog for each player for each game within the date range specified in the api pull
    # desired stats are: team, player id, player first name, player last name, player points
    for i in range(0, len(eodPullData['gamelogs'])):
        playerTeam = eodPullData['gamelogs'][i]['team']['abbreviation']
        playerID = eodPullData['gamelogs'][i]['player']['id']
        playerFirstName = eodPullData['gamelogs'][i]['player']['firstName']
        playerLastName = eodPullData['gamelogs'][i]['player']['lastName']
        playerPoints = int(eodPullData['gamelogs'][i]['stats']['scoring']['points'])
        eodList.append([playerTeam, playerID, playerFirstName, playerLastName, playerPoints])

    # build dataframe from the desired cumulative data
    # set dataframe column names
    eodColumns = ['Team','ID', 'FirstName', 'LastName', 'Points']
    # create dataframe from set columns and appended list
    rawPastStatsDF = pd.DataFrame(data = eodList, columns = eodColumns)
    # since there are multiple gamelogs for a single player (from multiple games) the points must be summed tog et the total points
    sendEodStatDF = rawPastStatsDF.groupby(['Team','ID','FirstName','LastName'], as_index = False).sum()
    # temp dataframe to count the number of gamelogs belonging to each player to calculate the games played
    countEodStatDF = rawPastStatsDF.groupby(['Team','ID','FirstName','LastName'], as_index = False).count()
    # insert games played into the points dataframe
    sendEodStatDF.insert(loc = 4,column = 'GamesPlayed', value = countEodStatDF['Points'])
    # fill any NaN values with a 0
    sendEodStatDF.fillna(0, inplace = True)
    # changing the team abbreviations for florida and winnipeg
    sendEodStatDF['Team'].replace({'FLO':'FLA', 'WPJ':'WPG'}, inplace = True)
    # drop the Sam Bennet entry for calgary that hasn't been removed from the API
    sendEodStatDF = sendEodStatDF.drop(sendEodStatDF[(sendEodStatDF['Team'] == 'CGY') & (sendEodStatDF['ID'] == 5415)].index)

    # save the fully formatted dataframe to a .csv
    sendEodStatDF.to_csv(
        'playerStats.csv', 
        index = False)    
        
formatStats()