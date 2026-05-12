"""
Módulo de modelo OrdenMantenimiento.
Relaciona un cliente, un equipo y los datos del técnico que realizó el servicio.
"""

from datetime import datetime


class OrdenMantenimiento:
    """
    Representa una orden de mantenimiento emitida para un equipo de un cliente.
    Relación entre Cliente y Equipo (agregación).
    """

    _contador = 1  # variable de clase para numerar órdenes

    def __init__(self, cliente_nombre: str, equipo_n_serie: str,
                 tecnico: str, empresa: str):
        self.__numero = OrdenMantenimiento._contador
        OrdenMantenimiento._contador += 1

        self.__cliente_nombre = cliente_nombre
        self.__equipo_n_serie = equipo_n_serie
        self.__tecnico = tecnico
        self.__empresa = empresa
        self.__fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.__estado = "Pendiente"

    # --- Getters ---
    @property
    def numero(self):
        return self.__numero

    @property
    def cliente_nombre(self):
        return self.__cliente_nombre

    @property
    def equipo_n_serie(self):
        return self.__equipo_n_serie

    @property
    def tecnico(self):
        return self.__tecnico

    @property
    def empresa(self):
        return self.__empresa

    @property
    def fecha(self):
        return self.__fecha

    @property
    def estado(self):
        return self.__estado

    # --- Métodos ---
    def completar(self):
        """Marca la orden como completada."""
        self.__estado = "Completada"

    def cancelar(self):
        """Cancela la orden."""
        self.__estado = "Cancelada"

    def mostrar(self) -> str:
        return (f"  Orden N°  : {self.__numero}\n"
                f"  Empresa   : {self.__empresa}\n"
                f"  Técnico   : {self.__tecnico}\n"
                f"  Cliente   : {self.__cliente_nombre}\n"
                f"  Equipo S/N: {self.__equipo_n_serie}\n"
                f"  Fecha     : {self.__fecha}\n"
                f"  Estado    : {self.__estado}")

    def to_dict(self) -> dict:
        return {
            "numero": self.__numero,
            "cliente_nombre": self.__cliente_nombre,
            "equipo_n_serie": self.__equipo_n_serie,
            "tecnico": self.__tecnico,
            "empresa": self.__empresa,
            "fecha": self.__fecha,
            "estado": self.__estado,
        }

    def __str__(self):
        return f"Orden #{self.__numero} | {self.__cliente_nombre} | S/N {self.__equipo_n_serie} | {self.__estado}"
