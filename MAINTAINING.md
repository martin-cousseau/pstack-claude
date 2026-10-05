# Maintaining pstack-claude

This file is the runbook for the Claude agents that maintain this repo, and for the owner, `martin-cousseau`. Read all of it before changing anything.

## Ground rules

- `plugin/` is generated. Never edit it by hand. Change `tools/`, then run `tools/build.sh`.
- Keep upstream's meaning. Translate only tools, models, paths, and Cursor product features, per the spec below. Workflows, playbooks, principles, and prose stay as poteto wrote them.
- Bundled scripts stay byte-identical to upstream, except `worktree-audit.sh`, whose transcript scan is patched for Claude.
- `UPSTREAM` holds the `cursor/plugins` commit that `plugin/` was built from. Update it only together with the `plugin/` it produced, after `tools/verify.py` passes.
- Only the owner's issues and pull requests stay open. `.github/workflows/close-external.yml` closes the rest, and the daily sync sweeps up anything it missed.
- Never take an irreversible action beyond pushing this repo and cutting its releases. Never force-push `main`.

## Layout

| Path | What it is |
|---|---|
| `plugin/` | The generated Claude plugin. `.claude-plugin/marketplace.json` points Claude Code here. |
| `tools/convert.py` | Copies upstream pstack plus three `cursor-team-kit` skills, applies the ordered `REWRITES` table to every markdown file, and cleans frontmatter. |
| `tools/apply_patches.py` | Exact `(file, old, new)` hand edits in `PATCHES`. It exits non-zero and prints `MISSING` when upstream text drifted. It also writes `plugin.json`, `NOTICE.md`, and the benny note. |
| `tools/patches/` | Whole-file replacements: `setup-pstack.md`, the `pstack` router skill, the README port header, and the two `worktree-audit.sh` blocks. |
| `tools/residual-allowlist.tsv` | Lines that mention Cursor on purpose, reviewed. |
| `tools/build.sh [ref]` | Clones `cursor/plugins` into `.upstream/plugins`, checks out `ref` (default `origin/main`), builds `plugin/`, and packages `dist/pstack.plugin`. |
| `tools/verify.py [--smoke]` | Static checks, plus two headless Claude runs with `--smoke`. |
| `shortcuts/` | User-level `pstack` and `poteto-mode` skills that drop the plugin prefix. |
| `CHANGELOG.md` | One entry per landed sync or fix. |

## Translation spec

| Cursor | Claude |
|---|---|
| `Task` tool, `subagent_type: generalPurpose` | Agent tool (named `Task` in some Claude Code versions), `subagent_type: general-purpose` |
| `poteto-agent`, `Comment Sicko` | `pstack:poteto-agent`, `pstack:comment-sicko` (agent files `poteto-agent.md`, `comment-sicko.md`) |
| `claude-opus-*` / `grok-*` / `gpt-*-sol-*` | `opus` / `sonnet` / `fable`. Panels default to `opus, fable, sonnet`. There are no vendor families. Diversity is per model, and a rejected model falls back to the strongest accepted model not already on the panel. |
| Reasoning budget (effort tokens) | Model tiers per budget (see `tools/patches/setup-pstack.md`) |
| `~/.cursor/rules/pstack-models.mdc`, always applied | `pstack-models.md` in `.claude/rules/` (project, read first) or `~/.claude/rules/` (user). Claude Code loads rule files every session. |
| `AskQuestion` | `AskUserQuestion` (2 to 4 options, `multiSelect`, free-text answer built in) |
| Todo list | Task list (TaskCreate/TaskUpdate, or TodoWrite) |
| `readonly: true` | Append "Do not edit, write, or commit anything." to the prompt |
| `readonly: false` / agent mode | `general-purpose` (not the read-only `Explore` type) so MCP tools stay reachable |
| Cloud agents, `environment: "cloud"` | `isolation: "remote"`, falling back to `isolation: "worktree"` when the Agent tool lacks it or refuses the call |
| `~/.cursor/projects/<slug>/agent-transcripts/` | `~/.claude/projects/<slug>/<session-id>.jsonl`, where the slug is the absolute cwd with each non-alphanumeric character turned into `-`. Subagents are under `<session-id>/subagents/`. |
| `.cursor/skills/`, `~/.cursor/skills/`, `~/.cursor/plugins/` | `.claude/skills/`, `~/.claude/skills/`, `~/.claude/plugins/` |
| Cursor's `create-skill` | Anthropic's `skill-creator` skill (fall back to writing the SKILL.md directly) |
| `cursor-team-kit` `deslop`, `control-cli`, `control-ui` | Bundled in `plugin/skills/` |
| Custom Mode | None. A loaded skill stays for the chat. A rule file turns it on everywhere. |
| Cursor `/loop`, Plan Mode | Claude Code `/loop`, plan mode |
| "path in the system prompt" (agent store) | `~/.claude/pstack/<project-slug>/` |
| `pstack/skills/...` repo paths, `git show origin/main:pstack/...` | `<pstack root>/skills/...` (poteto-mode defines it as the plugin root), keeping `git show origin/main:` as the vendored-repo alternative so `check-plan.mjs` still passes |
| Skill references by name | Skills Read their siblings at `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`. A note is injected into every skill that names another. Never write that variable where text describes its unexpanded form, because Claude substitutes every occurrence in a loaded skill. |

