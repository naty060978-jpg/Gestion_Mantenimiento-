"""
Sistema de Gestión de Mantenimiento de Equipos de Climatización
TP N°2 - Programación Avanzada - UNAB

Punto de entrada principal del sistema.
"""

import sys
import os

# Asegura que Python encuentre los módulos al ejecutar desde cualquier carpeta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.gestion_service import GestionService
from models.equipo import SplitPared, Cassette, Rooftop


# DECORADORES

def separador(titulo: str = ""):
    linea = "─" * 50
    if titulo:
        print(f"\n{linea}")
        print(f"  {titulo}")
        print(linea)
    else:
        print(linea)


def pedir(campo: str, requerido: bool = True) -> str:
    while True:
        valor = input(f"  {campo}: ").strip()
        if valor or not requerido:
            return valor
        print(f"El campo '{campo}' es obligatorio.")


def pedir_numero(campo: str, tipo=int):
    while True:
        valor = input(f"  {campo}: ").strip()
        try:
            return tipo(valor)
        except ValueError:
            print(f"Ingrese un número válido.")


def confirmar(mensaje: str) -> bool:
    resp = input(f"  {mensaje} (s/n): ").strip().lower()
    return resp == "s"


# ──────────────────────────────────────────────────────────────
#  FLUJOS DE EQUIPOS
# ──────────────────────────────────────────────────────────────

def crear_equipo() -> object:
    """Guía al usuario para crear un equipo según el tipo elegido."""
    separador("TIPO DE EQUIPO")
    tipos = {
        "1": ("Split Pared", SplitPared),
        "2": ("Cassette",    Cassette),
        "3": ("Rooftop",     Rooftop),
    }
    for k, (nombre, _) in tipos.items():
        print(f"  {k}. {nombre}")

    while True:
        opcion = input("  Seleccione tipo: ").strip()
        if opcion in tipos:
            break
        print("Opción inválida.")

    nombre_tipo, clase = tipos[opcion]
    print(f"\n  >> Cargando datos para {nombre_tipo}")

    sector      = pedir("Sector")
    marca       = pedir("Marca")
    modelo      = pedir("Modelo")
    n_serie     = pedir("N° de Serie")
    refrigerante = pedir("Gas Refrigerante (ej: R-410A)")
    consumo     = pedir_numero("Consumo (W)", float)

    if clase == SplitPared:
        frigorias = pedir_numero("Frigorías")
        return SplitPared(sector, marca, modelo, n_serie, refrigerante, consumo, frigorias)
    elif clase == Cassette:
        vias = pedir_numero("Cantidad de vías")
        return Cassette(sector, marca, modelo, n_serie, refrigerante, consumo, vias)
    elif clase == Rooftop:
        potencia = pedir_numero("Potencia (kW)", float)
        return Rooftop(sector, marca, modelo, n_serie, refrigerante, consumo, potencia)


def flujo_mantenimiento(servicio: GestionService, nombre_cliente: str):
    """Registra el mantenimiento de un equipo específico."""
    cliente = servicio.obtener_cliente(nombre_cliente)
    if not cliente or cliente.cantidad_equipos() == 0:
        print("El cliente no tiene equipos registrados.")
        return

    separador(f"EQUIPOS DE {nombre_cliente.upper()}")
    equipos = cliente.equipos
    for i, eq in enumerate(equipos, 1):
        print(f"  {i}. {eq}")

    idx = pedir_numero("Número de equipo a mantener") - 1
    if not (0 <= idx < len(equipos)):
        print("Número de equipo inválido.")
        return

    equipo = equipos[idx]
    separador(f"CHECKLIST — {equipo.sector}")

    filtros     = "OK" if confirmar("¿Filtros limpios?") else "SUCIOS"
    presion     = pedir("Presión de refrigerante (PSI)")
    condensadora = "OK" if confirmar("¿Condensadora limpia?") else "SUCIA"
    drenaje     = "OK" if confirmar("¿Drenaje despejado?") else "OBSTRUIDO"
    obs         = pedir("Observaciones generales", requerido=False)

    ok = servicio.actualizar_mantenimiento(
        nombre_cliente, equipo.n_serie,
        filtros, presion, condensadora, drenaje, obs
    )

    tecnico = pedir("Nombre del técnico")
    empresa = pedir("Empresa mantenedora")
    orden   = servicio.crear_orden(nombre_cliente, equipo.n_serie, tecnico, empresa)
    orden.completar()

    if ok:
        print("Mantenimiento registrado correctamente.")
        print(f"  📋 {orden}")
    else:
        print("No se pudo actualizar el mantenimiento.")


# ──────────────────────────────────────────────────────────────
#  SUBMENÚS
# ──────────────────────────────────────────────────────────────

