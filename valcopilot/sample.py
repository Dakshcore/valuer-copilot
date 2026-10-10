"""A fictional worked example. Every name, number and date here is made up for demonstration."""

SAMPLE = {
    "fields": {
        "client": "[SAMPLE] Mr. A. Example, Resolution Professional, IBBI/IPA-000/IP-N00000/2024-2025/00000",
        "corporate_debtor": "[SAMPLE] Sample Polymers Private Limited, manufacturer of polymer granules. "
                            "CIN U00000XX2010PTC000000. Registered office: 1 Example Road, Pune. "
                            "Incorporated 01/04/2010.",
        "purpose": "Determination of fair value and liquidation value of the securities or financial assets "
                   "of the corporate debtor under Regulation 35 of the CIRP Regulations.",
        "subject_asset": "74% equity stake in Sample Packaging Private Limited, trade receivables, a loan to a "
                         "related party, units of a debt mutual fund and bank balances.",
        "scope": "Fair value and liquidation value of the securities or financial assets as on the insolvency "
                 "commencement date.",
        "icd": "01/04/2026",
        "appointment_date": "20/04/2026",
        "inspection_date": "05/05/2026",
        "report_date": "30/06/2026",
        "valuer_name": "[SAMPLE] B. Example",
        "registration_no": "IBBI/RV/00/0000/00000",
        "cop_status": "active",
        "valuation_date": "01/04/2026",
        "vrin": "SAMPLE-VRIN-0000",
        "scope_detail": "As per the appointment letter dated 20/04/2026, the scope covers all securities and "
                        "financial assets in the books of the corporate debtor as on the insolvency commencement "
                        "date. Land and building and plant and machinery are valued by other registered valuers.",
        "experts": "None. No other expert was involved.",
        "conflict": "The valuer has no personal, financial or professional interest in the corporate debtor or "
                    "its subsidiary, and no conflict of interest with the client or stakeholders.",
        "other_users": "Committee of Creditors",
        "background": "The corporate debtor holds 1,48,00,000 equity shares of INR 10 each in Sample Packaging "
                      "Private Limited, an unlisted company with no trading history. The shares are held in "
                      "dematerialised form and are not pledged. Trade receivables are spread across six "
                      "customers. A loan was given to a related party, Sample Trading LLP, which has not "
                      "serviced it since 2024. Surplus cash is held in a debt mutual fund and bank accounts.",
        "currency": "INR",
        "sources_info": "Audited financial statements of the corporate debtor and the subsidiary for FY24 to FY26\n"
                        "Projections for FY27 to FY31 prepared by subsidiary management\n"
                        "Shareholding pattern and demat statement\n"
                        "Receivables ledger and ageing as on the insolvency commencement date\n"
                        "Bank statements and mutual fund account statement\n"
                        "Discussions with management along with the resolution professional",
        "standards": "[SAMPLE] Valuation Standards notified by the Board. The valuer lists each standard and "
                     "section applied here.",
        "coc_meetings": "The methodology was explained to the Committee of Creditors at its meeting on 25/05/2026.",
        "approaches_text": "The income approach values the subsidiary on the cash flows it is expected to generate, "
                           "using a discounted cash flow of free cash flow to the firm. The market approach "
                           "values it on multiples of comparable listed companies. The cost approach is not "
                           "used for the subsidiary because it does not reflect its earning capacity as a going "
                           "concern.",
        "discounts_rationale": "A 15% discount for lack of marketability is applied to the subsidiary's equity "
                               "value because the shares are unlisted and a buyer would face a long "
                               "sale process. Liquidation values apply recovery percentages that reflect a "
                               "forced sale within the liquidation timeline.",
        "data_inputs": "Risk-free rate: yield on 10-year government securities\n"
                       "Equity risk premium and beta: published market studies and comparable companies\n"
                       "Comparable listed companies: five packaging companies (illustrative peers)\n"
                       "Projections: subsidiary management, discussed with the Committee of Creditors",
        "inspections": "Visit to the registered office on 05/05/2026\n"
                       "Management interviews\n"
                       "Review of the loan agreement with Sample Trading LLP and customer contracts",
        "sustainability": "Governance: the subsidiary has a three-member board and clean audit reports. "
                          "Customers: the top three customers make up about half of revenue. Business risks: "
                          "polymer price volatility and customer concentration.",
        "assumptions": "Reliance on management representations for projections\n"
                       "No contingent liabilities beyond those disclosed in the audited accounts\n"
                       "No pending litigation affecting the subsidiary's shares",
        "value_rationale": "Fair value combines the income and market approaches for the subsidiary, the "
                           "expected recovery on receivables and the realisable value of the other assets. "
                           "Liquidation value applies forced-sale recovery rates to each asset.",
        "replacement_cost": "",
        "caveats": "[SAMPLE] Caveats, limitations and disclaimers as per the IBBI (Use of Caveats, Limitations, "
                   "and Disclaimers in Valuation Reports) Guidelines, 2020. The valuer inserts the full text here.",
        "summary": "The securities and financial assets of the corporate debtor have been valued using the "
                   "approaches set out in section m. The values and workings are in section s and the annexures.",
        "annex_appointment": "Yes",
        "annex_engagement": "Yes",
        "annex_financials": "Yes",
        "annex_coc_minutes": "Yes",
        "annex_photos": "N/A: no site photographs are relevant to securities or financial assets",
        "annex_expert_letter": "N/A: no expert was involved",
    },
    "assumptions": {
        "risk_free": 0.068, "beta": 1.1, "erp": 0.07, "specific_premium": 0.03, "cost_of_debt": 0.105,
        "tax_rate": 0.2517, "debt_weight": 0.25, "terminal_growth": 0.04, "mid_year": True,
        "debt": 18.0, "cash": 2.5, "shares": 20_000_000, "dlom": 0.15,
        "comps_multiple": "EV/EBITDA", "comps_stat": "median", "cost_value": 38.0,
    },
    # Year, Type, Revenue, EBITDA, D&A, Capex, Increase in NWC, PAT
    "financials": [
        ("FY24", "Actual", 82.0, 11.1, 3.0, 4.0, 1.0, 4.6),
        ("FY25", "Actual", 88.5, 12.2, 3.2, 4.2, 1.1, 5.2),
        ("FY26", "Actual", 94.0, 13.0, 3.4, 4.5, 0.9, 5.6),
        ("FY27", "Projected", 99.0, 13.9, 3.6, 4.6, 0.8, None),
        ("FY28", "Projected", 104.5, 14.8, 3.8, 4.8, 0.9, None),
        ("FY29", "Projected", 110.0, 15.7, 4.0, 5.0, 0.9, None),
        ("FY30", "Projected", 115.5, 16.6, 4.2, 5.2, 0.9, None),
        ("FY31", "Projected", 121.0, 17.5, 4.4, 5.4, 0.9, None),
    ],
    # Company, Market Cap, Net Debt, Revenue, EBITDA, PAT (illustrative peers, not real companies)
    "comps": [
        ("Illustrative Peer 1", 520.0, 40.0, 410.0, 62.0, 30.0),
        ("Illustrative Peer 2", 310.0, 25.0, 260.0, 36.0, 17.0),
        ("Illustrative Peer 3", 880.0, 120.0, 700.0, 98.0, 45.0),
        ("Illustrative Peer 4", 150.0, 10.0, 160.0, 18.0, 6.0),
        ("Illustrative Peer 5", 240.0, 30.0, 230.0, -4.0, -12.0),
    ],
    "approaches": [
        ("Income", "Yes", "Discounted cash flow (FCFF)", 0.6,
         "Management projections are available and were discussed with the Committee of Creditors."),
        ("Market", "Yes", "Comparable companies (EV/EBITDA)", 0.4,
         "Listed packaging companies with similar operations exist."),
        ("Cost", "No", "Adjusted net asset value", 0.0,
         "Not adopted: net assets do not reflect the subsidiary's earning capacity as a going concern."),
    ],
    # Asset, Category, Premise, Book Value, Basis, Stake, Fair Value (Input), LV % of FV, Remarks
    "assets": [
        ("Equity shares of Sample Packaging Pvt Ltd (74%)", "Unlisted equity", "Going concern", 40.0,
         "Valuation", 0.74, None, 0.55, "Liquidation value reflects a forced sale of an unlisted stake"),
        ("Trade receivables", "Receivables", "Orderly realisation", 9.6, "Receivables", None, None, None,
         "See receivables schedule"),
        ("Loan to Sample Trading LLP", "Loans and advances", "Orderly realisation", 3.0, "Input", None, 0.9, 0.5,
         "Related party; not serviced since 2024"),
        ("Units of a debt mutual fund", "Mutual fund units", "Market value", 4.0, "Input", None, 4.2, 0.98,
         "NAV as on the valuation date"),
        ("Balances with banks", "Cash and bank", "Face value", 1.35, "Input", None, 1.35, 1.0, ""),
    ],
    # Debtor, Nature, Related party, Secured, Disputed, Age, Amount, FV %, LV %, Remarks
    "receivables": [
        ("Customer A", "Trade receivable", "No", "No", "No", "<3 months", 3.2, 0.95, 0.8, ""),
        ("Customer B", "Trade receivable", "No", "No", "No", "<3 months", 2.1, 0.95, 0.8, ""),
        ("Customer C", "Trade receivable", "No", "No", "No", "3-6 months", 1.6, 0.85, 0.6, ""),
        ("Customer D", "Trade receivable", "No", "No", "No", "6-12 months", 1.2, 0.6, 0.35, ""),
        ("Customer E", "Trade receivable", "No", "No", "Yes", ">12 months", 0.9, 0.2, 0.05,
         "Disputed quality claim; legal notice sent"),
        ("Customer F", "Trade receivable", "No", "No", "No", ">12 months", 0.6, 0.3, 0.1, "Slow payer"),
    ],
}
