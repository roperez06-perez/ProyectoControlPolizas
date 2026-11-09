# AGENTS.md — Proyecto Control de Pólizas

## Propósito del proyecto

Proyecto académico de la **Universidad Fundepos — Técnico en IA Empresarial** para el control de pólizas de seguros. El repositorio contiene pólizas ficticias en formato PDF, organizadas por aseguradora y ramo, para ser procesadas con IA (extracción de datos, análisis de vigencia, primas, coberturas, etc.).

> ⚠️ Todas las pólizas son **documentos ficticios con fines académicos**. No contienen datos reales de personas.

---

## Estructura del repositorio

```
Proyecto Control de Polizas/
├── AGENTS.md                 # este archivo (instrucciones para agentes)
├── polizas/                  # pólizas en PDF
│   ├── Poliza_AIS-2026-0001.pdf   # Aseguradora del Istmo S.A. — Automóvil (5)
│   ├── Poliza_PCS-2026-0001.pdf   # Protección Caribe S.A. — Hogar (9)
│   └── Poliza_SPC-2026-0001.pdf   # Seguros Pacífico Central S.A. — Vida (6)
```

### Convención de nombres de archivo

`Poliza_<CODIGO_ASEGURADORA>-<AAAA>-<NNNN>.pdf`

| Código | Aseguradora | Ramo | Cantidad |
|--------|-------------|------|----------|
| `AIS` | Aseguradora del Istmo S.A. | Automóvil | 5 |
| `PCS` | Protección Caribe S.A. | Hogar | 9 |
| `SPC` | Seguros Pacífico Central S.A. | Vida | 6 |

---

## Modelo de datos de cada póliza

Cada PDF contiene los siguientes campos (extraer en este orden):

| Campo | Ejemplo | Notas |
|-------|---------|-------|
| Aseguradora | `Aseguradora del Istmo S.A.` | Nombre completo de la compañía |
| Tipo | `POLIZA DE SEGURO DE AUTOMOVIL` | Automóvil / Hogar / Vida |
| Número de póliza | `AIS-2026-0001` | Coincide con el nombre del archivo |
| Ramo | `Automovil` | `Automovil`, `Hogar` o `Vida` |
| Tomador / Asegurado | `Laura Jimenez Solano` | Nombre de la persona |
| Cédula | `1-0456-0789` | Formato costarricense |
| Vigencia desde | `14/11/2025` | Formato DD/MM/AAAA |
| Vigencia hasta | `14/11/2026` | Formato DD/MM/AAAA |
| Prima anual | `CRC 228,000.00` | Colón costarricense (CRC) |
| Forma de pago | `Anual` | `Anual` o `Mensual` |
| Suma asegurada | `CRC 18,240,000.00` | Monto asegurado en CRC |
| Intermediario | `Corredora de Seguros Horizonte` | Corredora de seguros |
| Asesor | `Karla Umana` | Asesor asignado |
| Coberturas principales | `dano propio, responsabilidad civil...` | Lista de coberturas |

Ejemplo de registro extraído:

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

---

## Cómo leer los PDFs

Este modelo de lenguaje **no puede leer PDFs directamente**. Usa una librería de extracción de texto:

- Python: `pypdf` (`PdfReader(file).pages[0].extract_text()`)
- Shell: `pdftotext` (si está disponible)

Todas las pólizas son de una sola página (`Pagina 1 de 1`).

---

## Tareas comunes para agentes

1. **Inventario de pólizas**: listar todos los archivos en `polizas/` con aseguradora, ramo, número y tomador.
2. **Conteo por ramo / aseguradora**: agrupar pólizas por código de aseguradora o ramo.
3. **Control de vigencia**: identificar pólizas vencidas o por vencerse comparando `vigencia_hasta` con la fecha actual (hoy es 09/11/2026).
4. **Análisis de primas**: sumar primas anuales por ramo, aseguradora o asesor (convertir `CRC X,XXX.00` a número).
5. **Búsqueda por tomador/cédula**: localizar pólizas de un cliente específico.
6. **Reporte de coberturas**: listar coberturas principales por ramo.

---

## Reglas y convenciones

- **No modifiques ni elimines** los PDF originales; son la fuente de verdad del proyecto académico.
- Los archivos se nombran con mayúsculas, guiones bajos y guiones: `Poliza_AIS-2026-0001.pdf`. Mantén esa convención si agregas archivos.
- Las fechas usan formato **DD/MM/AAAA** y las monedas usan **CRC** con separador de miles en coma (ej. `228,000.00`).
- El texto de los PDF está en español; mantén los nombres de campos en español al extraerlos.
- Si generas reportes o código nuevo, documenta el campo de origen de cada dato.

---

## Contexto útil

- Fecha actual: **lunes 09 de noviembre de 2026**.
- Todas las pólizas tienen vigencia de 1 año.
- Intermediario común: `Corredora de Seguros Horizonte`; asesor común: `Karla Umana`.