# AGENTS.md — Proyecto Control de Pólizas

## Repositorio

Solo contiene pólizas ficticias en PDF bajo `polizas/`. **No hay código, build, tests ni CI.** Todo el procesamiento se hace extrayendo texto de los PDF con IA.

- `polizas/` — 20 PDFs de una sola página.
- `.gitignore` ignora `.polizas_cache/` y `*.log`: guarda ahí los datos extraídos; no confirmes nada dentro del repo.

## Nombrado de archivos

`Poliza_<CODIGO>-<AAAA>-<NNNN>.pdf`

| Código | Aseguradora | Ramo | Cantidad |
|--------|-------------|------|----------|
| AIS | Aseguradora del Istmo S.A. | Automóvil | 5 |
| PCS | Protección Caribe S.A. | Hogar | 9 |
| SPC | Seguros Pacífico Central S.A. | Vida | 6 |

## Modelo de datos (extraer en este orden)

`archivo, aseguradora, tipo, numero_poliza, ramo, tomador, cedula, vigencia_desde, vigencia_hasta, prima_anual, forma_pago, suma_asegurada, intermediario, asesor, coberturas` (lista).

Ejemplo:

```json
{
  "archivo": "polizas/Poliza_AIS-2026-0001.pdf",
  "aseguradora": "Aseguradora del Istmo S.A.",
  "tipo": "POLIZA DE SEGURO DE AUTOMOVIL",
  "numero_poliza": "AIS-2026-0001",
  "ramo": "Automovil",
  "tomador": "Laura Jimenez Solano",
  "cedula": "1-0456-0789",
  "vigencia_desde": "14/11/2025",
  "vigencia_hasta": "14/11/2026",
  "prima_anual": "CRC 228,000.00",
  "forma_pago": "Anual",
  "suma_asegurada": "CRC 18,240,000.00",
  "intermediario": "Corredora de Seguros Horizonte",
  "asesor": "Karla Umana",
  "coberturas": ["dano propio", "responsabilidad civil", "asistencia en carretera"]
}
```

## Leer PDFs

Este modelo **no lee PDFs directamente**. Usa `pypdf` (`PdfReader(file).pages[0].extract_text()`) o `pdftotext`. Cada póliza tiene una sola página.

## Reglas

- No modifiques ni elimines los PDF originales; son la fuente de verdad.
- Fechas: DD/MM/AAAA. Monedas: CRC con miles en coma (ej. `228,000.00`).
- Texto en español; nombres de campo en español.
- Intermediario siempre `Corredora de Seguros Horizonte`. El asesor **varía** (`Karla Umana`, `Diego Chaves`, `Mariana Solis`) — no asumas uno único.

## Vigencia (fecha de referencia: 09/11/2026)

Compara `vigencia_hasta` con la fecha actual para detectar pólizas vencidas o por vencerse. Algunas ya vencieron antes de 09/11/2026 (ej. `AIS-2026-0005` hasta 26/08/2026, `PCS-2026-0009` hasta 05/09/2026).
