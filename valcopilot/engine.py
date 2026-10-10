"""Deterministic valuation maths. No AI here: every number in the report comes from this module."""
from dataclasses import dataclass, field
from statistics import mean, median

from .model import Assumptions, Comp, Inputs, Receivable, Year


class ValuationError(ValueError):
    pass


# ---------- Income approach: DCF (FCFF) ----------

def cost_of_equity(a: Assumptions) -> float:
    return a.risk_free + a.beta * a.erp + a.specific_premium


def wacc(a: Assumptions) -> float:
    return cost_of_equity(a) * (1 - a.debt_weight) + a.cost_of_debt * (1 - a.tax_rate) * a.debt_weight


def fcff(y: Year, tax_rate: float) -> float:
    ebit = y.ebitda - y.da
    return ebit * (1 - tax_rate) + y.da - y.capex - y.nwc_change


@dataclass
class DCFRow:
    label: str
    fcff: float
    period: float
    factor: float
    pv: float


@dataclass
class DCFResult:
    ke: float
    wacc: float
    rows: list[DCFRow]
    terminal_value: float
    pv_terminal: float
    enterprise_value: float
    equity_value: float
    per_share: float  # INR per share


def run_dcf(years: list[Year], a: Assumptions, rate: float | None = None, growth: float | None = None) -> DCFResult:
    """Valuation date is taken as the start of the first projected year. The terminal value
    (Gordon growth on the last year's FCFF) is discounted from the end of the last year."""
    projected = [y for y in years if y.projected]
    if not projected:
        raise ValuationError("The DCF needs at least one projected year.")
    r = wacc(a) if rate is None else rate
    g = a.terminal_growth if growth is None else growth
    if r <= g:
        raise ValuationError(f"WACC ({r:.2%}) must be above terminal growth ({g:.2%}).")
    rows = []
    for t, y in enumerate(projected, start=1):
        period = t - 0.5 if a.mid_year else float(t)
        cf = fcff(y, a.tax_rate)
        factor = 1 / (1 + r) ** period
        rows.append(DCFRow(y.label, cf, period, factor, cf * factor))
    tv = rows[-1].fcff * (1 + g) / (r - g)
    pv_tv = tv / (1 + r) ** len(projected)
    ev = sum(row.pv for row in rows) + pv_tv
    equity = ev - a.debt + a.cash
    return DCFResult(cost_of_equity(a), r, rows, tv, pv_tv, ev, equity, per_share(equity, a.shares))


def per_share(equity_crore: float, shares: float) -> float:
    return equity_crore * 1e7 / shares if shares else 0.0


def sensitivity(years: list[Year], a: Assumptions, rate_step=0.01, growth_step=0.005, n=2):
    """Equity value (INR crore) over a grid of WACC x terminal growth, centred on the base case."""
    base_r, base_g = wacc(a), a.terminal_growth
    rates = [base_r + i * rate_step for i in range(-n, n + 1)]
    growths = [base_g + j * growth_step for j in range(-n, n + 1)]
    grid = [[run_dcf(years, a, r, g).equity_value if r > g else None for g in growths] for r in rates]
    return rates, growths, grid


# ---------- Market approach: trading comps ----------

MULTIPLES = {
    "EV/EBITDA": (lambda c: c.market_cap + c.net_debt, lambda c: c.ebitda),
    "EV/Revenue": (lambda c: c.market_cap + c.net_debt, lambda c: c.revenue),
    "P/E": (lambda c: c.market_cap, lambda c: c.pat),
}


@dataclass
class CompsResult:
    multiple: str
    stat: str
    table: list[tuple[str, dict[str, float | None]]]  # company -> multiple name -> value
    used: list[float]
    excluded: list[str]
    selected: float
    subject_metric: float
    enterprise_value: float | None
    equity_value: float
    per_share: float
    summary: dict[str, dict[str, float]] = field(default_factory=dict)  # multiple -> stat -> value


def multiple_of(c: Comp, name: str) -> float | None:
    num, den = MULTIPLES[name]
    d = den(c)
    return num(c) / d if d > 0 else None   # negative or zero earnings are not meaningful


def run_comps(comps: list[Comp], years: list[Year], a: Assumptions) -> CompsResult:
    if a.comps_multiple not in MULTIPLES:
        raise ValuationError(f"Unknown multiple {a.comps_multiple!r}; use one of {', '.join(MULTIPLES)}.")
    if a.comps_stat not in ("median", "mean"):
        raise ValuationError("comps_stat must be 'median' or 'mean'.")
    actuals = [y for y in years if not y.projected]
    if not actuals:
        raise ValuationError("The market approach needs at least one actual year for the subject's metrics.")
    latest = actuals[-1]
    table = [(c.name, {m: multiple_of(c, m) for m in MULTIPLES}) for c in comps]
    used = [v[a.comps_multiple] for _, v in table if v[a.comps_multiple] is not None]
    excluded = [name for name, v in table if v[a.comps_multiple] is None]
    if not used:
        raise ValuationError(f"No comparable has a meaningful {a.comps_multiple}.")
    summary = {}
    for m in MULTIPLES:
        vals = [v[m] for _, v in table if v[m] is not None]
        if vals:
            summary[m] = {"min": min(vals), "median": median(vals), "mean": mean(vals), "max": max(vals)}
    selected = median(used) if a.comps_stat == "median" else mean(used)
    if a.comps_multiple == "P/E":
        if latest.pat is None or latest.pat <= 0:
            raise ValuationError("P/E needs a positive PAT for the latest actual year.")
        metric, ev = latest.pat, None
        equity = selected * metric
    else:
        metric = latest.ebitda if a.comps_multiple == "EV/EBITDA" else latest.revenue
        if metric <= 0:
            raise ValuationError(f"The subject's {a.comps_multiple.split('/')[1]} must be positive.")
        ev = selected * metric
        equity = ev - a.debt + a.cash
    return CompsResult(a.comps_multiple, a.comps_stat, table, used, excluded, selected, metric, ev,
                       equity, per_share(equity, a.shares), summary)


