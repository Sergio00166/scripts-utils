#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone
from collections import OrderedDict

def run(cmd, cwd=None, env=None, capture=True):
    if capture:
        return subprocess.check_output(cmd, cwd=cwd, env=env)
    else:
        return subprocess.check_call(cmd, cwd=cwd, env=env)

def git(cmd_args, **kwargs):
    cmd = ["git"] + cmd_args
    return run(cmd, **kwargs)

def ensure_clean_worktree():
    st = git(["status", "--porcelain"], capture=True).decode()
    if st.strip():
        print("Working tree is not clean. Commit or stash changes before running this script.", file=sys.stderr)
        sys.exit(1)

def get_current_branch():
    out = git(["rev-parse", "--abbrev-ref", "HEAD"], capture=True).decode().strip()
    if out == "HEAD":
        # Detached HEAD: still fine; use HEAD as ref
        return "HEAD"
    return out

def read_commits(branch=None, all_refs=False):
    """
    Returns a list of dicts: {hash, ts, msg}
    Uses NUL-separated records to avoid delimiter collisions.
    """
    fmt = "%H%x00%at%x00%B%x00"  # NUL-separated fields; NUL at end for record sep
    args = ["log", "--reverse", f"--format={fmt}"]
    if all_refs:
        args.append("--all")
    else:
        args.append(branch or "HEAD")
    out = git(args, capture=True).decode("utf-8", errors="replace")
    # Split by NUL at record ends: records are sequences of three NUL-separated fields followed by NUL
    parts = out.split("\x00")
    commits = []
    # parts come in triples: hash, ts, msg, then next record continues
    for i in range(0, len(parts) - 1, 3):
        h = parts[i].strip()
        if not h:
            continue
        try:
            ts = int(parts[i + 1].strip() or "0")
        except (ValueError, IndexError):
            ts = 0
        msg = parts[i + 2] if i + 2 < len(parts) else ""
        commits.append({"hash": h, "ts": ts, "msg": msg})
    return commits

def make_week_key(ts, tz_mode="utc"):
    if tz_mode == "local":
        dt = datetime.fromtimestamp(ts)
    else:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    year, week, _weekday = dt.isocalendar()
    return f"{year}-W{week:02d}"

def unique_subjects_in_order(commits):
    seen = set()
    out = []
    for c in commits:
        first_line = c["msg"].splitlines()[0].strip() if c["msg"] else ""
        if first_line and first_line not in seen:
            seen.add(first_line)
            out.append(first_line)
    return out

def create_commit_from_tree(tree_hash, parent_hash, message, author_date_ts):
    env = os.environ.copy()
    # Use unix timestamp with explicit UTC offset
    env["GIT_AUTHOR_DATE"] = f"{author_date_ts} +0000"
    env["GIT_COMMITTER_DATE"] = f"{author_date_ts} +0000"
    cmd = ["git", "commit-tree", tree_hash]
    if parent_hash:
        cmd += ["-p", parent_hash]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
    out, _ = proc.communicate(input=message.encode("utf-8"))
    if proc.returncode != 0:
        raise RuntimeError("git commit-tree failed")
    return out.decode().strip()

def main():
    parser = argparse.ArgumentParser(description="Merge commits by ISO week into a new branch.")
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument("--branch", "-b", default=None, help="Source branch (default: current HEAD)")
    grp.add_argument("--all", action="store_true", help="Use all refs (all reachable commits)")
    parser.add_argument("--out", "-o", default="weekly-merged", help="Output branch name")
    parser.add_argument("--tz", choices=["utc", "local"], default="utc", help="Timezone for week grouping")
    args = parser.parse_args()

    # Ensure in a git repo
    try:
        git(["rev-parse", "--git-dir"], capture=True)
    except subprocess.CalledProcessError:
        print("Not a git repository.", file=sys.stderr)
        sys.exit(1)

    ensure_clean_worktree()

    src_ref = args.branch or get_current_branch()
    out_branch = args.out

    commits = read_commits(branch=src_ref, all_refs=args.all)
    if not commits:
        print("No commits found in the selected scope.", file=sys.stderr)
        sys.exit(1)

    # Group commits by week
    weeks = OrderedDict()
    for c in commits:
        key = make_week_key(c["ts"], tz_mode=args.tz)
        weeks.setdefault(key, []).append(c)

    print(f"Grouping by {args.tz.upper()} timezone. Found {len(weeks)} week groups.")

    new_head = None
    for week_key, group in weeks.items():
        last = group[-1]
        tree = git(["rev-parse", f"{last['hash']}^{{tree}}"], capture=True).decode().strip()
        subjects = unique_subjects_in_order(group)
        body = "\n".join(f"- {s}" for s in subjects) if subjects else "- (no subject)"
        message = f"{week_key}\n\n{body}\n"
        new_commit = create_commit_from_tree(tree, new_head, message, last["ts"])
        print(f"Created {new_commit} for {week_key} ({len(group)} commits)")
        new_head = new_commit

    if not new_head:
        print("No weekly commits created.", file=sys.stderr)
        sys.exit(1)

    # Create or update output branch
    git(["branch", "-f", out_branch, new_head], capture=True)
    print(f"New branch '{out_branch}' created at {new_head}")
    print("Done. Original refs left untouched. Inspect the new branch before any ref updates.")

if __name__ == "__main__": main()
