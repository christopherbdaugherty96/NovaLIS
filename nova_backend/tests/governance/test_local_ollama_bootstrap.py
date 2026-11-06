"""Narrow bootstrap regressions; synthetic service proof, no real model calls."""

import pytest
from src.governor.disclosure_policy import DisclosureDecisionValue
from src.llm import local_ollama_bootstrap as bootstrap
from src.llm.model_network_mediator import ModelNetworkMediator, ModelNetworkMediatorError


class _Sink:
    def __init__(self, fail=False):
        self.events = []
        self.fail = fail

    def append(self, record):
        if self.fail:
            raise OSError("evidence disk unavailable")
        self.events.append(record.as_dict())


def _mediator(monkeypatch, sink=None):
    monkeypatch.setattr(bootstrap, "_attest_ollama_listener", lambda: None)
    monkeypatch.setattr(
        bootstrap, "localhost_resolves_exclusively_to_loopback",
        lambda: True,
    )
    evidence = sink or _Sink()
    return bootstrap.VerifiedLoopbackOllamaMediator(
        model="gemma2:2b", evidence_sink=evidence
    ), evidence


def _approve(mediator, url, method, payload):
    mediator._authorize_disclosure(
        method=method,
        url=url,
        json_payload=payload,
        has_body=payload is not None,
        request_id="bootstrap-test",
        session_id="session-test",
    )


def test_verified_loopback_ollama_identity_read_is_admitted_and_evidenced(monkeypatch):
    mediator, sink = _mediator(monkeypatch)
    _approve(mediator, "http://localhost:11434/api/show", "POST", {"model": "gemma2:2b"})
    assert mediator._validate_url("http://localhost:11434/api/show") == "http://127.0.0.1:11434/api/show"
    assert sink.events[0]["decision"] == DisclosureDecisionValue.ALLOW.value
    assert sink.events[0]["destination"] == "http://127.0.0.1:11434"
    assert sink.events[0]["data_categories"] == ["structural_metadata"]


def test_local_model_chat_disclosure_does_not_store_prompt_or_response(monkeypatch):
    mediator, sink = _mediator(monkeypatch)
    secret = "never-log-the-user-prompt-7812"
    payload = {
        "model": "gemma2:2b",
        "messages": [{"role": "user", "content": secret}],
        "stream": False,
        "options": {"num_predict": 128, "num_ctx": 4096},
    }
    _approve(mediator, "http://127.0.0.1:11434/api/chat", "POST", payload)
    assert secret not in str(sink.events)
    assert sink.events[0]["decision"] == "allow"


@pytest.mark.parametrize("url", [
    "http://192.168.1.2:11434/api/show",
    "http://10.0.0.9:11434/api/show",
    "http://127.0.0.1:11435/api/show",
    "https://127.0.0.1:11434/api/show",
    "http://user@127.0.0.1:11434/api/show",
    "http://127.0.0.1:11434/api/show?model=gemma2",
    "http://127.0.0.1:11434/api/show#fragment",
    "http://127.0.0.1:11434/api/unknown",
])
def test_loopback_bootstrap_rejects_substituted_destinations(monkeypatch, url):
    mediator, sink = _mediator(monkeypatch)
    with pytest.raises(ModelNetworkMediatorError):
        _approve(mediator, url, "POST", {"model": "gemma2:2b"})
    assert not sink.events


def test_localhost_must_not_resolve_to_lan(monkeypatch):
    mediator, sink = _mediator(monkeypatch)
    monkeypatch.setattr(
        bootstrap, "localhost_resolves_exclusively_to_loopback",
        lambda: False,
    )
    with pytest.raises(ModelNetworkMediatorError):
        _approve(mediator, "http://localhost:11434/api/show", "POST", {"model": "gemma2:2b"})
    assert not sink.events


def test_unverified_process_owner_denied_before_evidence(monkeypatch):
    mediator, sink = _mediator(monkeypatch)
    def deny():
        raise ModelNetworkMediatorError("unverified listener")
    monkeypatch.setattr(bootstrap, "_attest_ollama_listener", deny)
    with pytest.raises(ModelNetworkMediatorError):
        _approve(mediator, "http://localhost:11434/api/show", "POST", {"model": "gemma2:2b"})
    assert not sink.events


def test_listener_attestation_requires_valid_ollama_publisher(monkeypatch, tmp_path):
    executable = tmp_path / "Programs" / "Ollama" / "ollama.exe"
    executable.parent.mkdir(parents=True)
    executable.write_bytes(b"not the signed Ollama executable")

    class _Connection:
        status = bootstrap.psutil.CONN_LISTEN
        laddr = type("_Address", (), {"ip": "127.0.0.1", "port": 11434})()
        pid = 4812

    class _Process:
        pid = 4812

        def exe(self):
            return str(executable)

        def cmdline(self):
            return [str(executable), "serve"]

        def create_time(self):
            return 1741132800.0

    monkeypatch.setattr(bootstrap, "_is_windows", lambda: True)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(
        bootstrap, "_ollama_authenticode_is_valid", lambda _path: False
    )
    monkeypatch.setattr(
        bootstrap.psutil, "net_connections", lambda **_kwargs: [_Connection()]
    )
    monkeypatch.setattr(bootstrap.psutil, "Process", lambda _pid: _Process())
    monkeypatch.setattr(bootstrap, "_ATTESTED_PROCESS", None)

    with pytest.raises(ModelNetworkMediatorError, match="publisher"):
        bootstrap._attest_ollama_listener()


