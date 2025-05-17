# Journalisation (logs des actions et connexions)
import logging


LOG_FILE = "Security/user_management.log"

def get_logger(name: str = "security"):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = logging.FileHandler(LOG_FILE)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    return logger

def log_action(username: str, action: str, details: str = None):
    """
    Log an action for a given user.
    """
    logger = get_logger()
    msg = f"User: {username} | Action: {action}"
    if details:
        msg += f" | Details: {details}"
    logger.info(msg)