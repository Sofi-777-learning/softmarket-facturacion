"""Pruebas de los adaptadores de Google Cloud con objetos falsos.

No se conectan a Google Cloud: comprueban la lógica propia de cada adaptador.
La conexión real se comprueba en Cloud Shell y en Cloud Run.
"""

import json
from decimal import Decimal

from adaptadores_gcp import (
    NotificadorPubSub,
    RepositorioFirestore,
    diccionario_a_factura,
    factura_a_diccionario,
)

from facturacion.modelos import Cliente, Factura, LineaFactura


def crear_factura() -> Factura:
    return Factura(
        cliente=Cliente(1, "Luis", "luis@x.co", "vip"),
        lineas=[LineaFactura("Licencia", Decimal("100000"), 2)],
        descuento=Decimal("20000.00"),
        impuesto=Decimal("34200.00"),
        id=7,
    )


def test_ida_y_vuelta_no_pierde_centavos():
    original = crear_factura()
    copia = diccionario_a_factura(factura_a_diccionario(original))
    assert copia == original
    assert copia.total == Decimal("214200.00")


class FuturoFalso:
    def result(self):
        return "id-mensaje"


class PublicadorFalso:
    def __init__(self):
        self.publicados = []

    def publish(self, tema, datos):
        self.publicados.append((tema, datos))
        return FuturoFalso()


def test_notificador_publica_un_mensaje_json():
    publicador = PublicadorFalso()
    NotificadorPubSub(publicador, "temas/facturas").enviar("luis@x.co", "Hola")
    tema, datos = publicador.publicados[0]
    assert tema == "temas/facturas"
    assert json.loads(datos) == {"para": "luis@x.co", "mensaje": "Hola"}


class DocumentoFalso:
    def __init__(self, datos=None):
        self._datos = datos
        self.exists = datos is not None

    def get(self):
        return self

    def to_dict(self):
        return self._datos


class ColeccionFalsa:
    def __init__(self, documentos):
        self._documentos = documentos

    def document(self, nombre):
        return self._documentos.get(nombre, DocumentoFalso())


class BaseFalsa:
    def __init__(self, documentos):
        self._documentos = documentos

    def collection(self, nombre):
        return ColeccionFalsa(self._documentos if nombre == "facturas" else {})


def test_obtener_lee_la_factura_guardada():
    guardada = factura_a_diccionario(crear_factura())
    repo = RepositorioFirestore(BaseFalsa({"7": DocumentoFalso(guardada)}))
    assert repo.obtener(7) == crear_factura()
    assert repo.obtener(8) is None
