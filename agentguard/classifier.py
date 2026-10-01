import re
from pathlib import Path

SECRET_RE = re.compile(r"(?:api[_-]?key|secret|password|token)\s*[:=]\s*\S+", re.I)

def is_secret_path(relative: Path, policy) -> bool:
    return policy.matches(relative, "sensitive_patterns")

def is_untrusted_path(relative: Path, policy) -> bool:
    return policy.matches(relative, "untrusted_patterns")

def contains_secret(text: str) -> bool:
    return bool(SECRET_RE.search(text))
