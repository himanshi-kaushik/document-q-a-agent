from types import SimpleNamespace

import pytest

from app import llm


class FakeModel:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    def invoke(self, messages):
        if self.error:
            raise self.error

        return SimpleNamespace(content=self.response)


def test_fallback_model_is_used_when_primary_fails(monkeypatch):
    requested_models = []

    def fake_get_llm(model_name):
        requested_models.append(model_name)

        if model_name == "primary-model":
            return FakeModel(error=RuntimeError("Primary unavailable"))

        return FakeModel(response="Fallback answer")

    monkeypatch.setenv("OPENROUTER_MODEL", "primary-model")
    monkeypatch.setenv("OPENROUTER_FALLBACK_MODEL", "fallback-model")
    monkeypatch.setattr(llm, "get_llm", fake_get_llm)

    response = llm.invoke_with_fallback("Question")

    assert response.content == "Fallback answer"
    assert requested_models == ["primary-model", "fallback-model"]


def test_primary_error_is_raised_without_fallback(monkeypatch):
    monkeypatch.setenv("OPENROUTER_MODEL", "primary-model")
    monkeypatch.delenv("OPENROUTER_FALLBACK_MODEL", raising=False)
    monkeypatch.setattr(
        llm,
        "get_llm",
        lambda model_name: FakeModel(error=RuntimeError("Unavailable")),
    )

    with pytest.raises(RuntimeError, match="Unavailable"):
        llm.invoke_with_fallback("Question")
