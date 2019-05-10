from importlib import reload

from elmo import conf


def test_default_is_invalid():
    """Settings are invalid if env vars are not set"""
    settings = conf.Settings()
    is_valid, errors = settings.is_valid(raise_exception=False)
    assert is_valid is False


def test_environment_variables(monkeypatch):
    """Settings are valid if env vars are set"""
    with monkeypatch.context() as m:
        # create the test environment
        m.setenv("ELMO_BASE_URL", "https://example.com")
        m.setenv("ELMO_VENDOR", "test")
        reload(conf)
    try:
        settings = conf.Settings()
        is_valid, errors = settings.is_valid(raise_exception=False)
        assert settings.base_url == "https://example.com"
        assert settings.vendor == "test"
        assert is_valid is True
    finally:
        reload(conf)
