import logging
import os
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from flask import Flask, jsonify, request

LOG_FORMATTER = logging.Formatter('[%(asctime)s] - [%(levelname)s] - %(module)s:%(funcName)s[%(lineno)d] - %(message)s')
root_logger = logging.getLogger()
console_handler = logging.StreamHandler()
console_handler.setFormatter(LOG_FORMATTER)
root_logger.addHandler(console_handler)
from wmata_locator import WmataLocator

load_dotenv()
app = Flask(__name__)

API_KEY = os.getenv('WMATA_API_KEY')
ADDRESS = '300 M ST NE, Washington, DC, 20002'

def format_esp32(train_predictions):
    result = []
    line = train_predictions['line']
    timestamp = train_predictions['timestamp']
    for line_color, trains in line.items():
        for end_station, timing_list in trains.items():
            station_formatted = end_station[:4]
            times_formatted = ','.join([str(time) for time in timing_list[:2]])
            result.append(f'{station_formatted} {times_formatted}')
    result = sorted(result)
    return {
        'line': result,
        'timestamp': timestamp
    }

@app.route('/', methods=['GET'])
def get():
    try:
        locator = WmataLocator(API_KEY, ADDRESS)
        train_predictions = locator.find_closest_train_prediction()
        esp32_formatted = format_esp32(train_predictions)
    except Exception as e:
        logging.error(e, exc_info=e)
        return 'ERROR', 500
    return jsonify(esp32_formatted), 200
    
if __name__ == '__main__':
    # Configure logging
    root_logger.setLevel('INFO')
    file_handler = RotatingFileHandler('wmata.log', mode='a', maxBytes=1000000, backupCount=1, encoding=None, delay=0)
    file_handler.setFormatter(LOG_FORMATTER)
    root_logger.addHandler(file_handler)
    app.run(host='0.0.0.0', debug=True)