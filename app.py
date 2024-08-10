import argparse
import logging
from wmata_locator import WmataLocator
from dotenv import load_dotenv
import os
import json
from requests import Request, Session
from datetime import datetime
from utils import convert_for_esp32_led_matrix_64_32

  
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


  result_or_error = None
  try:
    # Create WmataLocator object
    locator = WmataLocator(API_KEY, args.address)
    result_or_error = locator.find_closest_train_prediction()
  except Exception as e:
    logger.error(e)
    result_or_error = {
      "error": f"Error occured when trying to get fetch train predictions: {e}",
      "timestamp": datetime.now().isoformat()
    }
  if args.esp32:
    led_matrix_friendly_format = convert_for_esp32_led_matrix_64_32(result_or_error)
    print(json.dumps(led_matrix_friendly_format))
  else:
    print(json.dumps(result_or_error, indent=4))

if __name__ == "__main__":
  main()
