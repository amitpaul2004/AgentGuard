from dataclasses import dataclass, field
from typing import Any

@dataclass
class Session:
    task: str
    untrusted: bool = False
    secret: bool = False
    events: list[dict[str, Any]] = field(default_factory=list)
    untrusted_excerpt: str = ""

    def record(self, tool: str, args: dict, decision: str, reason: str = "") -> None:
        self.events.append({"tool": tool, "args": args, "decision": decision, "reason": reason,
                            "untrusted": self.untrusted, "secret": self.secret})
