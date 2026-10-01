"""Measure actual decisions over the local declarative attack corpus."""
from pathlib import Path
import tempfile, yaml
from agentguard import Gateway, Session
from agentguard.policy import Policy

ROOT = Path(__file__).parent
def prepare(root, setup):
    (root / "README.md").write_text("untrusted instructions", encoding="utf8")
    (root / "app.py").write_text("print('ok')", encoding="utf8")
    (root / "key.pem").write_text("KEY", encoding="utf8")
    (root / ".env").write_text("API_KEY=FAKE", encoding="utf8")
    (root / ".aws").mkdir(); (root / ".aws/credentials").write_text("x")
    (root / "src").mkdir(); (root / "src/main.py").write_text("x")
    g = Gateway(root, Policy.load(ROOT / "policy.yaml"), Session("Setup and test"))
    if setup in {"readme", "issue"}: g.request("read_file", path="README.md")
    elif setup == "web": g.session.untrusted = True  # represents prior allowed trusted-host page fetch
    elif setup == "secret": g.request("read_file", path=".env")
    return g
def evaluate(group, expected_allowed):
    correct, misses = 0, []
    for case in group:
        with tempfile.TemporaryDirectory() as temp:
            gateway = prepare(Path(temp), case.get("setup", "none"))
            decision = gateway.request(case["tool"], **case["args"])
            if decision.allowed == expected_allowed: correct += 1
            else: misses.append(case["name"])
    return correct, misses
if __name__ == "__main__":
    corpus = yaml.safe_load((ROOT / "corpus/cases.yaml").read_text())
    attacks, benign = corpus["attacks"], corpus["benign"]
    blocked, attack_misses = evaluate(attacks, False)
    allowed, benign_misses = evaluate(benign, True)
    print(f"Total attacks: {len(attacks)}\nAttacks blocked: {blocked}\nTotal benign cases: {len(benign)}\nBenign cases allowed: {allowed}")
    print(f"False positives: {len(benign)-allowed}\nFalse negatives: {len(attacks)-blocked}")
    print(f"Detection/block rate: {blocked / len(attacks):.1%}")
    if benign_misses: print("False-positive cases:", ", ".join(benign_misses))
    if attack_misses: print("False-negative cases:", ", ".join(attack_misses))
