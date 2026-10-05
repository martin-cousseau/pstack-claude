# Transcripts: Claude Code keeps one dir per working directory under
# ~/.claude/projects/, named by the path with each non-alphanumeric char as "-"
# (long paths are cut at 200 chars plus a hash suffix, hence the trailing glob).
# A session started inside a worktree lives under that worktree's own slug, so
# each row scans the main repo's dirs and the worktree's dirs.
slugify() { printf '%s' "$1" | sed 's#[^A-Za-z0-9]#-#g' | cut -c1-200; }
mtime() { stat -c '%Y %n' "$1" 2>/dev/null || stat -f '%m %N' "$1"; }
projects="$HOME/.claude/projects"