def menu_clientes(servicio: GestionService):
    while True:
        separador("GESTIÓN DE CLIENTES")
        print("  1. Nuevo cliente")
        print("  2. Ver todos los clientes")
        print("  3. Ver equipos de un cliente")
        print("  4. Modificar datos de cliente")
        print("  5. Eliminar cliente")
        print("  0. Volver")
        opcion = input("\n  Opción: ").strip()

        if opcion == "1":
            separador("NUEVO CLIENTE")
            nombre    = pedir("Nombre del cliente")
            sitio     = pedir("Sitio / Edificio")
            direccion = pedir("Dirección")
            try:
                cliente = servicio.agregar_cliente(nombre, sitio, direccion)
                print(f"Cliente '{cliente.nombre}' registrado.")
            except ValueError as e:
                print(f"  ❌ {e}")

        elif opcion == "2":
            clientes = servicio.listar_clientes()
            if not clientes:
                print("No hay clientes registrados.")
            else:
                separador("LISTADO DE CLIENTES")
                for c in clientes:
                    print(f"  • {c}")

        elif opcion == "3":
            nombre = pedir("Nombre del cliente")
            cliente = servicio.obtener_cliente(nombre)
            if not cliente:
                print("  ❌ Cliente no encontrado.")
            else:
                separador(f"EQUIPOS — {cliente.nombre}")
                if cliente.cantidad_equipos() == 0:
                    print("  Sin equipos registrados.")
                for eq in cliente.equipos:
                    print(eq.mostrar_datos())
                    separador()

        elif opcion == "4":
            nombre = pedir("Nombre del cliente a modificar")
            nuevo_sitio = pedir("Nuevo sitio")
            nueva_dir   = pedir("Nueva dirección")
            try:
                servicio.modificar_cliente(nombre, nuevo_sitio, nueva_dir)
                print("Cliente actualizado.")
            except ValueError as e:
                print(f"  ❌ {e}")

        elif opcion == "5":
            nombre = pedir("Nombre del cliente a eliminar")
            if confirmar(f"¿Confirma eliminar '{nombre}'?"):
                if servicio.eliminar_cliente(nombre):
                    print("Cliente eliminado.")
                else:
                    print("Cliente no encontrado.")

        elif opcion == "0":
            break
        else:
            print("Opción inválida.")


def menu_equipos(servicio: GestionService):
    while True:
        separador("GESTIÓN DE EQUIPOS")
        print("  1. Agregar equipo a cliente")
        print("  2. Ver equipos de un cliente")
        print("  3. Eliminar equipo")
        print("  0. Volver")
        opcion = input("\n  Opción: ").strip()

        if opcion == "1":
            nombre = pedir("Nombre del cliente")
            try:
                equipo = crear_equipo()
                servicio.agregar_equipo(nombre, equipo)
                print(f"Equipo '{equipo}' agregado a '{nombre}'.")
            except ValueError as e:
                print(f"  ❌ {e}")

        elif opcion == "2":
            nombre  = pedir("Nombre del cliente")
            cliente = servicio.obtener_cliente(nombre)
            if not cliente:
                print("Cliente no encontrado.")
            else:
                separador(f"EQUIPOS — {cliente.nombre}")
                if cliente.cantidad_equipos() == 0:
                    print("  Sin equipos registrados.")
                for eq in cliente.equipos:
                    print(eq.mostrar_datos())
                    separador()

        elif opcion == "3":
            nombre  = pedir("Nombre del cliente")
            n_serie = pedir("N° de Serie del equipo a eliminar")
            if confirmar(f"¿Eliminar equipo S/N {n_serie}?"):
                try:
                    if servicio.eliminar_equipo(nombre, n_serie):
                        print("Equipo eliminado.")
                    else:
                        print("  ❌ Equipo no encontrado.")
                except ValueError as e:
                    print(f"  ❌ {e}")

        elif opcion == "0":
            break
        else:
            print("Opción inválida.")


def menu_mantenimiento(servicio: GestionService):
    while True:
        separador("MANTENIMIENTO")
        print("  1. Registrar mantenimiento a equipo")
        print("  2. Ver órdenes de mantenimiento")
        print("  0. Volver")
        opcion = input("\n  Opción: ").strip()

        if opcion == "1":
            nombre = pedir("Nombre del cliente")
            flujo_mantenimiento(servicio, nombre)

        elif opcion == "2":
            ordenes = servicio.listar_ordenes()
            if not ordenes:
                print("No hay órdenes registradas.")
            else:
                separador("ÓRDENES DE MANTENIMIENTO")
                for o in ordenes:
                    print(o.mostrar())
                    separador()

        elif opcion == "0":
            break
        else:
            print(" Opción inválida.")


# ──────────────────────────────────────────────────────────────
#  MENÚ PRINCIPAL
# ──────────────────────────────────────────────────────────────

def menu_principal():
    servicio = GestionService()

    while True:
        separador("SISTEMA DE GESTIÓN DE MANTENIMIENTO")
        print("  1. Gestión de Clientes")
        print("  2. Gestión de Equipos")
        print("  3. Registro de Mantenimiento")
        print("  0. Salir")
        opcion = input("\n  Opción: ").strip()

        if opcion == "1":
            menu_clientes(servicio)
        elif opcion == "2":
            menu_equipos(servicio)
        elif opcion == "3":
            menu_mantenimiento(servicio)
        elif opcion == "0":
            print("\n  Hasta luego!\n")
            break
        else:
            print(" Opción inválida.")


if __name__ == "__main__":
    menu_principal()
