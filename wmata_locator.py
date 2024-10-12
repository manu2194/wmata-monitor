from datetime import datetime
import logging
import requests
from geopy.distance import geodesic
from cache import jsonfilecache
from utils import get_coordinates_of_address, MONTH_IN_SECONDS, DAY_IN_SECONDS, HUMAN_FRIENDLY_TIME_FORMAT

logger = logging.getLogger()

STATION_INFORMATION_FILEPATH = 'station-information.json'
STATION_LIST_URL = 'http://api.wmata.com/Rail.svc/json/jStations?contentType=application/json&api_key={api_key}'
STATION_TIMING_URL = 'http://api.wmata.com/Rail.svc/json/jStationTimes?contentType=application/json&api_key={api_key}'
REAL_TIME_RAIL_PREDICTIONS_URL = 'http://api.wmata.com/StationPrediction.svc/json/GetPrediction/{station_code}?contentType=application/json&api_key={api_key}'

class WmataLocator:
    def __init__(self, api_key: str, current_address: str):
        self.api_key = api_key
        self.station_list = self.get_station_list()
        self.station_timings = self.get_station_timings()
        self.closest_station = self.find_closest_station(current_address)
        self.closest_station_name = self.closest_station["Name"]

    @jsonfilecache(MONTH_IN_SECONDS)
    def get_station_list(self):
        logger.info(f'Getting WMATA station info...')
        URL = STATION_LIST_URL.format_map({
            'api_key': self.api_key
        })
        response = requests.get(URL)
        return response.json()

    @jsonfilecache(DAY_IN_SECONDS)
    def get_station_timings(self):
        logger.info(f'Getting station timings...')
        URL = STATION_TIMING_URL.format_map({
            'api_key': self.api_key
        })
        response = requests.get(URL)
        return response.json()
        
    def find_closest_station(self, current_address: str):
        stations = self.station_list['Stations']

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
        '''
        _summary_

        :return dict: 
        
        ```python
        {
            "line": {
                "RD": {
                    "Forest Glen: [9, 15, 20],
                    "Shady Grove: [9, 15, 20],
                }
            }
        }
        ```
        '''
        # get real time rail predictions
        current_time = datetime.now()
        current_day = current_time.strftime('%A')
        logging.info(f'Finding closest train predictions for {self.closest_station_name}...')
        logging.info(f'Checking for station timings for the {current_day}')
        closest_station_timing = [station for station in self.station_timings['StationTimes'] if station['StationName'] == self.closest_station_name][0]
        todays_station_timing = closest_station_timing[current_day]
        opening_time_hour_and_minute = datetime.strptime(todays_station_timing['OpeningTime'], '%H:%M')
        first_datetime = current_time.replace(hour=opening_time_hour_and_minute.hour, minute=opening_time_hour_and_minute.minute)
        
        closing_times_hour_and_minute = [
            datetime.strptime(last_train['Time'], '%H:%M') for last_train in todays_station_timing['LastTrains']
        ]
        closing_times = [
            current_time.replace(hour=closing_time_hr_min.hour, minute=closing_time_hr_min.minute) for closing_time_hr_min in closing_times_hour_and_minute
        ]
        last_datetime = max(closing_times)
        
        # if not ( current_time >= first_datetime and current_time <= last_datetime ):
        #     if current_time > last_datetime:
        #         logger.info(f"The current time {current_time.strftime(HUMAN_FRIENDLY_TIME_FORMAT)} but the last train has left the station at {last_datetime.strftime(HUMAN_FRIENDLY_TIME_FORMAT)}")
        #     if current_time < first_datetime:
        #         logger.info(f"The current time {current_time.strftime(HUMAN_FRIENDLY_TIME_FORMAT)} but the first train will start at {first_datetime.strftime(HUMAN_FRIENDLY_TIME_FORMAT)}")
        #     return {
        #         "line": {},
        #         "timestamp": current_time.isoformat(),
        #         "first_train": first_datetime.isoformat(),
        #         "last_train": last_datetime.isoformat()
        #     }
        
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
            time = 'N'
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
                line_map[line][dest] = sorted(line_map[line][dest], key=lambda x: (x is None or x == 'N', x))
        
        # current timestamp
        now = current_time.isoformat()

        result_dict = {}
        result_dict['line'] = line_map
        result_dict['timestamp'] = now
        result_dict["first_train"] = first_datetime.isoformat()
        result_dict["last_train"] = last_datetime.isoformat()
        return result_dict
