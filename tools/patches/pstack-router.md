---
name: pstack
description: Entry point for pstack, poteto's rigorous engineering workflows ported from Cursor. Use for /pstack, "use pstack", or "run <skill> from pstack". Routes work to poteto-mode, a named pstack skill to that skill, and questions about pstack to poteto-help.
argument-hint: "[/skill-name] <task or question>"
---

# pstack

pstack lives at `${CLAUDE_PLUGIN_ROOT}`. Each pstack skill is `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`. Most are user-invocable only, so the Skill tool does not list them, and reading the file is how you run one. Files you Read from disk show the plugin-root variable unexpanded. It means the path above. The Agent tool is named `Task` in some Claude Code versions. Treat the two names as one tool.

## Route by the first word of the arguments

Decide the route from the first word alone, before you read anything else.

1. **The first word starts with `/` or `pstack:`.** Strip that prefix. If what remains names a directory under `${CLAUDE_PLUGIN_ROOT}/skills/`, run that skill with the rest of the arguments as its input. This is a direct request for that skill, so never substitute `poteto-mode` for it.
2. **The first word is a skill name that is not also an ordinary English word.** Route to it the same way. These are `interrogate`, `architect`, `blast-radius`, `setup-pstack`, `unslop`, `deslop`, `tdd`, `automate-me`, `figure-it-out`, `show-me-your-work`, `technical-writing`, `benchmark-checklist`, `no-comments`, `create-verification-skill`, `maintain-verification-skill`, `typescript-best-practices`, `control-cli`, `control-ui`, `make-bot-ui`, `poteto-mode`, `poteto-help`, and every `principle-*`.
3. **No arguments, or a question about pstack itself** (install, setup, cost, which skill or playbook fits) → `poteto-help`.
4. **Anything else** → `poteto-mode`, with the full arguments as the task. Bare `how`, `why`, `correct`, `reflect`, `recall`, `teach`, `swarm`, `arena`, and `bro` are ordinary words here.

| Arguments | Route |
|---|---|
| `/how does run cancellation work?` | `how` |
| `pstack:why is this flag still off?` | `why` |
| `interrogate review this pr` | `interrogate` |
| `how does run cancellation work?` | `poteto-mode` (Investigation playbook) |
| `why does checkout fail on safari? fix it` | `poteto-mode` (Bug fix playbook) |
| `which skill reviews a pr?` | `poteto-help` |
| (nothing) | `poteto-help` |

## Run the chosen skill

For `poteto-mode`, invoke the Skill tool with `pstack:poteto-mode` and the task as its arguments, then follow it in full: match a playbook, open its file, and copy its steps into the task list before any other work. For any other skill, Read its SKILL.md in full and follow it exactly as if the user had typed `/pstack:<name> <rest>`. Do not summarize the skill to the user or ask whether to proceed. Start the work.
