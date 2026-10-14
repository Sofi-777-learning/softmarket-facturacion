from decimal import Decimal
from typing import List, Tuple

import pytest

from facturacion.descuentos import DescuentoPorCategoria, SinDescuento
from facturacion.impuestos import IVA_COLOMBIA, Exento
from facturacion.modelos import Cliente, LineaFactura
from facturacion.notificador import Notificador
from facturacion.repositorio import RepositorioEnMemoria
from facturacion.servicio import ServicioFacturacion


class NotificadorFalso(Notificador):
    def __init__(self) -> None:
        self.enviados: List[Tuple[str, str]] = []

    def enviar(self, destinatario: str, mensaje: str) -> None:
        self.enviados.append((destinatario, mensaje))


DESCUENTOS = DescuentoPorCategoria({"vip": Decimal("10"), "mayorista": Decimal("20")})


@pytest.fixture
def lineas() -> List[LineaFactura]:
    # subtotal = 2 x 100.000 + 1 x 50.000 = 250.000
    return [
        LineaFactura("Licencia", Decimal("100000"), 2),
        LineaFactura("Soporte", Decimal("50000"), 1),
    ]


def crear_servicio(descuento=SinDescuento(), impuesto=IVA_COLOMBIA):
    repo, notificador = RepositorioEnMemoria(), NotificadorFalso()
    return ServicioFacturacion(repo, impuesto, descuento, notificador), repo, notificador


def test_cliente_normal_paga_iva_sin_descuento(lineas):
    servicio, _, _ = crear_servicio(DESCUENTOS)
    factura = servicio.emitir(Cliente(1, "Ana", "ana@x.co"), lineas)
    assert factura.descuento == Decimal("0")
    assert factura.impuesto == Decimal("47500")
    assert factura.total == Decimal("297500")


def test_cliente_vip_recibe_10_por_ciento(lineas):
    servicio, _, _ = crear_servicio(DESCUENTOS)
    factura = servicio.emitir(Cliente(2, "Luis", "luis@x.co", "vip"), lineas)
    assert factura.descuento == Decimal("25000.00")
    assert factura.total == Decimal("267750.00")


def test_cliente_exento_no_paga_impuesto(lineas):
    servicio, _, _ = crear_servicio(impuesto=Exento())
    factura = servicio.emitir(Cliente(3, "Eva", "eva@x.co"), lineas)
    assert factura.total == Decimal("250000")


def test_emitir_persiste_y_notifica(lineas):
    servicio, repo, notificador = crear_servicio()
    factura = servicio.emitir(Cliente(4, "Sol", "sol@x.co"), lineas)
    assert repo.obtener(factura.id) is factura
    assert notificador.enviados[0][0] == "sol@x.co"


@pytest.mark.parametrize("politica", [SinDescuento(), DESCUENTOS])
def test_contrato_lsp_descuento_dentro_de_rango(politica):
    subtotal = Decimal("250000")
    for categoria in ("normal", "vip", "mayorista", "desconocida"):
        descuento = politica.calcular(Cliente(9, "X", "x@x.co", categoria), subtotal)
        assert Decimal("0") <= descuento <= subtotal


def test_descuento_por_volumen_solo_sobre_umbral(lineas):
    from facturacion.descuentos import DescuentoPorVolumen

    politica = DescuentoPorVolumen(Decimal("200000"), Decimal("5"))
    cliente = Cliente(5, "Teo", "teo@x.co")
    assert politica.calcular(cliente, Decimal("250000")) == Decimal("12500.00")
    assert politica.calcular(cliente, Decimal("100000")) == Decimal("0")
