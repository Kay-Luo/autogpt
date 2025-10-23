from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .project_service import ProjectService


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    service = ProjectService()

    if args.command == "init":
        project = service.create_project(
            title=args.title,
            brief=args.brief,
            tone=args.tone,
            target_audience=args.audience,
            duration_minutes=args.duration,
        )
        print(project.project_id)
    elif args.command == "script":
        project = service.load_project(args.project_id)
        project = service.generate_script(project)
        print(json.dumps(project.to_dict(), indent=2))
    elif args.command == "storyboard":
        project = service.load_project(args.project_id)
        project = service.design_storyboard(project)
        print(json.dumps(project.to_dict(), indent=2))
    elif args.command == "render":
        project = service.load_project(args.project_id)
        destination = Path(args.out) if args.out else None
        path = service.render_preview(project, destination=destination)
        print(path)
    elif args.command == "list":
        for project in service.list_projects():
            print(f"{project.project_id}\t{project.title}\t{project.created_at}")
    else:
        parser.print_help()
        sys.exit(1)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Offline Revid AI clone CLI")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Create a new project")
    init_parser.add_argument("title")
    init_parser.add_argument("--brief", required=True)
    init_parser.add_argument("--tone", default="friendly")
    init_parser.add_argument("--audience", default="general audience")
    init_parser.add_argument("--duration", type=int, default=2)

    script_parser = subparsers.add_parser("script", help="Generate a script for a project")
    script_parser.add_argument("project_id")

    storyboard_parser = subparsers.add_parser("storyboard", help="Design storyboards")
    storyboard_parser.add_argument("project_id")

    render_parser = subparsers.add_parser("render", help="Render a preview JSON payload")
    render_parser.add_argument("project_id")
    render_parser.add_argument("--out")

    list_parser = subparsers.add_parser("list", help="List projects")
    list_parser.set_defaults()

    return parser


if __name__ == "__main__":
    main()
