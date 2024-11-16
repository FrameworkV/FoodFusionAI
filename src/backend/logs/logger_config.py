import logging
from backend.utils import config

handlers = [logging.StreamHandler()]

if  config['app']['status'] == "dev":   # only add to log files in development for debugging purposes and to avoid Azure costs
    handlers.append(logging.FileHandler(filename=config['logging']['path']))

logging.basicConfig(
    format='[%(filename)s, %(funcName)s] %(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=config['logging']['level'],
    handlers=handlers
)

logger = logging.getLogger("logger")