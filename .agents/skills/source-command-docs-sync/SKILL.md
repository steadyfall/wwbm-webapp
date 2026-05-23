---
name: "source-command-docs-sync"
description: "Check if documentation is in sync with code"
---

# source-command-docs-sync

Use this skill when the user asks to run the migrated source command `docs-sync`.

## Command Template

# Documentation Sync

Check if documentation matches the current code state.

## Instructions

1. **Find recent code changes**:
   ```bash
   git log --since="30 days ago" --name-only --pretty=format: -- "*.py" "*.html" "Makefile" "pyproject.toml" ".env.example" | sort -u
   ```

2. **Find related documentation**:
   - Search `docs/CODEMAPS/` for codemaps covering changed apps
   - Check `docs/DESIGN/` if templates or static assets changed
   - Check `docs/CONTRIB.md` if `Makefile` or `pyproject.toml` changed
   - Check `docs/RUNBOOK.md` if `kbc/settings.py` or `.env.example` changed

3. **Verify documentation accuracy** using the source-of-truth files:
   - `Makefile` → `docs/CONTRIB.md` make-commands table
   - `pyproject.toml` → `docs/CONTRIB.md` dependencies section
   - `.env.example` → `docs/RUNBOOK.md` env-vars table
   - `<app>/models.py` → `docs/CODEMAPS/<app>.md` models table and `docs/CODEMAPS/database.md`
   - `<app>/views.py` + `<app>/urls.py` → `docs/CODEMAPS/<app>.md` views and URL tables
   - `templates/` + `static/` → `docs/DESIGN/pages.md` and `docs/DESIGN/components.md`
   - `templates/base.html` → `docs/DESIGN/design-system.md` colour map and layout classes

4. **Report only actual problems**:
   - Documentation is a living document
   - Only flag things that are WRONG, not missing
   - Don't suggest documentation for documentation's sake

5. **Output a checklist** of documentation that needs updating

## Migration Notes

Migrated from source command `docs-sync` into a Codex skill. Invoke it as `$source-command-docs-sync` or ask to check documentation sync in plain language. The original slash-command behavior is preserved as prose.

Claude `allowed-tools` metadata is guidance only in Codex, not a permission boundary.
