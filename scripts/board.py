#!/usr/bin/env python3
"""Task board for the two operators — phase-branch aware (v2).

Usage:
  python scripts/board.py                 # everything
  python scripts/board.py --me            # tasks of the current git user (matched via docs/TEAM.md)
  python scripts/board.py --op A          # tasks of operator A (AB tasks included)
  python scripts/board.py --next [--me]   # startable now: READY only
  python scripts/board.py --task P3-01    # one task block + state
  python scripts/board.py --base P3-01    # prints the base branch of a task (main | phase/N)
  python scripts/board.py --summary       # progress per phase only

How statuses are read (so that parallel phase branches work):
  * A task is DONE when `Status: DONE` in docs/tasks/phase-K.md ON THE BRANCH OF ITS OWN PHASE
    (origin/phase/K for K>=2, origin/main for K<2). Falls back to local branches / working tree.
  * Dependencies are checked against the task's BASE branch (what its branch would be cut from):
      READY     all deps DONE in the base branch  -> /task-start
      UPSTREAM  deps DONE elsewhere (earlier phase branch) but not yet in the base branch -> /propagate first
      BLOCKED   some dep is not DONE anywhere yet
      WIP       a task branch containing the id exists (local or remote)
      DONE
"""
import argparse, glob, os, re, subprocess, sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REL = "docs/tasks/phase-{}.md"
_cache_show = {}


def run(*cmd):
    try:
        return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=30)
    except Exception:
        return None


def sh(*cmd):
    r = run(*cmd)
    return r.stdout.strip() if r and r.returncode == 0 else ""


def ref_ok(ref):
    r = run("git", "rev-parse", "--verify", "-q", ref)
    return bool(r and r.returncode == 0)


def pick_ref(*cands):
    for c in cands:
        if ref_ok(c):
            return c
    return None


def base_branch(task_id):
    n = int(task_id[1])
    return "main" if n < 2 else f"phase/{n}"


def base_ref(task_id):
    b = base_branch(task_id)
    return pick_ref(f"origin/{b}", b)


def phase_ids():
    ids = set()
    for p in glob.glob(os.path.join(ROOT, "docs", "tasks", "phase-*.md")):
        m = re.search(r"phase-(\d)\.md$", p)
        if m:
            ids.add(int(m.group(1)))
    return sorted(ids)


def read_phase_file(k, ref):
    """text of docs/tasks/phase-k.md at ref (None -> working tree)."""
    key = (k, ref)
    if key in _cache_show:
        return _cache_show[key]
    text = None
    if ref:
        r = run("git", "show", f"{ref}:{REL.format(k)}")
        if r and r.returncode == 0:
            text = r.stdout
    if text is None:
        p = os.path.join(ROOT, REL.format(k))
        text = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    _cache_show[key] = text
    return text


def parse(text):
    tasks = []
    for b in re.split(r"(?m)^### ", text)[1:]:
        head, *rest = b.split("\n", 1)
        m = re.match(r"(P\d-\d\d) · (.+)", head.strip())
        if not m:
            continue
        body = re.split(r"(?m)^## ", rest[0] if rest else "")[0]

        def field(name, default=""):
            mm = re.search(rf"(?m)^- {name}:\s*(.+)$", body)
            return mm.group(1).strip() if mm else default

        deps = [d for d in re.split(r"[,\s]+", field("Depends")) if re.match(r"P\d-\d\d$", d)]
        tasks.append(dict(id=m.group(1), title=m.group(2).strip(), owner=field("Owner"), deps=deps,
                          size=field("Size"), prio=field("Priority"), status=field("Status", "TODO").upper(),
                          raw="### " + b.rstrip()))
    return tasks


def own_phase_ref(k):
    if k >= 2:
        return pick_ref(f"origin/phase/{k}", f"phase/{k}")
    return pick_ref("origin/main", "main")


def done_ids_at(ref, ks):
    out = set()
    for k in ks:
        out |= {t["id"] for t in parse(read_phase_file(k, ref)) if t["status"] == "DONE"}
    return out


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


def load():
    ks = phase_ids()
    tasks = []
    for k in ks:
        for t in parse(read_phase_file(k, own_phase_ref(k))):
            t["phase"] = k
            tasks.append(t)
    done_global = {t["id"] for t in tasks if t["status"] == "DONE"}
    brs = branches()
    base_done_cache = {}
    for t in tasks:
        t["base"] = base_branch(t["id"])
        if t["status"] == "DONE":
            t["state"] = "DONE"; continue
        if any(re.search(rf"(^|/){t['id']}-", b) for b in brs):
            t["state"] = "WIP"; continue
        missing_global = [d for d in t["deps"] if d not in done_global]
        if missing_global:
            t["state"] = "BLOCKED"; t["waiting"] = missing_global; continue
        ref = base_ref(t["id"])
        if ref not in base_done_cache:
            base_done_cache[ref] = done_ids_at(ref, ks)
        missing_local = [d for d in t["deps"] if d not in base_done_cache[ref]]
        if missing_local:
            t["state"] = "UPSTREAM"; t["waiting"] = missing_local
        else:
            t["state"] = "READY"
    return tasks


def mine(t, op):
    return t["owner"] == op or t["owner"] == "AB"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--me", action="store_true")
    ap.add_argument("--op", choices=["A", "B"])
    ap.add_argument("--next", action="store_true")
    ap.add_argument("--task")
    ap.add_argument("--base")
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args()

    if a.base:
        if not re.match(r"P\d-\d\d$", a.base.upper()):
            print("usage: --base P3-01"); return 1
        print(base_branch(a.base.upper())); return 0

    tasks = load()
    if not tasks:
        print("No tasks found in docs/tasks/"); return 1

    if a.task:
        for t in tasks:
            if t["id"] == a.task.upper():
                print(t["raw"])
                extra = f" waiting for {', '.join(t['waiting'])}" if t.get("waiting") else ""
                print(f"\n[state: {t['state']}] [base branch: {t['base']}]{extra}")
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

    phases = {}
    for t in tasks:
        p = t["id"][:2]
        phases.setdefault(p, [0, 0]); phases[p][1] += 1; phases[p][0] += t["state"] == "DONE"
    td = sum(v[0] for v in phases.values()); tt = sum(v[1] for v in phases.values())
    print("PROGRESS  " + "  ".join(f"{p}: {d}/{n}" for p, (d, n) in phases.items()) + f"   | total {td}/{tt} ({100*td//tt}%)")
    if op:
        print(f"VIEW      operator {op}" + ("  (READY only)" if a.next else ""))
    if a.summary:
        return 0
    print()
    icon = {"DONE": "✔", "WIP": "…", "READY": "▶", "UPSTREAM": "↧", "BLOCKED": "✖"}
    cur = None
    for t in sel:
        if t["id"][:2] != cur:
            cur = t["id"][:2]; print(f"== {cur}  (base: {t['base']}) ==")
        extra = ""
        if t["state"] == "UPSTREAM":
            extra = f"  (run /propagate: {', '.join(t['waiting'])} not yet in {t['base']})"
        elif t.get("waiting"):
            extra = f"  (waiting: {', '.join(t['waiting'])})"
        print(f" {icon[t['state']]} {t['id']} [{t['owner']:>2}] {t['size']:<1} {t['prio']:<8} {t['state']:<8} {t['title']}{extra}")
    if not sel:
        print("(nothing to show)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
