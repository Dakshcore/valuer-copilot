"""Inputs to a valuation, as read from the input workbook. Amounts are INR crore unless noted."""
from dataclasses import dataclass, field


@dataclass
class Year:
    label: str          # e.g. "FY27"
    projected: bool
    revenue: float
    ebitda: float
    da: float = 0.0      # depreciation and amortisation
    capex: float = 0.0
    nwc_change: float = 0.0  # increase in net working capital
    pat: float | None = None


@dataclass
class Assumptions:
    risk_free: float         # decimals, e.g. 0.068
    beta: float
    erp: float
    specific_premium: float  # size / company-specific risk premium
    cost_of_debt: float      # pre-tax
    tax_rate: float
    debt_weight: float       # D / (D + E)
    terminal_growth: float
    mid_year: bool
    debt: float
    cash: float
    shares: float            # number of equity shares (units)
    dlom: float = 0.0        # discount for lack of marketability on the concluded equity value
    comps_multiple: str = "EV/EBITDA"   # EV/EBITDA, EV/Revenue or P/E
    comps_stat: str = "median"          # median or mean
    cost_value: float | None = None     # adjusted net asset value, for the cost approach


@dataclass
class Comp:
    name: str
    market_cap: float
    net_debt: float
    revenue: float
    ebitda: float
    pat: float


@dataclass
class Approach:
    name: str        # Market, Income or Cost
    applicable: bool
    method: str
    weight: float    # decimals; weights of applicable approaches sum to 1
    reason: str


@dataclass
class Asset:
    name: str
    category: str
    premise: str
    book_value: float
    basis: str               # "Valuation", "Receivables" or "Input"
    stake: float = 1.0       # share of the valued entity held, for basis "Valuation"
    fair_value: float | None = None   # for basis "Input"
    lv_recovery: float = 1.0          # liquidation value as a share of fair value (not for Receivables)
    remarks: str = ""


@dataclass
class Receivable:
    debtor: str
    nature: str
    related_party: bool
    secured: bool
    disputed: bool
    age: str
    amount: float
    fv_recovery: float
    lv_recovery: float
    remarks: str = ""


@dataclass
class Inputs:
    fields: dict[str, str] = field(default_factory=dict)   # engagement, body text and annexure answers
    years: list[Year] = field(default_factory=list)
    assumptions: Assumptions | None = None
    comps: list[Comp] = field(default_factory=list)
    approaches: list[Approach] = field(default_factory=list)
    assets: list[Asset] = field(default_factory=list)
    receivables: list[Receivable] = field(default_factory=list)

    def get(self, key: str) -> str:
        return (self.fields.get(key) or "").strip()
