"""The IBBI report format for Securities or Financial Assets (SFA) under the IBC.

Source: IBBI Circular No. IBBI/RV/103/2026 dated 15 June 2026, "Guidelines for Conducting
Valuation Under the Insolvency and Bankruptcy Code, 2016", Annexure I, Part I(b) and Part II
(Valuation Report Format for Securities or Financial Assets). Titles and standard wording
below are taken from that text.
"""
from dataclasses import dataclass

CIRCULAR = "IBBI Circular No. IBBI/RV/103/2026 dated 15 June 2026"
CLASS_OF_ASSET = "Securities or Financial Assets"


@dataclass(frozen=True)
class Field:
    key: str
    label: str
    hint: str = ""
    required: bool = True


# Executive summary table, in the circular's order. Fair value and liquidation value are computed.
EXEC_SUMMARY = [
    Field("client", "Client / Appointing Agency",
          "Name and registration number of the insolvency professional acting as IRP, RP, "
          "Liquidator or Bankruptcy Trustee"),
    Field("corporate_debtor", "Details of the Corporate Debtor",
          "Name, business profile, CIN/LLP No., LEI (if available), registered and principal "
          "office address, date of incorporation"),
    Field("purpose", "Purpose of Valuation"),
    Field("class_of_asset", "Class of Asset", "Fixed: Securities or Financial Assets", required=False),
    Field("subject_asset", "Subject Asset", "Brief description, e.g. Equity Shares of XYZ Ltd."),
    Field("scope", "Scope of Work", "Scope summary"),
    Field("icd", "Insolvency commencement date (ICD)", "dd/mm/yyyy"),
    Field("appointment_date", "Date of appointment", "dd/mm/yyyy"),
    Field("inspection_date", "Inspection Date", "dd/mm/yyyy"),
    Field("report_date", "Report Date", "dd/mm/yyyy"),
    Field("fair_value", "Fair Value", "Computed", required=False),
    Field("liquidation_value", "Liquidation Value", "Computed", required=False),
    Field("valuer_name", "Details of the Registered Valuer", "Name of the RV or RV Entity"),
    Field("registration_no", "Registration Number", "IBBI/RV/..."),
    Field("cop_status", "Status of CoP as on appointment date", "active / inactive"),
    Field("valuation_date", "Valuation Date", "dd/mm/yyyy"),
    Field("vrin", "VRIN as generated from the website of the Authority",
          "Valuation Report Identification Number"),
]

DATE_FIELDS = ("icd", "appointment_date", "inspection_date", "report_date", "valuation_date")

# Inputs for the body of the report that the valuer writes (or asks the AI to draft).
# "draftable" sections can be drafted from the computed figures when left blank.
BODY_FIELDS = [
    Field("scope_detail", "Scope of work as agreed in the engagement/appointment letter (section a)"),
    Field("experts", "Other experts involved: name, qualifications, role (section c)",
          "Write 'None' if no expert was used"),
    Field("conflict", "Disclosure of valuer interest or conflict (section d)",
          "Personal, financial or professional interest, or 'No interest or conflict'"),
    Field("other_users", "Other intended users (section e)", "e.g. Committee of Creditors", required=False),
    Field("background", "Background and other relevant information about the asset (section h)",
          "Instrument type, issuer, quantity, ownership, marketability, loans, intangibles, "
          "inventories, receivables"),
    Field("currency", "Valuation currency (section i)", "INR unless there is a reason"),
    Field("fx_rate", "Exchange rate to INR, if not INR (section i)", required=False),
    Field("fx_date", "Date of exchange rate (section i)", required=False),
    Field("fx_source", "Source of exchange rate (section i)", required=False),
    Field("sources_info", "Sources of information (section j)", "One per line"),
    Field("standards", "Valuation standards followed, with relevant sections (section l)"),
    Field("coc_meetings", "Meetings with the Committee of Creditors to explain methodology (section m)",
          "Dates and brief details, as required by Regulation 35(1)(b) of the CIRP Regulations"),
    Field("approaches_text", "Conceptual description of the approaches (section m)",
          "Leave blank to draft from the Approaches sheet"),
    Field("discounts_rationale", "Rationale for discounts and premiums (section n)"),
    Field("data_inputs", "Sources of data and inputs with rationale (section o)", "One per line"),
    Field("inspections", "Inspections and investigations undertaken (section p)", "One per line"),
    Field("sustainability", "Sustainability and functional factors (section q)",
          "ESG, customers and suppliers, business risks, intangibles"),
    Field("assumptions", "Significant or special assumptions and limiting conditions (section r)",
          "One per line"),
    Field("value_rationale", "Rationale for the values (section s)"),
    Field("replacement_cost", "Replacement cost, INR crore (section s)",
          "Required where the cost approach is adopted", required=False),
    Field("caveats", "Caveats, limitations and disclaimers (section t)",
          "As per the IBBI (Use of Caveats, Limitations, and Disclaimers in Valuation Reports) "
          "Guidelines, 2020"),
    Field("summary", "Summary of conclusions (section u)", "Leave blank to draft"),
]

