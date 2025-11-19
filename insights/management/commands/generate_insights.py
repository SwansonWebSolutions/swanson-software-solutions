import json
import os
import random
import uuid
from datetime import datetime
from typing import Iterable, List

from django.core.management.base import BaseCommand, CommandError

from openai import OpenAI

from insights.models import Insight


class Command(BaseCommand):
    help = "Generate AI-written insights and store them in the database."

    AVAILABLE_TOPICS = [
        Insight.TOPIC_MARKETING,
        Insight.TOPIC_WEB_DEV,
        Insight.TOPIC_IOS,
        Insight.TOPIC_ECOMMERCE,
        Insight.TOPIC_DATA_PRIVACY,
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--mode",
            choices=["random", "order", "choice"],
            default="random",
            help="Topic selection: random, cycling order, or explicit choice.",
        )
        parser.add_argument(
            "--topic",
            choices=self.AVAILABLE_TOPICS,
            help="Topic slug when --mode=choice.",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=1,
            help="Number of insights to generate.",
        )
        parser.add_argument(
            "--model",
            default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            help="OpenAI model to use (default from OPENAI_MODEL or gpt-4o-mini).",
        )

    def handle(self, *args, **options):
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_API_KEY")
        if not api_key:
            raise CommandError("OPENAI_API_KEY is required in environment/.env")

        count = options["count"]
        mode = options["mode"]
        topic = options.get("topic")
        model = options["model"]

        if count < 1:
            raise CommandError("--count must be at least 1")

        topics = list(self.topic_sequence(mode, topic, count))

        client = OpenAI(api_key=api_key)
        created: List[Insight] = []
        for topic_slug in topics:
            payload = self.generate_for_topic(client, model, topic_slug)
            insight = Insight.objects.create(
                title=payload["title"],
                description=payload["description"],
                topic=topic_slug,
            )
            created.append(insight)
            self.stdout.write(self.style.SUCCESS(f"Created insight: {insight.title} ({topic_slug})"))

        return f"Generated {len(created)} insights."

    def topic_sequence(self, mode: str, topic: str | None, count: int) -> Iterable[str]:
        if mode == "choice":
            if not topic:
                raise CommandError("--topic is required when --mode=choice")
            for _ in range(count):
                yield topic
        elif mode == "order":
            idx = 0
            for _ in range(count):
                yield self.AVAILABLE_TOPICS[idx % len(self.AVAILABLE_TOPICS)]
                idx += 1
        else:  # random
            for _ in range(count):
                yield random.choice(self.AVAILABLE_TOPICS)

    def generate_for_topic(self, client: OpenAI, model: str, topic: str) -> dict:
        uniqueness_hint = str(uuid.uuid4())
        current_year = datetime.utcnow().year
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert copywriter creating concise, unique insights for a company website. "
                        "Always return JSON with keys: title (<=120 characters) and description (<=400 words). "
                        "Avoid repetition across requests; each response must be substantially unique."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Topic: {topic}. Write a short article with a strong title and a 300-400 word or shorter paragraph. "
                        f"Make it SEO-friendly and unique. Uniqueness hint: {uniqueness_hint}. "
                        f"The current year is {current_year}. Output ONLY JSON without code fences."
                    ),
                },
            ],
            temperature=0.9,
        )

        message = response.choices[0].message.content or ""
        payload = self._parse_json_payload(message)

        if not payload.get("title") or not payload.get("description"):
            raise CommandError(f"Response missing title/description: {payload}")
        return payload

    def _parse_json_payload(self, message: str) -> dict:
        trimmed = message.strip()
        # Remove code fences if present
        if trimmed.startswith("```"):
            lines = [ln for ln in trimmed.splitlines() if not ln.strip().startswith("```")]
            trimmed = "\n".join(lines).strip()

        try:
            return json.loads(trimmed)
        except json.JSONDecodeError:
            # Try to extract JSON object substring
            start = trimmed.find("{")
            end = trimmed.rfind("}")
            if start != -1 and end != -1 and end > start:
                snippet = trimmed[start : end + 1]
                return json.loads(snippet)
            raise CommandError(f"Unexpected response format: {message}")
