from app.services.oracle_service import OracleService


def test_transform_uses_oracle_styled_prefix(monkeypatch) -> None:
    monkeypatch.setattr("app.services.oracle_service.random.choice", lambda _: "Signs indicate...")

    output = OracleService.transform("The answer is near.")

    assert output == "Signs indicate... The answer is near."


def test_transform_handles_empty_ai_response(monkeypatch) -> None:
    monkeypatch.setattr("app.services.oracle_service.random.choice", lambda _: "The system whispers...")

    output = OracleService.transform("   \n  ")

    assert output == "The system whispers... silence moves through the circuit."

