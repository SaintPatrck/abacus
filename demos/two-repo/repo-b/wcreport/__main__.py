"""wc-report: report statistics about text files."""
import argparse
import sys

from vendor.textkit.core import slugify


def main(argv=None):
    p = argparse.ArgumentParser(prog="wcreport")
    p.add_argument("path")
    p.add_argument("--slug", action="store_true", help="print a slug of the first line")
    a = p.parse_args(argv)
    text = open(a.path).read()
    if a.slug:
        print(slugify(text.splitlines()[0] if text else ""))
    else:
        print(f"{len(text.splitlines())} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
