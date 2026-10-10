"""Command line: python -m valcopilot {template,sample,check,build} ..."""
import argparse
import sys
from pathlib import Path

from .build import build, evaluate
from .report import cr
from .workbook import InputError, write_workbook


def _print_result(result) -> None:
    for issue in result.issues:
        print(issue)
    errors, warnings = len(result.errors), len(result.issues) - len(result.errors)
    print(f"\n{errors} error(s), {warnings} warning(s).")
    c = result.conclusion
    if c:
        print(f"Fair value: INR {cr(c.fair_value)} crore | Liquidation value: INR {cr(c.liquidation_value)} crore"
              f" | Book value: INR {cr(c.book_value)} crore")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="valcopilot", description="IBC valuation report builder (Securities or Financial Assets)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("template", help="write a blank input workbook").add_argument("out", type=Path)
    sub.add_parser("sample", help="write a filled, fictional sample workbook").add_argument("out", type=Path)
    sub.add_parser("check", help="check a workbook against the IBBI format").add_argument("xlsx", type=Path)
    b = sub.add_parser("build", help="build the Word report")
    b.add_argument("xlsx", type=Path)
    b.add_argument("-o", "--out", type=Path, required=True)
    b.add_argument("--draft", action="store_true", help="draft blank narrative sections with Claude (needs ANTHROPIC_API_KEY)")
    b.add_argument("--strict", action="store_true", help="do not build if the checklist has errors")
    args = p.parse_args(argv)

    try:
        if args.cmd in ("template", "sample"):
            print(f"Wrote {write_workbook(args.out, sample=args.cmd == 'sample')}")
            return 0
        if args.cmd == "check":
            result = evaluate(args.xlsx)
            _print_result(result)
            return 1 if result.errors else 0
        result = build(args.xlsx, args.out, draft=args.draft, strict=args.strict)
    except (InputError, RuntimeError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    _print_result(result)
    if result.drafts:
        tin = sum(d.input_tokens for d in result.drafts.values())
        tout = sum(d.output_tokens for d in result.drafts.values())
        print(f"AI drafted {len(result.drafts)} section(s): {tin} input tokens, {tout} output tokens.")
    if result.report:
        print(f"Report written to {result.report}")
        return 0
    print("Report not written." + (" Fix the errors above or drop --strict." if args.strict else ""))
    return 1


if __name__ == "__main__":
    sys.exit(main())
