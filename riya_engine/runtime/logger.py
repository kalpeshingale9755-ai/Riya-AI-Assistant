# runtime/logger.py
# Logging utilities for the Riya runtime
# riya_engine/runtime/logger.py

import json
import logging
from datetime import datetime


logging.basicConfig(
    filename="riya_runtime.log",
    level=logging.INFO,
    format="%(message)s"
)


class RiyaLogger:

    @staticmethod
    def log(event, data=None):

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "data": data or {}
        }

        logging.info(json.dumps(log_entry, indent=2))

        print(json.dumps(log_entry, indent=2))


logger = RiyaLogger()