from valcopilot.checklist import bare_na, check


def messages(inp, **kw):
    return [str(i) for i in check(inp, **kw)]


def test_sample_is_clean(sample_inputs):
    assert check(sample_inputs) == []


def test_bare_na_needs_a_reason():
    assert bare_na("N/A") and bare_na("na") and bare_na("Not applicable.") and bare_na("-")
    assert not bare_na("N/A: no expert was involved")


def test_bare_na_in_a_required_field_is_an_error(sample_inputs):
    sample_inputs.fields["experts"] = "N/A"
    assert any("without a reason" in m for m in messages(sample_inputs))


def test_blank_draftable_section_is_an_error_unless_drafting(sample_inputs):
    sample_inputs.fields["summary"] = ""
    assert any("--draft" in m for m in messages(sample_inputs))
    assert check(sample_inputs, will_draft=True) == []


def test_blank_required_field(sample_inputs):
    sample_inputs.fields["conflict"] = ""
    assert any("conflict" in m.lower() and "blank" in m for m in messages(sample_inputs))


def test_dates(sample_inputs):
    sample_inputs.fields["report_date"] = "31/03/2026"   # before valuation date and appointment
    sample_inputs.fields["inspection_date"] = "2026-05-05"
    msgs = messages(sample_inputs)
    assert any("before the valuation date" in m for m in msgs)
    assert any("not a dd/mm/yyyy date" in m for m in msgs)


def test_valuation_date_other_than_icd_is_a_warning(sample_inputs):
    sample_inputs.fields["valuation_date"] = "02/04/2026"
    issues = check(sample_inputs)
    assert [i.level for i in issues] == ["warning"]


def test_inactive_cop_and_bad_registration(sample_inputs):
    sample_inputs.fields["cop_status"] = "inactive"
    sample_inputs.fields["registration_no"] = "RV-123"
    msgs = messages(sample_inputs)
    assert any("inactive" in m for m in msgs)
    assert any("IBBI/RV" in m for m in msgs)


def test_foreign_currency_needs_rate_date_and_source(sample_inputs):
    sample_inputs.fields["currency"] = "USD"
    assert sum("required when the currency is not INR" in m for m in messages(sample_inputs)) == 3


def test_every_approach_must_be_discussed(sample_inputs):
    sample_inputs.approaches = [ap for ap in sample_inputs.approaches if ap.name != "Cost"]
    assert any("Cost approach missing" in m for m in messages(sample_inputs))


def test_cost_approach_needs_replacement_cost(sample_inputs):
    cost = next(ap for ap in sample_inputs.approaches if ap.name == "Cost")
    cost.applicable, cost.weight = True, 0.2
    sample_inputs.approaches[0].weight = 0.4
    assert any("replacement cost" in m for m in messages(sample_inputs))


def test_disputed_receivable_needs_remarks(sample_inputs):
    sample_inputs.receivables[4].remarks = ""
    assert any("Customer E" in m and "Part I(c)" in m for m in messages(sample_inputs))


def test_lv_above_fv_is_an_error(sample_inputs):
    sample_inputs.receivables[0].lv_recovery = 0.99
    assert any("Customer A" in m for m in messages(sample_inputs))


def test_discounts_need_a_rationale(sample_inputs):
    sample_inputs.fields["discounts_rationale"] = ""
    assert any("rationale" in m for m in messages(sample_inputs))
