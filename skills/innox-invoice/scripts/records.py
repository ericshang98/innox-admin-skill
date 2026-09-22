#!/usr/bin/env python3
"""Private, versioned team/member/case records. Python standard library only."""
import argparse
import json
import os
import re
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


def identifier(value):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", value):
        raise argparse.ArgumentTypeError("Use 1–80 lowercase letters, digits, _ or -.")
    return value


def root_dir():
    return Path(os.environ.get("INNOX_ADMIN_DATA_DIR", "~/.local/share/innox-admin")).expanduser().resolve()


def location(args):
    if not args.team:
        raise ValueError("--team is required for get/put")
    base = root_dir() / "teams" / args.team
    if args.member:
        return base / "members" / (args.member + ".json")
    if args.case:
        return base / "cases" / (args.case + ".json")
    return base / "profile.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


@contextmanager
def locked(path):
    # Exclusion works across processes; a crashed writer may leave a lock for inspection.
    lock = path.with_suffix(".lock")
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("Record locked; inspect the active writer before retrying")
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def put(args):
    data = read(Path(args.input))
    if not isinstance(data, dict):
        raise ValueError("Input must be a complete JSON object")
    path = location(args)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with locked(path):
        old = read(path) if path.exists() else None
        revision = old["revision"] if old else 0
        if revision != args.expected_revision:
            raise ValueError(f"Revision conflict: expected {args.expected_revision}, found {revision}")
        history = old.get("history", []) + [{k: v for k, v in old.items() if k != "history"}] if old else []
        value = {
            "schema_version": 1,
            "kind": "case" if args.case else "member" if args.member else "team",
            "team_id": args.team,
            "id": args.case or args.member or args.team,
            "revision": revision + 1,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "data": data,
            "history": history,
        }
        fd, temp_name = tempfile.mkstemp(prefix=".record-", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(value, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
        return {"path": str(path), "record": read(path)}


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["list", "get", "put"])
    parser.add_argument("--team", type=identifier)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--member", type=identifier)
    selection.add_argument("--case", type=identifier)
    parser.add_argument("--input")
    parser.add_argument("--expected-revision", type=int)
    args = parser.parse_args()
    try:
        if args.action == "list":
            if args.member or args.case:
                raise ValueError("Use get for a specific member or case")
            base = root_dir() / "teams"
            paths = sorted((base / args.team).glob("*/*.json")) if args.team else sorted(base.glob("*/profile.json"))
            result = [{"path": str(p), "id": read(p)["id"], "kind": read(p)["kind"], "revision": read(p)["revision"]} for p in paths]
        elif args.action == "get":
            result = read(location(args))
        else:
            if not args.input or args.expected_revision is None or args.expected_revision < 0:
                raise ValueError("put needs --input and a nonnegative --expected-revision")
            result = put(args)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
