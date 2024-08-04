import os
from dotenv import load_dotenv
from wmata_locator import WmataLocator
import logging
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger()

load_dotenv()

API_KEY = os.getenv('WMATA_API_KEY')

locator = WmataLocator(API_KEY, '607 13th St NW, Washington, DC 20005')