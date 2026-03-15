# Session Context

## User Prompts

### Prompt 1

<system_instruction>
You are working inside Conductor, a Mac app that lets the user run many coding agents in parallel.
Your work should take place in the /Users/himankdave/conductor/workspaces/trivivo/montevideo directory (unless otherwise directed), which has been set up for you to work in.
Each workspace has a .context directory (gitignored) where you can save files to collaborate with other agents.
The target branch for this workspace is main. Use this for actions like creating new PRs, bise...

### Prompt 2

<system-instruction>
The user has added 1 comment to the diff for this workspace. Please review and address these comments as part of your response. When addressing comments on the "original" side or on specific commits, read the file from that version (not the current version). Below are the comments, including metadata about what git state they were left on:

Comment #1:

File: tests/unit/test_auth_views.py
Line: 92
User comment: "Abstract all occurences of `username="superuser", password="sup...

### Prompt 3

Create a PR.

### Prompt 4

## Context

- Current git status: On branch steadyfall/tri-63-test-adminlogin-superuser-redirect-non-superuser-redirect-v1
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   tests/unit/test_auth_views.py

no changes added to commit (use "git add" and/or "git commit -a")
- Current git diff (staged and unstaged changes): diff --git a/tests/unit/test_auth_views.py b/tests/un...

