from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable

from .models import Project


def get_default_home() -> Path:
    return Path(os.environ.get("REVID_HOME", Path.home() / ".revid_clone"))


class ProjectStorage:
    """Filesystem backed persistence layer."""

    def __init__(self, home: Path | None = None) -> None:
        self.home = Path(home) if home else get_default_home()
        self.home.mkdir(parents=True, exist_ok=True)

    def path_for(self, project_id: str) -> Path:
        return self.home / f"{project_id}.json"

    def save(self, project: Project) -> None:
        payload = project.to_dict()
        self.path_for(project.project_id).write_text(json.dumps(payload, indent=2, sort_keys=True))

    def load(self, project_id: str) -> Project:
        data = json.loads(self.path_for(project_id).read_text())
        return Project.from_dict(data)

    def list_projects(self) -> Iterable[Project]:
        for path in sorted(self.home.glob("*.json")):
            yield Project.from_dict(json.loads(path.read_text()))
