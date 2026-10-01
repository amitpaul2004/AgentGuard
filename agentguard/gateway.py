from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
import shlex
from .session import Session
from .policy import Policy
from .classifier import is_secret_path, is_untrusted_path, contains_secret
from . import tools

@dataclass
class Decision:
    allowed: bool
    reason: str
    result: str | None = None

class Gateway:
    def __init__(self, sandbox: str | Path, policy: Policy, session: Session, advisor=None):
        self.sandbox = Path(sandbox).resolve()
        self.policy, self.session, self.advisor = policy, session, advisor

    def _path(self, value):
        candidate = Path(value)
        full = (self.sandbox / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
        try: relative = full.relative_to(self.sandbox)
        except ValueError: raise PermissionError("Path escapes configured sandbox")
        return full, relative

    def _host_allowed(self, url):
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return False
        # hostname is exact; github.com.evil.example never equals github.com
        return parsed.hostname.lower().rstrip(".") in self.policy.allowed_hosts

    def _deny(self, tool, args, reason):
        self.session.record(tool, args, "BLOCK", reason)
        return Decision(False, reason)

    def request(self, tool, **args):
        try:
            if tool == "read_file": return self._read(args)
            if tool == "write_file": return self._write(args)
            if tool == "fetch_url": return self._fetch(args)
            if tool == "run_shell": return self._shell(args)
            return self._deny(tool, args, "Unknown tool")
        except (PermissionError, ValueError) as exc:
            return self._deny(tool, args, str(exc))
        except Exception as exc:
            return self._deny(tool, args, f"Tool failed safely: {type(exc).__name__}")

    def _read(self, args):
        full, rel = self._path(args["path"])
        if self.session.untrusted and is_secret_path(rel, self.policy):
            return self._deny("read_file", args, "Untrusted content is influencing access to a sensitive file")
        content = tools.read_file(full)
        if is_secret_path(rel, self.policy) or contains_secret(content): self.session.secret = True
        if is_untrusted_path(rel, self.policy):
            self.session.untrusted = True; self.session.untrusted_excerpt = content[:2000]
        self.session.record("read_file", args, "ALLOW")
        return Decision(True, "Allowed", content)

    def _write(self, args):
        full, rel = self._path(args["path"])
        if is_secret_path(rel, self.policy): return self._deny("write_file", args, "Writing sensitive paths is not permitted")
        result = tools.write_file(full, args["content"])
        self.session.record("write_file", args, "ALLOW")
        return Decision(True, "Allowed", result)

    def _fetch(self, args):
        url = args["url"]
        if not self._host_allowed(url): return self._deny("fetch_url", args, "Network destination is not on the exact allowlist")
        if self.session.secret: return self._deny("fetch_url", args, "Secret-tainted session cannot send data over the network")
        content = tools.fetch_url(url)
        self.session.untrusted = True; self.session.untrusted_excerpt = content[:2000]
        self.session.record("fetch_url", args, "ALLOW")
        return Decision(True, "Allowed", content)

    def _shell(self, args):
        cmd = args["cmd"]
        argv = shlex.split(cmd, posix=True)
        if not argv: return self._deny("run_shell", args, "Empty shell command")
        # Reject shell grammar that subprocess(shell=False) would not execute safely.
        if any(token in {"|", ">", ">>", "<", ";", "&&", "||"} for token in argv):
            return self._deny("run_shell", args, "Shell operators are not allowed")
        program = Path(argv[0]).name.lower()
        risky = program in self.policy.risky_programs
        urls = [x for x in argv[1:] if urlparse(x).scheme in {"http", "https"}]
        if any(not self._host_allowed(url) for url in urls): return self._deny("run_shell", args, "Shell network destination is not on the exact allowlist")
        if self.session.secret and (risky or urls): return self._deny("run_shell", args, "Secret-tainted session cannot run network/exfiltration command")
        if self.session.untrusted and risky:
            verdict = self.advisor.assess(self.session.task, "run_shell", args, self.session.untrusted_excerpt) if self.advisor else None
            if not verdict or not verdict["follows_task"] or verdict["confidence"] < .8:
                return self._deny("run_shell", args, "Risky command after untrusted content requires a valid approving local advisor")
        result = tools.run_shell(argv, self.sandbox)
        self.session.record("run_shell", args, "ALLOW")
        return Decision(True, "Allowed", result)
