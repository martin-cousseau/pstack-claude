#!/usr/bin/env python3
"""Convert cursor/plugins pstack into a Claude Code plugin.

Copies the source tree, applies an ordered table of term rewrites to every
markdown file, and cleans skill/agent frontmatter. Rerunnable: it always
rebuilds the output from the pristine source. Hand edits live in
apply_patches.py and tools/patches/, applied after this script.

Env: UPSTREAM_DIR (cursor/plugins checkout, default .upstream/plugins),
OUT (default plugin/).
"""
import re
import shutil
import sys
from pathlib import Path

import os

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
UPSTREAM = Path(os.environ.get("UPSTREAM_DIR", REPO / ".upstream" / "plugins"))
SRC = UPSTREAM / "pstack"
TEAM_KIT = UPSTREAM / "cursor-team-kit"
OUT = Path(os.environ.get("OUT", REPO / "plugin"))
PATCHES = TOOLS / "patches"

# Ordered (pattern, replacement). Literal unless flagged regex.
REWRITES = [
    # Model config: Cursor always-applied rule -> Claude config file imported from CLAUDE.md.
    ("`~/.cursor/rules/pstack-models.mdc`", "`pstack-models.md`"),
    ("~/.cursor/rules/pstack-models.mdc", "pstack-models.md"),
    ("the `pstack-models.mdc` rule", "the `pstack-models.md` config"),
    ("pstack-models.mdc", "pstack-models.md"),
    ("If the rule or that line is missing", "If the config or that line is missing"),
    ("if the rule or the line is missing", "if the config or the line is missing"),
    ("If the rule or the line is missing", "If the config or the line is missing"),
    # Model slugs -> Claude Agent tool model aliases.
    ("claude-opus-5-5-max", "opus"),
    ("claude-opus-5-5-medium", "sonnet"),
    ("gpt-5.6-sol-max", "fable"),
    ("grok-4.7-xhigh-fast", "sonnet"),
    ("grok-4.7-medium-fast", "haiku"),
    # Subagent types.
    ('subagent_type: "poteto-agent"', 'subagent_type: "pstack:poteto-agent"'),
    ('subagent_type: "Comment Sicko"', 'subagent_type: "pstack:comment-sicko"'),
    ("generalPurpose", "general-purpose"),
    ("agent mode (`readonly: false`)", "full tool access (not the read-only `Explore` type)"),
    ('`environment: "cloud"`', '`isolation: "remote"` (fall back to `isolation: "worktree"` when the Agent tool lacks the remote option or refuses the call)'),
    ('`environment: "local"`', 'no `isolation` (or `isolation: "worktree"` when it writes files)'),
    # Cursor Task tool -> Claude Agent tool.
    ("`Task`", "`Agent`"),
    (r"\bTask tool\b", "Agent tool", "re"),
    (r"\bTask calls?\b", lambda m: m.group(0).replace("Task", "Agent"), "re"),
    (r"\bTask subagent", "Agent subagent", "re"),
    (r"\bTask prompts\b", "Agent prompts", "re"),
    ("Task `model`", "Agent `model`"),
    # Structured questions.
    ("AskQuestion", "AskUserQuestion"),
    # Skill and plugin locations.
    ("~/.cursor/skills/", "~/.claude/skills/"),
    (".cursor/skills/", ".claude/skills/"),
    ("~/.cursor/plugins/", "~/.claude/plugins/"),
    (".cursor/automations/benny/", ".claude/automations/benny/"),
    (".cursor/benny/", ".claude/benny/"),
    # Cursor built-ins -> Claude equivalents.
    ("**create-skill** skill (Cursor's built-in for authoring SKILL.md files)",
     "**skill-creator** skill (Anthropic's built-in for authoring SKILL.md files)"),
    ("Cursor's built-in `create-skill` skill", "the `skill-creator` skill"),
    ("Cursor's built-in `create-skill`", "the `skill-creator` skill"),
    ("`create-skill`", "`skill-creator`"),
    ("create-skill", "skill-creator"),
    ("the `deslop` skill from the `cursor-team-kit` plugin (`/deslop`)", "the **deslop** skill (`/deslop`, bundled with pstack)"),
    ("`/deslop` from `cursor-team-kit`", "`/deslop`"),
    ("`cursor-team-kit` publishes `control-cli` (CLIs and TUIs) and `control-ui` (browser / Electron / web UIs)",
     "pstack bundles `control-cli` (CLIs and TUIs) and `control-ui` (browser / Electron / web UIs)"),
    (" (from `cursor-team-kit`)", ""),
    (" from `cursor-team-kit`", ""),
    ("Cursor's `/loop` command", "Claude Code's `/loop` command"),
    ("Cursor's built-in babysit skill", "any built-in or third-party babysit skill"),
    ("Cursor restart", "Claude Code restart"),
    ("in the Cursor dashboard", "in the remote session list"),
    # Claude has no readonly flag on the Agent tool; read-only is a brief constraint.
    ("- `readonly`: `true`", "- read-only: append \"Do not edit, write, or commit anything.\" to its prompt"),
    ("Cursor cloud agent", 'remote agent (`isolation: "remote"`, else `isolation: "worktree"`)'),
    (" Readonly strips MCPs.", ""),
    ("- Tool calls (Shell, Grep, MCP, etc.) that match a skill's documented commands",
     "- `Skill` tool calls, and user turns that invoke a skill as a slash command (`/pstack:<name>`)\n- Tool calls (Bash, Grep, MCP, etc.) that match a skill's documented commands"),
    ("`node pstack/skills/", "`node <pstack root>/skills/"),
    ("`git show origin/main:pstack/skills/poteto-mode/playbooks/<execution playbook>.md`", "`cat <pstack root>/skills/poteto-mode/playbooks/<execution playbook>.md`"),
    ("`git show origin/main:pstack/skills/swarm/SKILL.md`", "`cat <pstack root>/skills/swarm/SKILL.md`"),
    ("`git show origin/main:pstack/skills/poteto-mode/playbooks/opening-a-pr.md`", "`cat <pstack root>/skills/poteto-mode/playbooks/opening-a-pr.md`"),
    ("`git show origin/main:pstack/skills/<each other leaf skill the program uses>`", "`cat <pstack root>/skills/<each other leaf skill the program uses>`"),
    ("`pstack/skills/", "`<pstack root>/skills/"),
    ("**skill-creator** skill (Anthropic's built-in for authoring SKILL.md files)",
     "**skill-creator** skill (Anthropic's skill-authoring skill. If it isn't installed, write the SKILL.md directly, with `name` and `description` frontmatter)"),
    ("readonly judge", "read-only judge"),
    # Claude model aliases have no vendor families; diversity is per model.
    ("different model families", "different models"),
    ("different model family", "different model"),
    ("use the closest valid slug of the same family from its error message", "use `opus` and say so"),
    ("full Task schema including `environment`", "full Agent schema including `isolation`"),
]

