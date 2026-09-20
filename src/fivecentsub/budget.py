"""Budget authorization and charge recording for one subtitle job."""

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation


class BudgetExceededError(ValueError):
    """Raised when a planned or recorded charge exceeds the job budget."""


def as_usd(value: Decimal | str | int | float) -> Decimal:
    try:
        amount = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"Invalid USD amount: {value!r}") from exc
    if amount < 0:
        raise ValueError("USD amounts cannot be negative")
    return amount.quantize(Decimal("0.000001"))


@dataclass
class BudgetLedger:
    """Tracks authorized estimates and actual charges for one job."""

    limit_usd: Decimal | str | int | float = Decimal("0.05")
    _authorized_usd: Decimal = field(default=Decimal("0"), init=False)
    _actual_usd: Decimal = field(default=Decimal("0"), init=False)

    def __post_init__(self) -> None:
        self.limit_usd = as_usd(self.limit_usd)
        if self.limit_usd == 0:
            raise ValueError("Job budget must be greater than zero")

    @property
    def authorized_usd(self) -> Decimal:
        return self._authorized_usd

    @property
    def actual_usd(self) -> Decimal:
        return self._actual_usd

    def authorize(self, estimate_usd: Decimal | str | int | float) -> Decimal:
        estimate = as_usd(estimate_usd)
        projected = self._authorized_usd + estimate
        if projected > self.limit_usd:
            raise BudgetExceededError(
                f"Projected cost ${projected:.6f} exceeds job budget ${self.limit_usd:.6f}"
            )
        self._authorized_usd = projected
        return projected

    def record_charge(self, charge_usd: Decimal | str | int | float) -> Decimal:
        charge = as_usd(charge_usd)
        projected = self._actual_usd + charge
        self._actual_usd = projected
        if projected > self.limit_usd:
            raise BudgetExceededError(
                f"Actual cost ${projected:.6f} exceeds job budget ${self.limit_usd:.6f}"
            )
        return projected
