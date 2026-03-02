def test_validate_url_blocks_private_dns_resolution(monkeypatch):
    from src.governor.network_mediator import NetworkMediator
    from src.governor.exceptions import NetworkMediatorError

    mediator = NetworkMediator()

    def fake_getaddrinfo(host, port):
        return [(None, None, None, None, ("127.0.0.1", 0))]

    monkeypatch.setattr("src.governor.network_mediator.socket.getaddrinfo", fake_getaddrinfo)

    try:
        mediator._validate_url("https://example.com/path")
        assert False, "Expected private resolved address to be blocked"
    except NetworkMediatorError:
        assert True
