#!/usr/bin/env python3
"""Hand edits for the Claude port of pstack, applied after convert.py.

Each patch is (relative path, exact old text, new text). A patch whose old
text is missing aborts the run, so drift in the source shows up immediately.
"""
import json
import re
import sys
from pathlib import Path

import os

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
PATCH_DIR = TOOLS / "patches"
UPSTREAM = Path(os.environ.get("UPSTREAM_DIR", REPO / ".upstream" / "plugins"))
OUT = Path(os.environ.get("OUT", REPO / "plugin"))
UPSTREAM_SHA = os.environ["UPSTREAM_SHA"]
UPSTREAM_VERSION = os.environ["UPSTREAM_VERSION"]
PORT_REV = os.environ.get("PORT_REV", "1")

TX_DIR = ("`~/.claude/projects/<slug>/`, where `<slug>` is the absolute working directory "
          "with every non-alphanumeric character turned into `-` (so `/Users/you/proj` becomes `-Users-you-proj`)")

SIBLING_NOTE = (
    "> **pstack in Claude.** Other pstack skills named here (`/name` or **name**) live at "
    "`${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`. Read one in full before following it. "
    "Users type them as `/pstack:<name>`.\n\n"
)

MODELS_WHERE = "`pstack-models.md` (the project's `.claude/rules/pstack-models.md`, else `~/.claude/rules/pstack-models.md`)"

