"""Utility to clone the Revid AI repository (or any Git repo) and install dependencies.

The script is designed for offline automation pipelines where we want to replicate
Revid AI's project structure locally with minimal manual steps.  By default it will
clone the public Revid AI repository, initialise submodules, and attempt to install
any detected JavaScript or Python dependencies so the project runs with "full
functionality" out of the box.  A different repository URL can be supplied if
needed.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List

DEFAULT_REPO_URL = "https://github.com/revidai/revid.git"


class CommandError(RuntimeError):
    """Raised when a subprocess exits with a non-zero status."""


def run_command(command: Iterable[str], cwd: Path | None = None) -> None:
    """Run *command* and raise :class:`CommandError` on failure.

    Parameters
    ----------
    command:
        The command and arguments to execute.
    cwd:
        Directory to execute the command in.  When ``None`` (the default)
        the current working directory is used.
    """

    process = subprocess.run(command, cwd=cwd, check=False)
    if process.returncode != 0:
        command_display = " ".join(command)
        raise CommandError(
            f"Command '{command_display}' failed with exit code {process.returncode}."
        )


def clone_repository(repo_url: str, destination: Path, branch: str | None) -> Path:
    """Clone *repo_url* into *destination* and return the path to the clone."""

    destination = destination.expanduser().resolve()

    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"Destination {destination} is not empty.")

    clone_cmd: List[str] = ["git", "clone", repo_url, str(destination)]
    if branch:
        clone_cmd.insert(2, "-b")
        clone_cmd.insert(3, branch)

    run_command(clone_cmd)
    return destination


def initialise_submodules(project_root: Path) -> None:
    """Initialise any git submodules contained within *project_root*."""

    git_dir = project_root / ".git"
    if not git_dir.exists():
        return

    try:
        run_command(["git", "submodule", "update", "--init", "--recursive"], cwd=project_root)
    except CommandError as exc:
        print(f"[warning] {exc}")


def install_node_dependencies(project_root: Path) -> None:
    """Install Node.js dependencies if the project declares them."""

    package_json = project_root / "package.json"
    if not package_json.exists():
        return

    preferred_tool: tuple[str, List[str]] | None = None

    if (project_root / "pnpm-lock.yaml").exists() and shutil.which("pnpm"):
        preferred_tool = ("pnpm", ["pnpm", "install"])
    elif (project_root / "yarn.lock").exists() and shutil.which("yarn"):
        preferred_tool = ("yarn", ["yarn", "install"])
    elif shutil.which("npm"):
        preferred_tool = ("npm", ["npm", "install"])

    if preferred_tool is None:
        print("[warning] No supported Node.js package manager found; skipping JS install.")
        return

    tool_name, command = preferred_tool
    print(f"[info] Installing Node.js dependencies with {tool_name}...")
    try:
        run_command(command, cwd=project_root)
    except CommandError as exc:
        print(f"[warning] {exc}")


def install_python_dependencies(project_root: Path) -> None:
    """Install Python dependencies based on common manifest files."""

    def pip_available() -> bool:
        return shutil.which("pip") is not None or shutil.which("pip3") is not None

    if (project_root / "poetry.lock").exists() or _contains_poetry_table(project_root / "pyproject.toml"):
        if shutil.which("poetry"):
            print("[info] Installing Python dependencies with Poetry...")
            try:
                run_command(["poetry", "install"], cwd=project_root)
            except CommandError as exc:
                print(f"[warning] {exc}")
            return
        print("[warning] Poetry manifest detected but Poetry is not installed; skipping.")

    requirements = project_root / "requirements.txt"
    if requirements.exists() and pip_available():
        pip_cmd = "pip3" if shutil.which("pip3") else "pip"
        print(f"[info] Installing Python dependencies via {pip_cmd}...")
        try:
            run_command([pip_cmd, "install", "-r", "requirements.txt"], cwd=project_root)
        except CommandError as exc:
            print(f"[warning] {exc}")
        return

    pipfile = project_root / "Pipfile"
    if pipfile.exists():
        if shutil.which("pipenv"):
            print("[info] Installing Python dependencies with Pipenv...")
            try:
                run_command(["pipenv", "install"], cwd=project_root)
            except CommandError as exc:
                print(f"[warning] {exc}")
            return
        print("[warning] Pipfile detected but Pipenv is not installed; skipping.")


def _contains_poetry_table(pyproject_path: Path) -> bool:
    """Return ``True`` if *pyproject_path* contains a Poetry tool definition."""

    if not pyproject_path.exists():
        return False

    try:
        content = pyproject_path.read_text(encoding="utf-8")
    except OSError:
        return False

    return "[tool.poetry]" in content


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Clone the Revid AI repository (or an arbitrary Git repository) and "
            "attempt to install all detected dependencies so the project is ready to run."
        )
    )
    parser.add_argument(
        "--repo-url",
        default=DEFAULT_REPO_URL,
        help="Git URL for the project. Defaults to the public Revid AI repository.",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Optional branch or tag to check out after cloning.",
    )
    parser.add_argument(
        "--destination",
        default="revid-ai",
        help="Destination directory for the clone. Defaults to './revid-ai'.",
    )
    parser.add_argument(
        "--skip-installs",
        action="store_true",
        help="Skip dependency installation steps after cloning.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_arguments(argv)
    destination = Path(args.destination)

    try:
        project_root = clone_repository(args.repo_url, destination, args.branch)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[error] {exc}")
        return 1

    initialise_submodules(project_root)

    if not args.skip_installs:
        install_node_dependencies(project_root)
        install_python_dependencies(project_root)

    print(f"[info] Clone ready at {project_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