def test_reparse_attribute_is_treated_as_unsafe(monkeypatch, tmp_path):
    target = tmp_path / "junction"
    target.mkdir()
    attributes = getattr(bootstrap.stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)

    monkeypatch.setattr(bootstrap.Path, "is_symlink", lambda _path: False)
    monkeypatch.setattr(
        bootstrap.Path,
        "stat",
        lambda _path, **_kwargs: type(
            "_Stat", (), {"st_file_attributes": attributes}
        )(),
    )

    assert bootstrap._is_link_or_reparse(target)


def test_evidence_target_rejects_reparse_backed_parent(monkeypatch, tmp_path):
    root = tmp_path.resolve()
    monkeypatch.setattr(bootstrap, "_is_windows", lambda: True)
    monkeypatch.setattr(bootstrap, "runtime_root", lambda _file: root)
    monkeypatch.setattr(
        bootstrap,
        "ctypes",
        type(
            "_Ctypes",
            (),
            {
                "windll": type(
                    "_Windll",
                    (),
                    {
                        "kernel32": type(
                            "_Kernel32",
                            (),
                            {"GetDriveTypeW": staticmethod(lambda _drive: 3)},
                        )()
                    },
                )()
            },
        )(),
    )
    monkeypatch.setattr(
        bootstrap,
        "_path_has_link_or_reparse",
        lambda path, _root: path.name == "nova_state",
    )

    with pytest.raises(ModelNetworkMediatorError, match="reparse point"):
        bootstrap._verified_evidence_target()


def test_publisher_attestation_is_cached_only_for_same_process(monkeypatch, tmp_path):
    executable = tmp_path / "Programs" / "Ollama" / "ollama.exe"
    executable.parent.mkdir(parents=True)
    executable.write_bytes(b"signed fixture")
    creation_time = [1741132800.0]
    signature_checks = []

    class _Connection:
        status = bootstrap.psutil.CONN_LISTEN
        laddr = type("_Address", (), {"ip": "127.0.0.1", "port": 11434})()
        pid = 4812

    class _Process:
        pid = 4812

        def exe(self):
            return str(executable)

        def cmdline(self):
            return [str(executable), "serve"]

        def create_time(self):
            return creation_time[0]

    monkeypatch.setattr(bootstrap, "_is_windows", lambda: True)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(
        bootstrap,
        "_ollama_authenticode_is_valid",
        lambda path: signature_checks.append(path) or True,
    )
    monkeypatch.setattr(
        bootstrap.psutil, "net_connections", lambda **_kwargs: [_Connection()]
    )
    monkeypatch.setattr(bootstrap.psutil, "Process", lambda _pid: _Process())
    monkeypatch.setattr(bootstrap, "_ATTESTED_PROCESS", None)

    bootstrap._attest_ollama_listener()
    bootstrap._attest_ollama_listener()
    assert len(signature_checks) == 1

    creation_time[0] += 1
    bootstrap._attest_ollama_listener()
    assert len(signature_checks) == 2


def test_failed_evidence_write_denies_before_connection(monkeypatch):
    mediator, sink = _mediator(monkeypatch, _Sink(fail=True))
    with pytest.raises(ModelNetworkMediatorError, match="evidence_write_failed"):
        _approve(mediator, "http://localhost:11434/api/show", "POST", {"model": "gemma2:2b"})
    assert not sink.events


def test_unsupported_payload_model_and_credentials_are_denied(monkeypatch):
    mediator, sink = _mediator(monkeypatch)
    for payload in (
        {"model": "other:model"},
        {"model": "gemma2:2b", "prompt": "injected"},
        {"model": "gemma2:2b", "messages": [], "stream": False, "options": {}},
    ):
        with pytest.raises(ModelNetworkMediatorError):
            _approve(mediator, "http://localhost:11434/api/show", "POST", payload)
    assert not sink.events


def test_default_mediator_without_policy_and_evidence_remains_fail_closed(monkeypatch):
    mediator = ModelNetworkMediator()
    with pytest.raises(ModelNetworkMediatorError):
        _approve(mediator, "http://127.0.0.1:11434/api/show", "POST", {"model": "gemma2:2b"})


def test_provider_status_probe_uses_exact_verified_tags_request(monkeypatch):
    calls = []

    class _Mediator:
        def request_json(self, **kwargs):
            calls.append(kwargs)
            return type("_Response", (), {"status_code": 200})()

    monkeypatch.setattr(
        bootstrap,
        "build_local_ollama_mediator",
        lambda base_url, model: (
            calls.append({"bootstrap": (base_url, model)}) or _Mediator()
        ),
    )

    assert bootstrap.verified_local_ollama_status(
        base_url="http://localhost:11434",
        model="gemma2:2b",
        request_id="provider-status-test",
        session_id="session-test",
    )
    assert calls == [
        {"bootstrap": ("http://localhost:11434", "gemma2:2b")},
        {
            "method": "GET",
            "url": "http://localhost:11434/api/tags",
            "timeout": 2.0,
            "request_id": "provider-status-test",
            "session_id": "session-test",
        },
    ]