PATCHES = [
    # ---- poteto-mode -------------------------------------------------------
    ("skills/poteto-mode/SKILL.md",
     "disable-model-invocation: true\n---\n", "---\n"),
    ("skills/poteto-mode/SKILL.md",
     "# Poteto mode\n\n",
     "# Poteto mode\n\n"
     "## Running in Claude\n\n"
     "- Every pstack skill this file names (**how**, `/how`, **principle-fix-root-causes**) is a sibling of this skill: "
     "`${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`. Read it in full and follow it. Most are user-invocable only, so the Skill tool does not list them.\n"
     "- Playbook, `references/`, and `scripts/` paths are relative to `${CLAUDE_PLUGIN_ROOT}/skills/poteto-mode/`.\n"
     "- The todo list is the task list (TaskCreate and TaskUpdate, or TodoWrite). A structured question is AskUserQuestion.\n"
     "- Model roles come from " + MODELS_WHERE + ", written by `/setup-pstack`. With no file, every role keeps its default.\n"
     "- There is no Custom Mode. Once loaded, this file stays in the conversation and keeps applying to later turns. "
     "\"New task\" rematches a playbook. The user opts out by saying so.\n\n"),
    ("skills/poteto-mode/SKILL.md",
     "Never spawn a `poteto-agent` to run the playbook itself.",
     "Never spawn a `poteto-agent` to run the playbook itself. If the Agent tool does not list `pstack:poteto-agent`, use `general-purpose` "
     "and open the brief with \"Before any work, read `${CLAUDE_PLUGIN_ROOT}/skills/poteto-mode/SKILL.md` in full, including its Principles index.\" with the path expanded."),
    ("skills/poteto-mode/SKILL.md",
     "`run_in_background: true`, agent mode (readonly strips MCP),",
     "`run_in_background: true` where the Agent tool offers it (otherwise launch independent agents in one message so they run in parallel), "
     "full tool access (the read-only `Explore` type cannot edit),"),
    ("skills/poteto-mode/SKILL.md",
     "from a transcript, cloud-agent URL, or pushed branch.",
     "from a transcript, remote session URL, or pushed branch."),
    ("skills/poteto-mode/playbooks/orchestrate.md",
     "the cloud agent's status in the remote session list.",
     "the remote agent's status in the remote session list."),
    ("skills/poteto-mode/SKILL.md",
     "Per-role lines in the `/setup-pstack` rule override",
     "Per-role lines in the `/setup-pstack` config override"),
    ("skills/poteto-mode/SKILL.md",
     "Prose and judgment read `judgment and prose`.",
     "Prose and judgment read `judgment and prose`. If a subagent cannot spawn subagents of its own in this harness, "
     "the parent runs that fan-out itself and hands the results down."),
    ("skills/poteto-mode/SKILL.md",
     "**Match the model to the job.** Before each spawn, start from the role's line or default and pick the reasoning level and speed the job needs. "
     "The `/setup-pstack` budget sets each role's starting level, xhigh by default. Raise it one step, up to max, for the hardest or subtlest work. "
     "Lower it one step for judgment and two or more steps for routine work. Use fast mode only when the job is urgent, meaning CI or trunk is red "
     "or a person is blocked on the result right now. Otherwise use standard speed, the same slug without `-fast`. Verification is the exception "
     "and stays on the `swarm workers` model and speed (`sonnet` by default). Change only the effort level and whether the slug is fast, and keep "
     "the family the role names, so a diverse panel stays diverse. If the family has no slug at that level and speed, use its nearest slug. "
     "A role on `auto` or `inherit-parent` stays on the parent model. If the Agent tool rejects the adjusted slug, do not try another adjusted slug. "
     "Use the role's line or default and say so.",
     "**Match the effort to the job.** Before each spawn, start from the role's line or default and pick the effort the job needs, through the "
     "Agent tool's `effort` parameter (`low`, `medium`, `high`, `xhigh`, `max`). Every role starts at `xhigh`. The `/setup-pstack` budget picks "
     "each role's model, not its effort. Raise it one step, up to `max`, for the hardest or subtlest work. Lower it one step for judgment and two "
     "or more steps for routine work. Verification is the exception and stays on the `swarm workers` model at `xhigh` (`sonnet` by default). "
     "Change only the effort, never the model the role names, so a diverse panel stays diverse. A role on `auto` or `inherit-parent` stays on the "
     "parent model. If the Agent tool has no `effort` parameter or rejects the level, spawn without `effort` and say so. Claude has no per-subagent "
     "fast mode, so every subagent runs at standard speed."),

    # ---- agents --------------------------------------------------------------
    ("agents/poteto-agent.md",
     "Read the `poteto-mode` skill's `SKILL.md` in full before doing any work, including its inline Principles index. "
     "Use the absolute path your parent gave you. "
     "With no path, before any other work, search `~/.claude/plugins/` for a file whose path ends in `skills/poteto-mode/SKILL.md`. "
     "If more than one file matches, use the copy whose `.cursor-plugin/plugin.json` has the highest `version`. "
     "Your skill catalog hides this skill, so a missing catalog entry does not mean pstack is absent. "
     "If no such file exists, stop and tell your parent. "
     "Navigate to a leaf `principle-*` skill whenever you apply that principle.",
     "Load the pstack `poteto-mode` skill in full before doing any work, including its inline Principles index. "
     "Invoke the Skill tool with `pstack:poteto-mode`, or Read its `SKILL.md` at the absolute path your parent gave you "
     "(`${CLAUDE_PLUGIN_ROOT}/skills/poteto-mode/SKILL.md`). "
     "With neither, before any other work, search `~/.claude/plugins/` for a file whose path ends in `skills/poteto-mode/SKILL.md`. "
     "If more than one file matches, use the copy whose `.claude-plugin/plugin.json` has the highest `version`. "
     "If no such file exists, stop and tell your parent. "
     "Navigate to a leaf `principle-*` skill (a sibling directory under `skills/`) whenever you apply that principle."),
    ("agents/comment-sicko.md",
     "description: A deranged comment-hater that savors deletion and condemns workaround code.",
     "description: A deranged comment-hater that savors deletion and condemns workaround code. Spawned by the pstack /no-comments skill to review comments in a scoped diff."),
    ("agents/comment-sicko.md",
     "I run `/how`, `/why`, or both from the **how** and **why** skills",
     "I run `/how`, `/why`, or both from the **how** and **why** skills (`${CLAUDE_PLUGIN_ROOT}/skills/how/SKILL.md`, `${CLAUDE_PLUGIN_ROOT}/skills/why/SKILL.md`)"),

    # ---- transcripts ---------------------------------------------------------
    ("skills/recall/SKILL.md",
     "Transcripts live at `~/.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>.jsonl`, where `<slug>` is the workspace path with the leading slash dropped "
     "and each \"/\" turned into \"-\" (so `/Users/you/proj` becomes `Users-you-proj`). Every line is one chat message.",
     "Claude Code keeps transcripts at `~/.claude/projects/<slug>/<session-id>.jsonl`, where `<slug>` is the absolute workspace path with every "
     "non-alphanumeric character turned into \"-\" (so `/Users/you/proj` becomes `-Users-you-proj`). Subagent transcripts, when present, sit under "
     "`<session-id>/subagents/`. Every line is one JSON event: a message, a tool call, or a tool result. If the directory is missing, as in a fresh "
     "cloud session that keeps no history, say so and build the brief from the shared record and live state."),
    ("skills/reflect/SKILL.md",
     "find this conversation's transcript in the `agent-transcripts/` directory the system prompt names. Do not glob across `~/.cursor/projects/*/`.",
     "find this conversation's transcript. Claude Code keeps the active workspace's transcripts in " + TX_DIR + ". "
     "Do not glob across `~/.claude/projects/*/`."),
    ("skills/reflect/SKILL.md",
     "ls -t <agent-transcripts>/*.jsonl <agent-transcripts>/*/*.jsonl <agent-transcripts>/*/subagents/*.jsonl 2>/dev/null | head -10",
     "ls -t <transcripts>/*.jsonl <transcripts>/*/subagents/*.jsonl 2>/dev/null | head -10"),
    ("skills/reflect/SKILL.md",
     "That covers the legacy flat (`<id>.jsonl`), current nested (`<id>/<id>.jsonl`), and subagent (`<parent>/subagents/<child>.jsonl`) layouts. "
     "For each candidate, read the first JSONL line. Take the file whose `message.content[0].text` contains the conversation's opening user prompt.",
     "That covers the session (`<session-id>.jsonl`) and its subagents (`<session-id>/subagents/<agent-id>.jsonl`). If the directory is missing "
     "(a fresh cloud session), digest the current conversation instead and say so. For each candidate, find the first line whose `type` is `user`. "
     "Take the file whose `message.content` contains the conversation's opening user prompt. That field is a string, or, when it is an array, "
     "the `text` of its first text block."),
    ("skills/poteto-mode/playbooks/session-pickup.md",
     "A local transcript under the active workspace's `agent-transcripts/` directory (the system prompt names the path. Do not glob across "
     "`~/.cursor/projects/*/`, that crosses workspace boundaries and reads private chats from unrelated projects), a cloud-agent URL, or a pushed branch.",
     "A local transcript under the active workspace's transcript directory, " + TX_DIR + " (do not glob across `~/.claude/projects/*/`, "
     "that crosses workspace boundaries and reads private chats from unrelated projects), a remote session URL, or a pushed branch."),
    ("skills/poteto-mode/playbooks/eval.md",
     "under the active workspace's `agent-transcripts/` directory (the system prompt names this path). Do not glob across `~/.cursor/projects/*/`.",
     "under the active workspace's transcript directory, " + TX_DIR + ". Subagent runs sit under `<session-id>/subagents/`. "
     "Do not glob across `~/.claude/projects/*/`."),
    ("skills/show-me-your-work/SKILL.md",
     "under the active workspace's `agent-transcripts/` directory (the system prompt names the path). Don't glob across `~/.cursor/projects/*/`.",
     "under the active workspace's transcript directory, " + TX_DIR + ". Don't glob across `~/.claude/projects/*/`."),
    ("skills/automate-me/SKILL.md",
     "The system prompt names the workspace's `agent-transcripts/` directory. Use only that path. Don't glob across `~/.cursor/projects/*/`.",
     "Claude Code keeps them in " + TX_DIR + ". Use only that path. Don't glob across `~/.claude/projects/*/`."),
    ("skills/automate-me/SKILL.md",
     "Look recursively for `.claude/skills/**/*-mode/SKILL.md` and `~/.claude/skills/*-mode/SKILL.md` matching the user's handle.",
     "Look recursively for `.claude/skills/**/*-mode/SKILL.md` and `~/.claude/skills/*-mode/SKILL.md` matching the user's handle, and check the skills already listed in this session."),
    ("skills/automate-me/SKILL.md",
     "- Path: preserve an existing mode skill's category. For a new mode, use `.claude/skills/<handle>/<handle>-mode/SKILL.md` when the repo has an "
     "established personal category for that handle. Otherwise default to `.claude/skills/<handle>-mode/SKILL.md` in the project (or "
     "`~/.claude/skills/<handle>-mode/` if the user prefers a personal skill).",
     "- Path: Claude Code discovers skills one level deep, so use `.claude/skills/<handle>-mode/SKILL.md` in the project (or "
     "`~/.claude/skills/<handle>-mode/` if the user prefers a personal skill). In the Claude app, where the user's skills are not files you can write, "
     "hand the finished SKILL.md to the propose_skills tool so the user can save it."),

    # ---- model panels --------------------------------------------------------
    ("skills/interrogate/SKILL.md",
     "| Reviewer A | `opus` |\n| Reviewer B | `sonnet` |\n",
     "| Reviewer A | `opus` |\n| Reviewer B | `fable` |\n| Reviewer C | `sonnet` |\n"),
    ("skills/interrogate/SKILL.md",
     "If the Agent tool rejects a configured entry, run that reviewer on its family's table default and say so. Families go by prefix: "
     "`claude-*`, and `grok-*` with `cursor-grok-*` and `composer-*`. A refused `composer-*` entry runs on Reviewer B's default. "
     "With no family match, use Reviewer A's default. If it rejects a table default, spawn with the closest "
     "equivalent from the valid slugs in its error message (prefer the same family and reasoning tier), and open a separate PR to update "
     "the default table.",
     "If the Agent tool rejects a configured entry, run that reviewer on Reviewer A's default and say so. If it rejects a table default "
     "(`fable` is not on every plan), pick the strongest model the Agent tool accepts that is not already on the panel, spawn with it, and say so."),
    ("skills/interrogate/SKILL.md",
     "Each reviewer gets `subagent_type: general-purpose`, `readonly: true`, and `model` set to",
     "Each reviewer gets `subagent_type: general-purpose`, \"Do not edit, write, or commit anything.\" appended to its prompt (Claude has no "
     "read-only flag), and `model` set to"),
    ("skills/how/SKILL.md",
     "Every spawn is a Agent subagent with `subagent_type: general-purpose` and `readonly: true`.",
     "Every spawn is an Agent subagent with `subagent_type: general-purpose` and \"Do not edit, write, or commit anything.\" appended to its "
     "prompt (Claude has no read-only flag)."),
    ("skills/arena/SKILL.md",
     "default to one each on `opus` and `sonnet`.", "default to one each on `opus`, `fable`, `sonnet`."),
    ("skills/arena/SKILL.md",
     "choose from `opus` and `sonnet`.", "choose from `opus`, `fable`, `sonnet`."),
    ("skills/architect/SKILL.md",
     "use `opus` and `sonnet`.", "use `opus`, `fable`, `sonnet`."),
    ("skills/reflect/SKILL.md",
     "| Tooling | `reflect tooling` | `sonnet` |", "| Tooling | `reflect tooling` | `fable` |"),
    ("skills/arena/SKILL.md",
     "If the Agent tool rejects a configured entry, run that seat on its family's default and say so. Families go by prefix: `claude-*`, "
     "and `grok-*` with `cursor-grok-*` and `composer-*`. A refused `composer-*` entry runs on `sonnet`. "
     "With no family match, use `opus`. If it rejects a default, use `opus` and say so.",
     "If the Agent tool rejects a configured entry or a default (`fable` is not on every plan), run that seat on `opus` and say so."),
    ("skills/why/SKILL.md",
     "Before spawning investigators, list the available MCPs from the Cursor environment. Use the available-tools map when present. Otherwise "
     "inspect the `mcps/` directory Cursor exposes for enabled MCP servers.",
     "Before spawning investigators, list the MCP servers available in this session. Their tools are named `mcp__<server>__<tool>`. "
     "Deferred tools show up by name only, so search with ToolSearch when it exists. `gh` and `git` cover source control without an MCP."),
    ("skills/why/SKILL.md",
     "Every spawn is `general-purpose` with `readonly: false` (agent mode). **Do not use readonly/Ask mode.** It strips MCP access, which "
     "disables the MCP-backed investigators and the synthesizer's citation spot-checks.",
     "Every spawn is `general-purpose` with full tool access. **Never use the read-only `Explore` type.** It cannot reach MCP tools, which "
     "disables the MCP-backed investigators and the synthesizer's citation spot-checks."),
    ("skills/swarm/SKILL.md",
     "Use no `isolation` (or `isolation: \"worktree\"` when it writes files) only when the worker needs access to something on the user's",
     "Run it in this checkout (with `isolation: \"worktree\"` when it writes files) only when the worker needs access to something on the user's"),
    ("skills/swarm/SKILL.md",
     "When a worker must start from a non-default pushed branch, pass `cloud_base_branch`.",
     "When a worker must start from a non-default pushed branch, name the branch in its brief and have it check that branch out first."),
    ("skills/poteto-mode/playbooks/orchestrate.md",
     "Reading local transcripts under `agent-transcripts/`.",
     "Reading local transcripts under `~/.claude/projects/`."),
    ("skills/poteto-mode/playbooks/autonomous-run.md",
     "Pick the wake mechanism using Claude Code's `/loop` command (a built-in, not a pstack skill).",
     "Pick the wake mechanism using Claude Code's `/loop` command (a built-in, not a pstack skill; with no interval it self-paces through ScheduleWakeup)."),

    # ---- setup and help ------------------------------------------------------
    # setup-pstack is replaced wholesale by patches/setup-pstack.md (see below).
    ("skills/poteto-help/SKILL.md",
     "and mention once that a Custom Mode keeps it on.",
     "and mention once that it stays on for the rest of the chat once loaded."),
    ("skills/poteto-help/SKILL.md",
     "The links here point into the installed plugin, which the user may not be able to open, so give the user the file's public copy: "
     "`https://github.com/cursor/plugins/blob/main/pstack/` followed by its path.",
     "The links here point into the installed plugin, which the user may not be able to open. Quote the relevant lines, and for the upstream "
     "Cursor original give `https://github.com/cursor/plugins/blob/main/pstack/` followed by its path. In Claude every pstack command carries the "
     "plugin prefix, so `/how` here is typed `/pstack:how`. The optional `/pstack` and `/poteto-mode` personal shortcut skills drop the prefix."),
    ("skills/poteto-help/SKILL.md",
     "- No `pstack-models.md` means `/setup-pstack` hasn't run for this user, so every role uses its default model.",
     "- No " + MODELS_WHERE + " means `/setup-pstack` hasn't run for this user or project, so every role uses its default model."),
    ("skills/poteto-help/SKILL.md",
     "1. Install with `/add-plugin pstack` in chat, or from Customize in the sidebar.\n"
     "2. Run [`/setup-pstack`](../setup-pstack/SKILL.md). It asks for a reasoning budget, maps a model to each role, and writes a rule. The rule applies to new chats.",
     "1. Install the `pstack.plugin` file: accept it from the chat card in the Claude app, or add it to Claude Code as a plugin.\n"
     "2. Run [`/pstack:setup-pstack`](../setup-pstack/SKILL.md). It asks for a budget, maps a Claude model to each role, and writes `pstack-models.md` into a `.claude/rules/` directory, which Claude loads every session. It applies to new sessions."),
    ("skills/poteto-help/SKILL.md",
     "Installing changes nothing until the user invokes a skill. Only `/setup-pstack` loads from the user's words.",
     "Installing changes nothing until the user invokes a skill. Only `/setup-pstack`, `/poteto-mode`, `/pstack`, and the bundled `deslop`, "
     "`control-cli`, and `control-ui` load from the user's words."),
    ("skills/poteto-help/SKILL.md",
     "pick a model for each role and a reasoning budget now.", "pick a model for each role and a budget now."),
    ("skills/poteto-help/SKILL.md",
     "A role set to `auto` or `inherit-parent` runs on the chat's model, which saves tokens when the chat runs on Auto or a cheaper model.",
     "A role set to `auto` or `inherit-parent` runs on the chat's model, which saves tokens when the chat runs on a cheaper model."),
    ("skills/poteto-help/SKILL.md",
     "pstack is built for Cursor, and it also installs in Claude Code with `/plugin marketplace add cursor/plugins`, then "
     "`/plugin install pstack@cursor-plugins`. There, each command takes a `pstack:` prefix, such as `/pstack:poteto-mode`. "
     "The [Claude Code adapter](../../docs/harness/claude-code.md) maps the Cursor names, and a step that needs a Cursor-only feature, "
     "such as Bugbot or Automations, is skipped with a one-line note.\n\n"
     "Other tools can read the skills, because they use the Agent Skills format. But most workflow skills, including "
     "`/poteto-mode`, `/how`, `/why`, and `/teach`, spawn Cursor subagents with per-role models, and Custom Modes and `/loop` are Cursor features, "
     "so those parts may not work there.",
     "This is the Claude port of pstack, which was built for Cursor. Subagents run through Claude's Agent tool with Claude models per role "
     "(`opus`, `sonnet`, `haiku`, `fable`), so review panels get diversity from different Claude models rather than different vendors. "
     "`/loop` and plan mode are Claude Code built-ins. Cursor's Custom Modes and Grok Bot routines have no Claude equivalent."),
    ("skills/poteto-help/SKILL.md",
     "- Enter on `/poteto-mode` attaches the skill to one message. It fades as the chat moves on.\n"
     "- Option+Enter on Mac or Alt+Enter on Windows, or Use as Mode from the skill entry, makes it a Custom Mode. It stays in context every turn "
     "until the user exits the mode, and it stays out of casual turns.\n"
     "- Cursor's docs list Custom Modes in the Agents Window and the CLI. Elsewhere, start each new task with `/poteto-mode`.\n\n"
     "Link [Cursor's skills docs](https://cursor.com/docs/skills) when this comes up.",
     "- Invoking `/poteto-mode` (or `/pstack:poteto-mode`) loads the skill into the conversation, and it keeps applying for the rest of that chat. "
     "Context compaction can thin it out on very long runs, so restate `/poteto-mode` when a new task starts.\n"
     "- For every chat, add a rule file such as `~/.claude/rules/poteto-mode.md` containing \"For non-trivial engineering work, load the pstack:poteto-mode skill first.\" Claude loads rule files every session.\n\n"),
    ("skills/poteto-help/SKILL.md",
     "- `/deslop`, `control-cli`, and `control-ui` ship in the `cursor-team-kit` plugin.\n"
     "- `/loop` and `/skill-creator` are Cursor built-ins.",
     "- `/deslop`, `control-cli`, and `control-ui` come from Cursor's `cursor-team-kit` plugin. This port bundles them, so `/pstack:deslop` works.\n"
     "- `/loop` is a Claude Code built-in. `skill-creator` is Anthropic's skill-authoring skill."),
    ("skills/poteto-help/SKILL.md",
     "can start Cursor's own skill for the same job instead.",
     "can start another skill for the same job instead."),
    ("skills/poteto-help/SKILL.md",
     "pstack has no planning skill. Cursor's Plan Mode works alongside it.",
     "pstack has no planning skill. Claude Code's plan mode works alongside it."),
    ("skills/poteto-help/SKILL.md",
     "| The mode stopped applying after a few turns | It was started with Enter. Start it as a Custom Mode, or start each task with `/poteto-mode`. |",
     "| The mode stopped applying after a few turns | A long chat compacted it out. Start each task with `/poteto-mode`, or add the rule file above. |"),
    ("skills/poteto-help/SKILL.md",
     "| A new model choice had no effect | The rule from `/setup-pstack` applies to new chats. Start one. |",
     "| A new model choice had no effect | Rule files load at session start, so the config from `/setup-pstack` applies to new sessions. Start one. |"),
    ("skills/poteto-help/SKILL.md",
     "| A skill didn't load on its own | Only `/setup-pstack` loads from the user's words.",
     "| A skill didn't load on its own | Only `/setup-pstack`, `/poteto-mode`, `/pstack`, and the bundled `deslop`, `control-cli`, and "
     "`control-ui` load from the user's words."),
    ("skills/poteto-help/SKILL.md",
     "or run them as cloud agents, which each get their own machine.",
     "or run them with `isolation: \"remote\"` where the Agent tool offers it, which gives each its own machine."),
    ("skills/poteto-help/SKILL.md",
     "| Build a page whose buttons wake a Grok Bot over a webhook | [`/make-bot-ui`](../make-bot-ui/SKILL.md) |",
     "| Build a page whose buttons wake a Cursor Grok Bot over a webhook (Cursor-only, kept for reference) | [`/make-bot-ui`](../make-bot-ui/SKILL.md) |"),

    # ---- make-bot-ui: Cursor-only ---------------------------------------------
    ("skills/make-bot-ui/SKILL.md",
     "# How to make a bot UI\n\n",
     "# How to make a bot UI\n\n"
     "> **Cursor-only.** This skill drives Cursor's Grok Bot webhook routines (`update_state`, `SendToUser` secret requests, the Routines panel). "
     "Claude has no equivalent, so it ships unchanged for reference. In Claude, tell the user so, then offer the parts that still apply: the local "
     "page and server, the server-side key handling, and the Tailscale exposure, pointed at a webhook URL the user supplies.\n\n"),

    # ---- README ---------------------------------------------------------------
    ("README.md", "# pstack\n\n", "# pstack\n\n" + Path(PATCH_DIR / "readme-port-header.md").read_text().replace("{UPSTREAM_VERSION}", UPSTREAM_VERSION)),
    ("README.md",
     "**cursor gives you the best of all worlds.** every frontier model has its strengths and weaknesses. use any model with pstack. in fact, "
     "many of my skills use multi-model workflows to take advantage of each model's unique strengths.",
     "**every model has its strengths and weaknesses.** many of these skills use multi-model workflows to take advantage of each model's "
     "unique strengths. in this claude port the panels mix claude models (opus, fable, sonnet, haiku)."),
    ("README.md", "## install\n\n```bash\n/add-plugin pstack\n```\n",
     "## install\n\naccept `pstack.plugin` from its chat card in the claude app, or load this directory in claude code with `claude --plugin-dir <path>`. "
     "commands carry the plugin prefix (`/pstack:poteto-mode`); the optional shortcut skills give you bare `/pstack` and `/poteto-mode`.\n"),
    ("README.md",
     "code delegates (feature, refactoring, bug fix, perf, hillclimb) go to grok, while the hardest changes, prose, and judgment go to opus 5.5. "
     "the default panel is opus 5.5 / grok.",
     "code delegates (feature, refactoring, bug fix, perf, hillclimb) go to sonnet, while the hardest changes, prose, and judgment go to opus. "
     "the default panel is opus / fable / sonnet."),
    ("README.md",
     "pick it from the `/` menu and press option+enter (mac) or alt+enter (windows) instead of enter. that makes it a "
     "[custom mode](https://cursor.com/docs/skills#using-a-skill-as-a-custom-mode), which cursor offers in the agents window and the cli. "
     "it stays in context every turn until you exit the mode. plain enter attaches it to one message only.",
     "just invoke it: claude has no custom modes, but once loaded the skill stays in the conversation for the rest of the chat. say so to opt out. "
     "to have it in every chat, add a rule file such as `~/.claude/rules/poteto-mode.md` saying \"for non-trivial engineering work, load the pstack:poteto-mode skill first.\""),
    ("README.md",
     "works extremely well with cursor's `/loop` command. you can make cursor work for many hours without sacrificing rigor.",
     "works extremely well with claude code's `/loop` command. you can make claude work for many hours without sacrificing rigor."),
    ("README.md",
     "you want a page or dashboard whose buttons wake a Grok Bot over a webhook, including the sender-key handoff and Tailscale. |",
     "cursor-only, kept for reference: a page whose buttons wake a cursor Grok Bot over a webhook. |"),
    ("README.md",
     "detects your models and writes a config rule. |",
     "writes an always-loaded `pstack-models.md` rule. |"),
    ("README.md",
     "a few things `poteto-mode` references but doesn't bundle:\n\n"
     "- `/deslop` and the `deslop` skill ship in the `cursor-team-kit` plugin.\n"
     "- `control-cli` (for CLIs and TUIs) and `control-ui` (for browser, Electron, web) ship in `cursor-team-kit` too.\n"
     "- `/skill-creator` is a cursor built-in. cursor also ships a built-in `/autopilot` that watches a pr. inside `poteto-mode`, "
     "pr-status requests go to the [babysit playbook](./skills/poteto-mode/playbooks/babysit.md) instead.\n\n"
     "install `cursor-team-kit` alongside pstack if you want the full set.",
     "in cursor, `/deslop`, `control-cli`, and `control-ui` ship in the `cursor-team-kit` plugin. this claude port bundles all three (MIT, "
     "copyright cursor). skill authoring routes to anthropic's `skill-creator` skill in place of cursor's built-in `create-skill`. inside "
     "`poteto-mode`, the [babysit playbook](./skills/poteto-mode/playbooks/babysit.md) handles pr-status requests."),
    ("README.md",
     "in claude code:\n\n```bash\n/plugin marketplace add cursor/plugins\n/plugin install pstack@cursor-plugins\n```\n\n"
     "claude code prefixes plugin commands and agents, so `/poteto-mode` is `/pstack:poteto-mode`. the [claude code adapter]"
     "(./docs/harness/claude-code.md) maps every other cursor name. in claude code, `/pstack:setup-pstack` writes your model choices to "
     "`~/.claude/rules/pstack-models.md`, and a step that needs a cursor-only feature, such as bugbot or automations, is skipped with a one-line note.\n\n"
     "claude code installs a generated copy of pstack, including this readme and the guide, from "
     "[`harness/pstack/`](https://github.com/cursor/plugins/tree/main/harness/pstack) at the repository root. after you change pstack, run "
     "`node scripts/generate-pstack-harness-trees.mjs` from the repository root and commit the result. ci fails while the generated copy is out of date.\n\n",
     ""),
    ("README.md", "cursor already has a great plan mode which works great with pstack.",
     "claude code already has a plan mode which works great with pstack."),
    ("README.md",
     "it detects the models you have access to and writes a small always-applied rule mapping each role (code, judgment, the review panels) to a "
     "model. every skill reads it and falls back to sensible defaults when the rule is absent, so you override only what you want.",
     "it reads the models the agent tool accepts and writes `pstack-models.md`, mapping each role (code, judgment, the review panels) to a "
     "model, as an always-loaded rule in `.claude/rules/`. every skill reads it and falls back to sensible defaults when it is absent, so you override only "
     "what you want."),
    ("README.md",
     "a rerun keeps any role whose model differs from the default.", "a rerun keeps the roles you changed by hand."),
    ("README.md",
     "to set it up, point cursor at [`FOR_AGENTS.md`](./automations/benny/FOR_AGENTS.md). setup copies the pack into the target repository at "
     "`.claude/automations/benny/`, enables pstack there for shared skills, and keeps user configuration outside the copied pack. "
     "benny runs on cursor automations, so it is cursor-only.",
     "benny runs on cursor automations (slack-triggered cloud agents), which claude has no direct equivalent for, so this port ships the pack "
     "verbatim for reference. in cursor, setup starts by pointing cursor at [`FOR_AGENTS.md`](./automations/benny/FOR_AGENTS.md)."),


    # ---- review round 2 --------------------------------------------------------
    ("skills/poteto-mode/SKILL.md",
     "- There is no Custom Mode. Once loaded, this file stays in the conversation and keeps applying to later turns. "
     "\"New task\" rematches a playbook. The user opts out by saying so.\n",
     "- There is no Custom Mode. Once loaded, this file stays in the conversation. On each later turn, apply it when a new task matches a "
     "playbook or needs rigor. Skip it for a casual turn or when the user opts out. \"New task\" rematches a playbook.\n"
     "- Playbooks write `<pstack root>` for the plugin root, `${CLAUDE_PLUGIN_ROOT}`. Files you Read from disk show the plugin-root "
     "variable unexpanded. It means this same path.\n"
     "- The Agent tool is named `Task` in some Claude Code versions. Treat the two names as one tool.\n"
     "- Durable working state (orchestrate stores, plan files) goes under `~/.claude/pstack/<project-slug>/` unless the operator names a path. "
     "A cloud session's home directory does not persist, so there keep what must survive in the repo or on a pushed branch, and say so.\n"),
    ("skills/poteto-mode/SKILL.md", "Open a todolist whose first items", "Open a task list (TaskCreate, or TodoWrite) whose first items"),
    ("skills/poteto-mode/playbooks/orchestrate.md",
     "Create `orchestrate/<project-slug>/` in the current agent's store (path in the system prompt).",
     "Create `~/.claude/pstack/<project-slug>/orchestrate/`, the pstack store poteto-mode names, and pass it to every `orch` call as `ORCH_STORE`."),
    ("skills/poteto-mode/playbooks/multi-phase-plan.md",
     "write the file under the agent store's `docs/`.",
     "write the file under `~/.claude/pstack/<project-slug>/docs/`."),
    ("skills/poteto-mode/playbooks/multi-phase-plan.md",
     "- [ ] Read these from trunk at program start. Re-read them at every tick.",
     "- [ ] Read these at program start from the pstack plugin root, `<pstack root>` (use `git show origin/main:<path>` instead when pstack is "
     "vendored in this repo). Re-read them at every tick."),
    ("skills/poteto-mode/playbooks/multi-phase-plan.md", "`git show origin/main:<control skill path>`", "`cat <control skill path>`"),
    ("skills/poteto-mode/playbooks/multi-phase-plan.md", "Re-read the execution playbook from trunk.", "Re-read the execution playbook from the pstack root."),
    ("skills/poteto-mode/playbooks/multi-phase-plan.md",
     "Each live lane runs on its own cloud VM at the PR head.",
     "Each live lane runs in its own remote agent (`isolation: \"remote\"`) or worktree at the PR head."),
    ("skills/poteto-mode/playbooks/autopilot-full.md",
     "Each tick re-reads this playbook from trunk and fixes drift,",
     "Each tick re-reads this playbook from the pstack root (`<pstack root>/skills/poteto-mode/playbooks/autopilot-full.md`, "
     "or `git show origin/main:<path>` when pstack is vendored in this repo) and fixes drift,"),
    ("skills/poteto-mode/playbooks/autopilot-full.md",
     "start a decision trail in the root agent's store (path in the system prompt)",
     "start a decision trail in the root's pstack store (`~/.claude/pstack/<project-slug>/`, or the repo or a pushed branch in a cloud session)"),
    ("skills/poteto-mode/playbooks/autopilot-stack.md",
     "Each tick re-reads both playbooks from trunk, and this one wins where they differ.",
     "Each tick re-reads both playbooks from the pstack root (`<pstack root>/skills/poteto-mode/playbooks/`, "
     "or `git show origin/main:<path>` when pstack is vendored in this repo), and this one wins where they differ."),
    ("skills/poteto-mode/playbooks/worktree-cleanup.md",
     "a hand-typed `myrepo-worktrees/x` misses one that lives at `.cursor/worktrees/myrepo/x`",
     "a hand-typed `myrepo-worktrees/x` misses one that lives at `.claude/worktrees/x`"),
    ("skills/poteto-mode/playbooks/worktree-cleanup.md",
     "The pinned and active chats are the real artifact (principle-prove-it-works). Get that set from the user or sidebar and cross-check every "
     "candidate. The lever has marked `safe` a worktree the user had pinned, so the pinned set wins.",
     "The active chats are the real artifact (principle-prove-it-works). Get that set from the user (open Claude Code sessions, background "
     "agents, remote sessions) and cross-check every candidate. The lever has marked `safe` a worktree an open chat still used, so the user's set wins."),
    ("skills/poteto-mode/playbooks/worktree-cleanup.md",
     "report whether the chat is pinned or ongoing and which worktrees it touches",
     "report whether the chat is ongoing and which worktrees it touches"),
    ("skills/poteto-mode/playbooks/worktree-cleanup.md",
     "A pinned chat spawns arena and repro trees into sibling worktrees via background subagents, and those are in use even when their names "
     "never hit the sidebar.",
     "An active chat spawns arena and repro trees into sibling worktrees via background subagents, and those are in use even when their names "
     "never show up in the chat list."),
    ("skills/poteto-mode/playbooks/worktree-cleanup.md",
     "`~/Library/Application Support/Cursor` (",
     "`~/Library/Application Support/Cursor` if Cursor is also installed ("),
    ("skills/automate-me/SKILL.md",
     "Mode skills can live in a personal category directory (`.claude/skills/<handle>/`), not only at the top level.",
     "Mode skills sit at `.claude/skills/<handle>-mode/` or `~/.claude/skills/<handle>-mode/`."),
    ("skills/automate-me/SKILL.md",
     "That crosses workspace boundaries and reads private chats from unrelated projects.",
     "That crosses workspace boundaries and reads private chats from unrelated projects. If the directory is missing (a fresh cloud session "
     "keeps no history), say so and lean on the step 2 interview."),
    ("skills/automate-me/SKILL.md",
     "Shape: one or two questions with 4-6 options each, `allow_multiple: true` for category questions.",
     "Shape: one or two questions with up to 4 options each (the tool's limit; it adds a free-text answer), `multiSelect: true` for category questions."),
    ("skills/arena/SKILL.md",
     "If the Agent tool rejects a configured entry or a default (`fable` is not on every plan), run that seat on `opus` and say so.",
     "If the Agent tool rejects a configured entry or a default (`fable` is not on every plan), run that seat on the strongest model the Agent "
     "tool accepts that is not already in the arena, or `opus` when all are, and say so."),
    ("skills/poteto-help/SKILL.md",
     "The optional `/pstack` and `/poteto-mode` personal shortcut skills drop the prefix.",
     "The optional `/pstack` and `/poteto-mode` personal shortcut skills drop the prefix. Port-only files (`skills/pstack`, `skills/deslop`, "
     "`skills/control-cli`, `skills/control-ui`) and the rewritten `skills/setup-pstack` have no matching upstream copy, so quote those instead of linking."),
    ("skills/poteto-help/SKILL.md", "\n\n Mid-chat, \"new task\"", "\n\nMid-chat, \"new task\""),
    ("skills/poteto-help/SKILL.md", "| Pick a model for each role and a reasoning budget |", "| Pick a model for each role and a budget |"),
    ("skills/poteto-help/SKILL.md", "or race workers, as cloud agents |", "or race workers, as remote agents |"),
    ("docs/guide/01-setup.md",
     "\n\nIn Claude Code, run `/plugin marketplace add cursor/plugins`, then `/plugin install pstack@cursor-plugins`. Claude Code prefixes plugin "
     "commands, so each command in this guide takes a `pstack:` prefix there, such as `/pstack:setup-pstack`, which writes its model rule to "
     "`~/.claude/rules/pstack-models.md`. The [Claude Code adapter](../harness/claude-code.md) covers the other differences.",
     ""),
    ("docs/guide/01-setup.md",
     "detects the models you have access to, asks for a reasoning budget, shows you each role",
     "detects the models you have access to, asks whether the config is just yours or committed with the project, asks for a budget, shows you each role"),
    ("docs/guide/01-setup.md",
     "keeps any role whose model differs from the default.",
     "keeps the roles you changed by hand."),
    ("skills/ketchup/SKILL.md",
     "a chart or diagram from `/visualize`, or a generated image.",
     "a chart or diagram you render (an image, or an artifact where the app offers one), or a generated image."),
    ("skills/ketchup/SKILL.md",
     "and a `/visualize` chart for numbers.",
     "and a chart you render for numbers (a Mermaid chart, an image, or an artifact where the app offers one)."),
    ("README.md",
     "pick `/poteto-mode` from the `/` menu before you type your task, so cursor attaches the skill to the message.",
     "pick `/pstack:poteto-mode` (or the `/poteto-mode` shortcut) from the `/` menu before you type your task, so claude loads the skill with the message."),
    # ---- docs ----------------------------------------------------------------
    ("docs/guide/01-setup.md",
     "In a Cursor chat, run:\n\n```text\n/add-plugin pstack\n```\n\nCursor confirms the plugin is installed.",
     "Accept the `pstack.plugin` file from its chat card in the Claude app, or add the plugin directory to Claude Code. "
     "In Claude every pstack command carries the plugin prefix: `/setup-pstack` on these pages is typed `/pstack:setup-pstack`. "
     "Save the optional `/pstack` and `/poteto-mode` shortcut skills to drop the prefix for those two."),
    ("docs/guide/01-setup.md",
     "It writes `pstack-models.md`, a small rule every pstack skill reads.",
     "It writes `pstack-models.md` into `.claude/rules/` (yours or the project's), which Claude loads every session, so every pstack skill sees it."),
    ("docs/guide/01-setup.md",
     "A role with no line in the rule keeps the skill's default.",
     "A role with no line in the config keeps the skill's default."),
    ("docs/guide/01-setup.md",
     "The defaults run at `xhigh` reasoning, the same as the `large` budget. `unlimited` lifts each model to its highest tier, up to `max`. "
     "Opus goes to `max`. Grok tops out at `xhigh`, so it stays there. `medium` and `small` lower the reasoning and spend fewer tokens.",
     "The defaults match the `unlimited` budget: `opus` for judgment, `sonnet` for code, and `opus, fable, sonnet` review panels. "
     "`large` drops `fable`. `medium` and `small` move roles to cheaper models and spend fewer tokens."),
    ("docs/guide/01-setup.md",
     "pick a smaller reasoning budget or cheaper models.", "pick a smaller budget or cheaper models."),
    ("docs/guide/01-setup.md",
     "You might be wondering what happens if you use Auto. Set a role",
     "You might be wondering how to keep a role on your chat's model. Set a role"),
    ("docs/guide/01-setup.md",
     "After setup, start a new chat. The model rule applies to new sessions.",
     "After setup, start a new chat. Rule files load at session start, so the config applies to new sessions."),
    ("docs/guide/01-setup.md",
     "To keep `/poteto-mode` on for the whole chat, pick it from the `/` menu with Option+Enter (Mac) or Alt+Enter (Windows) instead of Enter. "
     "That makes it a [Custom Mode](https://cursor.com/docs/skills#using-a-skill-as-a-custom-mode), which stays in context on every turn until you exit it. Custom Modes are "
     "available in the Agents Window and the CLI. Plain Enter attaches the skill to one message, and it fades as the chat moves on.",
     "Once invoked, `/poteto-mode` stays in the conversation and keeps applying for the rest of the chat. Claude has no Custom Modes, so to have it "
     "in every chat, add a rule file such as `~/.claude/rules/poteto-mode.md` saying \"For non-trivial engineering work, load the pstack:poteto-mode skill first.\""),
    ("docs/guide/02-poteto-mode.md",
     "and a Custom Mode keeps `/poteto-mode` in context on every turn.",
     "and `/poteto-mode` stays in context for the rest of the chat once loaded."),
    ("docs/guide/02-poteto-mode.md",
     "The cleanest isolation is a [cloud subagent](https://cursor.com/docs/subagents#cloud-subagents). Each one gets its own VM and branch, "
     "so it can install dependencies, run your app, and record video of the result without touching your machine. Type `/in-cloud` before the "
     "task, or ask the parent chat to hand work to cloud subagents.",
     "The cleanest isolation is a remote agent (`isolation: \"remote\"` on the Agent tool, where it is offered). Each one gets its own cloud "
     "machine and branch, so it can install dependencies, run your app, and record video of the result without touching your machine. Ask the "
     "parent chat to hand the work to remote agents."),
    ("docs/guide/07-overnight.md",
     "an isolated worktree or cloud agent,", "an isolated worktree or remote agent,"),
    ("docs/guide/07-overnight.md",
     "that you're about to go offline or restart Cursor.", "that you're about to go offline or restart Claude Code."),
    ("docs/guide/07-overnight.md",
     "A [Cursor Project](https://cursor.com/blog/projects) gives one coordinator agent a persistent thread. The coordinator doesn't write code. "
     "It directs subagents, which run in the cloud by default, so the work continues when your laptop is closed.",
     "Cursor Projects have no Claude equivalent. The nearest shape is one long-lived coordinator session, such as a Claude Code cloud session, "
     "with a persistent thread. The coordinator doesn't write code. It directs subagents, run as remote agents (`isolation: \"remote\"`) where "
     "the Agent tool offers it, so the work continues when your laptop is closed."),
    ("docs/guide/07-overnight.md",
     "- Give each body of work its own Project,", "- Give each body of work its own coordinator session,"),
    ("docs/guide/07-overnight.md",
     "- Drag related chats into the Project, finished ones included. They become context for every agent in it.",
     "- Have the coordinator `/recall` related chats, finished ones included. They become context for every agent it briefs."),
    ("docs/guide/07-overnight.md",
     "One prompt can carry a whole Project,", "One prompt can carry a whole coordinator session,"),
    ("docs/guide/07-overnight.md",
     "and name the target repository to set it up.",
     "and name the target repository to set it up. The pack runs on Cursor Automations, so this port ships it for reference. "
     "[`CLAUDE-PORT.md`](../../automations/benny/CLAUDE-PORT.md) says what porting it to Claude scheduled tasks takes."),
    ("docs/guide/10-recipes-and-pitfalls.md",
     "Run them as cloud agents, or say \"own worktree per attempt\".",
     "Run them as remote agents, or say \"own worktree per attempt\"."),
    ("docs/guide/07-overnight.md",
     "`/loop` is Cursor's built-in wake mechanism, not a pstack skill.",
     "`/loop` is Claude Code's built-in wake mechanism, not a pstack skill."),
    ("docs/guide/05-build-and-clean.md",
     "`/deslop` ships in the `cursor-team-kit` plugin, not in pstack. If you don't have it, ask for the same outcome in plain words: remove "
     "narrating comments, unsupported guards, dead compatibility paths, and unrelated edits.",
     "`/deslop` comes from Cursor's `cursor-team-kit` plugin. This Claude port bundles it as `/pstack:deslop`."),
]


