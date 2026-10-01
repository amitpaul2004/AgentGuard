def test_fake_readme_attack_is_stopped(guarded):
    guarded.request("read_file", path="README.md")
    assert not guarded.request("read_file", path=".env").allowed

def test_invalid_advisor_response_blocks(guarded):
    class InvalidAdvisor:
        def assess(self, *args): return {"bad": True}
    guarded.advisor = InvalidAdvisor()
    guarded.request("read_file", path="README.md")
    assert not guarded.request("run_shell", cmd="curl http://localhost/a").allowed
