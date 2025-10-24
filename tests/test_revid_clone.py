from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from revid_clone.project_service import ProjectService
from revid_clone.storage import ProjectStorage


@pytest.fixture()
def temp_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "revid_home"
    monkeypatch.setenv("REVID_HOME", os.fspath(home))
    return home


def test_full_generation_pipeline(temp_home: Path) -> None:
    service = ProjectService(storage=ProjectStorage(temp_home))

    project = service.create_project(
        title="Morning Routine Hacks",
        brief="Share three actionable tips. Focus on energising the viewer.",
        tone="upbeat",
        target_audience="busy professionals",
        duration_minutes=2,
    )

    project = service.generate_script(project)
    assert len(project.scenes) >= 3
    assert project.script_summary

    project = service.design_storyboard(project)
    assert project.storyboard_ready is True
    assert {scene.aspect_ratio for scene in project.scenes} == {"16:9", "9:16"}

    output_path = temp_home / "preview.json"
    rendered = service.render_preview(project, destination=output_path)
    payload = json.loads(rendered.read_text())

    assert payload["title"] == "Morning Routine Hacks"
    assert payload["render_metadata"]["rendered_with"] == "revid-clone"
    assert len(payload["scenes"]) == len(project.scenes)


def test_cli_roundtrip(temp_home: Path) -> None:
    service = ProjectService(storage=ProjectStorage(temp_home))
    project = service.create_project(
        title="Healthy Snacks",
        brief="Offer snappy snack ideas for remote workers.",
        tone="friendly",
        target_audience="remote workers",
        duration_minutes=3,
    )

    project = service.generate_script(project)
    project = service.design_storyboard(project)
    path = service.render_preview(project)

    assert path.exists()
    data = json.loads(path.read_text())
    assert data["project_id"] == project.project_id
