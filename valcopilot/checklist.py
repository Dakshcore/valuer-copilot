"""Check an input against the IBBI SFA format before a report is built.

"error" means the report would not meet the format (or the numbers cannot be computed).
"warning" means something the valuer should look at, but which may be fine.
"""
import re
from dataclasses import dataclass
from datetime import datetime

from . import ibbi
from .model import Inputs

DRAFT_HINT = "write it, or run build with --draft to have it drafted for review"


@dataclass
class Issue:
    level: str     # "error" or "warning"
    where: str     # report section or sheet
    message: str

    def __str__(self) -> str:
        return f"[{self.level.upper()}] {self.where}: {self.message}"


def parse_date(text: str) -> datetime | None:
    try:
        return datetime.strptime(text.strip(), "%d/%m/%Y")
    except ValueError:
        return None


def bare_na(text: str) -> bool:
    """'N/A' with no reason. Note 2 of the format: a parameter that is not applicable needs a justification."""
    return bool(re.fullmatch(r"(n/?a|not applicable|nil|-)\s*[.:\-]?\s*", text.strip(), re.I))


def check(inp: Inputs, will_draft: bool = False) -> list[Issue]:
    issues: list[Issue] = []
    err = lambda where, msg: issues.append(Issue("error", where, msg))      # noqa: E731
    warn = lambda where, msg: issues.append(Issue("warning", where, msg))   # noqa: E731

    for f in ibbi.EXEC_SUMMARY + ibbi.BODY_FIELDS + ibbi.ANNEXURES:
        value = inp.get(f.key)
        if not f.required:
            continue
        if not value:
            if f.key in ibbi.DRAFTABLE:
                if not will_draft:
                    err(f.label, f"blank; {DRAFT_HINT}.")
            else:
                err(f.label, "required by the IBBI format but blank.")
        elif bare_na(value):
            err(f.label, "says N/A without a reason. The format requires a justification, e.g. 'N/A: <reason>'.")

    for key in ibbi.DATE_FIELDS:
        value = inp.get(key)
        if value and parse_date(value) is None:
            err(key, f"{value!r} is not a dd/mm/yyyy date.")
    dates = {k: parse_date(inp.get(k)) for k in ibbi.DATE_FIELDS}
    if dates["report_date"] and dates["valuation_date"] and dates["report_date"] < dates["valuation_date"]:
        err("Report Date", "is before the valuation date.")
    if dates["appointment_date"] and dates["report_date"] and dates["report_date"] < dates["appointment_date"]:
        err("Report Date", "is before the date of appointment.")
    if dates["icd"] and dates["valuation_date"] and dates["icd"] != dates["valuation_date"]:
        warn("Valuation Date", "differs from the insolvency commencement date. Check the applicable regulation "
                               "and state the reason in the report.")

    reg = inp.get("registration_no")
    if reg and not reg.upper().startswith("IBBI/RV"):
        err("Registration Number", f"{reg!r} does not look like an IBBI registration number (IBBI/RV/...).")
    cop = inp.get("cop_status").lower()
    if cop and cop not in ("active", "inactive"):
        err("Status of CoP", "must be 'active' or 'inactive'.")
    elif cop == "inactive":
        err("Status of CoP", "is inactive on the appointment date.")

    currency = inp.get("currency").upper()
    if currency and currency != "INR":
        for key in ("fx_rate", "fx_date", "fx_source"):
            if not inp.get(key):
                err("i) Valuation Currency", f"{key} is required when the currency is not INR.")

    _check_numbers(inp, err, warn)
    return issues


def _check_numbers(inp: Inputs, err, warn) -> None:
    if not inp.assets:
        err("Assets sheet", "no assets listed. Section g needs the assets being valued.")
    names = {ap.name for ap in inp.approaches}
    for ap in ("Market", "Income", "Cost"):
        if ap not in names:
            err("m) Approaches", f"{ap} approach missing. The format needs each approach discussed, applicable or not.")
    for ap in inp.approaches:
        if not ap.reason:
            err("m) Approaches", f"{ap.name}: reason for applying or not applying is blank.")
        if ap.applicable and not ap.method:
            err("m) Approaches", f"{ap.name}: method adopted is blank.")
    applicable = [ap for ap in inp.approaches if ap.applicable]
    uses_valuation = any(a.basis == "Valuation" for a in inp.assets)
    if uses_valuation and applicable and abs(sum(ap.weight for ap in applicable) - 1) > 1e-6:
        err("Approaches sheet", f"weights of applicable approaches add up to "
                                f"{sum(ap.weight for ap in applicable):.0%}, not 100%.")
    if any(ap.name == "Cost" and ap.applicable for ap in inp.approaches) and not inp.get("replacement_cost"):
        err("s) Value and Rationale", "the cost approach is adopted, so the replacement cost must be disclosed.")

    a = inp.assumptions
    if uses_valuation and a is None:
        err("Assumptions sheet", "blank, but an asset uses basis 'Valuation'.")
    if a is not None:
        if a.terminal_growth >= 0.08:
            warn("Assumptions", f"terminal growth of {a.terminal_growth:.1%} is high for a perpetuity.")
        if not 0 <= a.dlom < 1:
            err("Assumptions", "the discount for lack of marketability must be between 0% and 100%.")
        if a.shares <= 0:
            err("Assumptions", "number of equity shares must be positive.")
    discounting = (a is not None and a.dlom > 0) or any(x.lv_recovery < 1 for x in inp.assets if x.basis != "Receivables")
    if discounting and not inp.get("discounts_rationale"):
        err("n) Discounts and premiums", "discounts are applied, so the rationale for each is required.")

    for x in inp.assets:
        if x.basis == "Valuation" and not 0 < x.stake <= 1:
            err("Assets sheet", f"{x.name}: stake must be between 0% and 100%.")
        if x.basis != "Receivables" and not 0 <= x.lv_recovery <= 1:
            err("Assets sheet", f"{x.name}: liquidation value % must be between 0% and 100%.")
        if not x.premise:
            err("k) Premise of value", f"{x.name}: premise of value is blank.")
    if any(x.basis == "Receivables" for x in inp.assets) and not inp.receivables:
        err("Receivables sheet", "an asset uses basis 'Receivables' but no receivables are listed.")
    for r in inp.receivables:
        if not (0 <= r.lv_recovery <= r.fv_recovery <= 1):
            err("Receivables sheet", f"{r.debtor}: recoveries must satisfy 0 <= LV % <= FV % <= 100%.")
        if (r.disputed or r.related_party) and not r.remarks:
            err("Receivables sheet", f"{r.debtor}: disputed or related-party receivables need remarks on "
                                     "enforceability and recovery (IBBI Part I(c)).")
        if not r.age:
            err("Receivables sheet", f"{r.debtor}: age bucket is blank (IBBI Part I(c)(iii)).")
