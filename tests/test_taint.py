def test_readme_sets_untrusted(guarded):
    assert guarded.request("read_file", path="README.md").allowed
    assert guarded.session.untrusted

def test_sensitive_read_sets_secret(guarded):
    assert guarded.request("read_file", path=".env").allowed
    assert guarded.session.secret
