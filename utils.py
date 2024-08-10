import json
import time
import logging
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from datetime import datetime

logger = logging.getLogger()

CACHE_FILE = '.geolocator-cache.json'
CACHE_EXPIRATION = 3600  # 1 hour in seconds

def load_cache():
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def get_coordinates_of_address(address):
    logger.info(f'Loading coordinates for {address} from cache {CACHE_FILE}')
    cache = load_cache()
    if address in cache and cache[address]['expiration_time'] > time.time():
        logger.info(f'Cache hit found for {address} = {cache[address]["value"]}')
        return cache[address]['value']

    logger.info(f'No cache hit found for {address}. Location using geopy')
    locator = Nominatim(user_agent="Geopy Library")
    location = locator.geocode(address)
    if not location:
        raise Exception(f'Unable to geocode address {address}')
    coordinates = (location.latitude, location.longitude)
    cache[address] = {'expiration_time': time.time() + CACHE_EXPIRATION, 'value': coordinates}
    logger.info(f'Found coordinates for {address} = {coordinates}. Saving to cache {CACHE_FILE}...')
    save_cache(cache)
    return coordinates


def convert_for_esp32_led_matrix_64_32(train_predictions):
  result = []
  timestamp = train_predictions['timestamp']
  timestamp = datetime.fromisoformat(timestamp).strftime('%I:%M:%S%p')
  if 'error' in train_predictions:
    return {
      'line': [{'name': 'ERROR'}],
      'timestamp': timestamp
    }
  lines = train_predictions['line']
  for line, dest_map in lines.items():
    dest_list = []
    for dest, times in dest_map.items():
      
      # only select first four letters of destination name
      dest_formatted = dest[:4]
      
      # replace all spaces
      dest_formatted = dest_formatted.replace(' ', '')
      
      # select only first two times, and make them into string
      # comma separated
      time_formatted = ','.join([str(t) for t in times[:2]])
      
      # right-justify by 5 characters
      time_formatted = time_formatted.rjust(5)
      
      full_string = f'{dest_formatted} {time_formatted}'
      
      # Last validation, ensure that the characters are not greater
      # than 11 letters
      # this is expected to never happen, but if it does
      # we don't wanna mess up the display
      
      full_string = full_string[:10]
      if len(full_string) == 11:
        raise Exception(f'The length of "{full_string}"({len(full_string)}) should be exactly 11')
      dest_list.append(full_string.strip())
    result.append({
      'name': line,
      'destinations': sorted(dest_list, key=lambda x: x[:1]), # sort by first letter
    })
  
  return {
    'line': result,
    'timestamp': timestamp
  }