import logging
from backend.utils import config

logging.basicConfig(
    format='[%(filename)s, %(funcName)s] %(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=config['logging']['level'],
    handlers=[logging.FileHandler(filename=config['logging']['path']), logging.StreamHandler()]
)

logger = logging.getLogger("logger")