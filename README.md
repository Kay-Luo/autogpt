# Revid AI Clone Helper

This repository provides a small automation script that can clone the public
[Revid AI](https://revid.ai/) project (or any other Git repository) and attempt
to install its dependencies so it works with full functionality straight after
cloning.

## Usage

```bash
python scripts/clone_revid_ai.py \
  --repo-url https://github.com/revidai/revid.git \
  --destination ./revid-ai
```

Optional flags:

- `--branch <name>` – check out a specific branch or tag during the clone.
- `--skip-installs` – clone the repository but skip the automatic dependency
  installation phase.

The script will try to detect common dependency manifests:

- JavaScript: installs with **pnpm**, **yarn**, or **npm** depending on which lock
  file is available and which tools are present in your environment.
- Python: installs using **Poetry**, **pip**, or **Pipenv** depending on the
  manifests it finds.

If a required tool is not installed locally, the script prints a warning so you
can install the missing tool manually and rerun the relevant step.
