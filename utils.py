import json
import time
import logging
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

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
