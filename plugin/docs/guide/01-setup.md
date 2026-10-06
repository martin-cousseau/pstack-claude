# Set up pstack

In this page you install the plugin, pick which models pstack uses, and run your first task. Setup is one command plus a short conversation.

## Install the plugin

Accept the `pstack.plugin` file from its chat card in the Claude app, or add the plugin directory to Claude Code. In Claude every pstack command carries the plugin prefix: `/setup-pstack` on these pages is typed `/pstack:setup-pstack`. Save the optional `/pstack` and `/poteto-mode` shortcut skills to drop the prefix for those two.

## Pick your models

Run:

```text
/setup-pstack
```

[`/setup-pstack`](../../skills/setup-pstack/SKILL.md) detects the models you have access to, asks whether the config is just yours or committed with the project, asks for a budget, shows you each role (code delegates, judgment, the review panels), and asks what you want. Answer the questions. It writes `pstack-models.md` into `.claude/rules/` (yours or the project's), which Claude loads every session, so every pstack skill sees it.

The defaults match the `unlimited` budget: `opus` for judgment, `sonnet` for code, and `opus, fable, sonnet` review panels. `large` drops `fable`. `medium` and `small` move roles to cheaper models and spend fewer tokens.

You only override what you care about. A role with no line in the config keeps the skill's default. To restore a default, delete that role's line. A rerun of `/setup-pstack` keeps the roles you changed by hand. When a default changes, a rule written before the change still pins the old default, so delete those role lines, or delete the file, then run `/setup-pstack` again.

You might be wondering how to keep a role on your chat's model. Set a role to `inherit-parent` or `auto` and pstack omits the subagent `model` field, so the subagent inherits your parent chat model. Both values mean the same thing, and neither is a model slug. For a panel role the value is a list, and one subagent runs per entry, so the list length sets the panel size. Setup also configures `swarm workers`, the default model for every `/swarm` worker unless a race names a model for each arm.

## Accept the verification offer, or don't

At the end of setup, `/setup-pstack` looks for a way to prove app behavior in your project, either a `verify-*` skill or an existing harness. If it finds neither, it offers once to generate one with [`/create-verification-skill`](../../skills/create-verification-skill/SKILL.md).

Say yes and it writes `.claude/skills/verify-<app>/`, a project-local skill that teaches agents to drive your app the way a user does. It proves the skill works once before handing it over. Say no and setup moves on. You can run `/create-verification-skill` yourself any time. [Verify and ship](./06-verify-and-ship.md#create-a-project-verification-skill) covers it in depth.

If you're new to pstack, say yes. An agent that can check its own work keeps going until the check passes. An agent that can't hands every result back to you to check by hand. Of everything in this guide, the verification skill pays off the most.

After setup, start a new chat. Rule files load at session start, so the config applies to new sessions.

## Keep the cost in check

pstack spends extra tokens on subagents and review panels. That's the price of the rigor. To spend fewer:

- Rerun `/setup-pstack` and pick a smaller budget or cheaper models. A strong model in the main chat with cheaper, faster models in the code roles is a good split.
- Set a role to `auto` or `inherit-parent` so it runs on the chat's own model.
- Shorten a panel list. Each entry runs one subagent.
- Save `/poteto-mode` for work that needs rigor. A small, obvious edit doesn't.

## Run your first task

Pick something real but small, and describe it the way you'd describe it to a colleague:

```text
/poteto-mode add a --json flag to this command. text output stays byte-identical. verify both.
```

Watch the todo list. Its first items are the matched playbook's steps copied in, the Feature playbook for this prompt. If `/poteto-mode` skips a step, the step stays in the list with `skip: <reason>`, so you can see what it chose not to do.

From here you can type normal follow-ups. Once invoked, `/poteto-mode` stays in the conversation and keeps applying for the rest of the chat. Claude has no Custom Modes, so to have it in every chat, add a rule file such as `~/.claude/rules/poteto-mode.md` saying "For non-trivial engineering work, load the pstack:poteto-mode skill first."

Next: [Route work through `/poteto-mode`](./02-poteto-mode.md).
