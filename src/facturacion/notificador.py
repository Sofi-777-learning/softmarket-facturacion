"""Puerto de notificación (DIP): el servicio no conoce SMTP ni SMS."""
from abc import ABC, abstractmethod
from typing import Callable


class Notificador(ABC):
    @abstractmethod
    def enviar(self, destinatario: str, mensaje: str) -> None: ...


class NotificadorConsola(Notificador):
    def enviar(self, destinatario: str, mensaje: str) -> None:
        print(f"[NOTIFICACION] para {destinatario}: {mensaje}")


class NotificadorSMS(Notificador):
    """Envía la notificación mediante una pasarela SMS inyectada."""

    def __init__(self, pasarela: Callable[[str, str], None]) -> None:
        self._pasarela = pasarela

    def enviar(self, destinatario: str, mensaje: str) -> None:
        self._pasarela(destinatario, mensaje)
