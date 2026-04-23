from __future__ import annotations

import html
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
QUERY_RESULTS_DIR = ROOT / "results" / "query_results"
DATASET_PATH = ROOT / "data cleaning" / "teatros-auditorios.csv"
QUERIES_DIR = ROOT / "queries"
README_PATH = ROOT / "README.md"
KG_TRIPLES = 884
OWL_SAMEAS = 44
MAP_SELECTION_KEY = "centers_map_chart"

PROVINCE_HEX = {
    "A Coruña": "#63a4ff",
    "Pontevedra": "#52d6b7",
    "Lugo": "#ff8b6b",
    "Ourense": "#f4c46a",
}

PROVINCE_COLORS = {
    "A Coruña": [39, 92, 148, 190],
    "Pontevedra": [70, 150, 130, 190],
    "Lugo": [227, 111, 81, 190],
    "Ourense": [214, 169, 78, 190],
}

QUERY_OPTIONS = {
    "local_query_1.csv": {
        "label": "Consulta local 1: espacios por provincia",
        "description": "Cuenta cuantos espacios culturales hay en cada provincia del KG local.",
        "query_file": "local_query_1.rq",
    },
    "local_query_2.csv": {
        "label": "Consulta local 2: estadisticas por municipio",
        "description": "Resume numero de espacios y aforo medio por concello enlazado con Wikidata.",
        "query_file": "local_query_2.rq",
    },
    "local_query_3.csv": {
        "label": "Consulta local 3: ranking por aforo",
        "description": "Muestra los espacios con mayor capacidad dentro del KG local.",
        "query_file": "local_query_3.rq",
    },
    "local_query_4.csv": {
        "label": "Consulta local 4: provincias enlazadas",
        "description": "Lista provincias con su owl:sameAs a Wikidata y el numero de espacios asociados.",
        "query_file": "local_query_4.rq",
    },
    "municipalities_enriched.csv": {
        "label": "Municipios enriquecidos",
        "description": "Fusiona resultados locales con poblacion, coordenadas y web oficial recuperadas desde Wikidata.",
        "query_file": "federated_query_1.rq",
    },
    "provinces_enriched.csv": {
        "label": "Provincias enriquecidas",
        "description": "Combina el KG local con poblacion, area y capital de cada provincia enlazada con Wikidata.",
        "query_file": "federated_query_2.rq",
    },
}


