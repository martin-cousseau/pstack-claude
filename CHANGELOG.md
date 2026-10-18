# Changelog

Newest first. The Claude agent that syncs this repo adds one entry per landed update.

## 0.15.25-claude.4 (2026-10-18)

Synced `cursor/plugins@df58112..16541c6` (pstack 0.15.15 to 0.15.25). This includes the 0.15.17, 0.15.19, 0.15.21, 0.15.23, 0.15.25-claude.1, 0.15.25-claude.2, and 0.15.25-claude.3 syncs from #2 through #8, which never reached `main`.

Upstream:

- fix(pstack): list every waiting item so each ketchup call is decidable (#692)
- pstack: refresh the docs and add a docs-vs-tree check (#704)
- fix(pstack): close three gaps in the Claude Code plugin (#705)
- fix(pstack): name every skill after its folder (#702)
- fix(pstack): make a brand with a type guard, not as (#700)
- feat(pstack): install pstack in Claude Code from a generated tree (#637)
- refactor(pstack): cut marginal sections from four skills (#634)
- pstack: restate four overspecified principles as reasoning, not rules (#633)
- chore(pstack): bump to 0.15.25 (#614)
- feat(pstack): have /ketchup explain changes with screenshots, videos, and diagrams (#628)
- chore(pstack): bump to 0.15.24 (#617)
- feat(pstack): add /sharpen (#615)
- pstack: autopilot loops catch the operator up with /ketchup (#616)
- feat(pstack): match subagent effort to the job, drop Graphite from orchestrate, and cut playbooks to principles (#613)
- refactor(pstack): make /ketchup read like /bro in 150 words (#609)
- refactor(pstack): reword /in-your-own-words around goals and the problem (#606)
- chore(pstack): bump to 0.15.22 (#605)
- feat(pstack): propose a cheap always-on signal after a deep debugging dig (#604)
- feat(pstack): shorten /ketchup replies and build them on real visuals (#595)
- feat(pstack): add /in-your-own-words to play back the goal before work (#602)
- fix(pstack): let poteto-agent find poteto-mode, drop ignored frontmatter, document the / menu (#597)
- chore(pstack): bump to 0.15.21 (#584)
- fix(pstack): tell agents where bundled leaf skills live (#577)
- chore(pstack): bump to 0.15.20 (#581)
- fix(pstack): create-verification-skill readiness means the app is usable (#573)
- feat(pstack): add Agent Plugins v1 root manifest (#576)
- fix(pstack): make the /poteto-mode chat the runner, poteto-agent a delegate (#575)
- fix(pstack): worktree-audit checks MERGED against the default branch, not origin/main (#574)
- fix(pstack): drop "Must always apply." from unslop description (#572)
- fix(watch-pr): paginate review threads instead of reading only the first 100 (#484)
- fix(pstack): respect fenced code blocks in plan checks (#536)
- fix(pstack): rename Comment Sicko agent id so Grok can spawn it (#486)
- refactor(pstack): cut unneeded sections from seven skills (#571)
- feat(pstack): show /ketchup decisions as before/after visuals (#570)
- feat(pstack): add /ketchup skill (#539)
- refactor(pstack): distill skill prompts to cut tokens (#538)

Port changes:

- Upstream now names `poteto-mode` and `make-bot-ui` after their folders, so the port's two frontmatter rename patches are gone.
- Four README and guide patches drifted under upstream's doc refresh (the custom-mode paragraph and its new `#using-a-skill-as-a-custom-mode` link, the "doesn't bundle" list that now names Cursor's built-in `/autopilot`, and the reworded Claude Code install block). Each now targets the new text with the same translation, and the install block is still deleted.
- The `/ketchup` rewrite (every waiting item listed and decidable from the reply) and the TypeScript type-guard brand pattern ship as is. They have no Cursor-specific wording.
- Upstream's Claude Code adapter (`docs/harness/claude-code.md`) gained rows and is still left out.
- Upstream's new Claude Code adapter, `docs/harness/claude-code.md`, is left out. It maps Cursor names at runtime, and the port translates the skills instead, so a rewritten copy would map Claude names to themselves.
- The README drops upstream's new Claude Code install lines and the note on regenerating `harness/pstack/`. A "not ported" line in the port header says why.
- The benny README patch now also covers upstream's added "so it is cursor-only" sentence, which the port's note already says.
- Upstream cut the `swarm` line "N is total workers, not the cloud concurrency limit.", so the patch that made it "remote concurrency limit" is gone. The other cuts in `interrogate`, `swarm`, and two principles ship as is.
- `/sharpen`, the reworded principles, the `/ketchup` visuals rewrite, and the autopilot `/ketchup` replies ship as is. They have no Cursor-specific wording, and every patch still applied. `/sharpen` is typed-only like upstream, and `sharpen` is an ordinary word, so the `/pstack` router sends it by name only as `/sharpen` or `pstack:sharpen`.
- `/ketchup` ships as is. It has no Cursor-specific wording.
- Seven patches drifted under upstream's rewording of `reflect`, `interrogate`, and `why`. Each now targets the new text with the same Claude translation: transcripts under `~/.claude/projects/<slug>/`, the `type: user` first-line check, no model families in the `interrogate` fallback, and full tool access instead of agent mode in `why`.
- The `interrogate` "A/B/C labels" patch is gone. Upstream now labels reviewers to match the entry count.
- Upstream's new inline `readonly: true` in `how` and `interrogate` becomes the "Do not edit, write, or commit anything." prompt line.
- New rewrite: ", and readonly strips MCPs." is dropped, as the existing " Readonly strips MCPs." rewrite already does.
- Upstream renamed the Comment Sicko agent to `comment-sicko`, so the port's frontmatter rename patch is gone. New rewrite: `subagent_type: "comment-sicko"` becomes `pstack:comment-sicko`.
- New rewrite: "Task spawn" becomes "Agent spawn" (new in `poteto-agent`).
- Upstream's new root `plugin.json` (Agent Plugins v1) ships with the port's name, version, and description, so it matches `.claude-plugin/plugin.json`.
- `worktree-audit.sh` now prints a `# base:` line before its header. The verify check skips it. The Claude transcript blocks still apply unchanged.
- Upstream's per-spawn "reasoning level and fast or standard speed" becomes the Agent tool's `effort` parameter. Every role starts at `xhigh`, since the port's `/setup-pstack` budget picks models, not effort levels. Claude has no per-subagent fast mode, so the speed half is dropped. With no `effort` parameter, agents spawn without it. New rewrite for the one-line pointer repeated across ~30 skills and playbooks.
- `poteto-agent`'s new no-path fallback searches `~/.claude/plugins/` and compares `.claude-plugin/plugin.json` versions. The "skill catalog hides this skill" sentence is dropped, because the port's `poteto-mode` is listed by the Skill tool and loads from it first.
- `poteto-mode` dropped "`/poteto-mode` and `poteto-agent` route through the same wrapper", so the port's `general-purpose` fallback now follows "Never spawn a `poteto-agent` to run the playbook itself."
- The `arena` and `interrogate` fallback patches now match upstream's new `cursor-grok-*` and `composer-*` families. The port still has no families and falls back by model.
- Rewritten `autopilot-full` and `autopilot-stack`: the per-tick re-read points at the pstack root (or `git show origin/main:` when vendored), and the decision trail goes in `~/.claude/pstack/<project-slug>/`. "Branches from that item's branch, not from trunk" is allowlisted, since it is about branching, not reading from trunk.
- `/ketchup`'s `/visualize` (a Cursor built-in) becomes a chart you render: a Mermaid chart, an image, or an artifact where the app offers one.
- The README's new `/` menu line names `/pstack:poteto-mode` and the shortcut, and says Claude loads the skill.
- `/in-your-own-words` ships as is, typed-only like upstream. The `/pstack` router routes it by name.
- The `poteto-agent` load patch now keeps upstream's new "Use the absolute path your parent gave you": it loads `pstack:poteto-mode` through the Skill tool, or Reads the `SKILL.md` at that path (`${CLAUDE_PLUGIN_ROOT}/skills/poteto-mode/SKILL.md`). The new `poteto-mode` line about `../<name>/SKILL.md` ships as is, because the layout is the same under `plugin/skills/`.

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
