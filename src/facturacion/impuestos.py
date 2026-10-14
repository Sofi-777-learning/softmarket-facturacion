"""Políticas de impuestos (patrón Strategy)."""
from abc import ABC, abstractmethod
from decimal import Decimal


class PoliticaImpuesto(ABC):
    """Contrato (LSP): devuelve un monto >= 0 calculado sobre la base gravable."""

    @abstractmethod
    def calcular(self, base: Decimal) -> Decimal: ...


class ImpuestoPorcentaje(PoliticaImpuesto):
    def __init__(self, tasa: Decimal) -> None:
        self._tasa = tasa

    def calcular(self, base: Decimal) -> Decimal:
        return base * self._tasa


class Exento(PoliticaImpuesto):
    def calcular(self, base: Decimal) -> Decimal:
        return Decimal("0")


IVA_COLOMBIA = ImpuestoPorcentaje(Decimal("0.19"))
IVA_ECUADOR = ImpuestoPorcentaje(Decimal("0.12"))
