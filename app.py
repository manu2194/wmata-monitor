import argparse
import logging
from wmata_locator import WmataLocator
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import requests
from requests import Request, Session
def convert_for_esp32_led_matrix_64_32(train_predictions):
  result = []
  lines = train_predictions['line']
  timestamp = train_predictions['timestamp']
  timestamp = datetime.fromisoformat(timestamp).strftime('%m/%d %H:%M:%S')
  for line, dest_map in lines.items():
    dest_list = []
    for dest, times in dest_map.items():
      dest_formatted = dest[:4]
      dest_formatted = dest_formatted.replace(' ', '')
      time_formatted = ','.join([str(t) for t in times[:2]])
      time_formatted = time_formatted.rjust(5)
      full_string = f'{dest_formatted}{time_formatted}'
      if len(full_string) > 11:
        raise Exception(f'The length of {full_string}({len(full_string)}) is greated than 16')
      dest_list.append(f'{dest_formatted} {time_formatted}')
    result.append({
      'name': line,
      'destinations': dest_list,
    })
  
  return {
    'line': result,
    'timestamp': timestamp
  }

  
def main():
  # Load environment variables
  load_dotenv()
  API_KEY = os.getenv('WMATA_API_KEY')

  # Configure argument parser
  parser = argparse.ArgumentParser(description="WMATA station locator")
  parser.add_argument("address", type=str, help="Starting address for search")
  parser.add_argument(
      "-l", "--log_level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
      help="Set logging level (default: INFO)"
  )
  parser.add_argument(
      "--esp32", action='store_true'
  )
  parser.add_argument(
      "--esp32-hostname", type=str, help='hostname of esp32'
  )

  args = parser.parse_args()

  # Configure logging
  logging.basicConfig(level=getattr(logging, args.log_level))
  logger = logging.getLogger()

  # Create WmataLocator object
  locator = WmataLocator(API_KEY, args.address)

  train_predictions = locator.find_closest_train_prediction()
  if args.esp32:
    result = convert_for_esp32_led_matrix_64_32(train_predictions)
    result = json.dumps(result)
    print(result)
  else:
    print(json.dumps(train_predictions, indent=4))

if __name__ == "__main__":
  main()
