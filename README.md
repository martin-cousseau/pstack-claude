# pstack for Claude

[poteto's pstack](https://github.com/cursor/plugins/tree/main/pstack), ported from Cursor to Claude Code and the Claude app.

pstack turns an agent into a careful engineering team. `/poteto-mode` reads your task, picks one of 23 playbooks (bug fix, perf, feature, refactor, babysit a PR, overnight run, and more), and works through it with 24 engineering principles, reproduce-first debugging, verified results, and multi-model review. The goal is less code, of higher quality.

This repo is maintained by Claude agents. Every day, an agent checks Cursor's repo for pstack changes. When it finds some, it rebuilds the port, verifies it, and publishes a new version.

## Install

### Claude Code

Inside Claude Code:

```text
/plugin marketplace add martin-cousseau/pstack-claude
/plugin install pstack@pstack-claude
```

Or from your shell:

```bash
claude plugin marketplace add martin-cousseau/pstack-claude
claude plugin install pstack@pstack-claude
```

On Claude Code 2.1.275 or later, one command does both:

```text
/plugin install pstack --marketplace martin-cousseau/pstack-claude
```

### Claude app (desktop and web)

Open **Customize → Plugins → Add → Add marketplace** and enter `martin-cousseau/pstack-claude`, then install **pstack**.

You can also download `pstack.plugin` from the [latest release](https://github.com/martin-cousseau/pstack-claude/releases/latest), then use **Customize → Plugins → Add → Upload plugin**.

### For a whole team

Commit this to your project's `.claude/settings.json`. Everyone who opens the project in Claude Code gets pstack.

```json
{
  "extraKnownMarketplaces": {
    "pstack-claude": {
      "source": {
        "source": "git",
        "url": "https://github.com/martin-cousseau/pstack-claude.git",
        "ref": "main"
      }
    }
  },
  "enabledPlugins": {
    "pstack@pstack-claude": true
  }
}
```

### Optional: `/pstack` and `/poteto-mode` without the prefix

Claude namespaces plugin commands, so they are `/pstack:poteto-mode`, `/pstack:how`, and so on. Two small shortcut skills give you the bare names:

```bash
git clone --depth 1 https://github.com/martin-cousseau/pstack-claude /tmp/pstack-claude
mkdir -p ~/.claude/skills && cp -r /tmp/pstack-claude/shortcuts/* ~/.claude/skills/
```

### Staying up to date

Claude Code doesn't auto-update third-party marketplaces by default. To update:

```text
/plugin marketplace update pstack-claude
```

Or turn on auto-update for `pstack-claude` in `/plugin` under **Marketplaces**.

## First run

Pick which Claude model handles each role:

```text
/pstack:setup-pstack
```

It writes `pstack-models.md` to `~/.claude/rules/` (just you) or `.claude/rules/` (committed with the project), and Claude loads it in every session. Code work defaults to `sonnet` and judgment to `opus`. Review panels default to `opus`, `fable`, and `sonnet`. If your plan doesn't include `fable`, setup detects that and substitutes another model.

## Use it

| You type | What happens |
|---|---|
| `/pstack:poteto-mode the scroll drifts every 750ms when idle. repro first, then fix and verify.` | Bug fix playbook: reproduce, root-cause, fix, prove it. |
| `/pstack:poteto-mode i'm going to bed. land the stack even if ci flakes.` | Autonomous run: drives to a checkable finish line. |
| `/pstack:how do we cancel runs?` | A subsystem walkthrough from parallel explorers. |
| `/pstack:why is this feature flag not on yet?` | History from git, PRs, tickets, and docs. |
| `/pstack:interrogate review this pr.` | Several models try to break the diff. |
| `/pstack:pstack <anything>` | Routes for you: a task goes to poteto-mode, `/name` goes to that skill, and a question goes to poteto-help. |
| `/pstack:poteto-help` | Which skill or playbook fits your situation. |

Once loaded, `/poteto-mode` stays in effect for the rest of the chat. To have it in every chat, add a rule file such as `~/.claude/rules/poteto-mode.md` that says: "For non-trivial engineering work, load the pstack:poteto-mode skill first."

The [plugin README](plugin/README.md) has poteto's full guide: every skill, playbook, and principle, plus the port notes. The [step-by-step guide](plugin/docs/guide/README.md) walks through a first real task.

## What's different from Cursor

The workflows, playbooks, and principles are unchanged. What changed is the plumbing.

- **Models.** Cursor's Grok, GPT, and Opus become Claude models.
- **Subagents.** These run through Claude's Agent tool. Cursor's cloud agents become remote or worktree-isolated agents.
- **Settings.** The model settings live in a Claude rules file.
- **Bundled skills.** `deslop`, `control-cli`, and `control-ui` come from Cursor's `cursor-team-kit` plugin, so they're bundled here.
- **Not ported.** `make-bot-ui` (Cursor Grok Bot webhooks) ships marked as Cursor-only. The benny automation pack, which runs on Cursor Automations, ships for reference only.

The full mapping is in [MAINTAINING.md](MAINTAINING.md#translation-spec).

## How it's maintained

- **Daily sync.** A scheduled Claude agent checks `cursor/plugins` main for commits that touch pstack. If there are none, it stops.
- **Rebuild.** The plugin is generated. `tools/build.sh` copies upstream pstack, applies a reviewed table of Cursor-to-Claude rewrites (`tools/convert.py`) and exact hand edits (`tools/apply_patches.py`), and packages `pstack.plugin`. Nothing in `plugin/` is edited by hand.
- **Verify.** `tools/verify.py` checks several things:
  - the manifests validate
  - every link and skill reference resolves
  - no unreviewed Cursor wording remains
  - the bundled scripts' test suites pass
  - the plan checker agrees with upstream
  - two headless Claude runs succeed: a routing check and a real bug fix through `/poteto-mode`

  CI runs the static checks on every push.
- **Land.** If everything passes, the agent updates [CHANGELOG.md](CHANGELOG.md), pushes to `main`, and cuts a release. An update that needs a judgment call goes to a pull request for the owner instead.

## Contributing

This is a single-maintainer repo run by automation. Issues and pull requests from accounts other than the owner are closed automatically.

- Problems with pstack itself belong upstream in [cursor/plugins](https://github.com/cursor/plugins).
- Forks are welcome. The build tooling in `tools/` works for any fork.

## Credits and license

- pstack is by [Lauren Tan (poteto)](https://github.com/poteto), MIT licensed.
- `deslop`, `control-cli`, and `control-ui` are from Cursor's `cursor-team-kit`, MIT licensed.
- The port and its tooling are MIT. See [LICENSE](LICENSE) and [plugin/NOTICE.md](plugin/NOTICE.md).

This is an independent community port. It is not affiliated with or endorsed by Cursor or Anthropic.