def first_mention_where(text: str) -> str:
    return text.replace("`pstack-models.md`", MODELS_WHERE, 1)


def main() -> None:
    failed = []
    for rel, old, new in PATCHES:
        path = OUT / rel
        text = path.read_text()
        if old not in text:
            failed.append((rel, old[:90]))
            continue
        path.write_text(text.replace(old, new, 1))

    port_manifest = {
        "name": "pstack",
        "version": f"{UPSTREAM_VERSION}-claude.{PORT_REV}",
        "description": "poteto's pstack, ported from Cursor to Claude. if you want to go fast, go deep first: rigorous agent workflows "
                       "(poteto-mode, 23 playbooks, 24 principles, multi-model review) you can parallelize with confidence.",
        "author": {"name": "Lauren Tan (poteto); Claude port"},
        "homepage": "https://github.com/cursor/plugins/tree/main/pstack",
        "repository": "https://github.com/cursor/plugins",
        "license": "MIT",
        "keywords": ["pstack", "poteto-mode", "workflow", "principles", "subagents", "code-review", "unslop"],
    }
    (OUT / ".claude-plugin" / "plugin.json").write_text(json.dumps(port_manifest, indent=2) + "\n")
    # Upstream's Agent Plugins v1 root manifest stays, with the port's identity and version so it never
    # disagrees with .claude-plugin/plugin.json. Upstream's $schema and any field the port does not set are kept.
    root_manifest = OUT / "plugin.json"
    if root_manifest.exists():
        root_manifest.write_text(json.dumps({**json.loads(root_manifest.read_text()), **port_manifest}, indent=2) + "\n")
    (OUT / "NOTICE.md").write_text(
        "# Notice\n\n"
        "pstack is by Lauren Tan (poteto), MIT licensed. See `LICENSE`. Source: https://github.com/cursor/plugins/tree/main/pstack "
        f"(commit {UPSTREAM_SHA[:7]}, plugin version {UPSTREAM_VERSION}).\n\n"
        "`skills/deslop`, `skills/control-cli`, and `skills/control-ui` come from Cursor's `cursor-team-kit` plugin "
        "(https://github.com/cursor/plugins/tree/main/cursor-team-kit), MIT licensed, copyright 2026 Cursor.\n\n"
        "This directory is a port to Claude. Tool names, subagent types, model choices, config paths, and transcript paths were "
        "translated; the workflows, playbooks, and principles are unchanged. `skills/pstack` is new in the port.\n" + "\n`skills/control-ui` mentions `verify-this`, a cursor-team-kit skill this port does not bundle.\n\n## cursor-team-kit license\n\n```\n" + (UPSTREAM / "cursor-team-kit" / "LICENSE").read_text() + "```\n")
    (OUT / "automations" / "benny" / "CLAUDE-PORT.md").write_text(
        "# benny in the Claude port\n\n"
        "benny runs as two Cursor Automations (Slack-triggered cloud agents) and enables pstack through `.cursor/settings.json`. "
        "Claude has no direct equivalent, so these files ship verbatim from the Cursor plugin, for reference. They are not registered as "
        "skills. Porting benny means re-creating its two automations as Claude scheduled tasks or routines that read Slack through a "
        "connector, and pointing their prompts at `templates/` here.\n")

    # setup-pstack is rewritten for Claude's config model.
    (OUT / "skills/setup-pstack/SKILL.md").write_text(Path(PATCH_DIR / "setup-pstack.md").read_text())

    skill_names = sorted(p.parent.name for p in (OUT / "skills").glob("*/SKILL.md"))
    name_re = re.compile(r"(\*\*|`/?|\[`/)(" + "|".join(map(re.escape, skill_names)) + r")\b")
    for skill_md in sorted((OUT / "skills").glob("*/SKILL.md")):
        name = skill_md.parent.name
        text = skill_md.read_text()
        if name not in {"setup-pstack", "poteto-help", "poteto-mode", "pstack"}:
            text = first_mention_where(text)
        # Frontmatter name must match the directory for /pstack:<name>.
        text = re.sub(r"^name: .*$", f"name: {name}", text, count=1, flags=re.M)
        fm_end = text.index("\n---\n", 4) + 5
        body = text[fm_end:]
        mentions_sibling = any(m.group(2) != name for m in name_re.finditer(body))
        if mentions_sibling and name not in {"poteto-mode", "pstack"} and SIBLING_NOTE not in text:
            heading = re.search(r"^# .*\n\n?", body, flags=re.M)
            at = fm_end + (heading.end() if heading and heading.start() < 5 else 0)
            text = text[:at] + SIBLING_NOTE + text[at:]
        skill_md.write_text(text)

    for path in (OUT / "skills").rglob("*.md"):
        if path.name != "SKILL.md" and "pstack-models.md" in path.read_text():
            path.write_text(first_mention_where(path.read_text()))

    if failed:
        for rel, old in failed:
            print(f"MISSING in {rel}: {old!r}", file=sys.stderr)
        sys.exit(1)
    print(f"applied {len(PATCHES)} patches", file=sys.stderr)


if __name__ == "__main__":
    main()
