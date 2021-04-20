import base64
import requests
import pandas as pd
import numpy as np
import json
from pandas import json_normalize

def send_request():
    # Request

    try:
        response = requests.get(
            url="https://api.mysportsfeeds.com/v1.2/pull/nhl/current_season.json?fordate=20210418",
            headers={
                "Authorization": "Basic " + base64.b64encode('{}:{}'.format("f3318aa7-8cb0-4c0f-bdaf-83f3c7","J332544443061j!").encode('utf-8')).decode('ascii')
            }
        )
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    return response.content

csTest = send_request()

csTest = csTest.decode('utf8').replace("'",'"')
csData = json.loads(csTest)

csData = json.dumps(csData, indent = 2, sort_keys = True)
print(csData)
