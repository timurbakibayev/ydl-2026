# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

`ydl-2026` is a teaching/lab workspace for the **YDL2026** course (YDL stands for
**Yessenov Data Lab**). It is used to
demonstrate Claude Code itself (CLAUDE.md, memory, sessions, MCP, tests) and to
build small example Python projects during lessons. `day1/plan-lecture.md` is the
running lecture outline — it describes the demos planned for each session (e.g.
building a pygame project, writing unit tests, using `/goal`, the Google browser
MCP plugin). Consult it to understand where a given day's work is heading.

The codebase is intentionally small and grows lesson-by-lesson; do not assume a
larger architecture exists than what is present on disk.

## Environment & running code

A Python 3.12 virtualenv lives at `venv/` (it is not on PATH).

```bash
venv/bin/python day1/simple.py     # run a script with the project interpreter
venv/bin/pip install <package>     # add a dependency (none are pinned yet)
```

There is no build, lint, test runner, or dependency manifest configured yet.
When the lecture plan reaches the testing/pygame demos, expect to introduce
`pytest` and `pygame` via `venv/bin/pip` and to create the corresponding files.

## External LLM service

`creds.txt` holds API keys for the course's LLM gateway at `https://llm.alem.ai`
(OpenAI-compatible). Two models are available:

- `gemma4` — chat completions: `POST /v1/chat/completions`
- `text-to-image` — image generation: `POST /v1/images/generations`

Both authenticate with `Authorization: Bearer <key>`. These are shared course
keys, not personal secrets; use them for the LLM/image demos.

## Conventions

- Work is organized by lecture day under `dayN/` directories. New material for a
  session goes in its own day folder alongside that day's plan and lab PDF.

