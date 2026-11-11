"""Emite facturas de ejemplo con SoftMarket y las guarda en facturas.csv.

Ese archivo se carga después en BigQuery para analizarlo con SQL.
Las facturas se emiten con el mismo ServicioFacturacion de siempre.
"""

import csv
from decimal import Decimal

from facturacion.descuentos import DescuentoPorCategoria
from facturacion.impuestos import IVA_COLOMBIA
from facturacion.modelos import Cliente, LineaFactura
from facturacion.notificador import Notificador
from facturacion.repositorio import RepositorioEnMemoria
from facturacion.servicio import ServicioFacturacion


class NotificadorSilencioso(Notificador):
    """No imprime nada: aquí solo nos interesa el archivo CSV."""

    def enviar(self, destinatario: str, mensaje: str) -> None:
        pass


CLIENTES = [
    Cliente(1, "Luis", "luis@x.co", "vip"),
    Cliente(2, "Ana", "ana@x.co", "normal"),
    Cliente(3, "Distribuidora Caribe", "compras@caribe.co", "mayorista"),
    Cliente(4, "Marta", "marta@x.co", "normal"),
    Cliente(5, "Tienda Norte", "pedidos@norte.co", "mayorista"),
    Cliente(6, "Jorge", "jorge@x.co", "vip"),
]

PRODUCTOS = [
    ("Licencia", Decimal("100000")),
    ("Soporte", Decimal("50000")),
    ("Capacitacion", Decimal("80000")),
]

servicio = ServicioFacturacion(
    RepositorioEnMemoria(),
    IVA_COLOMBIA,
    DescuentoPorCategoria({"vip": Decimal("10"), "mayorista": Decimal("20")}),
    NotificadorSilencioso(),
)

with open("facturas.csv", "w", newline="", encoding="utf-8") as archivo:
    escritor = csv.writer(archivo)
    escritor.writerow(
        ["id", "cliente", "categoria", "subtotal", "descuento", "impuesto", "total"]
    )
    for numero in range(30):
        cliente = CLIENTES[numero % len(CLIENTES)]
        descripcion, precio = PRODUCTOS[numero % len(PRODUCTOS)]
        cantidad = numero % 4 + 1
        factura = servicio.emitir(
            cliente, [LineaFactura(descripcion, precio, cantidad)]
        )
        escritor.writerow(
            [
                factura.id,
                cliente.nombre,
                cliente.categoria,
                factura.subtotal,
                factura.descuento,
                factura.impuesto,
                factura.total,
            ]
        )

print("Listo: 30 facturas guardadas en facturas.csv")
