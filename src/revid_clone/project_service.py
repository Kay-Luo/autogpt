from __future__ import annotations

import json
import os
import uuid
from dataclasses import replace
from pathlib import Path
from typing import Iterable

from .ai_engines import ScriptGenerator, StoryboardDesigner
from .models import Project, Scene
from .storage import ProjectStorage, get_default_home


class ProjectService:
    """High level façade for orchestrating Revid-style workflows."""

    def __init__(
        self,
        *,
        storage: ProjectStorage | None = None,
        script_generator: ScriptGenerator | None = None,
        storyboard_designer: StoryboardDesigner | None = None,
    ) -> None:
        self.storage = storage or ProjectStorage()
        self.script_generator = script_generator or ScriptGenerator()
        self.storyboard_designer = storyboard_designer or StoryboardDesigner()

    # Project lifecycle -------------------------------------------------
    def create_project(
        self,
        *,
        title: str,
        brief: str,
        tone: str,
        target_audience: str,
        duration_minutes: int,
    ) -> Project:
        project_id = uuid.uuid4().hex[:12]
        project = Project(
            project_id=project_id,
            title=title,
            brief=brief,
            tone=tone,
            target_audience=target_audience,
            duration_minutes=duration_minutes,
        )
        self.storage.save(project)
        return project

    def list_projects(self) -> Iterable[Project]:
        return self.storage.list_projects()

    def load_project(self, project_id: str) -> Project:
        return self.storage.load(project_id)

    # Generation steps --------------------------------------------------
    def generate_script(self, project: Project) -> Project:
        scenes = self.script_generator.generate(project.brief, duration_minutes=project.duration_minutes)
        summary = _summarize_scenes(scenes)
        project = replace(project, scenes=scenes, script_summary=summary)
        self.storage.save(project)
        return project

    def design_storyboard(self, project: Project) -> Project:
        if not project.scenes:
            project = self.generate_script(project)
        scenes = self.storyboard_designer.design(project.scenes)
        project = replace(project, scenes=scenes, storyboard_ready=True)
        self.storage.save(project)
        return project

    def render_preview(self, project: Project, *, destination: Path | None = None) -> Path:
        if not project.storyboard_ready:
            project = self.design_storyboard(project)
        preview = _build_preview_payload(project, assets_root=self.storage.home)
        destination = destination or self.storage.home / f"{project.project_id}_preview.json"
        destination.write_text(json.dumps(preview, indent=2, sort_keys=True))
        project = replace(project, preview_ready=True)
        self.storage.save(project)
        return destination


# Helpers -----------------------------------------------------------------

def _summarize_scenes(scenes: Iterable[Scene]) -> str:
    key_points = [scene.summary.split(":", 1)[-1].strip() for scene in scenes]
    return " | ".join(key_points)


def _build_preview_payload(project: Project, *, assets_root: Path | None = None) -> dict:
    base = Path(assets_root) if assets_root else get_default_home()
    assets_location = base / "assets" / project.project_id
    return {
        "project_id": project.project_id,
        "title": project.title,
        "tone": project.tone,
        "target_audience": project.target_audience,
        "script_summary": project.script_summary,
        "scenes": [scene.to_dict() for scene in project.scenes],
        "render_metadata": {
            "duration_minutes": project.duration_minutes,
            "rendered_with": "revid-clone",
            "assets_root": os.fspath(assets_location),
            },
    }
