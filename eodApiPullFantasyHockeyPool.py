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
concateURL = str("https://api.mysportsfeeds.com/v2.1/pull/nhl/current/date/20210423/player_gamelogs.json")
keyLoc = open('C:/Users/fortn/Documents/DataScience/Projects/fantasyHockeyPool/fantasyHockeyPool/key.txt','r')
key = str(keyLoc.readline())

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


eodPullData = pastRequest()
eodPullData = json.loads(eodPullData)
eodList = []

for i in range(0, len(eodPullData['gamelogs'])):
    playerTeam = eodPullData['gamelogs'][i]['team']['abbreviation']
    playerID = eodPullData['gamelogs'][i]['player']['id']
    playerFirstName = eodPullData['gamelogs'][i]['player']['firstName']
    playerLastName = eodPullData['gamelogs'][i]['player']['lastName']
    playerPoints = int(eodPullData['gamelogs'][i]['stats']['scoring']['points'])
    eodList.append([playerTeam, playerID, playerFirstName, playerLastName, playerPoints])

eodColumns = ['Team','ID', 'FirstName', 'LastName', 'Points']
rawPastStatsDF = pd.DataFrame(data = eodList, columns = eodColumns)
sendEodStatDF = rawPastStatsDF.groupby(['Team','ID','FirstName','LastName'], as_index = False).sum()
countEodStatDF = rawPastStatsDF.groupby(['ID','FirstName','LastName'], as_index = False).count()
sendEodStatDF.insert(loc = 4,column = 'PastGamesPlayed', value = countEodStatDF['Points'])
sendEodStatDF.fillna(0, inplace = True)


sendEodStatDF.to_csv(
    r'C:\Users\fortn\Documents\Fantasy Hockey\2020-2021\Playoffs\playerStats.csv', 
    index = False)
