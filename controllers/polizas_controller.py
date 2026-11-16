"""Rutas de Flask para el control de polizas.

Este controlador NO calcula nada: solo llama a models/ y services/.
"""

import io
import os
import zipfile

from flask import Blueprint, render_template, send_file, abort, request, session, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename

from models.polizas import (
    calcular_resultados,
    contar_por_estado,
    primas_por_aseguradora,
    buscar_inconsistencias,
    FECHA_CORTE,
    buscar_por_numero,
)
from services.generador_aviso import crear_aviso_pdf
from models.datos import cargar_clientes_desde_archivo

polizas_bp = Blueprint("polizas", __name__)

EXTENSIONES_PERMITIDAS = {".xlsx", ".xls"}


@polizas_bp.route("/")
def inicio():
    """Tablero principal: contadores, primas, inconsistencias y tabla de polizas."""
    df_clientes = None
    ruta_excel = session.get("ruta_excel_clientes")
    if ruta_excel and os.path.exists(ruta_excel):
        try:
            df_clientes = cargar_clientes_desde_archivo(ruta_excel)
        except Exception:
            flash("No se pudo leer el archivo Excel importado. Intenta nuevamente.", "error")
            session.pop("ruta_excel_clientes", None)

    resultados = calcular_resultados(df_clientes=df_clientes)
    conteo = contar_por_estado(resultados)
    primas = primas_por_aseguradora(resultados)
    inconsistencias = buscar_inconsistencias(resultados)

    return render_template(
        "inicio.html",
        resultados=resultados,
        conteo=conteo,
        primas=primas,
        inconsistencias=inconsistencias,
        fecha_corte=FECHA_CORTE,
    )


@polizas_bp.route("/importar-clientes", methods=["GET", "POST"])
def importar_clientes():
    """Recibe el archivo Excel de clientes subido por el usuario."""
    if request.method == "POST":
        if "archivo_excel" not in request.files:
            flash("No seleccionaste ningún archivo.", "error")
            return redirect(request.url)

        archivo = request.files["archivo_excel"]

        if archivo.filename == "":
            flash("No seleccionaste ningún archivo.", "error")
            return redirect(request.url)

        nombre_archivo = archivo.filename.lower()
        extension = os.path.splitext(nombre_archivo)[1]
        if extension not in EXTENSIONES_PERMITIDAS:
            flash("Solo se permiten archivos Excel (.xlsx, .xls).", "error")
            return redirect(request.url)

        # Guardar el archivo temporalmente en la carpeta de uploads
        carpeta_uploads = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(carpeta_uploads, exist_ok=True)

        nombre_seguro = secure_filename(archivo.filename)
        ruta_temp = os.path.join(carpeta_uploads, nombre_seguro)
        archivo.save(ruta_temp)

        # Guardar la ruta en la sesion para usarla en el tablero
        session["ruta_excel_clientes"] = ruta_temp

        flash("Clientes importados correctamente desde el Excel.", "exito")
        return redirect(url_for("polizas.inicio"))

    return render_template("inicio.html")


@polizas_bp.route("/procesar", methods=["POST"])
def procesar():
    """Ejecuta el proceso de calculo de estados y cruce con el maestro de clientes.

    Recarga los datos de los PDFs y del Excel (si hay uno importado en sesion),
    recalcula estados, dias para vencer, primas e inconsistencias.
    """
    try:
        df_clientes = None
        ruta_excel = session.get("ruta_excel_clientes")
        if ruta_excel and os.path.exists(ruta_excel):
            try:
                df_clientes = cargar_clientes_desde_archivo(ruta_excel)
            except Exception:
                flash("No se pudo leer el Excel importado. Se usara el maestro por defecto.", "error")

        resultados = calcular_resultados(df_clientes=df_clientes)
        conteo = contar_por_estado(resultados)
        primas = primas_por_aseguradora(resultados)
        inconsistencias = buscar_inconsistencias(resultados)

        flash(
            f"Proceso completado: {conteo.get('Vigente', 0)} vigentes, "
            f"{conteo.get('Por vencer', 0)} por vencer, "
            f"{conteo.get('Vencida', 0)} vencidas, "
            f"{len(inconsistencias)} inconsistencias detectadas.",
            "exito",
        )
    except Exception as exc:
        flash(f"Error al procesar: {exc}", "error")

    return redirect(url_for("polizas.inicio"))


@polizas_bp.route("/aviso/<numero>")
def aviso(numero):
    """Devuelve el aviso en PDF para ver en el navegador.

    Error 404 si la poliza no existe o esta Vigente.
    """
    resultados = calcular_resultados()
    poliza = buscar_por_numero(numero, resultados)

    if not poliza:
        abort(404)

    if poliza.get("estado") == "Vigente":
        abort(404)

    pdf_bytes = crear_aviso_pdf(poliza)

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"aviso_{numero}.pdf",
    )


@polizas_bp.route("/descargar-avisos")
def descargar_avisos():
    """Devuelve un .zip en memoria con los avisos de polizas Por vencer y Vencidas."""
    resultados = calcular_resultados()

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for r in resultados:
            if r.get("estado") in ("Por vencer", "Vencida"):
                pdf_bytes = crear_aviso_pdf(r)
                zf.writestr(f"aviso_{r.get('numero')}.pdf", pdf_bytes)

    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="avisos.zip",
    )
