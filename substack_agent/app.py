from __future__ import annotations

import argparse
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template_string, request


PROJECT_ROOT = Path(__file__).resolve().parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
load_dotenv(PROJECT_ROOT / ".env")
app = Flask(__name__)


def load_prompt(prompt_name: str) -> str:
    path = PROMPTS_DIR / f"{prompt_name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Missing prompt file: {path}")
    return path.read_text(encoding="utf-8").strip()


@lru_cache(maxsize=1)
def get_janus_model():
    from transformers import AutoModelForCausalLM
    from janus.models import VLChatProcessor

    model_name = "deepseek-ai/Janus-Pro-7B"
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise RuntimeError("HF_TOKEN is not set in the project .env file.")

    processor = VLChatProcessor.from_pretrained(model_name, token=hf_token)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        token=hf_token,
        trust_remote_code=True,
    )
    model.eval()
    return processor, model


def extract_text(response) -> str:
    if hasattr(response, "output_text") and response.output_text:
        return response.output_text.strip()

    chunks: list[str] = []
    for item in getattr(response, "output", []):
        for content in getattr(item, "content", []):
            text = getattr(content, "text", None)
            if text:
                chunks.append(text)

    joined = "\n".join(chunks).strip()
    if joined:
        return joined

    return str(response).strip()


def generate_with_janus(prompt: str) -> str:
    import torch

    processor, model = get_janus_model()
    conversation = [
        {"role": "<|User|>", "content": prompt, "images": []},
        {"role": "<|Assistant|>", "content": ""},
    ]
    inputs = processor(conversations=conversation, images=None, force_batchify=True).to(model.device)
    inputs_embeds = model.prepare_inputs_embeds(**inputs)

    with torch.inference_mode():
        output = model.language_model.generate(
            inputs_embeds=inputs_embeds,
            attention_mask=inputs.attention_mask,
            pad_token_id=processor.tokenizer.eos_token_id,
            bos_token_id=processor.tokenizer.bos_token_id,
            eos_token_id=processor.tokenizer.eos_token_id,
            max_new_tokens=1200,
            do_sample=True,
            temperature=0.7,
            use_cache=True,
        )

    return processor.tokenizer.decode(output[0].cpu().tolist(), skip_special_tokens=True).strip()


def generate_with_prompt(system_prompt: str, user_prompt: str, model: str = "deepseek-ai/Janus-Pro-7B") -> str:
    prompt = f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"
    return generate_with_janus(prompt)


def research_topic(topic: str, audience: str, tone: str, model: str = "deepseek-ai/Janus-Pro-7B") -> str:
    template = load_prompt("researcher")
    prompt = template.format(topic=topic, audience=audience, tone=tone)
    system_prompt = (
        "You are a careful technology researcher and editorial strategist. "
        "Your job is to identify the strongest angle, key arguments, evidence, and compelling examples for a thoughtful Substack post about technology, AI, or software engineering."
    )
    return generate_with_prompt(system_prompt, prompt, model=model)


def edit_research_brief(topic: str, research: str, model: str = "deepseek-ai/Janus-Pro-7B") -> str:
    template = load_prompt("editor")
    prompt = template.format(topic=topic, research=research)
    system_prompt = (
        "You are an experienced editor for high-signal technology writing. "
        "Turn research into a clean, persuasive, and readable editorial plan for a Substack audience."
    )
    return generate_with_prompt(system_prompt, prompt, model=model)


def write_post(topic: str, audience: str, tone: str, research: str, editorial_notes: str, model: str = "deepseek-ai/Janus-Pro-7B") -> str:
    template = load_prompt("writer")
    prompt = template.format(
        topic=topic,
        audience=audience,
        tone=tone,
        research=research,
        editorial_notes=editorial_notes,
    )
    system_prompt = (
        "You are a world-class technology writer. Write a polished, Substack-ready post that is insightful, practical, and highly readable. "
        "Focus on signal over hype and make the argument feel grounded in real engineering and product reality."
    )
    return generate_with_prompt(system_prompt, prompt, model=model)


