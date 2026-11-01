#!/usr/bin/env python3
"""Task board for the two operators.

Usage:
  python scripts/board.py                 # everything
  python scripts/board.py --me            # tasks of the current git user (matched via docs/TEAM.md)
  python scripts/board.py --op A          # tasks of operator A (AB tasks included)
  python scripts/board.py --next [--me]   # startable tasks: TODO, deps DONE, no branch yet
  python scripts/board.py --task P1-04    # print one task block
  python scripts/board.py --summary       # per-phase progress only

States: DONE (Status: DONE in file) | WIP (a git branch containing the ID exists) | READY (deps done) | BLOCKED.
"""
import argparse, glob, os, re, subprocess, sys

# Ensure UTF-8 output on Windows terminals where default charmap might fail on unicode icons
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TASK_DIR = os.path.join(ROOT, "docs", "tasks")


def sh(*cmd):
    try:
        return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return ""


def parse_tasks():
    tasks = []
    for path in sorted(glob.glob(os.path.join(TASK_DIR, "phase-*.md"))):
        text = open(path, encoding="utf-8").read()
        blocks = re.split(r"(?m)^### ", text)[1:]
        for b in blocks:
            head, *rest = b.split("\n", 1)
            m = re.match(r"(P\d-\d\d) · (.+)", head.strip())
            if not m:
                continue
            body = rest[0] if rest else ""
            # cut at the next level-2 heading (exit checklist)
            body = re.split(r"(?m)^## ", body)[0]
            def field(name, default=""):
                mm = re.search(rf"(?m)^- {name}:\s*(.+)$", body)
                return mm.group(1).strip() if mm else default
            deps = [d.strip() for d in re.split(r"[,\s]+", field("Depends")) if re.match(r"P\d-\d\d", d.strip())]
            tasks.append(dict(id=m.group(1), title=m.group(2).strip(), owner=field("Owner"), deps=deps,
                              size=field("Size"), prio=field("Priority"), status=field("Status", "TODO").upper(),
                              raw="### " + b.rstrip(), file=os.path.basename(path)))
    return tasks


def branches():
    out = sh("git", "branch", "-a", "--format=%(refname:short)")
    return out.splitlines() if out else []


def current_operator():
    email = sh("git", "config", "user.email").lower()
    team = os.path.join(ROOT, "docs", "TEAM.md")
    if not email or not os.path.exists(team):
        return None
    for line in open(team, encoding="utf-8"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and cells[0] in ("A", "B") and cells[2].lower() == email:
            return cells[0]
    return None


def classify(tasks):
    done = {t["id"] for t in tasks if t["status"] == "DONE"}
    brs = branches()
    for t in tasks:
        if t["status"] == "DONE":
            t["state"] = "DONE"
        elif any(t["id"] in b for b in brs):
            t["state"] = "WIP"
        elif all(d in done for d in t["deps"]):
            t["state"] = "READY"
        else:
            t["state"] = "BLOCKED"
            t["waiting"] = [d for d in t["deps"] if d not in done]


def mine(t, op):
    return t["owner"] == op or t["owner"] == "AB"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--me", action="store_true")
    ap.add_argument("--op", choices=["A", "B"])
    ap.add_argument("--next", action="store_true")
    ap.add_argument("--task")
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args()

    tasks = parse_tasks()
    if not tasks:
        print("No tasks found in docs/tasks/"); return 1
    classify(tasks)

    if a.task:
        for t in tasks:
            if t["id"] == a.task.upper():
                print(t["raw"]); print(f"\n[state: {t['state']}]" + (f" waiting for {', '.join(t['waiting'])}" if t.get("waiting") else ""))
                return 0
        print("Task not found"); return 1

    op = a.op
    if a.me:
        op = current_operator()
        if not op:
            print("Cannot identify operator: set `git config user.email` and fill docs/TEAM.md (use --op A|B meanwhile)."); return 2
    sel = [t for t in tasks if (not op or mine(t, op))]
    if a.next:
        sel = [t for t in sel if t["state"] == "READY"]

    # summary per phase
    phases = {}
    for t in tasks:
        p = t["id"][:2]
        phases.setdefault(p, [0, 0])
        phases[p][1] += 1
        phases[p][0] += t["state"] == "DONE"
    total_d = sum(v[0] for v in phases.values()); total = sum(v[1] for v in phases.values())
    print("PROGRESS  " + "  ".join(f"{p}: {d}/{n}" for p, (d, n) in phases.items()) + f"   | total {total_d}/{total} ({100*total_d//total}%)")
    if op:
        print(f"VIEW      operator {op}" + ("  (READY tasks only)" if a.next else ""))
    if a.summary:
        return 0
    print()
    icon = {"DONE": "✔", "WIP": "…", "READY": "▶", "BLOCKED": "✖"}
    cur = None
    for t in sel:
        if t["id"][:2] != cur:
            cur = t["id"][:2]; print(f"== {cur} ==")
        extra = f" (waiting: {', '.join(t['waiting'])})" if t.get("waiting") else ""
        print(f" {icon[t['state']]} {t['id']} [{t['owner']:>2}] {t['size']:<1} {t['prio']:<8} {t['state']:<7} {t['title']}{extra}")
    if not sel:
        print("(nothing to show)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
