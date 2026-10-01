def test_allowed_domain_matches_exactly(guarded):
    assert guarded._host_allowed("https://github.com/openai")

def test_lookalike_domain_is_blocked(guarded):
    result = guarded.request("fetch_url", url="https://github.com.evil.example/a")
    assert not result.allowed
