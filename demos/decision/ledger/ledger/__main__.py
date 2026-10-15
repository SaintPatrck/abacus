"""ledger: a tiny expense ledger (Abacus decision demo)."""
import argparse
import json
import os
import sys


def path():
    return os.environ.get("LEDGER_FILE", "ledger.json")


def load():
    try:
        with open(path()) as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save(entries):
    with open(path(), "w") as f:
        json.dump(entries, f, indent=2)


def main(argv=None):
    p = argparse.ArgumentParser(prog="ledger")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add", help="record an expense")
    a.add_argument("amount", type=float)
    a.add_argument("description")
    sub.add_parser("list", help="show all expenses")
    args = p.parse_args(argv)
    entries = load()
    if args.cmd == "add":
        entries.append({"amount": args.amount, "description": args.description})
        save(entries)
    else:
        for e in entries:
            print(f"{e['amount']:>9.2f}  {e['description']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