DRAFTABLE = ("background", "approaches_text", "sustainability", "value_rationale", "summary")

# Annexures listed in section v. "photos" and "expert_letter" apply only in some cases.
ANNEXURES = [
    Field("annex_appointment", "Appointment letter"),
    Field("annex_engagement", "Engagement terms"),
    Field("annex_financials", "Financial statement extracts"),
    Field("annex_coc_minutes", "Minutes of the meetings/discussions held with Committee of Creditors"),
    Field("annex_photos", "Photographs or screenshots (if applicable)", required=False),
    Field("annex_expert_letter", "Copy of engagement letter of expert, if involved", required=False),
]


@dataclass(frozen=True)
class Section:
    letter: str
    title: str
    guidance: str


SECTIONS = [
    Section("a", "Purpose and Scope of Work",
            "The purpose of this valuation is to estimate the Fair Value and/or Liquidation Value of "
            "the Securities & Financial asset(s), as required under the Insolvency and Bankruptcy "
            "Code, 2016 and rules & regulations made thereunder."),
    Section("b", "Details of the Registered Valuer & Registration Number",
            "The VRIN shall be mentioned in the footer on the left side of each page of the report."),
    Section("c", "Details of any other experts involved in the valuation process",
            "Name, qualifications, and role of any expert whose input was used."),
    Section("d", "Disclosure of Valuer Interest or Conflict, if Any",
            "Personal, financial, or professional interest in the valuation or any conflict of "
            "interest, as per the Companies (Registered Valuers & Valuation) Rules, 2017."),
    Section("e", "Identity of Client/Appointing Authority and Other Intended Users", ""),
    Section("f", "Intended Use",
            "This report is intended to determine valuation as per the provisions of the Insolvency "
            "and Bankruptcy Code, 2016 and rules and regulations made thereunder."),
    Section("g", "Details of Assets and/or Liabilities being valued",
            "Classification and type of assets, quantity, ownership, issuer details, rights, "
            "marketability, legal agreements, financial metrics, and regulatory compliance."),
    Section("h", "Background and Other Relevant Information about the Asset Being Valued",
            "Type of instruments; issuer; quantity and characteristics; ownership; historical "
            "performance and marketability; loans and advances; intangibles; inventories; receivables."),
    Section("i", "Valuation Currency(ies) and Measurement",
            "Ordinarily INR. If another currency is used, give reasons, the exchange rate, its date "
            "and its source."),
    Section("j", "Sources of Information", ""),
    Section("k", "Basis(es) and Premise of Value Adopted",
            "The basis of valuations under IBC is to determine the fair value and liquidation value "
            "as per relevant regulations."),
    Section("l", "Valuation Standards Followed",
            "State that the Valuation Standards notified by the Board were followed, with the "
            "relevant standards and sections."),
    Section("m", "Valuation Approaches and Methods or Valuation Model(s) Applied",
            "Conceptual description of the Market, Income and Cost approaches, their applicability "
            "or non-applicability, reasons for the selected approach(es) and method(s), and brief "
            "details of meetings with the Committee of Creditors under Regulation 35(1)(b) of the "
            "IBBI (Insolvency Resolution Process for Corporate Persons) Regulations, 2016."),
    Section("n", "Relevant discounts and premiums",
            "Detailed description of all relevant discounts and premiums with the rationale for "
            "each adjustment."),
    Section("o", "Sources of Data and Inputs used along with rationale/justification", ""),
    Section("p", "Description of Inspections and/or Investigations Undertaken", ""),
    Section("q", "Assessment of Sustainability and Functional Factors Considered",
            "Environmental, social and governance factors; major customers, suppliers and "
            "contracts; business risks and outlook; rights attached to intangible assets."),
    Section("r", "Significant or Special Assumptions, and/or Limiting Conditions", ""),
    Section("s", "Value and Rationale for Valuation",
            "Fair Value, Liquidation Value, Book Value (asset wise) and Replacement Cost (asset "
            "wise, if available), with the rationale for the values."),
    Section("t", "Caveats, Limitations and Disclaimers",
            "As per the IBBI (Use of Caveats, Limitations, and Disclaimers in Valuation Reports) "
            "Guidelines, 2020 as updated from time to time."),
    Section("u", "Summary of Conclusions",
            "Conclude the identified rights, the approach and method adopted, data availability and "
            "the final calculation workings (supported with Annexures)."),
    Section("v", "Annexures", ""),
]
