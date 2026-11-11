"""Aplicación web de SoftMarket.

Aquí se "arma" el servicio de facturación con las piezas que toquen:
- MODO=memoria: guarda en memoria y avisa por consola (para probar en Cloud Shell).
- MODO=nube: guarda en Firestore y avisa por Pub/Sub (en Cloud Run).
"""

import hmac
import os
from decimal import Decimal, InvalidOperation
from typing import Any, List, Tuple

from flask import Flask, abort, redirect, render_template, request, url_for

from facturacion.descuentos import DescuentoPorCategoria
from facturacion.impuestos import IVA_COLOMBIA
from facturacion.modelos import Cliente, LineaFactura
from facturacion.notificador import NotificadorConsola
from facturacion.repositorio import LectorFacturas, RepositorioEnMemoria
from facturacion.servicio import ServicioFacturacion

DESCUENTOS = DescuentoPorCategoria({"vip": Decimal("10"), "mayorista": Decimal("20")})
CATEGORIAS = ["normal", "vip", "mayorista"]


def armar_servicio() -> Tuple[ServicioFacturacion, LectorFacturas]:
    """Escoge los adaptadores según la variable de entorno MODO."""
    if os.environ.get("MODO", "memoria") == "nube":
        from adaptadores_gcp import NotificadorPubSub, RepositorioFirestore
        from google.cloud import firestore, pubsub_v1

        proyecto = os.environ["PROYECTO"]
        repositorio: Any = RepositorioFirestore(firestore.Client(project=proyecto))
        publicador = pubsub_v1.PublisherClient()
        tema = publicador.topic_path(proyecto, "facturas-emitidas")
        notificador: Any = NotificadorPubSub(publicador, tema)
    else:
        repositorio = RepositorioEnMemoria()
        notificador = NotificadorConsola()
    servicio = ServicioFacturacion(repositorio, IVA_COLOMBIA, DESCUENTOS, notificador)
    return servicio, repositorio


def leer_lineas(formulario: Any) -> List[LineaFactura]:
    """Lee hasta 3 líneas del formulario; las filas vacías se ignoran."""
    lineas = []
    for i in range(1, 4):
        descripcion = formulario.get(f"descripcion{i}", "").strip()
        if not descripcion:
            continue
        precio = Decimal(formulario.get(f"precio{i}", ""))
        cantidad = int(formulario.get(f"cantidad{i}", ""))
        if precio < 0 or cantidad <= 0:
            raise ValueError("precio o cantidad no válidos")
        lineas.append(LineaFactura(descripcion, precio, cantidad))
    if not lineas:
        raise ValueError("la factura necesita al menos una línea")
    return lineas


def crear_app(servicio: ServicioFacturacion, lector: LectorFacturas) -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def inicio() -> str:
        return render_template("inicio.html", categorias=CATEGORIAS, error=None)

    @app.post("/facturas")
    def emitir() -> Any:
        # La clave NO está en el código: llega como variable de entorno.
        # En Cloud Run, esa variable la llena Secret Manager.
        clave_correcta = os.environ.get("CLAVE_ADMIN", "")
        clave_recibida = request.form.get("clave", "")
        if not clave_correcta or not hmac.compare_digest(
            clave_recibida, clave_correcta
        ):
            return (
                render_template(
                    "inicio.html", categorias=CATEGORIAS, error="Clave incorrecta."
                ),
                403,
            )
        try:
            lineas = leer_lineas(request.form)
            categoria = request.form.get("categoria", "normal")
            if categoria not in CATEGORIAS:
                raise ValueError("categoría no válida")
            cliente = Cliente(
                1, request.form["nombre"], request.form["email"], categoria
            )
        except (ValueError, InvalidOperation, KeyError):
            return (
                render_template(
                    "inicio.html", categorias=CATEGORIAS, error="Revisa los datos."
                ),
                400,
            )
        factura = servicio.emitir(cliente, lineas)
        return redirect(url_for("ver_factura", id_factura=factura.id))

    @app.get("/facturas/<int:id_factura>")
    def ver_factura(id_factura: int) -> str:
        factura = lector.obtener(id_factura)
        if factura is None:
            abort(404)
        return render_template("factura.html", factura=factura)

    return app


app = crear_app(*armar_servicio())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
