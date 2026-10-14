"""Puerto de notificación (DIP): el servicio no conoce SMTP ni SMS."""
from abc import ABC, abstractmethod


class Notificador(ABC):
    @abstractmethod
    def enviar(self, destinatario: str, mensaje: str) -> None: ...


class NotificadorConsola(Notificador):
    def enviar(self, destinatario: str, mensaje: str) -> None:
        print(f"[NOTIFICACION] para {destinatario}: {mensaje}")
