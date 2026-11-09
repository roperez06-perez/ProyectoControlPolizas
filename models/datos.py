"""Lectura de archivos de origen (Excel y PDFs de polizas).

Es el unico lugar del proyecto que abre archivos.
"""

import os
from datetime import datetime

import pdfplumber
import pandas as pd

# Mapeo: etiqueta del PDF (como aparece en el texto) -> nombre del campo
CAMPOS = {
    "Numero de poliza": "numero",
    "Ramo": "ramo",
    "Tomador / Asegurado": "nombre",
    "Cedula": "cedula",
    "Vigencia desde": "desde",
    "Vigencia hasta": "hasta",
    "Prima anual": "prima",
    "Forma de pago": "pago",
    "Suma asegurada": "suma",
    "Asesor": "asesor",
}

# Campos que son fechas en formato dd/mm/aaaa
CAMPOS_FECHA = {"desde", "hasta"}

# Campos que son montos tipo "CRC 228,000.00"
CAMPOS_MONTO = {"prima", "suma"}


def _convertir_fecha(valor):
    """Convierte 'dd/mm/aaaa' a objeto date. Devuelve None si esta vacio."""
    if not valor or not valor.strip():
        return None
    return datetime.strptime(valor.strip(), "%d/%m/%Y").date()


def _convertir_monto(valor):
    """Convierte 'CRC 228,000.00' a numero float. Devuelve None si esta vacio."""
    if not valor or not valor.strip():
        return None
    texto = valor.strip()
    # Quitar prefijo de moneda si existe
    if texto.upper().startswith("CRC"):
        texto = texto[3:].strip()
    # Quitar separador de miles (coma) y convertir a float
    texto = texto.replace(",", "")
    try:
        return float(texto)
    except ValueError:
        return None


def cargar_clientes(ruta_excel="data/Maestro_Clientes.xlsx", hoja="Clientes"):
    """Lee el Excel de clientes y devuelve un DataFrame con Cedula como texto sin espacios."""
    df = pd.read_excel(ruta_excel, sheet_name=hoja, dtype={"Cedula": str})
    df["Cedula"] = df["Cedula"].str.strip()
    return df


def leer_poliza(ruta_pdf):
    """Extrae los datos de una poliza PDF y devuelve un diccionario.

    Diccionario devuelto:
        archivo, aseguradora, numero, ramo, nombre, cedula, desde, hasta,
        prima, pago, suma, asesor
    """
    nombre_archivo = os.path.basename(ruta_pdf)

    with pdfplumber.open(ruta_pdf) as pdf:
        pagina = pdf.pages[0]
        texto = pagina.extract_text() or ""

    lineas = texto.split("\n")

    # Primera linea: nombre de la aseguradora
    aseguradora = lineas[0].strip() if lineas else ""

    resultado = {
        "archivo": ruta_pdf,
        "aseguradora": aseguradora,
        "numero": None,
        "ramo": None,
        "nombre": None,
        "cedula": None,
        "desde": None,
        "hasta": None,
        "prima": None,
        "pago": None,
        "suma": None,
        "asesor": None,
    }

    # Recorrer el resto de lineas con un bucle
    for linea in lineas[1:]:
        if ":" not in linea:
            continue
        etiqueta, valor = linea.split(":", 1)
        etiqueta = etiqueta.strip()
        valor = valor.strip()

        if etiqueta in CAMPOS:
            campo = CAMPOS[etiqueta]

            if campo in CAMPOS_FECHA:
                resultado[campo] = _convertir_fecha(valor)
            elif campo in CAMPOS_MONTO:
                resultado[campo] = _convertir_monto(valor)
            elif campo == "cedula":
                resultado[campo] = valor.replace(" ", "")
            else:
                resultado[campo] = valor

    return resultado


def cargar_polizas(carpeta="data/polizas"):
    """Recorre la carpeta de PDFs en orden alfabetico y devuelve una lista de diccionarios."""
    if not os.path.isdir(carpeta):
        return []

    archivos = sorted(
        f for f in os.listdir(carpeta) if f.lower().endswith(".pdf")
    )

    polizas = []
    for nombre in archivos:
        ruta = os.path.join(carpeta, nombre)
        polizas.append(leer_poliza(ruta))

    return polizas
