from decimal import Decimal

import pytest

from fivecentsub.budget import BudgetExceededError, BudgetLedger


def test_ledger_rejects_projected_cost_over_budget() -> None:
    ledger = BudgetLedger("0.05")
    ledger.authorize("0.02")

    with pytest.raises(BudgetExceededError, match="Projected cost"):
        ledger.authorize("0.04")


def test_ledger_records_actual_cost_separately() -> None:
    ledger = BudgetLedger("0.05")
    ledger.authorize("0.04")
    ledger.record_charge(Decimal("0.03"))

    assert ledger.authorized_usd == Decimal("0.040000")
    assert ledger.actual_usd == Decimal("0.030000")
