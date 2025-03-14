import os
import logging
from foodfusionai.utils import project_config

handlers = [logging.StreamHandler()]

if  project_config['app']['status'] == "dev":   # only add to log files in development for debugging purposes and to avoid Azure costs
    handlers.append(logging.FileHandler(filename=os.path.join(os.path.dirname(__file__), "logs.log")))

logging.basicConfig(
    format='[%(filename)s, %(funcName)s] %(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=project_config['logging']['level'],
    handlers=handlers
)

logger = logging.getLogger("logger")