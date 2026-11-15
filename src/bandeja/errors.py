"""Errores que la aplicación explica en la consola."""

from bandeja.models import Result


class BandejaError(Exception):
    """La bandeja no se puede procesar con las rutas o las reglas dadas."""


class EjecucionError(BandejaError):
    """Un movimiento falló después de haber aplicado otros."""

    def __init__(self, message: str, result: Result) -> None:
        super().__init__(message)
        self.result = result
