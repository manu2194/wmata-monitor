import json
from datetime import datetime
import logging
import requests
from geopy.distance import geodesic
from utils import get_coordinates_of_address

logger = logging.getLogger()

STATION_INFORMATION_FILEPATH = 'station-information.json'
REAL_TIME_RAIL_PREDICTIONS_URL = 'http://api.wmata.com/StationPrediction.svc/json/GetPrediction/{station_code}?contentType=application/json&api_key={api_key}'

class WmataLocator:
    def __init__(self, api_key: str, current_address: str):
        self.api_key = api_key
        self.closest_station = WmataLocator.find_closest_station(current_address)
        self.closest_station_name = self.closest_station["Name"]

    @staticmethod
    def find_closest_station(current_address: str):
        logger.debug(f'Opening {STATION_INFORMATION_FILEPATH}...')
        with open(STATION_INFORMATION_FILEPATH) as f:
            station_information = json.load(f)
        stations = station_information['Stations']

        # get current coordinates
        logger.info(f'Getting current coordinates')
        current_cords = get_coordinates_of_address(current_address)
        logger.info(f'Current coordinates are {current_cords}')

        logger.info(f'Finding closest station')
        closest_station_geodesic_distance = float('inf')
        closest_station = None
        for station in stations:
            # get station coordinates in tuple
            station_cords = (station["Lat"], station["Lon"])
            # get geodesic distance
            distance_from_station = abs(geodesic(station_cords, current_cords).miles)
            if distance_from_station < closest_station_geodesic_distance:
                closest_station_geodesic_distance = distance_from_station
                closest_station = station
        logger.info(f'Found closest station = {closest_station["Name"]}')
        return closest_station

    def find_closest_train_prediction(self):
        # get real time rail predictions
        logging.info(f'Finding closest train predictions for {self.closest_station_name}...')
        URL = REAL_TIME_RAIL_PREDICTIONS_URL.format_map({
            'api_key': self.api_key,
            'station_code': self.closest_station['Code']
        })
        response = requests.get(URL)
        logging.info(f'Found closest train predictions for {self.closest_station_name}...')
        trains = response.json()["Trains"]
        line_map = {}
        for train in trains:
            line = train["Line"]
            min = train["Min"]
            destination = train["Destination"]

            # convert "Min" ( minutes ) to something integer
            time = None
            if min.lower() == 'arr':
                time = 0
            else:
                # try parsing min as integer
                # if failed, just pass None
                try:
                    time = int(min)
                except ValueError:
                    pass

            if line not in line_map:
                line_map[line] = {
                        destination: [time]
                    }
                
            else:
                if destination not in line_map[line]:
                    line_map[line][destination] = [time]
                else:
                    line_map[line][destination].append(time)
        
        # now sort all the times for all the destinations

        logger.info(f'Found lines {",".join(list(line_map.keys()))} for {self.closest_station_name}')
        for line, destinations in line_map.items():
            for dest, times in destinations.items():
                line_map[line][dest] = sorted(line_map[line][dest], key=lambda x: (x is None, x))
        
        # current timestamp
        now = datetime.now().strftime(r'%m/%d, %H:%M:%S')

        result_dict = {}
        result_dict['line'] = line_map
        result_dict['timestamp'] = now
        return result_dict
