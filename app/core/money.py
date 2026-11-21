"""Precision policy for this two-decimal-currency portfolio demo."""
from decimal import Decimal, ROUND_HALF_UP
from typing import Annotated, Literal
from pydantic import Field

Money = Annotated[Decimal, Field(ge=0, max_digits=14, decimal_places=2, allow_inf_nan=False)]
ExchangeRate = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=8, allow_inf_nan=False)]
Currency = Literal["USD", "EUR", "GBP", "SAR", "AED", "YER"]
CENT = Decimal("0.01")
ZERO = Decimal("0.00")

def convert_side(amounts, rate):
    """Cumulative rounding preserves the converted total on each journal side.

    Allocate cents in stable voucher-line order rather than independently rounding
    each line, which can make a balanced foreign-currency journal unbalanced.
    """
    running = ZERO
    previous = ZERO
    converted = []
    for amount in amounts:
        running += amount
        rounded = (running * rate).quantize(CENT, rounding=ROUND_HALF_UP)
        converted.append(rounded - previous)
        previous = rounded
    return converted
