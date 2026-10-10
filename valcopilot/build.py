"""Workbook in, report out: read, check, value, optionally draft, write."""
from dataclasses import dataclass, field
from pathlib import Path

from . import ibbi
from .checklist import Issue, check
from .draft import Draft, draft_section
from .engine import Conclusion, ValuationError, conclude
from .model import Inputs
from .report import facts_for, write_report
from .workbook import read_workbook


@dataclass
class BuildResult:
    inputs: Inputs
    issues: list[Issue]
    conclusion: Conclusion | None = None
    drafts: dict[str, Draft] = field(default_factory=dict)
    report: Path | None = None

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "error"]


def evaluate(xlsx: Path, will_draft: bool = False) -> BuildResult:
    inp = read_workbook(xlsx)
    result = BuildResult(inp, check(inp, will_draft))
    try:
        result.conclusion = conclude(inp)
    except ValuationError as e:
        result.issues.append(Issue("error", "Valuation", str(e)))
    return result


def build(xlsx: Path, out: Path, draft: bool = False, strict: bool = False, client=None) -> BuildResult:
    result = evaluate(xlsx, will_draft=draft)
    if result.conclusion is None or (strict and result.errors):
        return result
    inp, c = result.inputs, result.conclusion
    if draft:
        for key in ibbi.DRAFTABLE:
            if inp.get(key):
                continue
            d = draft_section(key, facts_for(key, inp, c), client=client)
            result.drafts[key] = d
            inp.fields[key] = d.text
            if not d.ok:
                result.issues.append(Issue("error", f"AI draft of {key}",
                                           f"contains figures not in the inputs: {', '.join(d.unknown_numbers)}."))
    sample = "[SAMPLE]" in inp.get("client") or inp.get("vrin").startswith("SAMPLE")
    result.report = write_report(out, inp, c, result.drafts, open_issues=len(result.errors), sample=sample)
    return result
