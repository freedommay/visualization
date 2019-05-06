import time

import requests
import pandas as pd

base = 'https://restapi.amap.com/v3/geocode/geo'

key1 = '**'
key2 = '**'
key3 = '**'
key4 = '**'


def geocode(address, key):
    parameters = {'address': address,
                  'key': key,
                  'city': '杭州',
                  'output': 'JSON'}
    response = requests.get(base, parameters)
    data = response.json()
    location = data['geocodes'][0]['location']
    return location


def insert_data():
    table = pd.read_csv('../data/food.csv')
    table['location'] = None
    for index, row in table.iterrows():
        try:
            if index < 5000:
                table['location'][index] = geocode(row['address'], key1)
            elif index < 10000:
                table['location'][index] = geocode(row['address'], key2)
            elif index < 15000:
                table['location'][index] = geocode(row['address'], key3)
            else:
                table['location'][index] = geocode(row['address'], key4)
            time.sleep(0.01)
        except Exception:
            pass
    table.to_csv('../data/food_dup.csv', encoding='utf_8_sig')


insert_data()
