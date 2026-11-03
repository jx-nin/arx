from pathlib import Path

import pytest
from pydantic import ValidationError

from arx.settings import DatabaseSettings, Settings

REQUIRED = {
    "ARX_SMTP_USERNAME": "arx.sender@gmail.com",
    "ARX_DELIVERY_FROM": "arx.sender@gmail.com",
    "ARX_DELIVERY_ALLOWED_RECIPIENTS": "reader@kindle.com",
}


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    for name, value in REQUIRED.items():
        monkeypatch.setenv(name, value)
    return monkeypatch


def load() -> Settings:
    return Settings(_env_file=None)  # type: ignore[call-arg]


@pytest.mark.req("FR-DLV-02")
@pytest.mark.req("FR-DLV-03")
def test_defaults_follow_the_gmail_decision(env: pytest.MonkeyPatch) -> None:
    settings = load()

    assert settings.smtp_host == "smtp.gmail.com"
    assert settings.smtp_port == 587
    assert settings.smtp_password_file == Path("/run/secrets/smtp_password")
    assert settings.delivery_max_bytes == 20 * 1024 * 1024


@pytest.mark.req("FR-DLV-07")
def test_allowed_recipients_are_comma_separated_and_normalised(
    env: pytest.MonkeyPatch,
) -> None:
    env.setenv(
        "ARX_DELIVERY_ALLOWED_RECIPIENTS", " Reader@Kindle.com, other@kindle.com"
    )

    assert load().delivery_allowed_recipients == frozenset(
        {"reader@kindle.com", "other@kindle.com"}
    )


@pytest.mark.req("FR-DLV-02")
def test_rejects_recipients_outside_kindle_com(env: pytest.MonkeyPatch) -> None:
    env.setenv("ARX_DELIVERY_ALLOWED_RECIPIENTS", "reader@kindle.com,me@gmail.com")

    with pytest.raises(ValidationError, match=r"me@gmail\.com"):
        load()


@pytest.mark.req("FR-DLV-02")
def test_checks_recipients_passed_to_the_constructor(env: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValidationError, match=r"me@gmail\.com"):
        Settings(  # type: ignore[call-arg]
            _env_file=None, delivery_allowed_recipients=frozenset({"me@gmail.com"})
        )


@pytest.mark.req("FR-DLV-07")
def test_rejects_an_empty_allowlist(env: pytest.MonkeyPatch) -> None:
    env.setenv("ARX_DELIVERY_ALLOWED_RECIPIENTS", " , ")

    with pytest.raises(ValidationError, match="at least one"):
        load()


def test_reads_settings_from_an_env_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    for name in REQUIRED:
        monkeypatch.delenv(name, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "".join(f"{name}={value}\n" for name, value in REQUIRED.items())
        + "ARX_DELIVERY_MAX_BYTES=1000\n"
    )

    settings = Settings(_env_file=env_file)  # type: ignore[call-arg]

    assert settings.delivery_from == "arx.sender@gmail.com"
    assert settings.delivery_max_bytes == 1000


@pytest.mark.req("NFR-16")
def test_arxiv_requests_default_to_three_seconds_apart(
    env: pytest.MonkeyPatch,
) -> None:
    settings = load()

    assert settings.arxiv_min_interval_s == 3.0
    assert settings.arxiv_user_agent is None


@pytest.mark.req("NFR-16")
def test_arxiv_interval_cannot_be_negative(env: pytest.MonkeyPatch) -> None:
    env.setenv("ARX_ARXIV_MIN_INTERVAL_S", "-1")

    with pytest.raises(ValidationError, match="arxiv_min_interval_s"):
        load()


def test_database_settings_need_no_delivery_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in REQUIRED:
        monkeypatch.delenv(name, raising=False)

    settings = DatabaseSettings(_env_file=None)  # type: ignore[call-arg]

    assert settings.database_url_file == Path("/run/secrets/database_url")


def test_database_url_file_is_read_from_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ARX_DATABASE_URL_FILE", "/tmp/db_url")

    settings = DatabaseSettings(_env_file=None)  # type: ignore[call-arg]

    assert settings.database_url_file == Path("/tmp/db_url")


def test_both_settings_share_one_env_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    for name in REQUIRED:
        monkeypatch.delenv(name, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "".join(f"{name}={value}\n" for name, value in REQUIRED.items())
        + "ARX_DATABASE_URL_FILE=/tmp/db_url\n"
    )

    settings = Settings(_env_file=env_file)  # type: ignore[call-arg]
    database = DatabaseSettings(_env_file=env_file)  # type: ignore[call-arg]

    assert settings.delivery_from == "arx.sender@gmail.com"
    assert database.database_url_file == Path("/tmp/db_url")
