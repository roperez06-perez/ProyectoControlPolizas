"""Reglas del negocio para el control de polizas.

Usa las funciones de models/datos para leer los archivos y aplica la logica
de vencimiento, cruce con el maestro y deteccion de inconsistencias.
"""

from collections import defaultdict
from datetime import date

from models.datos import cargar_clientes, cargar_polizas

FECHA_CORTE = date(2026, 11, 9)
DIAS_AVISO = 30


def estado_poliza(hasta, fecha_corte=FECHA_CORTE):
    """Devuelve el estado de una poliza: 'Vencida', 'Por vencer', 'Vigente' o 'Sin fecha'."""
    if hasta is None:
        return "Sin fecha"

    if hasta < fecha_corte:
        return "Vencida"

    dias = (hasta - fecha_corte).days
    if 0 <= dias <= DIAS_AVISO:
        return "Por vencer"

    return "Vigente"


def _cargar_maestro():
    """Carga el maestro de clientes. Si no existe el archivo, retorna diccionario vacio."""
    try:
        df_clientes = cargar_clientes()
        maestro = {}
        for _, fila in df_clientes.iterrows():
            cedula = str(fila["Cedula"]).strip()
            maestro[cedula] = {
                "correo": fila.get("Correo", ""),
            }
        return maestro
    except Exception:
        return {}


def calcular_resultados(fecha_corte=FECHA_CORTE, carpeta="polizas"):
    """Cruza cada poliza con el maestro por cedula, calcula dias hasta vencer y estado.

    Devuelve una lista de diccionarios ordenada de menos a mas dias
    (lo urgente primero). Cada diccionario incluye los campos de la poliza
    mas: correo, en_maestro, dias, estado.
    """
    maestro = _cargar_maestro()
    polizas = cargar_polizas(carpeta)

    resultados = []
    for p in polizas:
        cedula = p.get("cedula")
        en_maestro = cedula in maestro if cedula else False
        correo = maestro[cedula]["correo"] if en_maestro else ""

        hasta = p.get("hasta")
        estado = estado_poliza(hasta, fecha_corte)

        if hasta is not None:
            dias = (hasta - fecha_corte).days
        else:
            dias = None

        resultado = dict(p)
        resultado["correo"] = correo
        resultado["en_maestro"] = en_maestro
        resultado["dias"] = dias
        resultado["estado"] = estado
        resultados.append(resultado)

    # Ordenar: menos a mas dias (urgente primero). Sin fecha al final.
    resultados.sort(
        key=lambda r: (
            r["dias"] is None,
            r["dias"] if r["dias"] is not None else float("inf"),
        )
    )

    return resultados


def contar_por_estado(resultados):
    """Devuelve un diccionario con la cantidad de polizas por estado."""
    conteo = {}
    for r in resultados:
        estado = r.get("estado", "Sin fecha")
        conteo[estado] = conteo.get(estado, 0) + 1
    return conteo


def primas_por_aseguradora(resultados):
    """Devuelve {aseguradora: suma de primas} de polizas no vencidas, de mayor a menor."""
    suma = defaultdict(float)
    for r in resultados:
        if r.get("estado") == "Vencida":
            continue
        prima = r.get("prima")
        if prima is not None:
            aseguradora = r.get("aseguradora", "Desconocida")
            suma[aseguradora] += prima

    return dict(sorted(suma.items(), key=lambda item: item[1], reverse=True))


def buscar_inconsistencias(resultados):
    """Devuelve una lista de textos con los 3 tipos de problema de AGENTS.md.

    1. Cliente del maestro sin ninguna poliza.
    2. Poliza cuya cedula no esta en el maestro.
    3. Poliza sin prima o con fecha ilegible.
    """
    inconsistencias = []

    maestro = _cargar_maestro()
    cedulas_maestro = set(maestro.keys())

    cedulas_en_polizas = set()
    for r in resultados:
        cedula = r.get("cedula")
        numero = r.get("numero", "desconocida")

        if cedula:
            cedulas_en_polizas.add(cedula)
            # Tipo 2: cedula no esta en el maestro
            if cedula not in cedulas_maestro:
                inconsistencias.append(
                    f"Poliza {numero} con cedula {cedula} no esta en el maestro de clientes"
                )

        # Tipo 3: sin prima o fecha ilegible
        if r.get("prima") is None or r.get("desde") is None or r.get("hasta") is None:
            inconsistencias.append(
                f"Poliza {numero} sin prima o con fecha ilegible"
            )

    # Tipo 1: cliente del maestro sin ninguna poliza
    for cedula in cedulas_maestro:
        if cedula not in cedulas_en_polizas:
            inconsistencias.append(
                f"Cliente con cedula {cedula} no tiene ninguna poliza"
            )

    return inconsistencias


def buscar_por_numero(numero, resultados=None):
    """Busca una poliza por su numero en la lista de resultados."""
    if resultados is None:
        resultados = calcular_resultados()
    for r in resultados:
        if r.get("numero") == numero:
            return r
    return None
