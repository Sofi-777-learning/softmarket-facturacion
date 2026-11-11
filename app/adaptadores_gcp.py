"""Adaptadores de Google Cloud para SoftMarket.

Cada clase implementa un "puerto" (interfaz) que ya existía en src/facturacion.
Por eso servicio.py no cambia: solo le damos piezas nuevas.
"""

import json
from decimal import Decimal
from typing import Any, Dict, Optional

from google.cloud import firestore

from facturacion.modelos import Cliente, Factura, LineaFactura
from facturacion.notificador import Notificador
from facturacion.repositorio import EscritorFacturas, LectorFacturas


def factura_a_diccionario(factura: Factura) -> Dict[str, Any]:
    """Convierte la factura en un diccionario que Firestore puede guardar.

    Los Decimal se guardan como texto para no perder centavos.
    """
    return {
        "id": factura.id,
        "cliente": {
            "id": factura.cliente.id,
            "nombre": factura.cliente.nombre,
            "email": factura.cliente.email,
            "categoria": factura.cliente.categoria,
        },
        "lineas": [
            {
                "descripcion": linea.descripcion,
                "precio_unitario": str(linea.precio_unitario),
                "cantidad": linea.cantidad,
            }
            for linea in factura.lineas
        ],
        "subtotal": str(factura.subtotal),
        "descuento": str(factura.descuento),
        "impuesto": str(factura.impuesto),
        "total": str(factura.total),
    }


def diccionario_a_factura(datos: Dict[str, Any]) -> Factura:
    """Hace el camino contrario: de lo guardado en Firestore a una Factura."""
    cliente = Cliente(**datos["cliente"])
    lineas = [
        LineaFactura(
            linea["descripcion"], Decimal(linea["precio_unitario"]), linea["cantidad"]
        )
        for linea in datos["lineas"]
    ]
    return Factura(
        cliente=cliente,
        lineas=lineas,
        descuento=Decimal(datos["descuento"]),
        impuesto=Decimal(datos["impuesto"]),
        id=datos["id"],
    )


@firestore.transactional
def _siguiente_numero(transaccion: Any, contador: Any) -> int:
    """Lee el último número de factura y lo aumenta en 1, sin repetir números.

    La transacción evita que dos facturas emitidas al mismo tiempo
    reciban el mismo número.
    """
    documento = contador.get(transaction=transaccion)
    ultimo = documento.get("ultimo") if documento.exists else 0
    nuevo = int(ultimo) + 1
    transaccion.set(contador, {"ultimo": nuevo})
    return nuevo


class RepositorioFirestore(LectorFacturas, EscritorFacturas):
    """Guarda y lee facturas en Firestore, en la colección "facturas"."""

    def __init__(self, base_de_datos: Any) -> None:
        self._db = base_de_datos
        self._facturas = base_de_datos.collection("facturas")
        self._contador = base_de_datos.collection("contadores").document("facturas")

    def guardar(self, factura: Factura) -> Factura:
        if factura.id is None:
            factura.id = _siguiente_numero(self._db.transaction(), self._contador)
        self._facturas.document(str(factura.id)).set(factura_a_diccionario(factura))
        return factura

    def obtener(self, id_factura: int) -> Optional[Factura]:
        documento = self._facturas.document(str(id_factura)).get()
        if not documento.exists:
            return None
        return diccionario_a_factura(documento.to_dict())


class NotificadorPubSub(Notificador):
    """En vez de imprimir el aviso, lo publica como mensaje en un tema de Pub/Sub."""

    def __init__(self, publicador: Any, tema: str) -> None:
        self._publicador = publicador
        self._tema = tema

    def enviar(self, destinatario: str, mensaje: str) -> None:
        datos = json.dumps({"para": destinatario, "mensaje": mensaje})
        # .result() espera a que Pub/Sub confirme que recibió el mensaje.
        self._publicador.publish(self._tema, datos.encode("utf-8")).result()
