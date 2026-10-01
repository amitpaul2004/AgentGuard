from pathlib import Path
from urllib.request import Request, urlopen
import subprocess

def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def write_file(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"wrote {path.name}"

def fetch_url(url: str) -> str:
    request = Request(url, headers={"User-Agent": "AgentGuard/1.0"})
    with urlopen(request, timeout=8) as response:
        return response.read(200_000).decode("utf-8", errors="replace")

def run_shell(argv: list[str], cwd: Path) -> str:
    result = subprocess.run(argv, cwd=cwd, shell=False, text=True, capture_output=True, timeout=30)
    return (result.stdout + result.stderr).strip()
