# Proyecto Control de Pólizas

Aplicación Flask para el control de pólizas de seguros (vigencia, primas, avisos de renovación).

## Tecnología

- Python 3.12
- Flask, pandas, openpyxl, pdfplumber, fpdf2
- Gestor de paquetes: `uv`

## Despliegue en Render

1. Conecta este repositorio a Render como un servicio Web.
2. Build command: `uv sync --frozen`
3. Start command: `uv run app.py`
4. Añade la variable de entorno `PORT` si Render la requiere (Flask usa 5000 por defecto).

## Desarrollo local

```bash
uv sync
uv run app.py
```

La app corre en `http://127.0.0.1:5000`.

## Estructura

- `data/` — bodega de entrada (Maestro_Clientes.xlsx, polizas/ PDFs) — solo lectura
- `models/datos.py` — lectura de archivos
- `models/polizas.py` — reglas del negocio
- `services/generador_aviso.py` — generación de PDF de aviso
- `controllers/polizas_controller.py` — rutas Flask
- `views/` — plantillas HTML
- `public/static/estilos.css` — estilos
- `app.py` — punto de entrada Flask
