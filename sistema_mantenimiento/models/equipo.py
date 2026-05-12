"""
Módulo de modelos de equipos.
Define la clase base Equipo y sus subclases mediante herencia.
"""

from datetime import datetime


class Equipo:
    """Clase base que representa un equipo genérico de climatización."""

    def __init__(self, sector: str, marca: str, modelo: str, n_serie: str,
                 refrigerante: str, consumo: float):
        # Atributos encapsulados con _ (convención de acceso controlado)
        self.__sector = sector
        self.__marca = marca
        self.__modelo = modelo
        self.__n_serie = n_serie
        self.__refrigerante = refrigerante
        self.__consumo = consumo
        self.__fecha_registro = datetime.now().strftime("%d/%m/%Y")

        # Atributos de mantenimiento
        self._filtros = ""
        self._presion = ""
        self._condensadora = ""
        self._drenaje = ""
        self._observaciones = ""

    # --- Getters ---
    @property
    def sector(self):
        return self.__sector

    @property
    def marca(self):
        return self.__marca

    @property
    def modelo(self):
        return self.__modelo

    @property
    def n_serie(self):
        return self.__n_serie

    @property
    def refrigerante(self):
        return self.__refrigerante

    @property
    def consumo(self):
        return self.__consumo

    @property
    def fecha_registro(self):
        return self.__fecha_registro

    @property
    def filtros(self):
        return self._filtros

    @property
    def presion(self):
        return self._presion

    @property
    def condensadora(self):
        return self._condensadora

    @property
    def drenaje(self):
        return self._drenaje

    @property
    def observaciones(self):
        return self._observaciones

    # --- Setters con validación ---
    @sector.setter
    def sector(self, valor: str):
        if not valor.strip():
            raise ValueError("El sector no puede estar vacío.")
        self.__sector = valor.strip()

    @observaciones.setter
    def observaciones(self, valor: str):
        self._observaciones = valor

    def registrar_mantenimiento(self, filtros: str, presion: str,
                                condensadora: str, drenaje: str, obs: str):
        """Registra el estado del equipo luego del mantenimiento."""
        self._filtros = filtros
        self._presion = presion
        self._condensadora = condensadora
        self._drenaje = drenaje
        self._observaciones = obs

    def tipo(self) -> str:
        """Método polimórfico: cada subclase retorna su tipo."""
        return "Equipo Genérico"

    def descripcion_tecnica(self) -> str:
        """Método polimórfico: cada subclase describe sus datos específicos."""
        return f"Marca: {self.__marca} | Modelo: {self.__modelo} | S/N: {self.__n_serie}"

    def mostrar_datos(self) -> str:
        """Muestra los datos generales del equipo."""
        lineas = [
            f"  Tipo       : {self.tipo()}",
            f"  Sector     : {self.__sector}",
            f"  {self.descripcion_tecnica()}",
            f"  Refrigerante: {self.__refrigerante} | Consumo: {self.__consumo} W",
            f"  Registrado : {self.__fecha_registro}",
        ]
        if self._filtros:
            lineas += [
                f"  --- Último Mantenimiento ---",
                f"  Filtros    : {self._filtros}",
                f"  Presión    : {self._presion} PSI",
                f"  Condensadora: {self._condensadora}",
                f"  Drenaje    : {self._drenaje}",
                f"  Observ.    : {self._observaciones}",
            ]
        return "\n".join(lineas)

    def to_dict(self) -> dict:
        """Serializa el equipo a diccionario para persistencia JSON."""
        return {
            "clase": self.__class__.__name__,
            "sector": self.__sector,
            "marca": self.__marca,
            "modelo": self.__modelo,
            "n_serie": self.__n_serie,
            "refrigerante": self.__refrigerante,
            "consumo": self.__consumo,
            "filtros": self._filtros,
            "presion": self._presion,
            "condensadora": self._condensadora,
            "drenaje": self._drenaje,
            "observaciones": self._observaciones,
        }

    def __str__(self):
        return f"[{self.tipo()}] {self.__marca} {self.__modelo} - Sector: {self.__sector}"


# ──────────────────────────────────────────────────────────────
#  SUBCLASES  (herencia + polimorfismo sobre tipo() y descripcion_tecnica())
# ──────────────────────────────────────────────────────────────

class SplitPared(Equipo):
    """Equipo tipo Split de pared. Agrega atributo frigorías."""

    def __init__(self, sector, marca, modelo, n_serie,
                 refrigerante, consumo, frigorias: int):
        super().__init__(sector, marca, modelo, n_serie, refrigerante, consumo)
        self.__frigorias = frigorias

    @property
    def frigorias(self):
        return self.__frigorias

    def tipo(self) -> str:
        return "Split Pared"

    def descripcion_tecnica(self) -> str:
        base = super().descripcion_tecnica()
        return f"{base} | Frigorías: {self.__frigorias}"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["frigorias"] = self.__frigorias
        return d


class Cassette(Equipo):
    """Equipo tipo Cassette. Agrega cantidad de vías de descarga."""

    def __init__(self, sector, marca, modelo, n_serie,
                 refrigerante, consumo, vias: int):
        super().__init__(sector, marca, modelo, n_serie, refrigerante, consumo)
        self.__vias = vias

    @property
    def vias(self):
        return self.__vias

    def tipo(self) -> str:
        return "Cassette"

    def descripcion_tecnica(self) -> str:
        base = super().descripcion_tecnica()
        return f"{base} | Vías: {self.__vias}"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["vias"] = self.__vias
        return d


class Rooftop(Equipo):
    """Equipo tipo Rooftop. Agrega potencia en kW."""

    def __init__(self, sector, marca, modelo, n_serie,
                 refrigerante, consumo, potencia_kw: float):
        super().__init__(sector, marca, modelo, n_serie, refrigerante, consumo)
        self.__potencia_kw = potencia_kw

    @property
    def potencia_kw(self):
        return self.__potencia_kw

    def tipo(self) -> str:
        return "Rooftop"

    def descripcion_tecnica(self) -> str:
        base = super().descripcion_tecnica()
        return f"{base} | Potencia: {self.__potencia_kw} kW"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["potencia_kw"] = self.__potencia_kw
        return d


# Mapeo de nombre de clase → clase real (para deserialización)
CLASES_EQUIPO = {
    "SplitPared": SplitPared,
    "Cassette": Cassette,
    "Rooftop": Rooftop,
}
