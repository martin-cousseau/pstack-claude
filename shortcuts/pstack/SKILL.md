---
name: pstack
description: Shortcut for the pstack plugin's entry point. Use when the user types /pstack, optionally followed by a pstack skill (/how, /interrogate), a task, or a question about pstack.
---

# pstack (shortcut)

This skill only hands off to the pstack plugin, so `/pstack` works without the plugin prefix.

1. Invoke the Skill tool with skill `pstack:pstack`, passing the user's arguments verbatim as `args`.
2. Follow the loaded skill in full from there. It routes a task to poteto-mode, a named skill such as `/how` to that skill, and a question about pstack to poteto-help.

If `pstack:pstack` is not available, the pstack plugin is not installed or is disabled. Say so in one line and stop.
