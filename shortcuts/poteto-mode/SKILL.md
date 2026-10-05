---
name: poteto-mode
description: Shortcut for the pstack plugin's poteto-mode (poteto's rigorous engineering style). Use when the user types /poteto-mode or asks to work in poteto's style or with pstack rigor.
---

# poteto-mode (shortcut)

This skill only hands off to the pstack plugin, so `/poteto-mode` works without the plugin prefix.

1. Invoke the Skill tool with skill `pstack:poteto-mode`, passing the user's arguments verbatim as `args`.
2. Follow the loaded skill in full from there: match a playbook, open its file, copy its steps into the task list, and do the work.

If `pstack:poteto-mode` is not available, the pstack plugin is not installed or is disabled. Say so in one line and stop.