def test_provider_status_probe_has_no_direct_fallback_after_denial(monkeypatch):
    attempts = []

    class _DeniedMediator:
        def request_json(self, **kwargs):
            attempts.append(kwargs)
            raise ModelNetworkMediatorError("identity unavailable")

    monkeypatch.setattr(
        bootstrap,
        "build_local_ollama_mediator",
        lambda _base_url, _model: _DeniedMediator(),
    )

    assert not bootstrap.verified_local_ollama_status(
        base_url="http://localhost:11434",
        model="gemma2:2b",
        request_id="provider-status-test",
        session_id="session-test",
    )
    assert len(attempts) == 1


def test_startup_status_reports_offline_only_after_trust_preflight(monkeypatch):
    monkeypatch.setattr(
        bootstrap.VerifiedLoopbackOllamaMediator,
        "_strict_url",
        lambda url, method: url,
    )
    monkeypatch.setattr(bootstrap, "_verified_evidence_target", lambda: object())
    monkeypatch.setattr(bootstrap, "_ollama_listener_is_absent", lambda: True)
    monkeypatch.setattr(
        bootstrap,
        "verified_local_ollama_status",
        lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("an absent listener must not be probed")
        ),
    )

    result = bootstrap.verified_local_ollama_startup_status(
        base_url="http://127.0.0.1:11434",
        model="gemma2:2b",
        request_id="startup-test",
        session_id="startup-daemon",
    )
    assert result is bootstrap.LocalOllamaStartupStatus.OFFLINE


def test_startup_status_denies_when_evidence_preflight_fails(monkeypatch):
    monkeypatch.setattr(
        bootstrap.VerifiedLoopbackOllamaMediator,
        "_strict_url",
        lambda url, method: url,
    )
    monkeypatch.setattr(
        bootstrap,
        "_verified_evidence_target",
        lambda: (_ for _ in ()).throw(
            ModelNetworkMediatorError("evidence unavailable")
        ),
    )
    monkeypatch.setattr(
        bootstrap,
        "_ollama_listener_is_absent",
        lambda: (_ for _ in ()).throw(
            AssertionError("denial must stop before listener inspection")
        ),
    )

    result = bootstrap.verified_local_ollama_startup_status(
        base_url="http://127.0.0.1:11434",
        model="gemma2:2b",
        request_id="startup-test",
        session_id="startup-daemon",
    )
    assert result is bootstrap.LocalOllamaStartupStatus.DENIED


def test_startup_status_denies_invalid_destination_before_local_checks(monkeypatch):
    monkeypatch.setattr(
        bootstrap,
        "_verified_evidence_target",
        lambda: (_ for _ in ()).throw(
            AssertionError("invalid destination must stop before evidence inspection")
        ),
    )

    result = bootstrap.verified_local_ollama_startup_status(
        base_url="https://example.com:11434",
        model="gemma2:2b",
        request_id="startup-test",
        session_id="startup-daemon",
    )
    assert result is bootstrap.LocalOllamaStartupStatus.DENIED


def test_startup_status_fails_closed_on_unexpected_preflight_error(monkeypatch):
    monkeypatch.setattr(
        bootstrap.VerifiedLoopbackOllamaMediator,
        "_strict_url",
        lambda url, method: url,
    )
    monkeypatch.setattr(
        bootstrap,
        "_verified_evidence_target",
        lambda: (_ for _ in ()).throw(OSError("storage unavailable")),
    )

    result = bootstrap.verified_local_ollama_startup_status(
        base_url="http://127.0.0.1:11434",
        model="gemma2:2b",
        request_id="startup-test",
        session_id="startup-daemon",
    )
    assert result is bootstrap.LocalOllamaStartupStatus.DENIED


def test_startup_status_uses_verified_probe_when_listener_exists(monkeypatch):
    monkeypatch.setattr(
        bootstrap.VerifiedLoopbackOllamaMediator,
        "_strict_url",
        lambda url, method: url,
    )
    monkeypatch.setattr(bootstrap, "_verified_evidence_target", lambda: object())
    monkeypatch.setattr(bootstrap, "_ollama_listener_is_absent", lambda: False)
    calls = []
    monkeypatch.setattr(
        bootstrap,
        "verified_local_ollama_status",
        lambda **kwargs: (calls.append(kwargs) or True),
    )

    result = bootstrap.verified_local_ollama_startup_status(
        base_url="http://127.0.0.1:11434",
        model="gemma2:2b",
        request_id="startup-test",
        session_id="startup-daemon",
    )
    assert result is bootstrap.LocalOllamaStartupStatus.AVAILABLE
    assert len(calls) == 1
