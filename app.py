import click
from wmata_locator import WmataLocator
from dotenv import load_dotenv
import os
import json
from utils import convert_for_esp32_led_matrix_64_32, send_to_esp32, get_coordinates_of_address
import logging
from logging.handlers import RotatingFileHandler



# initialize logging
LOG_FORMATTER = logging.Formatter('[%(asctime)s] - [%(levelname)s] - %(module)s:%(funcName)s[%(lineno)d] - %(message)s')
root_logger = logging.getLogger()
console_handler = logging.StreamHandler()
console_handler.setFormatter(LOG_FORMATTER)
root_logger.addHandler(console_handler)


# load environmnet vars
load_dotenv()

@click.group()
def wmata():
  """WMATA station locator."""
  pass

@wmata.command(help='Get coordinates of given address')
@click.argument("address", type=str)
def geolocate(address):
  print(get_coordinates_of_address(address))

@wmata.command(help='Find the train predictions of the closest metro station')
@click.argument("address", type=str)
@click.option(
    "--log-file",
    type=click.Path(exists=False),
    help="Write to log file defiled by this path, instead of stdout"
)
@click.option(
    "-l", "--log-level", 
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]), 
    default="INFO",
    help="Set logging level (default: INFO)"
)
@click.option(
    "--esp32", is_flag=True, help="Format output for ESP32 LED matrix"
)
@click.option(
    "--esp32-hostname", 
    envvar='ESP32_HOSTNAME',
    type=str, 
    help='hostname of esp32 (for future use)'
)
def predict(address, log_level, esp32, esp32_hostname, log_file):
  """Find closest train prediction for the given address."""
  # get environment variables
  API_KEY = os.getenv('WMATA_API_KEY')
  
  
  # Configure logging
  root_logger.setLevel(level=getattr(logging, log_level.upper()))
  if log_file:
    file_handler = RotatingFileHandler(log_file, mode='a', maxBytes=1000000, backupCount=1, encoding=None, delay=0)
    file_handler.setFormatter(LOG_FORMATTER)
    root_logger.addHandler(file_handler)
  locator = WmataLocator(API_KEY, address)
  result = locator.find_closest_train_prediction()
  
  if esp32:
    esp32_friendly_data = convert_for_esp32_led_matrix_64_32(result)
    send_to_esp32(esp32_hostname, esp32_friendly_data)
    print(json.dumps(esp32_friendly_data, indent=4))
  else:
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
  wmata()
