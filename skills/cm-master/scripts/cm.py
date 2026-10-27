#!/usr/bin/env python3
"""Portable JSON CLI for CM Master. All network actions belong to the AI host."""
import argparse
import json
import os
from pathlib import Path
import sys

from cm_state import StateError, Store, read_json


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(os.environ.get("CM_MASTER_HOME", "~/.cm-master")).expanduser())
    sub = p.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init-brand")
    init.add_argument("brand")
    init.add_argument("--name", required=True)
    init.add_argument("--website", default="")
    sub.add_parser("list-brands")
    profile = sub.add_parser("profile")
    profile.add_argument("brand")
    profile.add_argument("--file", type=Path)
    for command in ("draft", "stage", "review", "approve", "revoke", "check", "begin", "record", "resolve", "cancel-scheduled"):
        command_parser = sub.add_parser(command)
        command_parser.add_argument("brand")
        command_parser.add_argument("post")
        if command in {"draft", "stage"}:
            command_parser.add_argument("--file", type=Path, required=True)
        elif command == "approve":
            command_parser.add_argument("--review-sha", required=True)
            command_parser.add_argument("--evidence", required=True)
            command_parser.add_argument("--by", required=True)
        elif command == "revoke":
            command_parser.add_argument("--reason", required=True)
        elif command in {"check", "begin"}:
            command_parser.add_argument("--mode", choices=("publish", "schedule"), default="publish")
        elif command == "record":
            command_parser.add_argument("--status", choices=("published", "scheduled", "uncertain", "blocked"), required=True)
            command_parser.add_argument("--evidence", required=True)
            command_parser.add_argument("--url")
            command_parser.add_argument("--reconciled", action="store_true")
        elif command == "resolve":
            command_parser.add_argument("--outcome", choices=("not-published",), required=True)
            command_parser.add_argument("--evidence", required=True)
        elif command == "cancel-scheduled":
            command_parser.add_argument("--evidence", required=True)
    due = sub.add_parser("due")
    due.add_argument("--brand")
    return p


def dispatch(store, args):
    c = args.command
    if c == "init-brand":
        return store.init_brand(args.brand, args.name, args.website)
    if c == "list-brands":
        return store.list_brands()
    if c == "profile":
        return store.save_profile(args.brand, read_json(args.file)) if args.file else store.profile(args.brand)
    if c == "due":
        return store.due(args.brand)
    if c == "stage":
        return store.stage(args.brand, args.post, read_json(args.file))
    if c == "draft":
        return store.draft(args.brand, args.post, read_json(args.file))
    if c == "review":
        return store.review(args.brand, args.post)
    if c == "approve":
        return store.approve(args.brand, args.post, args.review_sha, args.evidence, args.by)
    if c == "revoke":
        return store.revoke(args.brand, args.post, args.reason)
    if c == "check":
        return store.check(args.brand, args.post, args.mode)
    if c == "begin":
        return store.begin(args.brand, args.post, args.mode)
    if c == "record":
        return store.record(args.brand, args.post, args.status, args.evidence, args.url, args.reconciled)
    if c == "cancel-scheduled":
        return store.cancel_scheduled(args.brand, args.post, args.evidence)
    return store.resolve(args.brand, args.post, args.outcome, args.evidence)


def main():
    args = parser().parse_args()
    try:
        store = Store(args.root)
        with store.transaction():
            result = dispatch(store, args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (StateError, OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
