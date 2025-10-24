from __future__ import annotations

import itertools
import math
import textwrap
from typing import Iterable, List

from .models import Scene


class ScriptGenerator:
    """Deterministic script generator that mimics an LLM."""

    def __init__(self, *, max_sentences: int = 5) -> None:
        self.max_sentences = max_sentences

    def generate(self, brief: str, *, duration_minutes: int) -> list[Scene]:
        sentences = _normalize_sentences(brief)
        num_scenes = max(3, min(6, math.ceil(duration_minutes * 1.5)))
        template = _story_arc_templates()

        scenes: List[Scene] = []
        for index in range(num_scenes):
            arc = next(template)
            sentence = sentences[index % len(sentences)] if sentences else brief
            summary = textwrap.fill(f"{arc}: {sentence}", 90)
            scenes.append(
                Scene(
                    index=index,
                    title=_scene_title(index, arc),
                    summary=summary,
                    voiceover=_voiceover_from_summary(summary),
                    mood=_mood_from_arc(arc),
                    thumbnail_description=_thumbnail_from_arc(arc, sentence),
                )
            )
        return scenes


class StoryboardDesigner:
    """Assigns framing and visual cues for each scene."""

    def design(self, scenes: Iterable[Scene]) -> list[Scene]:
        designed = []
        for scene in scenes:
            aspect_ratio = "16:9" if scene.index % 2 == 0 else "9:16"
            thumbnail = scene.thumbnail_description or ""
            thumbnail = f"{thumbnail} | Shot suggestion: {self._shot_suggestion(scene.index)}"
            designed.append(
                Scene(
                    index=scene.index,
                    title=scene.title,
                    summary=scene.summary,
                    voiceover=scene.voiceover,
                    mood=scene.mood,
                    aspect_ratio=aspect_ratio,
                    thumbnail_description=thumbnail.strip(),
                )
            )
        return designed

    @staticmethod
    def _shot_suggestion(index: int) -> str:
        options = [
            "wide establishing",
            "medium action",
            "close-up reaction",
            "dynamic tracking",
            "graphic overlay",
        ]
        return options[index % len(options)]


def _normalize_sentences(text: str) -> list[str]:
    sentences = [segment.strip() for segment in text.replace("\n", " ").split(".") if segment.strip()]
    if not sentences:
        return ["Introduce the topic in an engaging manner"]
    return sentences[:10]


def _story_arc_templates() -> Iterable[str]:
    arcs = [
        "Hook the audience with a relatable question",
        "Present the core promise",
        "Deliver the first key insight",
        "Share the second key insight",
        "Explain how to put the advice into practice",
        "Close with a memorable takeaway",
    ]
    return itertools.cycle(arcs)


def _scene_title(index: int, arc: str) -> str:
    keywords = arc.split()[0:3]
    return f"Scene {index + 1}: {' '.join(word.capitalize() for word in keywords)}"


def _voiceover_from_summary(summary: str) -> str:
    sentences = textwrap.wrap(summary, 80)
    return " ".join(sentences)


def _mood_from_arc(arc: str) -> str:
    if "hook" in arc.lower():
        return "energetic"
    if "promise" in arc.lower():
        return "confident"
    if "insight" in arc.lower():
        return "informative"
    if "practice" in arc.lower():
        return "encouraging"
    return "uplifting"


def _thumbnail_from_arc(arc: str, sentence: str) -> str:
    keywords = " ".join(sentence.split()[:6])
    return f"{arc.lower()} featuring {keywords}".strip()
