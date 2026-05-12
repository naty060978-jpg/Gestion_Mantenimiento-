"""
Módulo de modelo Cliente.
Un Cliente puede tener múltiples equipos (composición/agregación).
"""

from models.equipo import Equipo


class Cliente:
    """Representa un cliente con su sitio, dirección y lista de equipos."""

    def __init__(self, nombre: str, sitio: str, direccion: str):
        self.__nombre = nombre
        self.__sitio = sitio
        self.__direccion = direccion
        self.__equipos: list[Equipo] = []   # composición: Cliente tiene Equipos

    # --- Getters ---
    @property
    def nombre(self):
        return self.__nombre

    @property
    def sitio(self):
        return self.__sitio

    @property
    def direccion(self):
        return self.__direccion

    @property
    def equipos(self) -> list:
        return list(self.__equipos)          # copia defensiva

    # --- Setters con validación ---
    @nombre.setter
    def nombre(self, valor: str):
        if not valor.strip():
            raise ValueError("El nombre del cliente no puede estar vacío.")
        self.__nombre = valor.strip()

    @sitio.setter
    def sitio(self, valor: str):
        self.__sitio = valor.strip()

    @direccion.setter
    def direccion(self, valor: str):
        self.__direccion = valor.strip()

    # --- Métodos ---
    def agregar_equipo(self, equipo: Equipo):
        """Agrega un equipo al cliente."""
        self.__equipos.append(equipo)

    def eliminar_equipo(self, n_serie: str) -> bool:
        """Elimina un equipo por número de serie. Retorna True si lo encontró."""
        for i, eq in enumerate(self.__equipos):
            if eq.n_serie == n_serie:
                self.__equipos.pop(i)
                return True
        return False

    def buscar_equipo(self, n_serie: str):
        """Busca un equipo por número de serie."""
        for eq in self.__equipos:
            if eq.n_serie == n_serie:
                return eq
        return None

    def cantidad_equipos(self) -> int:
        return len(self.__equipos)

    def mostrar_resumen(self) -> str:
        return (f"Cliente : {self.__nombre}\n"
                f"Sitio   : {self.__sitio}\n"
                f"Dir.    : {self.__direccion}\n"
                f"Equipos : {len(self.__equipos)}")

    def to_dict(self) -> dict:
        return {
            "nombre": self.__nombre,
            "sitio": self.__sitio,
            "direccion": self.__direccion,
            "equipos": [eq.to_dict() for eq in self.__equipos],
        }

    def __str__(self):
        return f"{self.__nombre} | {self.__sitio} | {len(self.__equipos)} equipo(s)"
