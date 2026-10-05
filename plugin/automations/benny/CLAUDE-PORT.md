# benny in the Claude port

benny runs as two Cursor Automations (Slack-triggered cloud agents) and enables pstack through `.cursor/settings.json`. Claude has no direct equivalent, so these files ship verbatim from the Cursor plugin, for reference. They are not registered as skills. Porting benny means re-creating its two automations as Claude scheduled tasks or routines that read Slack through a connector, and pointing their prompts at `templates/` here.
