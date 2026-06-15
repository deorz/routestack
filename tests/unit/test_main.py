import main


def test_run_server_uses_settings_for_uvicorn(monkeypatch) -> None:
    monkeypatch.setenv("ROUTESTACK_SERVER_HOST", "127.0.0.1")
    monkeypatch.setenv("ROUTESTACK_SERVER_PORT", "9000")

    captured: dict[str, object] = {}

    def fake_run(**kwargs: object) -> None:
        captured.update(kwargs)

    monkeypatch.setattr(main.uvicorn, "run", fake_run)

    main.run_server()

    assert captured == {
        "app": "presentation.http.app:create_app",
        "factory": True,
        "host": "127.0.0.1",
        "port": 9000,
    }
