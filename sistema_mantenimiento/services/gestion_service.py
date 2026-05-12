"""
Servicio de gestión de clientes y equipos.
Maneja la lógica de negocio y la persistencia en JSON.
"""

import json
import os

from models.cliente import Cliente
from models.equipo import SplitPared, Cassette, Rooftop, CLASES_EQUIPO
from models.orden_mantenimiento import OrdenMantenimiento


ARCHIVO_DATOS = "datos_mantenimiento.json"


class GestionService:
    """
    Servicio central del sistema.
    Encapsula toda la lógica: ABM de clientes, equipos y órdenes.
    Separación de responsabilidades: este servicio NO se encarga de la UI.
    """

    def __init__(self):
        self.__clientes: dict[str, Cliente] = {}
        self.__ordenes: list[OrdenMantenimiento] = []
        self._cargar_datos()

    # ──────────────────────────────────────────────────────────
    #  PERSISTENCIA
    # ──────────────────────────────────────────────────────────

    def _cargar_datos(self):
        """Carga clientes y equipos desde el archivo JSON."""
        if not os.path.exists(ARCHIVO_DATOS):
            return
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                datos = json.load(f)
            for nombre, info in datos.get("clientes", {}).items():
                cliente = Cliente(info["nombre"], info["sitio"], info["direccion"])
                for eq_data in info.get("equipos", []):
                    equipo = self._dict_a_equipo(eq_data)
                    if equipo:
                        cliente.agregar_equipo(equipo)
                self.__clientes[nombre] = cliente
        except (json.JSONDecodeError, KeyError):
            print("Archivo de datos corrupto. Se inicia con datos vacíos.")

    def guardar_datos(self):
        """Persiste el estado actual en JSON."""
        datos = {
            "clientes": {
                nombre: cliente.to_dict()
                for nombre, cliente in self.__clientes.items()
            }
        }
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    def _dict_a_equipo(self, d: dict):
        """Reconstruye un objeto Equipo a partir de un diccionario."""
        clase_nombre = d.get("clase", "")
        clase = CLASES_EQUIPO.get(clase_nombre)
        if not clase:
            return None

        try:
            if clase_nombre == "SplitPared":
                eq = SplitPared(d["sector"], d["marca"], d["modelo"], d["n_serie"],
                                d["refrigerante"], d["consumo"], d.get("frigorias", 0))
            elif clase_nombre == "Cassette":
                eq = Cassette(d["sector"], d["marca"], d["modelo"], d["n_serie"],
                              d["refrigerante"], d["consumo"], d.get("vias", 4))
            elif clase_nombre == "Rooftop":
                eq = Rooftop(d["sector"], d["marca"], d["modelo"], d["n_serie"],
                             d["refrigerante"], d["consumo"], d.get("potencia_kw", 0.0))
            else:
                return None

            eq.registrar_mantenimiento(
                d.get("filtros", ""), d.get("presion", ""),
                d.get("condensadora", ""), d.get("drenaje", ""),
                d.get("observaciones", "")
            )
            return eq
        except KeyError:
            return None

    # ──────────────────────────────────────────────────────────
    #  ABM CLIENTES
    # ──────────────────────────────────────────────────────────

    def agregar_cliente(self, nombre: str, sitio: str, direccion: str) -> Cliente:
        if nombre in self.__clientes:
            raise ValueError(f"Ya existe un cliente con el nombre '{nombre}'.")
        cliente = Cliente(nombre, sitio, direccion)
        self.__clientes[nombre] = cliente
        self.guardar_datos()
        return cliente

    def obtener_cliente(self, nombre: str):
        return self.__clientes.get(nombre)

    def listar_clientes(self) -> list:
        return list(self.__clientes.values())

    def modificar_cliente(self, nombre: str, nuevo_sitio: str, nueva_dir: str):
        cliente = self.__clientes.get(nombre)
        if not cliente:
            raise ValueError(f"Cliente '{nombre}' no encontrado.")
        cliente.sitio = nuevo_sitio
        cliente.direccion = nueva_dir
        self.guardar_datos()

    def eliminar_cliente(self, nombre: str) -> bool:
        if nombre in self.__clientes:
            del self.__clientes[nombre]
            self.guardar_datos()
            return True
        return False

    # ──────────────────────────────────────────────────────────
    #  ABM EQUIPOS
    # ──────────────────────────────────────────────────────────

    def agregar_equipo(self, nombre_cliente: str, equipo) -> bool:
        cliente = self.__clientes.get(nombre_cliente)
        if not cliente:
            raise ValueError(f"Cliente '{nombre_cliente}' no encontrado.")
        cliente.agregar_equipo(equipo)
        self.guardar_datos()
        return True

    def eliminar_equipo(self, nombre_cliente: str, n_serie: str) -> bool:
        cliente = self.__clientes.get(nombre_cliente)
        if not cliente:
            raise ValueError(f"Cliente '{nombre_cliente}' no encontrado.")
        resultado = cliente.eliminar_equipo(n_serie)
        if resultado:
            self.guardar_datos()
        return resultado

    def actualizar_mantenimiento(self, nombre_cliente: str, n_serie: str,
                                 filtros: str, presion: str, condensadora: str,
                                 drenaje: str, observaciones: str) -> bool:
        cliente = self.__clientes.get(nombre_cliente)
        if not cliente:
            return False
        equipo = cliente.buscar_equipo(n_serie)
        if not equipo:
            return False
        equipo.registrar_mantenimiento(filtros, presion, condensadora, drenaje, observaciones)
        self.guardar_datos()
        return True

    # ──────────────────────────────────────────────────────────
    #  ÓRDENES DE MANTENIMIENTO
    # ──────────────────────────────────────────────────────────

    def crear_orden(self, nombre_cliente: str, n_serie: str,
                    tecnico: str, empresa: str) -> OrdenMantenimiento:
        orden = OrdenMantenimiento(nombre_cliente, n_serie, tecnico, empresa)
        self.__ordenes.append(orden)
        return orden

    def listar_ordenes(self) -> list:
        return list(self.__ordenes)

    def completar_orden(self, numero: int) -> bool:
        for orden in self.__ordenes:
            if orden.numero == numero:
                orden.completar()
                return True
        return False