Where a change goes:

- **A term that means the same everywhere** goes in `REWRITES` in `tools/convert.py`. Order matters, so put specific patterns before general ones.
- **A sentence that needs rewording in one place** goes in `PATCHES` in `tools/apply_patches.py`. Copy `old` exactly from the converted text, since patches run after the rewrites, in order.
- **A file whose logic changes for Claude** goes in `tools/patches/`.
- **A Cursor mention that is correct as is** goes in `tools/residual-allowlist.tsv`.

## Daily sync

The scheduled task runs this. A quiet run, with nothing upstream and nothing from the owner, ends with no message.

1. **Set up.** Attach `martin-cousseau/pstack-claude` with push access and clone it (depth 1 is enough). Install anything `tools/verify.py` needs that is missing (`bun`, `zip`, `jq`, `rg`).
2. **Sweep external issues and PRs.** List open issues and pull requests through `gh api repos/martin-cousseau/pstack-claude/issues?state=open&per_page=100`. Close every one whose author is not `martin-cousseau`, with the same comment `close-external.yml` posts. This backs up the workflow.
3. **Detect upstream changes.** Clone `https://github.com/cursor/plugins` into `.upstream/plugins` with `--filter=blob:none`. Then run `git log --oneline $(cat UPSTREAM)..origin/main -- pstack cursor-team-kit/skills/deslop cursor-team-kit/skills/control-cli cursor-team-kit/skills/control-ui cursor-team-kit/LICENSE`. If `UPSTREAM` is not an ancestor of `origin/main` (upstream rewrote history), treat that as a change. If there is no change, skip to step 8.
4. **Build.** `tools/build.sh origin/main`. On `MISSING` patches, read `git -C .upstream/plugins diff $(cat UPSTREAM)..origin/main -- <file>` for each one. Then point the patch's `old` at the new upstream wording and re-derive `new` per the spec, or delete the patch if upstream removed the Cursor-ism. Rebuild until it applies. Every such edit is a judgment call.
5. **Verify.** `python3 tools/verify.py --smoke`.
   - **Residual hits:** translate them per the spec, or allowlist them if they are correct. Either is a judgment call.
   - **A new upstream skill or playbook** flows through automatically. Read it for Cursor-only concepts the spec doesn't cover.
   - **Script changes upstream** copy verbatim. If the `worktree-audit.sh` blocks drifted, update `tools/patches/audit-*.sh`.
   - **Smoke `FAIL`:** read `.verify/*.jsonl`. A model-compliance flake, such as skipping the task list, is a `WARN`, not a failure. Rerun once before treating a `FAIL` as real.
6. **Land.**
   - Write the new SHA to `UPSTREAM`. Add a `CHANGELOG.md` entry at the top with the date, version, upstream range, upstream commit subjects, and any port changes.
   - **No changes under `tools/` and every check passes:** commit `sync: pstack <version> (cursor/plugins@<sha7>)`, rebase on `origin/main`, and push `main`.
   - **Anything changed under `tools/`:** push branch `sync/<sha7>` and open a pull request with `gh api` (REST). The body lists each judgment call, the file, why, and the verify output. Do not merge it.
   - **Verify still fails after a real attempt:** open the pull request anyway, titled `sync blocked: ...`, with the failing check output. Leave `main` alone.
7. **Release.** After a push to `main`, create release `v<plugin version>` targeting that commit, with release notes from the changelog entry. Upload `dist/pstack.plugin` as an asset (`gh api` to `uploads.github.com`). If the upload is refused, publish the release without the asset and say so.
8. **Owner issues.** For each open issue by `martin-cousseau`:
   - If it is a port bug or a change inside this spec, fix it in `tools/`, build, verify, and land per step 6. Comment with what changed and close it once it is on `main`.
   - If it needs the owner's decision, comment once with the analysis and options, then leave it. Never comment twice without new information.
9. **Report.** If anything landed, opened, or broke, send the owner one short message. Cover what changed upstream, the new version, and links to the commit, release, or pull request. Attach `dist/pstack.plugin` when a new version landed. A quiet run sends nothing.

## Manual commands

```bash
tools/build.sh                 # rebuild from upstream main
tools/build.sh <sha>           # rebuild from a pinned upstream commit
python3 tools/verify.py        # static checks
python3 tools/verify.py --smoke  # plus headless Claude runs (needs Claude Code signed in, about $1)
```
