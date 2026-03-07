# 🚀 htag Project Rules

> [!NOTE]
> **Project Type**: `uv` Python project (editable install)

## 📁 Project Structure

- **Framework Source**: [htag](file://./htag)
- **Developer Guidelines**: [htag-development skill](file://.agent/skills/htag-development/SKILL.md)

## 🛠️ Standard Commands

| Action | Command |
| :--- | :--- |
| **Run a script** | `uv run python_file.py` |
| **Add dependency** | `uv add <package>` |
| **Run tests** | `uv run pytest` |

## rules

- always ensure a minimal, but robust, type hints in folder ./htag
- ensure comments are in english
- when you add/edit examples (main*.py files), always use the skill best practices
- when I say "core", focus on all files in ./htag folder
- when I say "docs", focus on .agent/skills/htag-development/SKILL.md, ./README.md, and alls files in ./docs folder, EXCEPT ./docs/v1 folder, (never touch files in ./docs/v1 folder)
- when I say "examples", focus on all files in **/main*.py**
- if you add/change core feature, always update docs
