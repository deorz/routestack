from presentation.http import cli


def test_http_cli_uses_settings_for_uvicorn(monkeypatch) -> None:
    monkeypatch.setenv("ROUTESTACK_SERVER_HOST", "127.0.0.1")
    monkeypatch.setenv("ROUTESTACK_SERVER_PORT", "9000")

    captured: dict[str, object] = {}

    def fake_run(app: str, **kwargs: object) -> None:
        captured["app"] = app
        captured.update(kwargs)

    monkeypatch.setattr(cli.uvicorn, "run", fake_run)

    cli.run()

    assert captured["app"] == "presentation.http.app:create_app"
    assert captured["factory"] is True
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 9000
