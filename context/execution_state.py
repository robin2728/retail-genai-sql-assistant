from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionState:
    """
    Stores everything generated while
    solving ONE user request.

    Every tool can read and update this state.
    """

    question: str

    messages: list[Any] = field(default_factory=list)

    current_tool: str | None = None

    tool_outputs: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)

    errors: list[str] = field(default_factory=list)

    final_response: str | None = None