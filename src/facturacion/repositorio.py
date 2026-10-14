"""Puertos de persistencia segregados (ISP) y una implementación en memoria."""
from abc import ABC, abstractmethod
from typing import Dict, Optional

from .modelos import Factura


class LectorFacturas(ABC):
    @abstractmethod
    def obtener(self, id_factura: int) -> Optional[Factura]: ...


class EscritorFacturas(ABC):
    @abstractmethod
    def guardar(self, factura: Factura) -> Factura: ...


class RepositorioEnMemoria(LectorFacturas, EscritorFacturas):
    def __init__(self) -> None:
        self._datos: Dict[int, Factura] = {}
        self._siguiente = 1

    def guardar(self, factura: Factura) -> Factura:
        if factura.id is None:
            factura.id = self._siguiente
            self._siguiente += 1
        self._datos[factura.id] = factura
        return factura

    def obtener(self, id_factura: int) -> Optional[Factura]:
        return self._datos.get(id_factura)
