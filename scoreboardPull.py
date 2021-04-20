import base64
import requests
import pandas as pd
import numpy as np

def send_request():
    # Request

    try:
        response = requests.get(
            url="https://api.mysportsfeeds.com/v1.2/pull/nhl/2021-regular/scoreboard.csv?fordate=20210126",
            headers={
                "Authorization": "Basic " + base64.b64encode('{}:{}'.format("f3318aa7-8cb0-4c0f-bdaf-83f3c7","J332544443061j!").encode('utf-8')).decode('ascii')
            }
        )
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    return response.text

test = send_request().split(',')

test = np.array(test)
test = [sub.replace("\n","") for sub in test]

testDate = test[0]
test = test[1:]
testColumns = test[0:46]
testData = test[47:]

reStructuredTest = []

for i in range(46, len(test), 46):
    reStructuredTest.append(test[i:i+46])


testDF = pd.DataFrame(data = reStructuredTest, columns = testColumns)
print(testDF)