# ---------- Receivables (IBBI Part I(c)) ----------

@dataclass
class ReceivablesResult:
    gross: float
    fair_value: float
    liquidation_value: float
    by_age: dict[str, tuple[float, float, float]]   # age -> (gross, fv, lv)


def run_receivables(rows: list[Receivable]) -> ReceivablesResult:
    by_age: dict[str, list[float]] = {}
    for r in rows:
        acc = by_age.setdefault(r.age, [0.0, 0.0, 0.0])
        acc[0] += r.amount
        acc[1] += r.amount * r.fv_recovery
        acc[2] += r.amount * r.lv_recovery
    gross = sum(r.amount for r in rows)
    fv = sum(r.amount * r.fv_recovery for r in rows)
    lv = sum(r.amount * r.lv_recovery for r in rows)
    return ReceivablesResult(gross, fv, lv, {k: tuple(v) for k, v in by_age.items()})


# ---------- Conclusion ----------

@dataclass
class AssetValue:
    name: str
    category: str
    premise: str
    book_value: float
    fair_value: float
    liquidation_value: float
    basis: str


@dataclass
class Conclusion:
    dcf: DCFResult | None
    comps: CompsResult | None
    approach_values: list[tuple[str, str, float, float]]  # approach, method, equity value, weight
    weighted_equity: float | None
    dlom: float
    concluded_equity: float | None
    receivables: ReceivablesResult | None
    assets: list[AssetValue]
    fair_value: float
    liquidation_value: float
    book_value: float


def conclude(inp: Inputs) -> Conclusion:
    a = inp.assumptions
    applicable = [ap for ap in inp.approaches if ap.applicable]
    needs_entity_value = any(asset.basis == "Valuation" for asset in inp.assets)
    dcf = comps = None
    approach_values = []
    weighted = concluded = None
    if needs_entity_value:
        if a is None:
            raise ValuationError("An asset uses basis 'Valuation' but the Assumptions sheet is empty.")
        if not applicable:
            raise ValuationError("An asset uses basis 'Valuation' but no approach is marked applicable.")
        total_w = sum(ap.weight for ap in applicable)
        if abs(total_w - 1) > 1e-6:
            raise ValuationError(f"Weights of applicable approaches add up to {total_w:.0%}, not 100%.")
        for ap in applicable:
            if ap.name == "Income":
                dcf = run_dcf(inp.years, a)
                value = dcf.equity_value
            elif ap.name == "Market":
                comps = run_comps(inp.comps, inp.years, a)
                value = comps.equity_value
            elif ap.name == "Cost":
                if a.cost_value is None:
                    raise ValuationError("The cost approach is applicable but cost_value is blank.")
                value = a.cost_value
            else:
                raise ValuationError(f"Unknown approach {ap.name!r}; use Market, Income or Cost.")
            approach_values.append((ap.name, ap.method, value, ap.weight))
        weighted = sum(v * w for _, _, v, w in approach_values)
        concluded = weighted * (1 - a.dlom)
    rec = run_receivables(inp.receivables) if inp.receivables else None
    values = []
    for asset in inp.assets:
        if asset.basis == "Valuation":
            fv = concluded * asset.stake
            lv = fv * asset.lv_recovery
        elif asset.basis == "Receivables":
            if rec is None:
                raise ValuationError(f"{asset.name!r} uses basis 'Receivables' but the Receivables sheet is empty.")
            fv, lv = rec.fair_value, rec.liquidation_value
        elif asset.basis == "Input":
            if asset.fair_value is None:
                raise ValuationError(f"{asset.name!r} uses basis 'Input' but has no fair value.")
            fv = asset.fair_value
            lv = fv * asset.lv_recovery
        else:
            raise ValuationError(f"{asset.name!r}: unknown basis {asset.basis!r}; use Valuation, Receivables or Input.")
        values.append(AssetValue(asset.name, asset.category, asset.premise, asset.book_value, fv, lv, asset.basis))
    return Conclusion(dcf, comps, approach_values, weighted, a.dlom if a else 0.0, concluded, rec, values,
                      sum(v.fair_value for v in values), sum(v.liquidation_value for v in values),
                      sum(v.book_value for v in values))