FRONTMATTER_DROP = {"mode", "icon", "color", "reminder", "is_background"}


def rewrite(text: str) -> str:
    for entry in REWRITES:
        if len(entry) == 3:
            pat, rep, _ = entry
            text = re.sub(pat, rep, text)
        else:
            pat, rep = entry
            text = text.replace(pat, rep)
    return text


def split_frontmatter(text: str):
    if not text.startswith("---\n"):
        return None, text
    end = text.index("\n---\n", 4)
    return text[4:end], text[end + 5:]


def clean_frontmatter(path: Path, text: str) -> str:
    fm, body = split_frontmatter(text)
    if fm is None:
        return text
    lines, skip_block = [], False
    for line in fm.split("\n"):
        key = line.split(":", 1)[0] if re.match(r"^[A-Za-z_-]+:", line) else None
        if key is not None:
            skip_block = key in FRONTMATTER_DROP
            if key == "is_background":
                lines.append("background: true")
                continue
        if not skip_block:
            lines.append(line)
    return "---\n" + "\n".join(lines) + "\n---\n" + body


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT, ignore=shutil.ignore_patterns(".cursor-plugin", "node_modules"))
    (OUT / ".claude-plugin").mkdir()


    # Vendor the cursor-team-kit skills poteto-mode routes to (MIT, Cursor).
    for name in ("deslop", "control-cli", "control-ui"):
        shutil.copytree(TEAM_KIT / "skills" / name, OUT / "skills" / name)

    # New /pstack entry skill (Cursor has no equivalent; it is the plugin itself).
    (OUT / "skills" / "pstack").mkdir()
    shutil.copy(Path(PATCHES / "pstack-router.md"), OUT / "skills" / "pstack" / "SKILL.md")

    # worktree-audit: Claude Code transcript dirs, GNU/BSD-portable stat and date.
    audit = OUT / "skills/poteto-mode/scripts/worktree-audit.sh"
    src = audit.read_text()
    for old, new in [
        ('# Transcripts dir: ~/.cursor/projects/<slugified-repo-path>/agent-transcripts.\n'
         'slug=$(printf \'%s\' "$main_wt" | sed \'s#^/##; s#/#-#g\')\n'
         'transcripts="$HOME/.cursor/projects/$slug/agent-transcripts"\n',
         Path(PATCHES / "audit-header.sh").read_text()),
        ('\tif [ -d "$transcripts" ]; then\n'
         '\t\tf=$(rg -l -e "${wt}/" -e "${wt}\\"" "$transcripts" 2>/dev/null \\\n'
         '\t\t\t| xargs stat -f \'%m %N\' 2>/dev/null | sort -rn | head -1)\n'
         '\t\tif [ -n "$f" ]; then last_ts=$(echo "$f" | awk \'{print $1}\')\n'
         '\t\t\tlast=$(date -r "$last_ts" \'+%Y-%m-%d\' 2>/dev/null); fi\n',
         Path(PATCHES / "audit-loop.sh").read_text()),
    ]:
        if old not in src:
            sys.exit(f"worktree-audit.sh drifted: {old[:60]!r}")
        src = src.replace(old, new)
    audit.write_text(src)

    changed = 0
    for path in sorted(OUT.rglob("*.md")):
        # benny drives Cursor Automations; it ships verbatim as a reference pack.
        if "automations" in path.relative_to(OUT).parts:
            continue
        original = path.read_text()
        text = rewrite(original)
        if path.name == "SKILL.md" or path.parent.name == "agents":
            text = clean_frontmatter(path, text)
        if text != original:
            path.write_text(text)
            changed += 1
    print(f"rewrote {changed} markdown files", file=sys.stderr)


if __name__ == "__main__":
    main()
