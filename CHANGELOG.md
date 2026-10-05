# Changelog

Newest first. The Claude agent that syncs this repo adds one entry per landed update.

## 0.15.10-claude.1 (2026-10-05)

First release. Ported from `cursor/plugins@4e5b1cf` (pstack 0.15.10, "feat(pstack): add /poteto-help skill (#502)").

- All 51 pstack skills, 23 playbooks, 24 principles, both subagents, the scripts, and the guide, translated from Cursor to Claude.
- Bundled `deslop`, `control-cli`, and `control-ui` from `cursor-team-kit`.
- New `pstack` router skill and optional `/pstack` and `/poteto-mode` shortcut skills.
- `setup-pstack` writes an always-loaded `pstack-models.md` rule with Claude model tiers.
