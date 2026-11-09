"""Generador de avisos de renovación de pólizas en PDF.

Usa fpdf2 para crear un documento A4 vertical y devolverlo en bytes.
"""

from datetime import date

from fpdf import FPDF

from models.polizas import estado_poliza, FECHA_CORTE

# Colores (rojo #AE1800 para la banda, gris para el pie de pagina)
ROJO = (174, 24, 0)
GRIS = (128, 128, 128)
NEGRO = (0, 0, 0)

ANCHO_PAGE = 210  # mm (A4 vertical)
ALTO_PAGE = 297   # mm


def _latin1(texto):
    """Convierte texto a latin-1 para que las tildes no fallen con Helvetica."""
    if texto is None:
        return ""
    return str(texto).encode("latin-1", errors="replace").decode("latin-1")


def _fecha_str(fecha):
    """Convierte date a 'dd/mm/aaaa' o devuelve 'No registrada'."""
    if fecha is None:
        return "No registrada"
    return fecha.strftime("%d/%m/%Y")


def _vigencia_str(desde, hasta):
    """Devuelve el rango de vigencia 'desde al hasta' o 'No registrada'."""
    if desde is None or hasta is None:
        return "No registrada"
    return f"{_fecha_str(desde)} al {_fecha_str(hasta)}"


def _moneda_str(valor):
    """Convierte monto a 'CRC 228,000.00' o 'No registrada'."""
    if valor is None:
        return "No registrada"
    return f"CRC {valor:,.2f}"


def crear_aviso_pdf(poliza):
    """Crea un aviso de renovación en PDF (A4 vertical) y lo devuelve en bytes.

    Recibe un diccionario de póliza (como los que devuelven models.datos y
    models.polizas) y genera el PDF con:
      - banda superior roja con la corredora y el título
      - saludo Estimado(a) {nombre}
      - párrafo distinto si está Vencida o Por vencer
      - tabla con los datos de la póliza
      - pie de página en gris (documento ficticio académico)
    """
    desde = poliza.get("desde")
    hasta = poliza.get("hasta")
    estado = estado_poliza(hasta)
    if hasta is not None:
        dias = (hasta - FECHA_CORTE).days
    else:
        dias = None

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    pdf.set_text_color(*NEGRO)

    # --- Banda superior roja ---
    pdf.set_fill_color(*ROJO)
    pdf.rect(0, 0, ANCHO_PAGE, 28, style="F")
    pdf.set_text_color(255, 255, 255)  # texto blanco sobre rojo
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_xy(12, 7)
    pdf.cell(0, 7, _latin1("Corredora de Seguros Horizonte"), ln=1)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 7, _latin1("Aviso de renovación de póliza"), ln=1)

    # --- Cuerpo del aviso ---
    pdf.set_text_color(*NEGRO)
    pdf.set_y(40)
    pdf.set_font("Helvetica", "", 11)

    nombre = poliza.get("nombre") or "cliente"
    pdf.cell(0, 7, _latin1(f"Estimado(a) {nombre}:"), ln=1)
    pdf.ln(4)

    # Párrafo distinto según estado
    if estado == "Vencida":
        texto_estado = (
            f"Esta póliza venció el {_fecha_str(hasta)}. "
            "Comuníquese con su asesor para renovarla."
        )
    elif estado == "Por vencer":
        texto_estado = (
            f"Esta póliza vence el {_fecha_str(hasta)} en {dias} días. "
            "Su asesor se comunicará con usted próximamente."
        )
    else:
        texto_estado = (
            f"Esta póliza está vigente hasta el {_fecha_str(hasta)}."
        )

    pdf.multi_cell(0, 6, _latin1(texto_estado))
    pdf.ln(6)

    # --- Tabla de datos ---
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(230, 230, 230)  # gris claro para encabezado
    pdf.cell(55, 7, _latin1("Concepto"), border=1, fill=True)
    pdf.cell(115, 7, _latin1("Valor"), border=1, fill=True, ln=1)

    pdf.set_font("Helvetica", "", 10)
    filas = [
        ("Número de póliza", poliza.get("numero") or "No registrada"),
        ("Aseguradora", poliza.get("aseguradora") or "No registrada"),
        ("Ramo", poliza.get("ramo") or "No registrada"),
        ("Cédula", poliza.get("cedula") or "No registrada"),
        ("Vigencia", _vigencia_str(desde, hasta)),
        ("Prima anual", _moneda_str(poliza.get("prima"))),
        ("Forma de pago", poliza.get("pago") or "No registrada"),
    ]
    for concepto, valor in filas:
        pdf.cell(55, 7, _latin1(concepto), border=1)
        pdf.cell(115, 7, _latin1(valor), border=1, ln=1)

    pdf.ln(10)

    # --- Pie de página en gris ---
    pdf.set_y(ALTO_PAGE - 15)
    pdf.set_text_color(*GRIS)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(
        0,
        6,
        _latin1("Documento ficticio con fines académicos. No contiene datos reales de personas."),
        align="C",
    )

    # Devolver bytes
    return pdf.output()
