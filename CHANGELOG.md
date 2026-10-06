# Changelog

Newest first. The Claude agent that syncs this repo adds one entry per landed update.

## 0.15.15-claude.1 (2026-10-06)

Synced `cursor/plugins@4e5b1cf..df58112` (pstack 0.15.10 to 0.15.15).

Upstream:

- feat(pstack): drop Sol, default to Opus xhigh and Grok (#511)
- feat(pstack): have /poteto-help ask about /setup-pstack when no model rule exists (#509)
- docs(pstack): refresh guide for /correct, checklist, prompting tips (#508)
- feat(pstack): add prompting references to /poteto-help (#507)
- fix(pstack): make /poteto-help typed-only (#506)

Port changes:

- `claude-opus-5-5-xhigh` maps to `opus`.
- Panels keep the spec's three seats (`opus, fable, sonnet`) and `reflect tooling` keeps `fable`, though upstream cut its panels to two models.
- `/poteto-help` is typed-only, as upstream. Its load-from-words lists drop it.
- The new guide text is translated: cloud subagents and cloud agents become remote agents, "restart Cursor" becomes "restart Claude Code", and Cursor Projects and the benny pack are marked as Cursor-only. The new defaults paragraph on guide page 1 describes the port's budget table.
- The note that an old rule pins old defaults stays, now in upstream's general wording.

## 0.15.10-claude.1 (2026-10-05)

First release. Ported from `cursor/plugins@4e5b1cf` (pstack 0.15.10, "feat(pstack): add /poteto-help skill (#502)").

- All 51 pstack skills, 23 playbooks, 24 principles, both subagents, the scripts, and the guide, translated from Cursor to Claude.
- Bundled `deslop`, `control-cli`, and `control-ui` from `cursor-team-kit`.
- New `pstack` router skill and optional `/pstack` and `/poteto-mode` shortcut skills.
- `setup-pstack` writes an always-loaded `pstack-models.md` rule with Claude model tiers.
