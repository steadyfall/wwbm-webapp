# Session Context

## User Prompts

### Prompt 1

Implement the following plan:

# Plan: TRI-19 — Register auth and adminpanel apps in INSTALLED_APPS

## Context

`auth` and `adminpanel` are functional Django apps that are not yet listed in `INSTALLED_APPS`. Django's migration runner, signal dispatch, and management command autodiscovery all require app registration. Currently the project works by accident because `game` imports models that the other apps depend on — this is a hidden ordering dependency that will break on a fresh DB.

## Pr...

### Prompt 2

Commit this, with the ticket number in the commit message.

### Prompt 3

## Context

- Current git status: On branch steadyfall/tri-19-register-auth-and-adminpanel-apps-in-installed_apps
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   auth/apps.py
	modified:   kbc/settings.py

no changes added to commit (use "git add" and/or "git commit -a")
- Current git diff (staged and unstaged changes): diff --git a/auth/apps.py b/auth/apps.py
index 6a0...

