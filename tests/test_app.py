"""Pruebas de la aplicación web en modo memoria (sin Google Cloud)."""

import pytest
from main import armar_servicio, crear_app

DATOS = {
    "nombre": "Luis",
    "email": "luis@x.co",
    "categoria": "vip",
    "descripcion1": "Licencia",
    "precio1": "100000",
    "cantidad1": "2",
    "descripcion2": "Soporte",
    "precio2": "50000",
    "cantidad2": "1",
    "clave": "secreta",
}


@pytest.fixture
def cliente_web(monkeypatch):
    monkeypatch.setenv("MODO", "memoria")
    monkeypatch.setenv("CLAVE_ADMIN", "secreta")
    return crear_app(*armar_servicio()).test_client()


def test_formulario_se_muestra(cliente_web):
    respuesta = cliente_web.get("/")
    assert respuesta.status_code == 200
    assert "Emitir factura" in respuesta.get_data(as_text=True)


def test_emitir_factura_vip_muestra_el_total(cliente_web):
    respuesta = cliente_web.post("/facturas", data=DATOS, follow_redirects=True)
    texto = respuesta.get_data(as_text=True)
    assert respuesta.status_code == 200
    assert "25000.00" in texto  # descuento VIP del 10 %
    assert "42750.00" in texto  # IVA sobre la base descontada
    assert "267750.00" in texto  # total


def test_clave_incorrecta_no_emite(cliente_web):
    respuesta = cliente_web.post("/facturas", data={**DATOS, "clave": "otra"})
    assert respuesta.status_code == 403


def test_datos_invalidos_responden_400(cliente_web):
    respuesta = cliente_web.post("/facturas", data={**DATOS, "precio1": "abc"})
    assert respuesta.status_code == 400


def test_factura_inexistente_responde_404(cliente_web):
    assert cliente_web.get("/facturas/999").status_code == 404
