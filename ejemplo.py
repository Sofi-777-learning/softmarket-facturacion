from decimal import Decimal

from facturacion.descuentos import DescuentoPorCategoria
from facturacion.impuestos import IVA_COLOMBIA
from facturacion.modelos import Cliente, LineaFactura
from facturacion.notificador import NotificadorConsola
from facturacion.repositorio import RepositorioEnMemoria
from facturacion.servicio import ServicioFacturacion

servicio = ServicioFacturacion(
    RepositorioEnMemoria(),
    IVA_COLOMBIA,
    DescuentoPorCategoria({"vip": Decimal("10")}),
    NotificadorConsola(),
)
cliente = Cliente(1, "Luis", "luis@x.co", "vip")
lineas = [
    LineaFactura("Licencia", Decimal("100000"), 2),
    LineaFactura("Soporte", Decimal("50000"), 1),
]

factura = servicio.emitir(cliente, lineas)

print("Factura número:", factura.id)
print("Cliente:", factura.cliente.nombre)
print("Subtotal:", factura.subtotal)
print("Descuento:", factura.descuento)
print("Impuesto:", factura.impuesto)
print("Total:", factura.total)