import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import generate_post, generate_variants, main


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


def test_generate_variants_creates_requested_count(monkeypatch):
    calls = []

    def fake_generate_post(topic, audience, tone, model):
        calls.append(topic)
        return {
            "topic": topic,
            "research": "research",
            "editorial_notes": "editorial",
            "article": f"article-{len(calls)}",
        }

    monkeypatch.setattr("app.generate_post", fake_generate_post)

    variants = generate_variants("AI agents", count=3, model="gpt-4o")

    assert len(variants) == 3
    assert len(calls) == 3
    assert variants[0]["topic"].endswith("Angle 1")


def test_main_uses_model_flag_and_saves_variants(monkeypatch, capsys, tmp_path):
    calls = {}

    def fake_generate_post(topic, audience, tone, model):
        calls.setdefault("models", []).append(model)
        return {
            "topic": topic,
            "research": "research",
            "editorial_notes": "editorial",
            "article": "article",
        }

    monkeypatch.setattr("app.generate_variants", lambda **kwargs: [
        {"topic": "AI agents", "research": "research", "editorial_notes": "editorial", "article": "article"},
        {"topic": "AI agents", "research": "research", "editorial_notes": "editorial", "article": "article"},
    ])
    monkeypatch.setattr("app.save_drafts", lambda results, output_dir: [tmp_path / "one.md", tmp_path / "two.md"])
    monkeypatch.setattr(sys, "argv", ["app.py", "--topic", "AI in teams", "--model", "gpt-4o", "--variants", "2", "--output-dir", str(tmp_path)])

    main()

    captured = capsys.readouterr().out
    assert "=== RESEARCH BRIEF ===" in captured
    assert "=== DRAFTS SAVED ===" in captured
