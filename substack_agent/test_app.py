import sys
from unittest.mock import Mock

from app import generate_post, main


def test_generate_post_passes_selected_model(monkeypatch):
    calls = {}

    def fake_research(topic, audience, tone, model):
        calls["research"] = model
        return "research"

    def fake_edit(topic, research, model):
        calls["edit"] = model
        return "editorial"

    def fake_write(topic, audience, tone, research, editorial_notes, model):
        calls["write"] = model
        return "article"

    monkeypatch.setattr("app.research_topic", fake_research)
    monkeypatch.setattr("app.edit_research_brief", fake_edit)
    monkeypatch.setattr("app.write_post", fake_write)

    result = generate_post("AI in dev teams", model="gpt-4o")

    assert result["article"] == "article"
    assert calls == {"research": "gpt-4o", "edit": "gpt-4o", "write": "gpt-4o"}


def test_main_uses_model_flag(monkeypatch, capsys):
    calls = {}

    def fake_research(topic, audience, tone, model):
        calls["research"] = model
        return "research"

    def fake_edit(topic, research, model):
        calls["edit"] = model
        return "editorial"

    def fake_write(topic, audience, tone, research, editorial_notes, model):
        calls["write"] = model
        return "article"

    monkeypatch.setattr("app.research_topic", fake_research)
    monkeypatch.setattr("app.edit_research_brief", fake_edit)
    monkeypatch.setattr("app.write_post", fake_write)
    monkeypatch.setattr(sys, "argv", ["app.py", "--topic", "AI in teams", "--model", "gpt-4o"])

    main()

    captured = capsys.readouterr().out
    assert "=== RESEARCH BRIEF ===" in captured
    assert calls == {"research": "gpt-4o", "edit": "gpt-4o", "write": "gpt-4o"}
