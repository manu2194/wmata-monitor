import requests
import os
import json
from dotenv import load_dotenv
from utils import find_closest_station

load_dotenv()

API_KEY = os.getenv('WMATA_API_KEY')

# response = requests.get(f'http://api.wmata.com/TrainPositions/TrainPositions?contentType=application/json&api_key={API_KEY}')

response = requests.get(f'http://api.wmata.com/Rail.svc/json/jLines?contentType=application/json&api_key={API_KEY}')

with open('line-information.json', 'w+') as f:
    json.dump(response.json(), f, indent=4)
        