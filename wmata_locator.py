import json
import time
import logging
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from utils import get_coordinates_of_address

STATION_INFORMATION_FILEPATH = 'station-information.json'

class WmataLocator:
    def __init__(self, api_key: str, current_address: str):
        self.api_key = api_key
        self.closest_station = WmataLocator.find_closest_station(current_address)

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
        logger.info(f'Found closest station = {closest_station}')
        return closest_station

def find_train_prediction_near_station(station_code):
    train_positions = train_positions['TrainPositions']