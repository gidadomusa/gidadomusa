from __future__ import annotations

import argparse
import os
from pathlib import Path

from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"


def load_prompt(prompt_name: str) -> str:
    path = PROMPTS_DIR / f"{prompt_name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Missing prompt file: {path}")
    return path.read_text(encoding="utf-8").strip()


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Export it in your shell before running this script."
        )
    return OpenAI(api_key=api_key)


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


def generate_with_prompt(system_prompt: str, user_prompt: str, model: str = "gpt-4.1-mini") -> str:
    client = get_client()
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return extract_text(response)


def research_topic(topic: str, audience: str, tone: str) -> str:
    template = load_prompt("researcher")
    prompt = template.format(topic=topic, audience=audience, tone=tone)
    system_prompt = (
        "You are a careful technology researcher and editorial strategist. "
        "Your job is to identify the strongest angle, key arguments, evidence, and compelling examples for a thoughtful Substack post about technology, AI, or software engineering."
    )
    return generate_with_prompt(system_prompt, prompt)


def edit_research_brief(topic: str, research: str) -> str:
    template = load_prompt("editor")
    prompt = template.format(topic=topic, research=research)
    system_prompt = (
        "You are an experienced editor for high-signal technology writing. "
        "Turn research into a clean, persuasive, and readable editorial plan for a Substack audience."
    )
    return generate_with_prompt(system_prompt, prompt)


def write_post(topic: str, audience: str, tone: str, research: str, editorial_notes: str) -> str:
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
    return generate_with_prompt(system_prompt, prompt)


def generate_post(topic: str, audience: str = "software engineers, founders, and curious builders", tone: str = "sharp and thoughtful") -> dict[str, str]:
    research = research_topic(topic, audience, tone)
    editorial_notes = edit_research_brief(topic, research)
    article = write_post(topic, audience, tone, research, editorial_notes)
    return {
        "topic": topic,
        "research": research,
        "editorial_notes": editorial_notes,
        "article": article,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Substack-ready technology article from a topic.")
    parser.add_argument("--topic", default="AI agents are changing software engineering and creative work", help="Core idea for the article")
    parser.add_argument("--audience", default="software engineers, founders, and curious builders", help="Who the article is written for")
    parser.add_argument("--tone", default="sharp and thoughtful", help="Writing tone")
    parser.add_argument("--model", default="gpt-4.1-mini", help="OpenAI model to use")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    research = research_topic(args.topic, args.audience, args.tone)
    editorial_notes = edit_research_brief(args.topic, research)
    article = write_post(args.topic, args.audience, args.tone, research, editorial_notes)

    print("=== RESEARCH BRIEF ===\n")
    print(research)
    print("\n=== EDITORIAL NOTES ===\n")
    print(editorial_notes)
    print("\n=== FINAL POST ===\n")
    print(article)


if __name__ == "__main__":
    main()