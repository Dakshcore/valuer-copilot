"""Optional AI drafting of narrative sections that the valuer left blank.

The model only writes prose from facts we pass in. A number guard then checks every figure in
the draft against those facts; a draft with an unknown figure is flagged in the report and the
checklist. Drafts are always marked for the valuer to review before signing.
"""
import json
import os
import re
from dataclasses import dataclass, field

from . import ibbi

DEFAULT_MODEL = "claude-haiku-4-5"   # cheapest current model; set VALCOPILOT_MODEL to override
MAX_TOKENS = 1200

SYSTEM = (
    "You draft one section of a valuation report prepared by an Indian registered valuer under the "
    "Insolvency and Bankruptcy Code, 2016. The valuer will review and sign the report.\n"
    "Rules:\n"
    "- Use only the facts provided. Do not add names, dates, figures, percentages, laws or standards "
    "that are not in the facts or the guidance.\n"
    "- Copy figures exactly as written in the facts. Do not compute new figures.\n"
    "- Each figure in the facts is labelled. Use a figure only for the item its label names. Keep 100% of a "
    "company's equity apart from a partial stake in it, and the company whose shares are valued apart from "
    "the corporate debtor.\n"
    "- State counts exactly as the facts give them.\n"
    "- Do not state opinions, findings or judgments (for example, that projections are reasonable) unless the "
    "facts state them.\n"
    "- If a point the guidance asks for is not covered by the facts, write [VALUER TO CONFIRM: <what is needed>].\n"
    "- Formal, plain English. Short paragraphs. Do not repeat the section title. No headings, no markdown, "
    "no bullet symbols.\n"
    "- Output only the section text."
)

NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


@dataclass
class Draft:
    key: str
    text: str
    unknown_numbers: list[str] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def ok(self) -> bool:
        return not self.unknown_numbers


def norm(n: str) -> str:
    n = n.replace(",", "")
    if "." in n:
        n = n.rstrip("0").rstrip(".")
    return n or "0"


def numbers_in(text: str) -> set[str]:
    return {norm(m) for m in NUMBER.findall(text)}


def unknown_numbers(draft: str, *sources: str) -> list[str]:
    allowed = set().union(*(numbers_in(s) for s in sources))
    return sorted(numbers_in(draft) - allowed, key=lambda s: (len(s), s))


def section_for(key: str) -> ibbi.Section:
    letter = {"background": "h", "approaches_text": "m", "sustainability": "q",
              "value_rationale": "s", "summary": "u"}[key]
    return next(s for s in ibbi.SECTIONS if s.letter == letter)


def _is_title(line: str, title: str) -> bool:
    line = re.sub(r"^(section\s+)?[a-v]\)\s*", "", line.lower()).rstrip(":. ")
    return line == title.lower()


def clean(text: str, title: str) -> str:
    """Remove markdown and a leading copy of the section title, which the model sometimes adds."""
    lines = [re.sub(r"^#+\s*", "", line.replace("**", "")).strip() for line in text.strip().splitlines()]
    while lines and (not lines[0] or _is_title(lines[0], title)):
        lines.pop(0)
    return "\n".join(lines)


def build_prompt(key: str, facts: dict[str, str]) -> tuple[str, str]:
    sec = section_for(key)
    guidance = f"Section {sec.letter}) {sec.title}. Guidance from {ibbi.CIRCULAR}: {sec.guidance}"
    facts_json = json.dumps(facts, indent=2, ensure_ascii=False)
    return f"{guidance}\n\nFacts:\n{facts_json}\n\nDraft the section text.", guidance + facts_json


def make_client():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is not set. Set it in the environment to use --draft, "
                           "or write the section yourself.")
    import anthropic
    return anthropic.Anthropic()


def draft_section(key: str, facts: dict[str, str], client=None, model: str | None = None) -> Draft:
    client = client or make_client()
    prompt, allowed_text = build_prompt(key, facts)
    resp = client.messages.create(
        model=model or os.environ.get("VALCOPILOT_MODEL", DEFAULT_MODEL),
        max_tokens=MAX_TOKENS,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    text = clean("".join(b.text for b in resp.content if getattr(b, "type", "") == "text"), section_for(key).title)
    usage = getattr(resp, "usage", None)
    return Draft(key, text, unknown_numbers(text, allowed_text),
                 getattr(usage, "input_tokens", 0), getattr(usage, "output_tokens", 0))
