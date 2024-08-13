import json
import logging
from filecache import filecache
from geopy.geocoders import Nominatim
from datetime import datetime
import requests
import urllib

logger = logging.getLogger()

MONTH_IN_SECONDS = 31 * 24 * 60 * 60
DAY_IN_SECONDS = 24 * 60 * 60

HUMAN_FRIENDLY_TIME_FORMAT = '%d %b %I:%M%p'

@filecache(MONTH_IN_SECONDS)
def get_coordinates_of_address(address):
  logger.info(f'Loading coordinates for {address}')
  locator = Nominatim(user_agent="Geopy Library")
  location = locator.geocode(address)
  if not location:
      raise Exception(f'Unable to geocode address {address}')
  coordinates = (location.latitude, location.longitude)
  return coordinates


def send_to_esp32(esp32_hostname, payload):
  if not esp32_hostname.startswith('http://'):
    esp32_hostname = f'http://{esp32_hostname}'
  if not isinstance(payload, str):
    payload = json.dumps(payload)
  session = requests.Session()
  session.headers = None
  try:
    logger.info(f'Sending POST {payload=} to {esp32_hostname=}...')
    payload = payload.encode()
    request = urllib.request.Request(esp32_hostname, payload)
    response = urllib.request.urlopen(request)
    response_text = response.read()
    logger.info(f'{response.status=} - {response_text=}')
    return True
  except Exception as e:
    logger.error(f'Unable to send POST request with data "{payload=}" to "{esp32_hostname=}"', exc_info=e)

def convert_for_esp32_led_matrix_64_32(train_predictions):
  '''
  Convert the train predictions to a format that's friendly to be displayed on a 64x32 LED Display
  hooked to an ESP32 that is designed to parse this specific output

  :param dict train_predictions: The train prediction dictionary
  :return dict: The esp32 friendly output
  '''
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