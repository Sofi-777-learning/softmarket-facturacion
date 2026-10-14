"""Políticas de descuento (Strategy). Nueva regla = nueva clase (OCP)."""
from abc import ABC, abstractmethod
from decimal import ROUND_HALF_UP, Decimal
from typing import Mapping

from .modelos import Cliente

CENTAVOS = Decimal("0.01")


def _porcentaje(monto: Decimal, porcentaje: Decimal) -> Decimal:
    valor = monto * porcentaje / Decimal("100")
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


class PoliticaDescuento(ABC):
    """Contrato (LSP): 0 <= descuento <= subtotal en cualquier implementación."""

    @abstractmethod
    def calcular(self, cliente: Cliente, subtotal: Decimal) -> Decimal: ...


class SinDescuento(PoliticaDescuento):
    def calcular(self, cliente: Cliente, subtotal: Decimal) -> Decimal:
        return Decimal("0")


class DescuentoPorCategoria(PoliticaDescuento):
    def __init__(self, porcentajes: Mapping[str, Decimal]) -> None:
        self._porcentajes = porcentajes

    def calcular(self, cliente: Cliente, subtotal: Decimal) -> Decimal:
        pct = self._porcentajes.get(cliente.categoria, Decimal("0"))
        return _porcentaje(subtotal, pct)


class DescuentoPorVolumen(PoliticaDescuento):
    """Aplica un porcentaje cuando el subtotal alcanza un umbral."""

    def __init__(self, umbral: Decimal, porcentaje: Decimal) -> None:
        self._umbral = umbral
        self._pct = porcentaje

    def calcular(self, cliente: Cliente, subtotal: Decimal) -> Decimal:
        if subtotal >= self._umbral:
            return _porcentaje(subtotal, self._pct)
        return Decimal("0")
