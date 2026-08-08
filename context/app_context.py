from dataclasses import dataclass
from typing import Any


@dataclass
class ApplicationContext:
    """
    Stores application-wide dependencies.

    These objects already exist before the agent starts
    processing a request.

    This class should NEVER contain business logic.
    """

    current_user: dict

    db_pool: Any

    redis_client: Any

    logger: Any

    config: dict

    memory_service: Any