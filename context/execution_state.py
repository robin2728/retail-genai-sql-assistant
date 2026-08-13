from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionState:
    """
    Tracks the state of one agent execution.
    """

    messages: list[Any] = field(default_factory=list)

    tool_calls: list[dict] = field(default_factory=list)

    tool_results: list[dict] = field(default_factory=list)

    status: str = "running"

    final_response: Any = None