def generate_post(
    topic: str,
    audience: str = "software engineers, founders, and curious builders",
    tone: str = "sharp and thoughtful",
    model: str = "deepseek-ai/Janus-Pro-7B",
) -> dict[str, str]:
    research = research_topic(topic, audience, tone, model=model)
    editorial_notes = edit_research_brief(topic, research, model=model)
    article = write_post(topic, audience, tone, research, editorial_notes, model=model)
    return {
        "topic": topic,
        "research": research,
        "editorial_notes": editorial_notes,
        "article": article,
    }


def slugify(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
    slug = "-".join(part for part in slug.split("-") if part)
    return slug or "draft"


def export_substack_markdown(result: dict[str, str]) -> str:
    article_lines = result["article"].strip().splitlines()
    title = article_lines[0].strip() if article_lines else result["topic"].strip()
    body = "\n".join(article_lines[1:]).strip() if len(article_lines) > 1 else result["article"].strip()

    return (
        f"---\n"
        f"title: {title}\n"
        f"subtitle: {result['topic']}\n"
        f"---\n\n"
        f"{body}\n"
    )


def save_draft(result: dict[str, str], output_dir: str = "output") -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    slug = slugify(result["topic"])
    file_path = directory / f"{slug}.md"
    payload = export_substack_markdown(result)
    payload += "\n## Research brief\n\n"
    payload += result["research"].strip() + "\n\n"
    payload += "## Editorial notes\n\n"
    payload += result["editorial_notes"].strip() + "\n\n"
    file_path.write_text(payload, encoding="utf-8")
    return file_path


def save_drafts(results: list[dict[str, str]], output_dir: str = "output") -> list[Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    saved: list[Path] = []
    for index, result in enumerate(results, start=1):
        topic_slug = slugify(result["topic"])
        final_slug = f"{topic_slug}-{index}" if len(results) > 1 else topic_slug
        file_path = directory / f"{final_slug}.md"
        payload = export_substack_markdown(result)
        payload += "\n## Research brief\n\n"
        payload += result["research"].strip() + "\n\n"
        payload += "## Editorial notes\n\n"
        payload += result["editorial_notes"].strip() + "\n\n"
        file_path.write_text(payload, encoding="utf-8")
        saved.append(file_path)
    return saved


def generate_variants(
    topic: str,
    audience: str = "software engineers, founders, and curious builders",
    tone: str = "sharp and thoughtful",
    model: str = "deepseek-ai/Janus-Pro-7B",
    count: int = 3,
) -> list[dict[str, str]]:
    variants: list[dict[str, str]] = []
    for index in range(count):
        variant_topic = f"{topic} (Angle {index + 1})" if count > 1 else topic
        variants.append(generate_post(variant_topic, audience=audience, tone=tone, model=model))
    return variants


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Substack-ready technology article from a topic.")
    parser.add_argument("--topic", default="AI agents are changing software engineering and creative work", help="Core idea for the article")
    parser.add_argument("--audience", default="software engineers, founders, and curious builders", help="Who the article is written for")
    parser.add_argument("--tone", default="sharp and thoughtful", help="Writing tone")
    parser.add_argument("--model", default="deepseek-ai/Janus-Pro-7B", help="Hugging Face or OpenAI model to use")
    parser.add_argument("--serve", action="store_true", help="Run the browser UI instead of the CLI output")
    parser.add_argument("--host", default="127.0.0.1", help="Host for the web UI")
    parser.add_argument("--port", type=int, default=8000, help="Port for the web UI")
    parser.add_argument("--output-dir", default="output", help="Directory for saved draft markdown files")
    parser.add_argument("--variants", type=int, default=3, help="Number of article angles to generate and save")
    return parser.parse_args()


@app.route("/", methods=["GET", "POST"])
def index():
    form_html = """
    <!doctype html>
    <html>
      <head>
        <title>Substack Agent</title>
        <style>
          body { font-family: Arial, sans-serif; max-width: 980px; margin: 40px auto; padding: 0 20px; color: #111827; }
          h1 { margin-bottom: 16px; }
          form { display: grid; gap: 16px; }
          label { display: grid; gap: 6px; font-weight: 600; }
          input, textarea, select { width: 100%; padding: 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 16px; }
          textarea { min-height: 120px; }
          button { background: #111827; color: white; border: none; border-radius: 8px; padding: 12px 18px; font-size: 16px; cursor: pointer; }
          .result { margin-top: 32px; padding: 20px; border: 1px solid #e5e7eb; border-radius: 12px; background: #f9fafb; }
          .result h2 { margin-top: 0; }
          .section { margin-top: 24px; }
          pre { white-space: pre-wrap; word-wrap: break-word; font-family: inherit; }
        </style>
      </head>
      <body>
        <h1>Substack AI Agent</h1>
        <form method="post">
          <label>
            Topic
            <textarea name="topic" placeholder="AI agents are changing software engineering and creative work">{{ topic or '' }}</textarea>
          </label>
          <label>
            Audience
            <input name="audience" value="{{ audience or 'software engineers, founders, and curious builders' }}" />
          </label>
          <label>
            Tone
            <input name="tone" value="{{ tone or 'sharp and thoughtful' }}" />
          </label>
          <label>
            Model
                        <select name="model">
                            <option value="deepseek-ai/Janus-Pro-7B" {% if model == 'deepseek-ai/Janus-Pro-7B' %}selected{% endif %}>deepseek-ai/Janus-Pro-7B (local)</option>
              <option value="gpt-4.1-mini" {% if model == 'gpt-4.1-mini' %}selected{% endif %}>gpt-4.1-mini</option>
              <option value="gpt-4o-mini" {% if model == 'gpt-4o-mini' %}selected{% endif %}>gpt-4o-mini</option>
              <option value="gpt-4o" {% if model == 'gpt-4o' %}selected{% endif %}>gpt-4o</option>
            </select>
          </label>
          <button type="submit">Generate article</button>
        </form>

        {% if result %}
        <div class="result">
          <h2>Research brief</h2>
          <pre>{{ result['research'] }}</pre>

          <div class="section">
            <h2>Editorial notes</h2>
            <pre>{{ result['editorial_notes'] }}</pre>
          </div>

          <div class="section">
            <h2>Final post</h2>
            <pre>{{ result['article'] }}</pre>
          </div>

          <div class="section">
            <p><strong>Draft saved to:</strong> {{ saved_path or 'not yet saved' }}</p>
          </div>
        </div>
        {% endif %}
      </body>
    </html>
    """

    if request.method == "POST":
        topic = (request.form.get("topic") or "").strip()
        audience = (request.form.get("audience") or "software engineers, founders, and curious builders").strip()
        tone = (request.form.get("tone") or "sharp and thoughtful").strip()
        model = (request.form.get("model") or "deepseek-ai/Janus-Pro-7B").strip()

        if not topic:
            return render_template_string(form_html, topic="", audience=audience, tone=tone, model=model, result=None, saved_path=None)

        result = generate_post(topic=topic, audience=audience, tone=tone, model=model)
        draft_path = save_draft(result, output_dir="output")
        return render_template_string(form_html, topic=topic, audience=audience, tone=tone, model=model, result=result, saved_path=str(draft_path))

    return render_template_string(form_html, topic="", audience="software engineers, founders, and curious builders", tone="sharp and thoughtful", model="deepseek-ai/Janus-Pro-7B", result=None, saved_path=None)


def main() -> None:
    args = parse_args()

    if args.serve:
        app.run(host=args.host, port=args.port, debug=False)
        return

    variants = generate_variants(
        topic=args.topic,
        audience=args.audience,
        tone=args.tone,
        model=args.model,
        count=max(1, args.variants),
    )

    saved_paths = save_drafts(variants, output_dir=args.output_dir)
    primary = variants[0]

    print("=== RESEARCH BRIEF ===\n")
    print(primary["research"])
    print("\n=== EDITORIAL NOTES ===\n")
    print(primary["editorial_notes"])
    print("\n=== FINAL POST ===\n")
    print(primary["article"])
    print("\n=== DRAFTS SAVED ===")
    for draft_path in saved_paths:
        print(draft_path)


if __name__ == "__main__":
    main()