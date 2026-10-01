from pathlib import Path
import fnmatch
import yaml

class Policy:
    def __init__(self, data: dict):
        self.data = data

    @classmethod
    def load(cls, path: str | Path):
        with open(path, encoding="utf-8") as handle:
            return cls(yaml.safe_load(handle) or {})

    def matches(self, path: Path, key: str) -> bool:
        patterns = self.data.get("taint", {}).get(key, [])
        normalized = path.as_posix().lower()
        name = path.name.lower()
        return any(fnmatch.fnmatch(normalized, p.lower()) or fnmatch.fnmatch(name, p.lower()) for p in patterns)

    @property
    def allowed_hosts(self): return set(self.data.get("network", {}).get("allowed_hosts", []))
    @property
    def risky_programs(self): return set(self.data.get("shell", {}).get("risky_programs", []))
