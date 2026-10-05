---
name: setup-pstack
description: Configure which Claude models pstack uses per role and how much it spends. Detects the models you can use and writes an always-loaded pstack-models.md rule that overrides the skill defaults. Use for /setup-pstack, "configure pstack models", "pstack budget", or changing pstack's model choices.
---

# Setup pstack

> **pstack in Claude.** Other pstack skills named here (`/name` or **name**) live at `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`. Read one in full before following it. Users type them as `/pstack:<name>`.

Write `pstack-models.md`, an always-loaded rule that sets pstack's model per role. Claude Code loads every markdown file in `~/.claude/rules/` and in the project's `.claude/rules/` at session start, which is the Claude counterpart of Cursor's always-applied rule.

## Steps

### 1. Pick where the rule lives

Ask with AskUserQuestion. Offer these two options with these labels.

- `user — ~/.claude/rules/pstack-models.md` covers every project on this machine.
- `project — .claude/rules/pstack-models.md` is committed with the repo. Pick it for cloud sessions, whose home directory does not persist.

When both files exist, every pstack skill reads the project file first.

### 2. Detect available models

The Agent tool's `model` parameter names the values Claude accepts: `opus`, `sonnet`, `haiku`, and `fable`. Every plan has the first three. `fable` is not on every plan, so probe it once: one Agent call with `model: "fable"`, `subagent_type: "general-purpose"`, and the prompt "Reply with the word OK." If the call fails, `fable` is missing. The models that remain are the detected set. Never write a model outside it. The aliases `inherit-parent` and `auto` always pass. Both mean the role runs on the parent chat model, so the skill omits the Agent `model` field.

### 3. Load current state

The default role-to-model mapping is the `unlimited` column in step 4. If the chosen file already exists, read it and treat its `# budget` line and its role values as the current choices. Otherwise start from the defaults. A line whose role is not in step 6 is from a retired role. Drop it.

### 4. Budget, map, and confirm

**(a) Ask for a budget.** Use AskUserQuestion. Offer these four options with these exact labels, and name the current budget when the file records one.

- `unlimited — strongest models everywhere`
- `large — opus for judgment, no fable`
- `medium — sonnet for most roles`
- `small — sonnet for judgment, haiku for code`

**(b) Apply it.** Build the working table from the new budget's column below. On a re-run, a role counts as the user's own choice only when its current value differs from the column of the budget recorded in the file's `# budget` line. Keep those roles. Re-derive every other role from the new column.

| Roles | unlimited | large | medium | small |
|---|---|---|---|---|
| `feature, refactoring`, `bug-fix`, `perf-issue`, `hillclimb`, `how explorer`, `why investigators`, `swarm workers` | `sonnet` | `sonnet` | `sonnet` | `haiku` |
| `judgment and prose`, `hardest tasks`, `how explainer`, `why synthesizer`, `reflect judgment, divergent, synthesizer` | `opus` | `opus` | `sonnet` | `sonnet` |
| `reflect tooling` | `fable` | `opus` | `sonnet` | `sonnet` |
| `arena runners`, `arena cross-judge pool`, `architect runners`, `interrogate reviewers` | `opus, fable, sonnet` | `opus, sonnet, haiku` | `opus, sonnet, haiku` | `sonnet, haiku, haiku` |

Panels keep three seats at every budget, so the budget changes cost, not panel size. If a value is not in the detected set, replace a single-model role with `opus`. In a panel, replace it with the strongest detected model not already in that list, or `opus` when every detected model is already there.

**(c) Show the roles and confirm.** Show every role with its model as a table, and list each line step 3 dropped. Then ask with AskUserQuestion whether to accept as-is or change specific roles (two options). For each role the user wants to change, ask again with the detected models as options, at most four. The user types `inherit-parent` or `auto` through the question's free-text answer. For panel roles (arena runners, architect runners, interrogate reviewers) the value is a list, and one subagent runs per entry, alias entries included, so the list length sets the count. Take a panel list as free text. `arena cross-judge pool` is also a list, but Arena picks one value from it, preferring a model different from the parent's. `swarm workers` is the default model for every worker unless a race or comparison assigns another model per arm.

### 5. Validate

Every model written must be in the detected set. `inherit-parent` and `auto` always pass. If a chosen model is not available, stop and ask again.

### 6. Write the rule

Create the `rules/` directory if needed, then overwrite the whole chosen file so re-runs stay idempotent. Shape:

```
# pstack model configuration. One line per role. Delete a line to fall back to the skill default.
# Values are Agent tool model aliases: opus, sonnet, haiku, fable.
# `inherit-parent` or `auto` as a value: the role runs on the parent chat model (omit Agent `model`). Alias entries in a panel list still count toward its fan-out.
# budget: unlimited
feature, refactoring: sonnet
bug-fix: sonnet
perf-issue: sonnet
hillclimb: sonnet
judgment and prose: opus
hardest tasks: opus
how explorer: sonnet
how explainer: opus
why investigators: sonnet
why synthesizer: opus
reflect tooling: fable
reflect judgment, divergent, synthesizer: opus
arena runners: opus, fable, sonnet
arena cross-judge pool: opus, fable, sonnet
swarm workers: sonnet
architect runners: opus, fable, sonnet
interrogate reviewers: opus, fable, sonnet
```

### 7. Confirm

Tell the user where the rule was written and that it loads at session start, so it applies to new sessions. Skills in the current session read the file directly. Re-running this skill updates it. A project-scope rule takes effect for others only once it is committed.

### 8. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /pstack:create-verification-skill." On yes, read `${CLAUDE_PLUGIN_ROOT}/skills/create-verification-skill/SKILL.md` and follow it. On no, move on without pushing.
