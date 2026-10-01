# AgentGuard skills

AgentGuard mediates `read_file`, `write_file`, `fetch_url`, and `run_shell`.
Tools must be requested through `Gateway.request`; calling the lower-level tool
module directly intentionally bypasses policy and is not part of the agent API.

Hard policy decisions always win.  The optional Ollama advisor only evaluates
risky shell requests after hard checks have passed.
