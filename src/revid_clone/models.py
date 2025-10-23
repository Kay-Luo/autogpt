from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Scene:
    """A single scene in the generated video."""

    index: int
    title: str
    summary: str
    voiceover: str | None = None
    mood: str | None = None
    aspect_ratio: str = "16:9"
    thumbnail_description: str | None = None

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "title": self.title,
            "summary": self.summary,
            "voiceover": self.voiceover,
            "mood": self.mood,
            "aspect_ratio": self.aspect_ratio,
            "thumbnail_description": self.thumbnail_description,
        }


@dataclass
class Project:
    """State container for a video project."""

    project_id: str
    title: str
    brief: str
    tone: str
    target_audience: str
    duration_minutes: int
    created_at: str = field(default_factory=lambda: _dt.datetime.utcnow().isoformat() + "Z")
    script_summary: Optional[str] = None
    scenes: List[Scene] = field(default_factory=list)
    storyboard_ready: bool = False
    preview_ready: bool = False

    def to_dict(self) -> dict:
        return {
            "project_id": self.project_id,
            "title": self.title,
            "brief": self.brief,
            "tone": self.tone,
            "target_audience": self.target_audience,
            "duration_minutes": self.duration_minutes,
            "created_at": self.created_at,
            "script_summary": self.script_summary,
            "scenes": [scene.to_dict() for scene in self.scenes],
            "storyboard_ready": self.storyboard_ready,
            "preview_ready": self.preview_ready,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "Project":
        scenes = [Scene(**scene_dict) for scene_dict in payload.get("scenes", [])]
        payload = {**payload, "scenes": scenes}
        return cls(**payload)
