# Session Context

## User Prompts

### Prompt 1

# Update Documentation

Sync documentation from source-of-truth:

1. Read package.json scripts section
   - Generate scripts reference table
   - Include descriptions from comments

2. Read .env.example
   - Extract all environment variables
   - Document purpose and format

3. Generate docs/CONTRIB.md with:
   - Development workflow
   - Available scripts
   - Environment setup
   - Testing procedures

4. Generate docs/RUNBOOK.md with:
   - Deployment procedures
   - Monitoring and alerts
   - ...

### Prompt 2

Modify @.claude/agents/doc-updater.md for this project, ie. Django project.

### Prompt 3

Modify @.claude/agents/doc-updater.md to make it more token efficient while not losing any detail and also include creating documentation of design system / UI / UX of the client-facing applications/views under clear sections.

### Prompt 4

[Request interrupted by user for tool use]

### Prompt 5

Modify @.claude/agents/doc-updater.md  to create/update documentation of design system / UI / UX of the client-facing applications/views under clear sections in a seperate file(s).

### Prompt 6

Remove unnecessary examples in @.claude/agents/doc-updater.md to make it more abstract. (once docs are generated, we will already have an example.)

### Prompt 7

[Request interrupted by user for tool use]

### Prompt 8

Keep examples limited to one or two entries in tables. Keep the skeleton example there as reference.

### Prompt 9

Can it be cut down more, ie. made more concise without losing any detail (and save tokens) in the process?

### Prompt 10

[Request interrupted by user for tool use]

