def test_traversal_cannot_escape_sandbox(guarded):
    result = guarded.request("read_file", path="../../.env")
    assert not result.allowed and "escapes" in result.reason

def test_symlink_escape_is_blocked(guarded, tmp_path):
    outside = tmp_path.parent / "outside-secret.txt"; outside.write_text("secret")
    link = tmp_path / "link"
    try: link.symlink_to(outside)
    except OSError: return
    assert not guarded.request("read_file", path="link").allowed