def normalize_text(series: pd.Series) -> pd.Series:
    return (
        series.fillna("")
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


def clean_province_name(value: object) -> str:
    text = "" if pd.isna(value) else str(value).strip()
    return text.removesuffix(" Province")


def read_required_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run `python3 src/run_queries.py` first.")
    return pd.read_csv(path)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
          :root, html, body, [data-testid="stAppViewContainer"] {
            color-scheme: dark !important;
          }
          html, body, [class*="css"] {
            font-family: "Space Grotesk", "Segoe UI", sans-serif;
          }
          .stApp {
            color: #e8eefc;
            background:
              radial-gradient(circle at top left, rgba(82, 214, 183, 0.10), transparent 22%),
              radial-gradient(circle at 86% 10%, rgba(255, 155, 113, 0.08), transparent 16%),
              linear-gradient(180deg, #09111d 0%, #0c1422 44%, #0f1727 100%);
          }
          [data-testid="stAppViewContainer"] {
            background: transparent;
          }
          .block-container {
            padding-top: 2.55rem;
            max-width: 1360px;
          }
          [data-testid="stHeader"] {
            display: block;
            background: rgba(7, 14, 24, 0.72);
            backdrop-filter: blur(14px);
            border-bottom: 1px solid rgba(141, 183, 255, 0.08);
          }
          [data-testid="stToolbar"] {
            display: flex !important;
          }
          [data-testid="stHeader"] *,
          [data-testid="stToolbar"] * {
            color: #d8e5fb !important;
          }
          footer {
            display: none !important;
          }
          [data-testid="stSidebar"] {
            background:
              linear-gradient(180deg, rgba(9, 18, 33, 0.98) 0%, rgba(11, 21, 37, 0.98) 100%);
            border-right: 1px solid rgba(141, 183, 255, 0.08);
          }
          .stApp p,
          .stApp label,
          .stApp span,
          .stApp h1,
          .stApp h2,
          .stApp h3 {
            color: #e8eefc;
          }
          .hero-panel,
          .hero-panel *,
          .hero-badge {
            color: white !important;
          }
          [data-testid="stMetric"] {
            background:
              linear-gradient(180deg, rgba(17, 28, 45, 0.92) 0%, rgba(12, 20, 34, 0.94) 100%);
            border: 1px solid rgba(141, 183, 255, 0.10);
            border-radius: 20px;
            padding: 14px 16px;
            box-shadow: 0 20px 40px rgba(2, 6, 12, 0.26);
          }
          [data-testid="stMetricLabel"] *,
          [data-testid="stMetricValue"] *,
          [data-testid="stMetricDelta"] * {
            color: #e8eefc !important;
          }
          [data-testid="stMetricLabel"] p {
            color: #93a9c8 !important;
            font-size: 0.9rem !important;
          }
          [data-testid="stMetricValue"] div {
            font-size: 2rem !important;
            font-weight: 700 !important;
          }
          div[data-baseweb="tab-list"] {
            gap: 8px;
            background: transparent;
          }
          button[data-baseweb="tab"] {
            border-radius: 999px;
            padding-left: 18px;
            padding-right: 18px;
            min-height: 42px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(141, 183, 255, 0.08);
          }
          button[data-baseweb="tab"] p {
            color: #8ea5c4 !important;
            font-weight: 500;
          }
          button[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, rgba(82, 214, 183, 0.18), rgba(27, 76, 103, 0.22)) !important;
            border-color: rgba(82, 214, 183, 0.26);
            box-shadow: 0 14px 28px rgba(5, 10, 18, 0.30);
          }
          button[data-baseweb="tab"][aria-selected="true"] p {
            color: #f5f8ff !important;
            font-weight: 700;
          }
          [data-testid="stMarkdownContainer"] code {
            color: #9fe7d8;
            background: rgba(82, 214, 183, 0.10);
            border-radius: 8px;
            padding: 0.12rem 0.4rem;
          }
          .stSidebar label,
          .stSidebar p,
          .stSidebar span,
          .stSidebar [data-testid="stMarkdownContainer"] * {
            color: #9fb4d1 !important;
          }
          .stSidebar [data-baseweb="select"] *,
          .stSidebar input,
          .stSidebar textarea {
            color: #edf3ff !important;
          }
          .stSidebar [data-baseweb="base-input"],
          .stSidebar [data-baseweb="select"] > div,
          .stSidebar .stTextInput > div > div,
          .stSidebar .stCodeBlock {
            background: rgba(17, 29, 49, 0.94) !important;
            border: 1px solid rgba(141, 183, 255, 0.10) !important;
            box-shadow: none !important;
          }
          .stSidebar [data-testid="stHeader"] * {
            color: #e8eefc !important;
          }
          .stSidebar .stSlider {
            margin-top: 0.15rem;
            margin-bottom: 0.8rem;
          }
          .stSidebar .stSlider > div[data-baseweb="slider"] {
            padding: 0 !important;
            border: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
          }
          .stSidebar .stSlider [role="slider"] {
            box-shadow: 0 0 0 4px rgba(255, 99, 99, 0.14);
          }
          .stSidebar .stSlider [data-testid="stTickBarMin"],
          .stSidebar .stSlider [data-testid="stTickBarMax"],
          .stSidebar .stSlider p {
            color: #b8c8df !important;
          }
          .stDataFrame, .stTable {
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(141, 183, 255, 0.08);
            box-shadow: 0 18px 34px rgba(2, 6, 12, 0.22);
          }
          [data-testid="stPlotlyChart"] {
            background: linear-gradient(180deg, rgba(18, 28, 46, 0.90), rgba(12, 20, 34, 0.94));
            border: 1px solid rgba(141, 183, 255, 0.08);
            border-radius: 20px;
            padding: 10px 10px 2px 10px;
            box-shadow: 0 18px 34px rgba(2, 6, 12, 0.24);
          }
          .section-note,
          .section-note *,
          .section-note strong {
            color: #e8eefc !important;
          }
          .hero-panel {
            background:
              radial-gradient(circle at 88% 18%, rgba(82, 214, 183, 0.10), transparent 24%),
              linear-gradient(135deg, #11182a 0%, #162235 42%, #19334a 100%);
            color: white;
            border: 1px solid rgba(141, 183, 255, 0.12);
            border-radius: 28px;
            padding: 28px 30px 24px;
            margin-top: 0.1rem;
            margin-bottom: 18px;
            box-shadow: 0 28px 60px rgba(2, 6, 12, 0.34);
          }
          .hero-eyebrow {
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-size: 0.76rem;
            color: rgba(255,255,255,0.72);
            margin-bottom: 10px;
          }
          .hero-title {
            font-size: 2.2rem;
            line-height: 1.02;
            font-weight: 700;
            margin: 0 0 10px 0;
          }
          .hero-copy {
            font-size: 1rem;
            color: rgba(255,255,255,0.88);
            max-width: 860px;
            margin-bottom: 16px;
          }
          .hero-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
          }
          .hero-badge {
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.16);
            border-radius: 999px;
            padding: 8px 12px;
            font-size: 0.92rem;
          }
          .section-note {
            background: linear-gradient(180deg, rgba(15, 28, 48, 0.92), rgba(11, 21, 37, 0.92));
            border: 1px solid rgba(141, 183, 255, 0.10);
            border-radius: 16px;
            padding: 12px 14px;
            margin-bottom: 12px;
            box-shadow: 0 16px 30px rgba(2, 6, 12, 0.22);
          }
          .section-note strong {
            color: #e8eefc;
          }
          .compact-note {
            color: #9fb1ca !important;
            margin: 0.35rem 0 0.55rem 0.05rem;
            font-size: 0.92rem;
          }
          .kg-table-card {
            background: linear-gradient(180deg, rgba(17, 28, 45, 0.92), rgba(12, 20, 34, 0.94));
            border: 1px solid rgba(141, 183, 255, 0.08);
            border-radius: 18px;
            box-shadow: 0 18px 34px rgba(2, 6, 12, 0.22);
            overflow: hidden;
          }
          .kg-table-scroll {
            overflow: auto;
            position: relative;
            isolation: isolate;
          }
          .kg-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
          }
          .kg-table thead th {
            position: sticky;
            top: 0;
            z-index: 12;
            text-align: left;
            padding: 11px 12px;
            background: linear-gradient(180deg, rgba(31, 43, 64, 0.98), rgba(23, 33, 51, 0.98));
            color: #b6c8e1;
            font-weight: 600;
            border-bottom: 1px solid rgba(141, 183, 255, 0.08);
            box-shadow: 0 8px 18px rgba(2, 6, 12, 0.32);
            white-space: nowrap;
          }
          .kg-table tbody td {
            position: relative;
            z-index: 1;
            padding: 11px 12px;
            border-bottom: 1px solid rgba(141, 183, 255, 0.06);
            color: #edf3ff;
            vertical-align: top;
            white-space: nowrap;
          }
          .kg-table tbody tr:nth-child(even) td {
            background: rgba(255, 255, 255, 0.015);
          }
          .kg-table tbody tr:hover td {
            background: rgba(82, 214, 183, 0.07);
          }
          .kg-table a,
          .selected-center-links a {
            color: #9fe7d8 !important;
            text-decoration: none;
          }
          .kg-table a:hover,
          .selected-center-links a:hover {
            text-decoration: underline;
          }
          .kg-link-stack,
          .selected-center-links {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
          }
          .kg-link-pill,
          .selected-center-link {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.32rem 0.6rem;
            border-radius: 999px;
            background: rgba(82, 214, 183, 0.10);
            border: 1px solid rgba(82, 214, 183, 0.16);
            color: #dffaf3 !important;
            line-height: 1.1;
            font-size: 0.86rem;
            max-width: 100%;
          }
          .selected-center-card {
            background:
              radial-gradient(circle at top right, rgba(99, 164, 255, 0.10), transparent 24%),
              linear-gradient(180deg, rgba(17, 28, 45, 0.94), rgba(12, 20, 34, 0.96));
            border: 1px solid rgba(141, 183, 255, 0.10);
            border-radius: 20px;
            padding: 18px 18px 16px;
            box-shadow: 0 18px 34px rgba(2, 6, 12, 0.22);
          }
          .selected-center-eyebrow {
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.72rem;
            color: #8ea5c4 !important;
            margin-bottom: 0.45rem;
          }
          .selected-center-title {
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
          }
          .selected-center-subtitle {
            color: #a9bdd9 !important;
            margin-bottom: 1rem;
          }
          .selected-center-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 0.85rem;
            margin-bottom: 1rem;
          }
          .selected-center-item {
            padding: 0.7rem 0.8rem;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid rgba(141, 183, 255, 0.08);
            min-width: 0;
            overflow: hidden;
          }
          .selected-center-label {
            display: block;
            font-size: 0.76rem;
            color: #8ea5c4 !important;
            margin-bottom: 0.35rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
          }
          .selected-center-value {
            color: #edf3ff !important;
            font-weight: 600;
            min-width: 0;
            overflow: hidden;
          }
          .selected-center-value .kg-link-pill,
          .selected-center-value .selected-center-link {
            max-width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
          .stRadio > div {
            gap: 0.4rem;
          }
          @media (max-width: 980px) {
            .block-container {
              padding-top: 1.35rem;
              padding-left: 1rem;
              padding-right: 1rem;
            }
            .hero-panel {
              padding: 22px 20px 18px;
              border-radius: 22px;
            }
            .hero-title {
              font-size: 1.7rem;
            }
            div[data-baseweb="tab-list"] {
              flex-wrap: wrap;
            }
            button[data-baseweb="tab"] {
              flex: 1 1 calc(50% - 8px);
              justify-content: center;
            }
            [data-testid="stPlotlyChart"] {
              padding: 8px 8px 0 8px;
            }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(municipalities: pd.DataFrame, provinces: pd.DataFrame) -> None:
    st.markdown(
        f"""
        <section class="hero-panel">
          <div class="hero-eyebrow">Demo Semantic Web + Knowledge Graph</div>
          <h1 class="hero-title">Pezapa KG Explorer</h1>
          <div class="hero-copy">
            Explora el KG de teatros y auditorios de Galicia con una interfaz ligera:
            mapa interactivo de centros, resultados SPARQL legibles, detalle por concello
            y una vista clara de las limitaciones detectadas en validación.
          </div>
          <div class="hero-badges">
            <span class="hero-badge">46 filas limpias</span>
            <span class="hero-badge">{KG_TRIPLES} triples en el KG</span>
            <span class="hero-badge">{len(municipalities)} concellos enriquecidos</span>
            <span class="hero-badge">{len(provinces)} provincias enriquecidas</span>
            <span class="hero-badge">{OWL_SAMEAS} enlaces owl:sameAs</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_quality_summary() -> tuple[pd.DataFrame, dict[str, int]]:
    dataframe = pd.read_csv(DATASET_PATH)
    dataframe["ESPAZO"] = normalize_text(dataframe["ESPAZO"])
    dataframe["CONCELLO"] = normalize_text(dataframe["CONCELLO"])
    dataframe["PROVINCIA"] = normalize_text(dataframe["PROVINCIA"])

    duplicates = (
        dataframe.groupby("ESPAZO", dropna=False)
        .agg(
            filas=("ESPAZO", "size"),
            concellos=("CONCELLO", lambda values: " | ".join(sorted(set(values)))),
            provincias=("PROVINCIA", lambda values: " | ".join(sorted(set(values)))),
            aforo_medio=("AFORAMENTO", "mean"),
        )
        .reset_index()
    )
    duplicates = duplicates[duplicates["filas"] > 1].rename(columns={"ESPAZO": "espazo"})

    readme_text = README_PATH.read_text(encoding="utf-8")
    counts = {"data": 22, "model": 111}
    if "`22` resultados en el resumen textual de pySHACL" not in readme_text:
        counts["data"] = 22
    if "`111` resultados en el resumen textual de pySHACL" not in readme_text:
        counts["model"] = 111

    return duplicates, counts


@st.cache_data(show_spinner=False)
def load_centers() -> pd.DataFrame:
    dataframe = pd.read_csv(DATASET_PATH).rename(
        columns={
            "ESPAZO": "espazo",
            "URL_ESPAZO": "wikidata_espazo",
            "ENDEREZO": "enderezo",
            "NUMERO": "numero",
            "CÓDIGO POSTAL": "codigo_postal",
            "CONCELLO": "concello",
            "URL_CONCELLO": "wikidata_concello",
            "PROVINCIA": "provincia",
            "URL_PROVINCIA": "wikidata_provincia",
            "TELÉFONO": "telefono",
            "E-MAIL": "email",
            "AFORAMENTO": "aforamento",
            "WEB": "web",
            "LATITUD": "latitud",
            "LONGUITUD": "longitud",
        }
    )

    for column in ("espazo", "enderezo", "concello", "provincia", "telefono", "email", "web"):
        dataframe[column] = normalize_text(dataframe[column])

    dataframe["provincia_ui"] = dataframe["provincia"].map(clean_province_name)
    dataframe["aforamento"] = pd.to_numeric(dataframe["aforamento"], errors="coerce")
    dataframe["latitud"] = pd.to_numeric(dataframe["latitud"], errors="coerce")
    dataframe["longitud"] = pd.to_numeric(dataframe["longitud"], errors="coerce")
    default_capacity = dataframe["aforamento"].dropna().median()
    dataframe["marker_radius"] = (
        dataframe["aforamento"].fillna(default_capacity if pd.notna(default_capacity) else 200)
        .clip(lower=120, upper=900)
        .mul(2.8)
    )
    dataframe["web_display"] = dataframe["web"].replace("", "No disponible")
    dataframe["telefono_display"] = dataframe["telefono"].replace("", "No disponible")
    dataframe["email_display"] = dataframe["email"].replace("", "No disponible")
    dataframe["fill_color"] = dataframe["provincia_ui"].map(
        lambda name: PROVINCE_COLORS.get(name, [39, 92, 148, 190])
    )
    dataframe["marker_hex"] = dataframe["provincia_ui"].map(
        lambda name: PROVINCE_HEX.get(name, "#63a4ff")
    )
    dataframe["constant_radius"] = 240
    dataframe["point_id"] = range(len(dataframe))
    return dataframe


@st.cache_data(show_spinner=False)
def load_enriched_municipalities() -> pd.DataFrame:
    dataframe = read_required_csv(QUERY_RESULTS_DIR / "municipalities_enriched.csv")
    dataframe["provinceDisplay"] = dataframe["provinceName"].map(clean_province_name)
    dataframe["municipalityName"] = normalize_text(dataframe["municipalityName"])
    dataframe["numSpaces"] = pd.to_numeric(dataframe["numSpaces"], errors="coerce")
    dataframe["avgCapacity"] = pd.to_numeric(dataframe["avgCapacity"], errors="coerce")
    dataframe["spacesPer100k"] = pd.to_numeric(dataframe["spacesPer100k"], errors="coerce")
    return dataframe


@st.cache_data(show_spinner=False)
def load_enriched_provinces() -> pd.DataFrame:
    dataframe = read_required_csv(QUERY_RESULTS_DIR / "provinces_enriched.csv")
    dataframe["provinceDisplay"] = dataframe["provinceName"].map(clean_province_name)
    dataframe["numSpaces"] = pd.to_numeric(dataframe["numSpaces"], errors="coerce")
    dataframe["spacesPerMillion"] = pd.to_numeric(dataframe["spacesPerMillion"], errors="coerce")
    return dataframe


@st.cache_data(show_spinner=False)
def load_query_output(filename: str) -> pd.DataFrame:
    dataframe = read_required_csv(QUERY_RESULTS_DIR / filename)

    if "provinceName" in dataframe.columns:
        dataframe["provinceDisplay"] = dataframe["provinceName"].map(clean_province_name)
    if "municipalityName" in dataframe.columns:
        dataframe["municipalityName"] = normalize_text(dataframe["municipalityName"])
    if "spaceName" in dataframe.columns:
        dataframe["spaceName"] = normalize_text(dataframe["spaceName"])

    return dataframe


def filter_centers(
    centers: pd.DataFrame,
    province: str,
    municipality: str,
    min_capacity: int,
    search: str,
) -> pd.DataFrame:
    filtered = centers.copy()

    if province != "Todas":
        filtered = filtered[filtered["provincia_ui"] == province]
    if municipality != "Todos":
        filtered = filtered[filtered["concello"] == municipality]
    if min_capacity > 0:
        filtered = filtered[filtered["aforamento"].fillna(0) >= min_capacity]
    if search.strip():
        filtered = filtered[
            filtered["espazo"].str.contains(search.strip(), case=False, na=False)
        ]

    return filtered


def build_map_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    valid = dataframe.dropna(subset=["latitud", "longitud"]).copy()
    if valid.empty:
        return valid

    valid["aforamento_label"] = (
        valid["aforamento"].round(0).fillna(0).astype(int).astype(str)
    )
    return valid


def scale_marker_sizes(points: pd.DataFrame, size_mode: str) -> pd.Series:
    if size_mode != "Aforo":
        return pd.Series([14.0] * len(points), index=points.index)

    capacity = pd.to_numeric(points["aforamento"], errors="coerce")
    fallback = capacity.dropna().median()
    scaled = capacity.fillna(fallback if pd.notna(fallback) else 300).clip(lower=120, upper=900)
    min_value = float(scaled.min())
    max_value = float(scaled.max())

    if abs(max_value - min_value) < 1e-9:
        return pd.Series([18.0] * len(points), index=points.index)

    return 12 + ((scaled - min_value) / (max_value - min_value)) * 14


def extract_selected_point_id(selection_state: object) -> int | None:
    if not selection_state:
        return None

    selection = getattr(selection_state, "selection", selection_state)
    if not hasattr(selection, "get"):
        return None

    points = selection.get("points", [])
    if not points:
        return None

    selected = points[-1]
    customdata = selected.get("customdata") or []
    if customdata:
        try:
            return int(customdata[0])
        except (TypeError, ValueError):
            return None

    point_index = selected.get("point_index")
    if point_index is None:
        return None

    try:
        return int(point_index)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# MAP — Scattermapbox with real Carto tiles (no Mapbox token needed)
# ---------------------------------------------------------------------------

_MAPBOX_STYLES = {
    "dark": "carto-darkmatter",
    "light": "carto-positron",
}


def build_map_figure(
    points: pd.DataFrame,
    map_style: str,
    size_mode: str,
    selected_point_id: int | None = None,
) -> go.Figure:
    """Return a Plotly figure using Scattermapbox so real map tiles are shown."""
    points = build_map_dataframe(points)
    if points.empty:
        return go.Figure()

    marker_sizes = scale_marker_sizes(points, size_mode)
    mapbox_style = _MAPBOX_STYLES.get(map_style, "carto-darkmatter")

    # Build customdata matrix with all columns needed for hover
    customdata_cols = points[
        ["point_id", "concello", "provincia_ui", "aforamento_label", "telefono_display", "web_display"]
    ].to_numpy()

    figure = go.Figure()

    # Main scatter trace
    figure.add_trace(
        go.Scattermapbox(
            lat=points["latitud"],
            lon=points["longitud"],
            mode="markers",
            customdata=customdata_cols,
            marker=go.scattermapbox.Marker(
                size=marker_sizes,
                color=points["marker_hex"],
                opacity=0.90,
            ),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Concello: %{customdata[1]}<br>"
                "Provincia: %{customdata[2]}<br>"
                "Aforo: %{customdata[3]}<br>"
                "Teléfono: %{customdata[4]}<br>"
                "Web: %{customdata[5]}<extra></extra>"
            ),
            text=points["espazo"],
            showlegend=False,
        )
    )

    # Selection ring overlay
    selected_row = points[points["point_id"] == selected_point_id]
    if not selected_row.empty:
        sel_size = float(scale_marker_sizes(selected_row, size_mode).iloc[0]) + 10
        figure.add_trace(
            go.Scattermapbox(
                lat=selected_row["latitud"],
                lon=selected_row["longitud"],
                mode="markers",
                marker=go.scattermapbox.Marker(
                    size=sel_size,
                    color="rgba(255,255,255,0.0)",
                    opacity=1.0,
                    allowoverlap=True,
                ),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        # White ring via a second trace with larger outline circle
        figure.add_trace(
            go.Scattermapbox(
                lat=selected_row["latitud"],
                lon=selected_row["longitud"],
                mode="markers",
                marker=go.scattermapbox.Marker(
                    size=sel_size + 6,
                    color="rgba(255,255,255,0.0)",
                    opacity=1.0,
                    allowoverlap=True,
                ),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # Compute center
    center_lat = float(points["latitud"].mean())
    center_lon = float(points["longitud"].mean())

    figure.update_layout(
        height=470,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        clickmode="event+select",
        uirevision="centers-map",
        mapbox=dict(
            style=mapbox_style,
            center=dict(lat=center_lat, lon=center_lon),
            zoom=7,
        ),
    )

    return figure


def to_csv_bytes(dataframe: pd.DataFrame) -> bytes:
    return dataframe.to_csv(index=False).encode("utf-8")


def format_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        if abs(value - round(value)) < 1e-9:
            return str(int(round(value)))
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def link_label(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.replace("www.", "")
    if "wikidata.org" in host:
        entity = parsed.path.rstrip("/").split("/")[-1]
        return f"Wikidata {entity}" if entity else "Wikidata"
    return host or url


def build_link_pill(url: str, label: str | None = None, css_class: str = "kg-link-pill") -> str:
    safe_url = html.escape(url, quote=True)
    safe_label = html.escape(label or link_label(url))
    return (
        f'<a class="{css_class}" href="{safe_url}" title="{safe_url}" target="_blank" rel="noopener noreferrer">'
        f"{safe_label}</a>"
    )


def format_table_cell_html(value: object) -> str:
    text = format_cell(value).strip()
    if not text:
        return ""

    if " | " in text:
        parts = [part.strip() for part in text.split(" | ") if part.strip()]
        if parts and all(part.startswith(("http://", "https://")) for part in parts):
            return '<div class="kg-link-stack">' + "".join(build_link_pill(part) for part in parts) + "</div>"

    if text.startswith(("http://", "https://")):
        return build_link_pill(text)

    if "@" in text and " " not in text:
        safe_text = html.escape(text)
        return (
            f'<a class="kg-link-pill" href="mailto:{safe_text}" title="{safe_text}" target="_blank" rel="noopener noreferrer">'
            f"{safe_text}</a>"
        )

    return html.escape(text)


def render_selected_center_card(center: pd.Series) -> None:
    details = [
        ("Concello", center.get("concello") or "N/D"),
        ("Provincia", center.get("provincia_ui") or "N/D"),
        ("Aforo", center.get("aforamento_label") or "N/D"),
        ("Telefono", center.get("telefono_display") or "N/D"),
        ("Email", center.get("email_display") or "N/D"),
        ("Enderezo", center.get("enderezo") or "N/D"),
    ]
    detail_html = "".join(
        (
            '<div class="selected-center-item">'
            f'<span class="selected-center-label">{html.escape(label)}</span>'
            f'<div class="selected-center-value">{format_table_cell_html(value)}</div>'
            "</div>"
        )
        for label, value in details
    )

    links: list[str] = []
    for label, url in (
        ("Wikidata espazo", center.get("wikidata_espazo")),
        ("Wikidata concello", center.get("wikidata_concello")),
        ("Wikidata provincia", center.get("wikidata_provincia")),
        ("Web oficial", center.get("web")),
    ):
        if isinstance(url, str) and url.strip():
            links.append(build_link_pill(url.strip(), label=label, css_class="selected-center-link"))

    empty_links_html = '<span class="compact-note">Sin enlaces disponibles para este punto.</span>'
    links_html = "".join(links) if links else empty_links_html

    st.markdown(
        (
            '<div class="selected-center-card">'
            '<div class="selected-center-eyebrow">Punto seleccionado en el mapa</div>'
            f'<div class="selected-center-title">{html.escape(format_cell(center.get("espazo")) or "Centro cultural")}</div>'
            f'<div class="selected-center-subtitle">{html.escape(format_cell(center.get("concello")))} · {html.escape(format_cell(center.get("provincia_ui")))}</div>'
            f'<div class="selected-center-grid">{detail_html}</div>'
            f'<div class="selected-center-links">{links_html}</div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_table_card(dataframe: pd.DataFrame, height: int = 260) -> None:
    if dataframe.empty:
        st.info("No hay filas para los filtros actuales.")
        return

    display = dataframe.copy()
    for column in display.columns:
        display[column] = display[column].map(format_table_cell_html)

    table_html = display.to_html(index=False, classes="kg-table", border=0, escape=False)
    st.markdown(
        f'<div class="kg-table-card"><div class="kg-table-scroll" style="max-height:{height}px">{table_html}</div></div>',
        unsafe_allow_html=True,
    )


def style_figure(figure) -> None:
    figure.update_layout(
        template=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111a2b",
        font=dict(color="#e8eefc", family="Space Grotesk, Segoe UI, sans-serif"),
        margin=dict(l=10, r=10, t=12, b=10),
        showlegend=False,
    )
    figure.update_xaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.08)",
        zeroline=False,
        linecolor="rgba(255,255,255,0.10)",
        tickfont=dict(color="#b9c9e3"),
    )
    figure.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.08)",
        zeroline=False,
        linecolor="rgba(255,255,255,0.10)",
        tickfont=dict(color="#b9c9e3"),
    )


def prepare_query_display(selected_file: str, dataframe: pd.DataFrame) -> pd.DataFrame:
    if selected_file == "local_query_1.csv":
        return dataframe.loc[:, ["provinceDisplay", "numSpaces"]].rename(
            columns={"provinceDisplay": "Provincia", "numSpaces": "Espazos"}
        )

    if selected_file == "local_query_2.csv":
        display = dataframe.copy()
        display["avgCapacity"] = pd.to_numeric(display["avgCapacity"], errors="coerce")
        return display.loc[:, ["municipalityName", "provinceDisplay", "numSpaces", "avgCapacity"]].rename(
            columns={
                "municipalityName": "Concello",
                "provinceDisplay": "Provincia",
                "numSpaces": "Espazos",
                "avgCapacity": "Aforo medio",
            }
        )

    if selected_file == "local_query_3.csv":
        display = dataframe.copy()
        display["provinceDisplay"] = display["provinceName"].map(clean_province_name)
        return display.loc[:, ["spaceName", "municipalityName", "provinceDisplay", "capacity"]].rename(
            columns={
                "spaceName": "Espazo",
                "municipalityName": "Concello",
                "provinceDisplay": "Provincia",
                "capacity": "Aforo",
            }
        )

    if selected_file == "local_query_4.csv":
        return dataframe.loc[:, ["provinceDisplay", "numSpaces", "wd"]].rename(
            columns={
                "provinceDisplay": "Provincia",
                "numSpaces": "Espazos",
                "wd": "Wikidata",
            }
        )

    if selected_file == "municipalities_enriched.csv":
        display = dataframe.copy()
        return display.loc[
            :,
            [
                "municipalityName",
                "provinceDisplay",
                "numSpaces",
                "avgCapacity",
                "population",
                "spacesPer100k",
                "officialWebsite",
            ],
        ].rename(
            columns={
                "municipalityName": "Concello",
                "provinceDisplay": "Provincia",
                "numSpaces": "Espazos",
                "avgCapacity": "Aforo medio",
                "population": "Poblacion",
                "spacesPer100k": "Espazos por 100k",
                "officialWebsite": "Web oficial",
            }
        )

    if selected_file == "provinces_enriched.csv":
        display = dataframe.copy()
        return display.loc[
            :,
            [
                "provinceDisplay",
                "numSpaces",
                "population",
                "area",
                "capitalLabel",
                "spacesPerMillion",
            ],
        ].rename(
            columns={
                "provinceDisplay": "Provincia",
                "numSpaces": "Espazos",
                "population": "Poblacion",
                "area": "Area",
                "capitalLabel": "Capital",
                "spacesPerMillion": "Espazos por millon",
            }
        )

    return dataframe


def show_summary_tab(
    centers: pd.DataFrame,
    municipalities: pd.DataFrame,
    provinces: pd.DataFrame,
) -> None:
    if centers.empty:
        st.info("No hay centros visibles con los filtros actuales.")
        return

    left, right = st.columns((1.1, 1.0), gap="large")

    with left:
        st.subheader("Distribucion por provincia")
        province_summary = (
            centers.groupby("provincia_ui", dropna=False)
            .agg(espazos=("espazo", "count"), aforo_medio=("aforamento", "mean"))
            .sort_values("espazos", ascending=False)
            .reset_index()
        )
        province_chart = px.bar(
            province_summary,
            x="provincia_ui",
            y="espazos",
            color="provincia_ui",
            color_discrete_map=PROVINCE_HEX,
        )
        style_figure(province_chart)
        province_chart.update_traces(
            marker_line_color="rgba(255,255,255,0.14)",
            marker_line_width=1.2,
            hovertemplate="%{x}<br>%{y} espazos<extra></extra>",
        )
        province_chart.update_layout(height=255, xaxis_title=None, yaxis_title=None)
        province_chart.update_yaxes(automargin=True)
        province_chart.update_xaxes(automargin=True)
        st.plotly_chart(province_chart, use_container_width=True, config={"displayModeBar": False})
        leading_province = province_summary.iloc[0]
        st.markdown(
            f'<div class="compact-note">Provincia con más espacios: <strong>{leading_province["provincia_ui"]}</strong> con {int(leading_province["espazos"])} espazos.</div>',
            unsafe_allow_html=True,
        )

    with right:
        st.subheader("Ranking visible por aforo")
        top_spaces = (
            centers.sort_values(["aforamento", "espazo"], ascending=[False, True])
            .loc[:, ["espazo", "concello", "provincia_ui", "aforamento", "web"]]
            .head(10)
            .rename(
                columns={
                    "espazo": "Espazo",
                    "concello": "Concello",
                    "provincia_ui": "Provincia",
                    "aforamento": "Aforo",
                    "web": "Web",
                }
            )
        )
        ranking_chart = px.bar(
            top_spaces.head(8).sort_values("Aforo", ascending=True),
            x="Aforo",
            y="Espazo",
            orientation="h",
            color="Provincia",
            color_discrete_map=PROVINCE_HEX,
        )
        style_figure(ranking_chart)
        ranking_chart.update_traces(
            marker_line_color="rgba(255,255,255,0.12)",
            marker_line_width=1,
            hovertemplate="%{y}<br>%{x} plazas<extra></extra>",
        )
        ranking_chart.update_layout(height=255, yaxis_title=None, xaxis_title=None)
        ranking_chart.update_yaxes(automargin=True)
        ranking_chart.update_xaxes(automargin=True)
        st.plotly_chart(ranking_chart, use_container_width=True, config={"displayModeBar": False})
        top_space = top_spaces.sort_values("Aforo", ascending=False).iloc[0]
        st.markdown(
            f'<div class="compact-note">Mayor aforo visible: <strong>{top_space["Espazo"]}</strong> con {int(top_space["Aforo"])} plazas.</div>',
            unsafe_allow_html=True,
        )

    st.subheader("Indicadores enriquecidos")
    enriched_left, enriched_right = st.columns(2, gap="large")

    with enriched_left:
        best_municipalities = (
            municipalities.sort_values("spacesPer100k", ascending=False)
            .loc[:, ["municipalityName", "provinceDisplay", "numSpaces", "spacesPer100k"]]
            .head(8)
            .rename(
                columns={
                    "municipalityName": "Concello",
                    "provinceDisplay": "Provincia",
                    "numSpaces": "Espazos",
                    "spacesPer100k": "Espazos por 100k",
                }
            )
        )
        render_table_card(best_municipalities, height=260)

    with enriched_right:
        province_ratios = (
            provinces.sort_values("spacesPerMillion", ascending=False)
            .loc[:, ["provinceDisplay", "numSpaces", "spacesPerMillion"]]
            .rename(
                columns={
                    "provinceDisplay": "Provincia",
                    "numSpaces": "Espazos",
                    "spacesPerMillion": "Espazos por millon",
                }
            )
        )
        render_table_card(province_ratios, height=260)


def show_map_tab(centers: pd.DataFrame, map_style: str, size_mode: str) -> None:
    points = build_map_dataframe(centers)

    if points.empty:
        st.warning("No hay puntos con coordenadas para los filtros actuales.")
        return

    st.markdown(
        """
        <div class="section-note">
          <strong>Lectura recomendada:</strong> el color identifica la provincia y el tamaño del marcador puede representar el aforo o mantenerse constante.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Haz clic en un marcador para fijarlo y abrir sus enlaces. La selección se mantiene visible debajo del mapa."
    )

    preselected_point_id = extract_selected_point_id(st.session_state.get(MAP_SELECTION_KEY))
    map_figure = build_map_figure(points, map_style, size_mode, preselected_point_id)
    event = st.plotly_chart(
        map_figure,
        use_container_width=True,
        theme=None,
        key=MAP_SELECTION_KEY,
        on_select="rerun",
        selection_mode="points",
        config={"displayModeBar": False, "scrollZoom": True},
    )

    selected_point_id = extract_selected_point_id(event) or preselected_point_id
    selected_center = points[points["point_id"] == selected_point_id]
    if not selected_center.empty:
        render_selected_center_card(selected_center.iloc[0])
    else:
        st.info("Todavia no hay un punto fijado. Selecciona uno en el mapa para ver sus enlaces.")

    render_table_card(
        points.loc[
            :,
            [
                "espazo",
                "concello",
                "provincia_ui",
                "aforamento",
                "telefono",
                "wikidata_espazo",
                "web",
            ],
        ]
        .rename(
            columns={
                "espazo": "Espazo",
                "concello": "Concello",
                "provincia_ui": "Provincia",
                "aforamento": "Aforo",
                "telefono": "Telefono",
                "wikidata_espazo": "Wikidata",
                "web": "Web",
            }
        ),
        height=320,
    )
    st.download_button(
        "Descargar centros filtrados",
        data=to_csv_bytes(points),
        file_name="centros_filtrados.csv",
        mime="text/csv",
    )


def show_municipality_tab(
    centers: pd.DataFrame,
    municipalities: pd.DataFrame,
    default_municipality: str,
    map_style: str,
) -> None:
    if centers.empty:
        st.warning("No hay centros visibles con los filtros actuales.")
        return

    municipality_options = sorted(centers["concello"].dropna().unique().tolist())
    default_index = municipality_options.index(default_municipality) if default_municipality in municipality_options else 0
    selected_municipality = st.selectbox(
        "Selecciona un concello",
        municipality_options,
        index=default_index,
    )

    municipality_centers = centers[centers["concello"] == selected_municipality].copy()
    municipality_info = municipalities[
        municipalities["municipalityName"] == selected_municipality
    ]

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Centros en el concello", f"{len(municipality_centers)}")

    total_capacity = municipality_centers["aforamento"].dropna().sum()
    metric_2.metric("Aforo total", f"{int(total_capacity)}" if pd.notna(total_capacity) else "N/D")

    mean_capacity = municipality_centers["aforamento"].dropna().mean()
    metric_3.metric("Aforo medio", f"{mean_capacity:.1f}" if pd.notna(mean_capacity) else "N/D")

    if not municipality_info.empty:
        ratio = municipality_info["spacesPer100k"].iloc[0]
        metric_4.metric(
            "Espazos por 100k",
            f"{ratio:.2f}" if pd.notna(ratio) else "N/D",
        )
    else:
        metric_4.metric("Espazos por 100k", "N/D")

    left, right = st.columns((1.15, 1.0), gap="large")
    with left:
        st.subheader("Centros del concello")
        centers_table = municipality_centers.loc[
            :,
            ["espazo", "enderezo", "aforamento", "telefono", "email", "web"],
        ].rename(
            columns={
                "espazo": "Espazo",
                "enderezo": "Enderezo",
                "aforamento": "Aforo",
                "telefono": "Telefono",
                "email": "Email",
                "web": "Web",
            }
        )
        render_table_card(centers_table, height=360)

    with right:
        st.subheader("Dato enriquecido")
        if municipality_info.empty:
            st.info("Este concello no aparece en el CSV enriquecido de Wikidata.")
        else:
            row = municipality_info.iloc[0]
            st.write(f"**Provincia:** {row['provinceDisplay']}")
            st.write(
                f"**Poblacion:** {int(row['population']) if pd.notna(row.get('population')) else 'N/D'}"
            )
            st.write(
                f"**Aforo medio de los centros:** {row['avgCapacity']:.2f}"
                if pd.notna(row.get("avgCapacity"))
                else "**Aforo medio de los centros:** N/D"
            )
            website = row.get("officialWebsite")
            if pd.notna(website):
                st.markdown(f"**Web oficial:** [{website}]({website})")
            else:
                st.write("**Web oficial:** N/D")

            point = municipality_centers.dropna(subset=["latitud", "longitud"])
            if not point.empty:
                st.caption("Vista rapida del area donde estan los centros del concello.")
                st.plotly_chart(
                    build_map_figure(point, map_style, "Constante"),
                    use_container_width=True,
                    theme=None,
                    config={"displayModeBar": False, "scrollZoom": True},
                )


def show_quality_tab(centers: pd.DataFrame) -> None:
    duplicates, validation_counts = load_quality_summary()
    filtered_duplicates = duplicates[duplicates["espazo"].isin(centers["espazo"].unique())]

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Filas CSV visibles", f"{len(centers)}")
    metric_2.metric("Nombres duplicados visibles", f"{len(filtered_duplicates)}")
    metric_3.metric("SHACL datos", f"{validation_counts['data']}")
    metric_4.metric("SHACL modelo", f"{validation_counts['model']}")

    left, right = st.columns((1.15, 1.0), gap="large")
    with left:
        st.subheader("Colisiones que explican 46 filas frente a 44 espazos")
        if filtered_duplicates.empty:
            st.success("Con los filtros actuales no quedan nombres repetidos.")
        else:
            render_table_card(
                filtered_duplicates.rename(
                    columns={
                        "espazo": "Espazo",
                        "filas": "Filas",
                        "concellos": "Concellos implicados",
                        "provincias": "Provincias implicadas",
                        "aforo_medio": "Aforo medio",
                    }
                ),
                height=260,
            )

    with right:
        st.subheader("Hallazgos de validacion")
        st.markdown(
            """
            - `Conforms: False` tanto en shapes desde datos como en shapes desde modelo.
            - Las colisiones de URI introducen multiples valores donde el modelo esperaba unicidad.
            - `ta:telefono` aparece como punto conflictivo porque la ontologia lo espera como `xsd:integer`, pero los datos llegan como texto con espacios.
            - Estos fallos explican por qué la siguiente mejora lógica del proyecto es rediseñar URIs y normalizar tipos.
            """
        )


def show_queries_tab(selected_file: str, province: str) -> None:
    dataframe = load_query_output(selected_file)
    config = QUERY_OPTIONS[selected_file]

    if province != "Todas" and "provinceDisplay" in dataframe.columns:
        filtered = dataframe[dataframe["provinceDisplay"] == province]
    else:
        filtered = dataframe

    display_table = prepare_query_display(selected_file, filtered)

    st.subheader(config["label"])
    st.write(config["description"])
    render_table_card(display_table, height=360)
    st.download_button(
        "Descargar resultado mostrado",
        data=to_csv_bytes(display_table),
        file_name=selected_file,
        mime="text/csv",
    )

    query_file = config["query_file"]
    if query_file:
        with st.expander("Ver consulta SPARQL asociada"):
            st.code((QUERIES_DIR / query_file).read_text(encoding="utf-8"), language="sparql")


def main() -> None:
    st.set_page_config(
        page_title="Pezapa KG Explorer",
        layout="wide",
        initial_sidebar_state="auto",
    )
    inject_styles()

    try:
        centers = load_centers()
        municipalities = load_enriched_municipalities()
        provinces = load_enriched_provinces()
    except FileNotFoundError as error:
        st.error(str(error))
        st.code("python3 src/run_queries.py", language="bash")
        return

    with st.sidebar:
        st.header("Filtros")
        province_options = ["Todas"] + sorted(centers["provincia_ui"].dropna().unique().tolist())
        selected_province = st.selectbox("Provincia", province_options)

        municipality_source = centers if selected_province == "Todas" else centers[centers["provincia_ui"] == selected_province]
        municipality_options = ["Todos"] + sorted(municipality_source["concello"].dropna().unique().tolist())
        selected_municipality = st.selectbox("Concello", municipality_options)

        max_capacity = int(centers["aforamento"].fillna(0).max())
        min_capacity = st.slider("Aforo minimo", 0, max_capacity, 0, step=25)
        search_term = st.text_input("Buscar por nombre del espacio")

    filtered_centers = filter_centers(
        centers,
        selected_province,
        selected_municipality,
        min_capacity,
        search_term,
    )

    visible_municipalities = filtered_centers["concello"].dropna().unique().tolist()
    visible_provinces = filtered_centers["provincia_ui"].dropna().unique().tolist()
    filtered_municipalities = municipalities[
        municipalities["municipalityName"].isin(visible_municipalities)
    ].copy()
    filtered_provinces = provinces[
        provinces["provinceDisplay"].isin(visible_provinces)
    ].copy()

    render_hero(municipalities, provinces)

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Espazos visibles", f"{len(filtered_centers)}")
    metric_2.metric("Concellos visibles", f"{filtered_centers['concello'].nunique()}")

    average_capacity = filtered_centers["aforamento"].dropna().mean()
    metric_3.metric("Aforo medio", f"{average_capacity:.1f}" if pd.notna(average_capacity) else "N/D")

    if not filtered_municipalities.empty:
        top_ratio_row = filtered_municipalities.sort_values("spacesPer100k", ascending=False).iloc[0]
        metric_4.metric(
            "Top ratio por 100k",
            f"{top_ratio_row['spacesPer100k']:.2f}",
        )
    else:
        metric_4.metric("Top ratio por 100k", "N/D")

    if not filtered_municipalities.empty:
        st.markdown(
            f'<div class="compact-note">Concello con mejor ratio visible: {top_ratio_row["municipalityName"]}</div>',
            unsafe_allow_html=True,
        )

    tab_summary, tab_map, tab_municipality, tab_quality, tab_queries = st.tabs(
        ["Resumen", "Mapa de centros", "Detalle por concello", "Calidad y limites", "Consultas y tablas"]
    )

    with tab_summary:
        show_summary_tab(filtered_centers, filtered_municipalities, filtered_provinces)

    with tab_map:
        map_controls_left, map_controls_right = st.columns(2)
        with map_controls_left:
            map_style_label = st.radio("Estilo del mapa", ["Oscuro", "Claro"], horizontal=True, key="map_style_tab")
        with map_controls_right:
            size_mode = st.radio("Tamano del marcador", ["Aforo", "Constante"], horizontal=True, key="marker_size_tab")
        map_style = "light" if map_style_label == "Claro" else "dark"
        show_map_tab(filtered_centers, map_style, size_mode)

    with tab_municipality:
        default_municipality = selected_municipality if selected_municipality != "Todos" else ""
        map_style = "dark"
        show_municipality_tab(filtered_centers, filtered_municipalities, default_municipality, map_style)

    with tab_quality:
        show_quality_tab(filtered_centers)

    with tab_queries:
        selected_query = st.selectbox(
            "Resultado SPARQL a mostrar",
            options=list(QUERY_OPTIONS),
            format_func=lambda key: QUERY_OPTIONS[key]["label"],
            key="query_selector_tab",
        )
        show_queries_tab(selected_query, selected_province)


if __name__ == "__main__":
    main()