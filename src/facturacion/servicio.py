"""Caso de uso: emitir una factura. Depende solo de abstracciones (DIP)."""
from typing import Sequence

from .descuentos import PoliticaDescuento
from .impuestos import PoliticaImpuesto
from .modelos import Cliente, Factura, LineaFactura
from .notificador import Notificador
from .repositorio import EscritorFacturas


class ServicioFacturacion:
    def __init__(
        self,
        repositorio: EscritorFacturas,
        impuesto: PoliticaImpuesto,
        descuento: PoliticaDescuento,
        notificador: Notificador,
    ) -> None:
        self._repositorio = repositorio
        self._impuesto = impuesto
        self._descuento = descuento
        self._notificador = notificador

    def emitir(self, cliente: Cliente, lineas: Sequence[LineaFactura]) -> Factura:
        factura = Factura(cliente=cliente, lineas=list(lineas))
        factura.descuento = self._descuento.calcular(cliente, factura.subtotal)
        base_gravable = factura.subtotal - factura.descuento
        factura.impuesto = self._impuesto.calcular(base_gravable)
        factura = self._repositorio.guardar(factura)
        self._notificador.enviar(
            cliente.email, f"Factura {factura.id} por un total de {factura.total}"
        )
        return factura
