import logging

def setup_logger(name: str = __name__):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name)

    if not logger.handlers:  # Prevent adding multiple handlers
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
