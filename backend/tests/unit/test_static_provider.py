import pytest

from app.domain.exceptions import UnsupportedCurrencyError
from app.infrastructure.clients.static_provider import StaticRateProvider


@pytest.mark.parametrize(
    ("base", "target", "expected"),
    [
        ("USD", "ARS", 1000.0),
        ("ARS", "USD", 0.001),
        ("USD", "USD", 1.0),
        ("EUR", "USD", 1 / 0.92),
    ],
)
def test_returns_expected_rate(base, target, expected):
    rate = StaticRateProvider().get_rate(base, target)

    assert rate.rate == pytest.approx(expected, rel=1e-5)


@pytest.mark.parametrize(("base", "target"), [("XYZ", "USD"), ("USD", "XYZ")])
def test_unsupported_currency_raises(base, target):
    with pytest.raises(UnsupportedCurrencyError):
        StaticRateProvider().get_rate(base, target)
