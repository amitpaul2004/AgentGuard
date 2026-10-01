def test_normal_test_command_allowed(guarded):
    result = guarded.request("run_shell", cmd="python --version")
    assert result.allowed

def test_unknown_tool_blocked(guarded):
    assert not guarded.request("delete_everything", path=".").allowed
