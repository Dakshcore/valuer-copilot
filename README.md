# valuer-copilot

Builds IBC valuation reports for **Securities or Financial Assets** in the format prescribed by
[IBBI Circular No. IBBI/RV/103/2026](https://ibbi.gov.in/uploads/legalframwork/9d426e3d5c806a7a8f763103960345ea.pdf)
(15 June 2026, "Guidelines for Conducting Valuation Under the Insolvency and Bankruptcy Code, 2016").

## Highlights

- Turns one Excel workbook into an IBC valuation report in the format prescribed by IBBI Circular
  IBBI/RV/103/2026, covering fair value and liquidation value for securities and financial assets.
- Deterministic valuation engine: FCFF DCF with CAPM/WACC, a WACC x terminal-growth sensitivity grid, trading comps
  (EV/EBITDA, EV/Revenue, P/E), receivables recovery by ageing bucket, weighting of approaches and a marketability
  discount, tested against hand-worked figures (52 unit tests).
- LLM drafting of narrative sections at about $0.02 per report. Code computes every figure, and an automated check
  rejects any number in the AI text that the engine did not produce. Live testing showed the model attaching correct
  figures to the wrong items; every input is now labelled with what it measures.

## How it works

The valuer fills in one Excel workbook. The tool:

1. **Values the assets** with deterministic code: a DCF (FCFF, CAPM cost of equity, WACC, Gordon terminal value),
   trading comps (EV/EBITDA, EV/Revenue or P/E), weighting of approaches, a discount for lack of marketability,
   receivables by ageing bucket (IBBI Part I(c)), and fair value and liquidation value per asset.
2. **Checks the input against the format**: every executive-summary field and section a) to v), dates,
   registration number and CoP status, "N/A" without a reason (Note 2 of the format), all three approaches discussed,
   weights adding to 100%, replacement cost where the cost approach is used, foreign-currency disclosures,
   remarks on disputed or related-party receivables, and the annexure list.
3. **Writes a Word report** with the executive summary table, sections a) to v) in the circular's order,
   the VRIN on the left of every page footer, and annexures for the comps and computation sheets
   (cost of capital, DCF, WACC x growth sensitivity, receivables).
4. **Optionally drafts prose** (`--draft`) for five narrative sections the valuer left blank, using Claude.
   The model gets only the computed facts. A number guard flags any figure in a draft that is not in those
   facts, and every drafted paragraph is marked for review before signing.

## Quick start

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m valcopilot sample samples/sample_input.xlsx
.venv/Scripts/python -m valcopilot check samples/sample_input.xlsx
.venv/Scripts/python -m valcopilot build samples/sample_input.xlsx -o samples/sample_report.docx
```

Start a real engagement from a blank workbook with `python -m valcopilot template my_case.xlsx`.
`build --strict` refuses to write a report while the checklist has errors; without it, the report is written
with `[MISSING]` markers and a "working draft" banner.

## The sample

`samples/` holds a fully fictional case (every name, number and date is made up) and the report built from it.
Current output of `check` on the sample:

```
0 error(s), 0 warning(s).
Fair value: INR 57.14 crore | Liquidation value: INR 35.41 crore | Book value: INR 57.95 crore
```

## AI drafting and cost

- Off by default. `--draft` needs `ANTHROPIC_API_KEY` in the environment.
- Default model `claude-haiku-4-5` (set `VALCOPILOT_MODEL` to change it). At most five calls per report,
  capped at 1,200 output tokens each. The CLI prints the actual token counts after each run. A live run on the
  sample used 5,012 input and 2,835 output tokens, about $0.02 at Haiku 4.5 list prices ($1 and $5 per million).
- No figure in the report comes from the model: tables and values are written by code.

## Tests

```bash
.venv/Scripts/python -m pytest -q
```

52 tests. Engine figures are checked against hand-worked values, and the sample's fair and liquidation values
are recomputed independently of the engine. The AI drafter is tested with a fake client, so the tests make no API calls.

## Limits of this version

- IBC, Securities or Financial Assets only. Land & Building, Plant & Machinery and the Coordinating Valuer report
  (Part III) are not built yet.
- One valued entity per workbook (for example one subsidiary's shares). Other assets take an input fair value.
- The valuation date is taken as the start of the first projected year (no stub period).
- The tool drafts; the registered valuer remains responsible for the report and signs it. Caveats must follow
  the IBBI (Use of Caveats, Limitations, and Disclaimers in Valuation Reports) Guidelines, 2020, which the
  valuer inserts.
