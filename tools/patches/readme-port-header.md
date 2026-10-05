> **Claude port.** This is [poteto's pstack](https://github.com/cursor/plugins/tree/main/pstack) (Cursor plugin v{UPSTREAM_VERSION}, MIT, by Lauren Tan) translated to Claude. Every skill, playbook, principle, reference, script, and subagent is here, rewired from Cursor's tools to Claude's. The original README follows the port notes.

## using it in claude

- every command carries the plugin prefix: `/pstack:poteto-mode`, `/pstack:how`, `/pstack:interrogate`. the rest of this readme uses the short names.
- `/pstack:pstack <anything>` routes for you: a task goes to `poteto-mode`, a skill named with a slash (`/pstack:pstack /how do we cancel runs?`) goes to that skill, and a question about pstack goes to `poteto-help`.
- two optional personal shortcut skills, `pstack` and `poteto-mode`, let you type `/pstack` and `/poteto-mode` with no prefix. they just hand off to the plugin.
- run `/pstack:setup-pstack` once. it writes `pstack-models.md` as an always-loaded rule in `.claude/rules/`.

## what changed from cursor

| in cursor | in this port |
|---|---|
| `Task` tool, `subagent_type: generalPurpose` | `Agent` tool, `subagent_type: general-purpose` |
| `poteto-agent`, `Comment Sicko` subagents | `pstack:poteto-agent`, `pstack:comment-sicko` |
| grok for code, opus 5.5 for judgment, panel opus / sol / grok | `sonnet` for code, `opus` for judgment, panel `opus` / `fable` / `sonnet` |
| reasoning budget (max, xhigh, high, medium) | model tiers per budget, since the agent tool picks a model, not an effort |
| `~/.cursor/rules/pstack-models.mdc`, always applied | `pstack-models.md` in `.claude/rules/` (project) or `~/.claude/rules/` (user), which claude code always loads |
| `AskQuestion`, todo list | `AskUserQuestion`, task list (TaskCreate / TodoWrite) |
| cloud agents (`environment: "cloud"`) | `isolation: "remote"`, falling back to `isolation: "worktree"` |
| `~/.cursor/projects/<slug>/agent-transcripts/` | `~/.claude/projects/<slug>/` |
| cursor's `create-skill` | anthropic's `skill-creator` |
| `deslop`, `control-cli`, `control-ui` from `cursor-team-kit` | bundled here |
| custom mode (option+enter) | none. once loaded, `poteto-mode` stays for the chat. a rule file in `~/.claude/rules/` turns it on everywhere |
| cursor's `/loop` and plan mode | claude code's `/loop` and plan mode |

## not ported

- `make-bot-ui` drives cursor's grok bot webhook routines. it ships unchanged, marked cursor-only.
- the benny automation pack runs on cursor automations. it ships verbatim under `automations/benny/` for reference.
- `watch-pr` and `orch` need [bun](https://bun.sh) and `gh`. stacked-pr flows also use `gt` (graphite). the first run does a `bun install` next to the scripts (`commander`, plus the `typescript` and `bun-types` dev dependencies), so the plugin directory must be writable.

---

