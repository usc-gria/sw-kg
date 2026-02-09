# Práctica: Data Preparation con OpenRefine (LOT4KG)

En esta práctica vais a realizar el paso de Data Preparation de la metodología LOT4KG, cuyo objetivo es transformar un dataset “tal cual” en una fuente de datos preparada (prepared data source) lista para su uso posterior (p. ej., en el mapeo a RDF).  ￼

## Objetivo

A partir de vuestro propio dataset (CSV/TSV/JSON/Excel…), debéis:
1. Importarlo en OpenRefine.
2. Analizar su calidad (valores nulos, inconsistencias, duplicados, formatos).
3. Limpiarlo y normalizarlo (transformaciones, clustering, filtrado, tipado básico…).
4. Exportar:
   1. el dataset limpio (CSV o el formato acordado), y
   2. el JSON de operaciones de OpenRefine (el historial de pasos reproducible).


## Requisitos y entrega

Debéis entregar en vuestra carpeta del repositorio:
- data/raw_nombre_archivo.csv --> Dataset original (o un enlace si es muy grande, pero incluid al menos una muestra).
- data/clean_nombre_archivo.csv --> Dataset limpio (por ejemplo clean.csv).
- openrefine/operations.json --> JSON exportado desde OpenRefine con todas las operaciones aplicadas (historial).



## Flujo de trabajo


### 1) Importación en OpenRefine
- Crear proyecto e importar el dataset (CSV/TSV/JSON/Excel…).
- Revisar que OpenRefine detecta bien separadores, cabeceras y tipos.

### 2) Exploración de calidad

Usad Facets / Filters para inspeccionar:
- valores vacíos / nulos,
- valores más frecuentes,
- outliers numéricos,
- inconsistencias tipográficas (mayúsculas/minúsculas, abreviaturas),
- duplicados.

### 3) Limpieza y normalización

Aplicad transformaciones típicas (según vuestro dataset):
- Trim / espacios: eliminar espacios al inicio/final.
- Normalización de mayúsculas/minúsculas (por ejemplo, títulos en formato “Title Case”, códigos en mayúsculas…).
- Reemplazos (valores inconsistentes: “USA”, “U.S.A.” → “US”).
- Separación o combinación de columnas (split/join si hay campos compuestos).
- Conversión de tipos (números, fechas, etc.).
- Clustering para unificar variantes tipográficas (muy útil para nombres/categorías).  ￼

### 4) Reconciliation

Si vuestro dataset tiene entidades textuales (p. ej., ciudades, países, barrios, organizaciones…), debéis usar Reconcile para enlazarlas contra un servicio (p. ej., Wikidata). Si lo hacéis:
- indicad qué columna reconciliasteis,
- qué porcentaje quedó “matched”,
- añadir una columna con el identificador/URL resultante.

### 5) Exportación del dataset limpio


### 6) Exportación del JSON de operaciones (obligatorio)

Exportad el historial de operaciones para que sea reproducible: En OpenRefine: Undo / Redo → Extract… (o “Export” del historial según versión)

