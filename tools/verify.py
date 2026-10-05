#!/usr/bin/env python3
"""Verify a built plugin/ against its upstream checkout.

Usage: tools/verify.py [--smoke]

Static checks always run. --smoke adds two headless Claude Code runs that
exercise /pstack routing and a /poteto-mode bug fix end to end (about $1).
Exits non-zero if any check fails. Each check prints PASS, FAIL, or WARN.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
PLUGIN = Path(os.environ.get("OUT", REPO / "plugin"))
UPSTREAM = Path(os.environ.get("UPSTREAM_DIR", REPO / ".upstream" / "plugins"))
SRC = UPSTREAM / "pstack"
PORT_ONLY_SKILLS = {"pstack", "deslop", "control-cli", "control-ui"}

# Cursor-only wording a model-facing file may still contain, as (path suffix, substring).
ALLOWED_RESIDUALS = [line.split("\t", 1) for line in (TOOLS / "residual-allowlist.tsv").read_text().splitlines()
                     if line and not line.startswith("#")]
RESIDUAL = re.compile(r"\bTask\b|\b[Cc]ursor\b|agent-transcripts|readonly|environment:|grok|gpt-5|\bsol\b|\.mdc|alwaysApply"
                      r"|cloud agent|AskQuestion\b|generalPurpose|claude-opus|system prompt|from trunk|pstack/skills|CLAUDE\.md")

failures = 0


def report(name: str, ok: bool, detail: str = "", warn: bool = False) -> None:
    global failures
    status = "PASS" if ok else ("WARN" if warn else "FAIL")
    if not ok and not warn:
        failures += 1
    print(f"{status}  {name}" + (f"\n      {detail}" if detail else ""))


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {}
    block = text[4:text.index("\n---\n", 4)]
    return dict(m.groups() for m in re.finditer(r"^([A-Za-z_-]+):\s*(.*)$", block, flags=re.M))


def check_validate() -> None:
    if not shutil.which("claude"):
        report("claude plugin validate", False, "claude CLI not installed", warn=True)
        return
    for target, label in ((PLUGIN, "plugin manifest"), (REPO, "marketplace manifest")):
        out = run(["claude", "plugin", "validate", str(target)])
        report(f"claude plugin validate ({label})", out.returncode == 0 and "passed" in out.stdout, out.stdout.strip()[-300:])


def check_frontmatter() -> None:
    bad = []
    for skill in sorted(PLUGIN.glob("skills/*/SKILL.md")):
        fm = frontmatter(skill.read_text())
        if fm.get("name") != skill.parent.name or not fm.get("description"):
            bad.append(skill.parent.name)
    for agent in sorted(PLUGIN.glob("agents/*.md")):
        fm = frontmatter(agent.read_text())
        if fm.get("name") != agent.stem or not fm.get("description"):
            bad.append(f"agent {agent.stem}")
    report("skill and agent frontmatter (name matches file, description set)", not bad, ", ".join(bad))


def check_skill_set() -> None:
    upstream = {p.parent.name for p in SRC.glob("skills/*/SKILL.md")}
    port = {p.parent.name for p in PLUGIN.glob("skills/*/SKILL.md")}
    missing, extra = upstream - port, port - upstream - PORT_ONLY_SKILLS
    report(f"skill set ({len(upstream)} upstream + {len(PORT_ONLY_SKILLS)} port-only = {len(port)})",
           not missing and not extra, f"missing={sorted(missing)} unexpected={sorted(extra)}")
    up_agents = len(list(SRC.glob("agents/*.md")))
    report(f"agents ({up_agents} upstream)", up_agents == len(list(PLUGIN.glob("agents/*.md"))))


def check_links() -> None:
    skills = {p.parent.name for p in PLUGIN.glob("skills/*/SKILL.md")}
    bad = []
    for md in PLUGIN.rglob("*.md"):
        if "automations" in md.relative_to(PLUGIN).parts:
            continue
        text = md.read_text()
        rel = md.relative_to(PLUGIN)
        for m in re.finditer(r"\]\((?!https?://|#|mailto:)([^)\s]+?)(#[^)]*)?\)", text):
            if m.group(1) != "url" and not (md.parent / m.group(1)).resolve().exists():
                bad.append(f"link {rel}: {m.group(1)}")
        for m in re.finditer(r"`((?:\.\./)?(?:playbooks|references|scripts)/[^`\s*<]+)`", text):
            cands = [md.parent / m.group(1), md.parent.parent / m.group(1), PLUGIN / "skills/poteto-mode" / m.group(1)]
            if not any(c.exists() for c in cands):
                bad.append(f"path {rel}: {m.group(1)}")
        for m in re.finditer(r"\*\*([a-z0-9]+(?:-[a-z0-9]+)*)\*\* (?:skill|principle)", text):
            n = m.group(1)
            if n not in skills and f"principle-{n}" not in skills and n != "skill-creator":
                bad.append(f"skill {rel}: {n}")
    report("links, bundled paths, and skill references resolve", not bad, "\n      ".join(sorted(set(bad))))


def check_residuals() -> None:
    hits = []
    # README.md, NOTICE.md, and make-bot-ui describe Cursor on purpose; everything else is model-facing.
    skip = {"README.md", "NOTICE.md", "skills/make-bot-ui/SKILL.md"}
    targets = [p for p in PLUGIN.rglob("*.md")
               if "automations" not in p.relative_to(PLUGIN).parts and str(p.relative_to(PLUGIN)) not in skip]
    for md in targets:
        rel = str(md.relative_to(PLUGIN))
        for n, line in enumerate(md.read_text().splitlines(), 1):
            for m in RESIDUAL.finditer(line):
                context = line[max(0, m.start() - 60): m.end() + 60]
                if not any(rel.endswith(path) and sub in line for path, sub in ALLOWED_RESIDUALS):
                    hits.append(f"{rel}:{n}: ...{context}...")
                break
    report("no unreviewed Cursor-specific wording", not hits,
           ("Judge each hit. Translate it per MAINTAINING.md, or add an allowlist line if it is correct as is.\n      "
            + "\n      ".join(hits[:40])) if hits else "")


def check_scripts() -> None:
    port_scripts = PLUGIN / "skills/poteto-mode/scripts"
    out = run(["diff", "-rq", "-x", "node_modules", str(SRC / "skills/poteto-mode/scripts"), str(port_scripts)])
    changed = [l for l in out.stdout.splitlines() if "worktree-audit.sh" not in l]
    report("bundled scripts match upstream (except worktree-audit.sh)", not changed, "\n      ".join(changed))
    if not shutil.which("bun"):
        report("script test suites (bun test)", False, "bun not installed", warn=True)
        return
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "scripts"
        shutil.copytree(port_scripts, work)
        run(["bun", "install", "--frozen-lockfile"], cwd=work)
        out = run(["bun", "test", "orch", "watch-pr"], cwd=work)
        tail = (out.stdout + out.stderr).strip().splitlines()[-4:]
        report("script test suites (bun test)", out.returncode == 0, " | ".join(tail))


def plan_skeleton(root: Path) -> str:
    text = (root / "skills/poteto-mode/playbooks/multi-phase-plan.md").read_text()
    blocks = re.findall(r"^(`{3,4})markdown\n(.*?)^\1$", text, flags=re.S | re.M)
    return max((b[1] for b in blocks), key=len)


def check_plan_parity() -> None:
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        for root in (SRC, PLUGIN):
            plan = Path(tmp) / "plan.md"
            plan.write_text(plan_skeleton(root))
            out = run(["node", str(root / "skills/poteto-mode/scripts/check-plan.mjs"), str(plan)])
            results.append(sorted(re.sub(r"^\S+plan\.md:\d+: ", "", l) for l in (out.stdout + out.stderr).splitlines()))
    report("check-plan.mjs gives the same verdict on the original and ported plan template", results[0] == results[1],
           f"original={results[0]} port={results[1]}")


def check_worktree_audit() -> None:
    script = PLUGIN / "skills/poteto-mode/scripts/worktree-audit.sh"
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        sh = lambda *a, cwd=None: run(list(a), cwd=cwd)
        sh("git", "init", "-q", "--bare", str(t / "origin.git"))
        sh("git", "clone", "-q", str(t / "origin.git"), str(t / "repo"))
        repo = t / "repo"
        for a in (["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            sh("git", *a, cwd=repo)
        (repo / "a").write_text("a")
        for a in (["add", "a"], ["commit", "-qm", "a"], ["branch", "-M", "main"], ["push", "-q", "origin", "main"],
                  ["worktree", "add", "-q", "-b", "feat-x", str(t / "elsewhere/feat-x")],
                  ["worktree", "add", "-q", "-b", "feat-y", str(t / "repo-wt/feat-y")]):
            sh("git", *a, cwd=repo)
        home = t / "home dir"
        slug = lambda p: re.sub(r"[^A-Za-z0-9]", "-", str(p))
        for cwd, mention in ((t / "elsewhere/feat-x", t / "elsewhere/feat-x"), (repo, t / "repo-wt/feat-y")):
            d = home / ".claude/projects" / slug(cwd)
            d.mkdir(parents=True, exist_ok=True)
            (d / f"{slug(mention)[-8:]}.jsonl").write_text(json.dumps({"cwd": f"{mention}/"}) + "\n")
        out = run(["bash", str(script), str(repo)], env={**os.environ, "HOME": str(home)})
        rows = [l.split("\t") for l in out.stdout.splitlines()[1:]]
        ok = len(rows) == 2 and all(r[6] != "-" and r[7] == "verify-recent-chat" for r in rows)
        report("worktree-audit.sh finds Claude transcripts (worktree outside repo path, HOME with a space)", ok, out.stdout + out.stderr)


def stream_calls(path: Path):
    calls, result = [], None
    for line in path.read_text().splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "assistant" and not event.get("parent_tool_use_id"):
            calls += [c for c in event["message"].get("content", []) if c.get("type") == "tool_use"]
        if event.get("type") == "result":
            result = event
    return calls, result


def headless(prompt: str, cwd: Path, model: str, log: Path, turns: int) -> None:
    with open(log, "w") as fh:
        subprocess.run(["claude", "-p", "--model", model, "--plugin-dir", str(PLUGIN), "--dangerously-skip-permissions",
                        "--max-turns", str(turns), "--output-format", "stream-json", "--verbose", prompt],
                       cwd=cwd, stdout=fh, stderr=subprocess.STDOUT, timeout=1500)


def check_smoke() -> None:
    logs = REPO / ".verify"
    logs.mkdir(exist_ok=True)
    headless("/pstack:pstack /how does pstack/skills/poteto-mode/scripts/worktree-audit.sh decide which bucket a worktree lands in?",
             UPSTREAM, "sonnet", logs / "router-how.jsonl", 40)
    calls, result = stream_calls(logs / "router-how.jsonl")
    read_how = any(c["name"] == "Read" and c["input"].get("file_path", "").endswith("skills/how/SKILL.md") for c in calls)
    spawned = any(c["name"] in ("Agent", "Task") for c in calls)
    report("smoke: /pstack /how routes to the how skill and spawns its explainer", read_how and spawned and result is not None,
           f"read how={read_how} spawned={spawned} log=.verify/router-how.jsonl")

    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "bugrepo"
        repo.mkdir()
        (repo / "sum.js").write_text("// Returns 1 + 2 + ... + n.\nfunction sumTo(n) {\n  let total = 0;\n"
                                     "  for (let i = 1; i < n; i++) total += i;\n  return total;\n}\nmodule.exports = { sumTo };\n")
        (repo / "package.json").write_text('{ "name": "bugrepo", "version": "1.0.0", "scripts": { "test": "node --test" } }\n')
        for a in (["init", "-q", "-b", "main"], ["config", "user.email", "t@t"], ["config", "user.name", "t"], ["add", "-A"], ["commit", "-qm", "init"]):
            run(["git", *a], cwd=repo)
        headless("/pstack:poteto-mode sumTo(3) in sum.js returns 3 instead of 6. repro first, then fix and verify. "
                 "there is no git remote, so stop before opening a PR.", repo, "opus", logs / "poteto-bugfix.jsonl", 80)
        calls, result = stream_calls(logs / "poteto-bugfix.jsonl")
        text = json.dumps([c["input"] for c in calls])
        playbook = "playbooks/bug-fix.md" in text
        tasks = any(c["name"] in ("TaskCreate", "TodoWrite") for c in calls)
        fixed = run(["node", "-e", "process.exit(require('./sum.js').sumTo(3) === 6 ? 0 : 1)"], cwd=repo).returncode == 0
        tests = run(["node", "--test"], cwd=repo).returncode == 0
        commits = int(run(["git", "rev-list", "--count", "HEAD"], cwd=repo).stdout.strip() or 0)
        report("smoke: /poteto-mode follows the bug-fix playbook to a verified fix",
               playbook and fixed and tests and commits >= 2 and result is not None,
               f"playbook={playbook} task_list={tasks} fixed={fixed} tests_pass={tests} commits={commits} log=.verify/poteto-bugfix.jsonl")
        if not tasks:
            report("smoke: /poteto-mode opened a task list with the playbook steps", False, "model skipped the task list", warn=True)


def main() -> None:
    if not SRC.exists() or not PLUGIN.exists():
        sys.exit("run tools/build.sh first")
    check_validate()
    check_frontmatter()
    check_skill_set()
    check_links()
    check_residuals()
    check_scripts()
    check_plan_parity()
    check_worktree_audit()
    if "--smoke" in sys.argv:
        check_smoke()
    print(f"\n{'ALL CHECKS PASSED' if failures == 0 else f'{failures} CHECK(S) FAILED'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
