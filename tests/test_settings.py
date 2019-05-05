from elmo.conf.settings import Settings


def test_default_is_invalid():
    """Without defining env vars settings must be invalid"""
    settings = Settings()
    is_valid, errors = settings.is_valid(raise_exception=False)
    assert is_valid is False
