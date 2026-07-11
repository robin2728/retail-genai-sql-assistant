import json
import logging


class JsonFormatter(logging.Formatter):

    def format(self, record):

        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage()
        }

        return json.dumps(log_record)


logger = logging.getLogger("retail_genai")

logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()

console_handler.setFormatter(JsonFormatter())

logger.handlers.clear()

logger.addHandler(console_handler)


def log_event(event: str, **kwargs):

    payload = {
        "event": event
    }

    payload.update(kwargs)

    logger.info(json.dumps(payload))