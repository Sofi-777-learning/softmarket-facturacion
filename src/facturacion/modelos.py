"""Modelos de dominio: solo datos y cálculos propios de cada entidad (SRP)."""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional


@dataclass(frozen=True)
class Cliente:
    id: int
    nombre: str
    email: str
    categoria: str = "normal"


@dataclass(frozen=True)
class LineaFactura:
    descripcion: str
    precio_unitario: Decimal
    cantidad: int

    @property
    def subtotal(self) -> Decimal:
        return self.precio_unitario * self.cantidad


@dataclass
class Factura:
    cliente: Cliente
    lineas: List[LineaFactura] = field(default_factory=list)
    descuento: Decimal = Decimal("0")
    impuesto: Decimal = Decimal("0")
    id: Optional[int] = None

    @property
    def subtotal(self) -> Decimal:
        return sum((linea.subtotal for linea in self.lineas), Decimal("0"))

    @property
    def total(self) -> Decimal:
        return self.subtotal - self.descuento + self.impuesto
