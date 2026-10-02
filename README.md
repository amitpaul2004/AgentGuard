# AgentGuard — AI Agent Security Gateway

AgentGuard is a local, policy-first gateway that prevents an AI coding agent
from directly using files, network access, or a terminal. Every request goes
through `Gateway.request()` and gets an `ALLOW` or `BLOCK` decision first.

```text
AI agent -> AgentGuard -> hard policy checks -> optional local Ollama advisor -> tool
```

Hard blocks take final authority. Ollama is optional, configurable with
`OLLAMA_MODEL`, and only assesses risky gray-area shell requests. A missing,
invalid, or timed-out advisor result fails closed.

## Quick start

```bash
cd AgentGuard
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest -q
python eval.py
python demo/agent.py
```

The guarded demo reads the poisoned README, marks the session `UNTRUSTED`, and
blocks `.env` before the fake credentials can leave the repository. To observe
the deliberately unsafe contrast, start `python demo/attacker_server.py` in one
terminal and run `python demo/agent.py --unguarded` in another. The collector is
bound to local host only and receives only the fake demo credentials.

## Policy and security behavior

`policy.yaml` controls sensitive/untrusted path patterns, exact network
allowlists, and risky shell programs. Paths are resolved and required to remain
under the configured sandbox, including symlink targets. URL host matching is
exact: `github.com.evil.example` does not match `github.com`. Shell commands are
tokenized with `shlex`, run with `shell=False`, and reject shell operators.

The session state is sticky:

- Reading README/HTML/issue-like content marks `UNTRUSTED`.
- Reading sensitive paths or obvious key/password/token content marks `SECRET`.
- `UNTRUSTED + sensitive file` is blocked.
- Unknown hosts are blocked; `SECRET + network/exfiltration` is blocked.

Run `python eval.py` for measured results from 25 attacks and 11 benign cases.
The evaluation invokes the real gateway and computes all reported counts.

# EOD
thats all
