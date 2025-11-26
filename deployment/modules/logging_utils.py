import logging
import os
from datetime import datetime 

def setup_logging():
    os.makedirs("logs", exist_ok = True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    logging.basicConfig(
        filename = "logs/device_access.log",
        level = logging.INFO,
        format = "%(asctime)s - %(levelname)s - %(message)s"
    )

    return timestamp