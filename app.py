import argparse
import logging
from wmata_locator import WmataLocator
from dotenv import load_dotenv
import os
import json

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

  args = parser.parse_args()

  # Configure logging
  logging.basicConfig(level=getattr(logging, args.log_level))
  logger = logging.getLogger()

  # Create WmataLocator object
  locator = WmataLocator(API_KEY, args.address)

  train_predictions = locator.find_closest_train_prediction()

  print(json.dumps(train_predictions, indent=4))

if __name__ == "__main__":
  main()