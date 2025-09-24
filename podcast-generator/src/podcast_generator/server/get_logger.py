import logging

import google.cloud.logging

from podcast_generator.server.environment import is_prod

if is_prod():
    # Set up cloud logging
    google.cloud.logging.Client().setup_logging()
else:
    logging.getLogger().addHandler(logging.StreamHandler())


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    return logger
