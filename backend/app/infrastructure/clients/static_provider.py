from app.domain.exceptions import UnsupportedCurrencyError
from app.domain.models import ExchangeRate

# Valores falsos expresados en USD. Más adelante lo reemplazamos por un client real.
_RATES_IN_USD = {"USD": 1.0, "EUR": 0.92, "ARS": 1000.0, "BRL": 5.0}


class StaticRateProvider:
    def get_rate(self, base: str, target: str) -> ExchangeRate:
        try:
            rate = _RATES_IN_USD[target] / _RATES_IN_USD[base]
        except KeyError as exc:
            raise UnsupportedCurrencyError(f"Unsupported currency: {exc.args[0]}") from exc
        return ExchangeRate(base=base, target=target, rate=round(rate, 6))
