# Revid Clone

This repository contains a self-contained, offline-friendly clone of the Revid AI workflow. It focuses on the core content automation loop:

1. Define a video brief describing the topic, tone, target audience, and duration.
2. Automatically generate a structured script broken down into scenes.
3. Produce a lightweight storyboard with scene thumbnails and narration text.
4. Assemble a preview package that can be consumed by downstream tooling.

The project is intentionally dependency-light so it can run in constrained environments without external services.

## Features

- **Project management** – create, persist, and reload projects locally.
- **Heuristic AI simulation** – deterministic content generation based on prompt analysis and storytelling templates.
- **Storyboard synthesis** – per-scene visual briefs with aspect ratio handling and mood cues.
- **Preview export** – generates a JSON handoff that mirrors the payload you would send to rendering pipelines.
- **Command line interface** – orchestrate the full workflow with a single `revid` executable.

## Quickstart

```bash
python -m revid_clone.cli init "Morning Routine Hacks" \
  --brief "Share three actionable tips for a calmer morning." \
  --tone upbeat --audience "busy professionals" --duration 2

# Generate script, storyboard, and preview assets
python -m revid_clone.cli script <project_id>
python -m revid_clone.cli storyboard <project_id>
python -m revid_clone.cli render <project_id> --out output.json
```

Every command prints the project identifier that is needed for the subsequent step. By default, projects are stored under `~/.revid_clone`. Use the `REVID_HOME` environment variable to override the location (helpful for tests or temporary runs).

## Development

```bash
pip install -e .
pytest
```
