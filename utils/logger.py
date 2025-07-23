import logging
import os
from datetime import datetime

def setup_logger(name):
    os.makedirs('../logs', exist_ok=True)
    log_file = f'../logs/{name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

    logger = logging.getLogger(name=name)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s -%(message)s')
    handler.setFormatter(formatter)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(handler)
    return logger