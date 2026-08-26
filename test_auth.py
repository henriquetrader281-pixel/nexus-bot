import auth


def test_password_requires_configuration(monkeypatch):
    monkeypatch.delenv("NEXUS_PASSWORD", raising=False)
    assert auth.check_password("admin") is False


def test_password_matches_without_exposing_default(monkeypatch):
    monkeypatch.setenv("NEXUS_PASSWORD", "senha-segura-de-teste")
    assert auth.check_password("senha-segura-de-teste") is True
    assert auth.check_password("admin") is False


def test_streamlit_secret_takes_precedence(monkeypatch):
    monkeypatch.setenv("NEXUS_PASSWORD", "senha-do-ambiente")
    monkeypatch.setattr(auth, "_streamlit_secret", lambda name: "senha-do-streamlit")
    assert auth.configured_password() == "senha-do-streamlit"
    assert auth.check_password("senha-do-streamlit") is True
