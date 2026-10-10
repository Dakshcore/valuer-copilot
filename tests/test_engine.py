"""Engine figures checked against values worked out by hand."""
import pytest

from valcopilot.engine import (ValuationError, conclude, cost_of_equity, fcff, run_comps, run_dcf,
                               run_receivables, sensitivity, wacc)
from valcopilot.model import Assumptions, Comp, Year


def flat_assumptions(**kw):
    """WACC of exactly 10%: all-equity, cost of equity = risk-free = 10%."""
    base = dict(risk_free=0.10, beta=0.0, erp=0.0, specific_premium=0.0, cost_of_debt=0.0, tax_rate=0.0,
                debt_weight=0.0, terminal_growth=0.02, mid_year=False, debt=100.0, cash=50.0, shares=1e7)
    base.update(kw)
    return Assumptions(**base)


def two_years():
    return [Year("FY26", False, 500, 90), Year("FY27", True, 600, 100), Year("FY28", True, 650, 110)]


def test_sample_cost_of_capital(sample_inputs):
    a = sample_inputs.assumptions
    # ke = 6.8% + 1.1 x 7% + 3% = 17.5%; WACC = 17.5% x 75% + 10.5% x (1 - 25.17%) x 25%
    assert cost_of_equity(a) == pytest.approx(0.175)
    assert wacc(a) == pytest.approx(0.175 * 0.75 + 0.105 * (1 - 0.2517) * 0.25)


def test_fcff():
    # EBIT 10.3 taxed at 25% = 7.725; + D&A 3.6 - capex 4.6 - NWC 0.8 = 5.925
    assert fcff(Year("FY27", True, 99, 13.9, 3.6, 4.6, 0.8), 0.25) == pytest.approx(5.925)


def test_dcf_end_year_by_hand():
    d = run_dcf(two_years(), flat_assumptions())
    assert [r.pv for r in d.rows] == pytest.approx([100 / 1.1, 110 / 1.21])
    assert d.terminal_value == pytest.approx(110 * 1.02 / 0.08)          # 1,402.50
    assert d.pv_terminal == pytest.approx(1402.5 / 1.21)
    ev = 100 / 1.1 + 110 / 1.21 + 1402.5 / 1.21
    assert d.enterprise_value == pytest.approx(ev)
    assert d.equity_value == pytest.approx(ev - 100 + 50)
    assert d.per_share == pytest.approx((ev - 50) * 1e7 / 1e7)   # 1 crore shares: INR per share = crore figure


def test_dcf_mid_year_discounts_half_a_year_earlier():
    d = run_dcf(two_years(), flat_assumptions(mid_year=True))
    assert [r.period for r in d.rows] == [0.5, 1.5]
    assert d.rows[0].pv == pytest.approx(100 / 1.1 ** 0.5)
    assert d.pv_terminal == pytest.approx(1402.5 / 1.21)   # terminal value still from the end of year 2


def test_dcf_rejects_growth_at_or_above_wacc():
    with pytest.raises(ValuationError, match="must be above terminal growth"):
        run_dcf(two_years(), flat_assumptions(terminal_growth=0.10))


def test_dcf_needs_projections():
    with pytest.raises(ValuationError, match="projected year"):
        run_dcf([Year("FY26", False, 1, 1)], flat_assumptions())


def test_sensitivity_centre_is_the_base_case(sample_inputs):
    rates, growths, grid = sensitivity(sample_inputs.years, sample_inputs.assumptions)
    assert len(rates) == len(growths) == 5
    assert grid[2][2] == pytest.approx(run_dcf(sample_inputs.years, sample_inputs.assumptions).equity_value)
    assert grid[0][4] > grid[2][2] > grid[4][0]   # lower WACC and higher growth give more value


def test_sample_comps_by_hand(sample_inputs):
    c = run_comps(sample_inputs.comps, sample_inputs.years, sample_inputs.assumptions)
    # EV/EBITDA: 560/62, 335/36, 1000/98, 160/18; peer 5 has negative EBITDA and is excluded
    assert c.excluded == ["Illustrative Peer 5"]
    selected = (560 / 62 + 335 / 36) / 2           # median of four
    assert c.selected == pytest.approx(selected)
    assert c.enterprise_value == pytest.approx(selected * 13.0)   # FY26 EBITDA
    assert c.equity_value == pytest.approx(selected * 13.0 - 18.0 + 2.5)


def test_pe_multiple_values_equity_directly():
    years = [Year("FY26", False, 100, 20, pat=10)]
    comps = [Comp("A", 200, 50, 100, 20, 20), Comp("B", 300, 0, 100, 20, 20)]   # P/E 10 and 15
    c = run_comps(comps, years, flat_assumptions(comps_multiple="P/E", comps_stat="mean"))
    assert c.selected == pytest.approx(12.5)
    assert c.enterprise_value is None
    assert c.equity_value == pytest.approx(125)


def test_comps_with_no_usable_peer_is_an_error():
    years = [Year("FY26", False, 100, 20)]
    with pytest.raises(ValuationError, match="No comparable"):
        run_comps([Comp("A", 100, 0, 50, -5, -1)], years, flat_assumptions())


def test_sample_receivables_by_hand(sample_inputs):
    r = run_receivables(sample_inputs.receivables)
    assert r.gross == pytest.approx(9.6)
    assert r.fair_value == pytest.approx(3.2 * .95 + 2.1 * .95 + 1.6 * .85 + 1.2 * .6 + 0.9 * .2 + 0.6 * .3)   # 7.475
    assert r.liquidation_value == pytest.approx(3.2 * .8 + 2.1 * .8 + 1.6 * .6 + 1.2 * .35 + 0.9 * .05 + 0.6 * .1)
    assert r.by_age[">12 months"][0] == pytest.approx(1.5)


def test_sample_conclusion_recomputed_independently(sample_inputs):
    a, years = sample_inputs.assumptions, sample_inputs.years
    # independent DCF: plain loop, no engine helpers
    r = 0.175 * 0.75 + 0.105 * (1 - 0.2517) * 0.25
    proj = [y for y in years if y.projected]
    cfs = [(y.ebitda - y.da) * (1 - 0.2517) + y.da - y.capex - y.nwc_change for y in proj]
    pv = sum(cf / (1 + r) ** (t - 0.5) for t, cf in enumerate(cfs, 1))
    pv += cfs[-1] * 1.04 / (r - 0.04) / (1 + r) ** len(cfs)
    dcf_equity = pv - 18.0 + 2.5
    comps_equity = (560 / 62 + 335 / 36) / 2 * 13.0 - 18.0 + 2.5
    concluded = (0.6 * dcf_equity + 0.4 * comps_equity) * (1 - 0.15)
    stake_fv = concluded * 0.74

    c = conclude(sample_inputs)
    assert c.concluded_equity == pytest.approx(concluded)
    assert c.fair_value == pytest.approx(stake_fv + 7.475 + 0.9 + 4.2 + 1.35)
    assert c.liquidation_value == pytest.approx(stake_fv * 0.55 + 5.725 + 0.45 + 4.2 * 0.98 + 1.35)
    assert c.book_value == pytest.approx(40 + 9.6 + 3.0 + 4.0 + 1.35)


def test_weights_must_add_to_100(sample_inputs):
    sample_inputs.approaches[0].weight = 0.5
    with pytest.raises(ValuationError, match="not 100%"):
        conclude(sample_inputs)
