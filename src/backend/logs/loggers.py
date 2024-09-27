import logging
from backend.utils import config

def create_logger(name: str, logging_path: str) -> logging.Logger:
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    api_logger = logging.getLogger(name)
    api_logger.setLevel(config['logging']['level'])

    file_handler = logging.FileHandler(logging_path)
    file_handler.setFormatter(logging.Formatter(format))
    api_logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(format))
    api_logger.addHandler(stream_handler)

    return api_logger