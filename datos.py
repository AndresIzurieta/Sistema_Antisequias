"""Carga y limpieza de la encuesta real (Google Forms exportado a Excel)."""
from pathlib import Path
import pandas as pd

ARCHIVO = Path(__file__).with_name("encuesta_respuestas.xlsx")

# Orden de columnas del formulario -> nombre corto
CAMPOS = ["marca", "visita", "seco", "lugar", "problema", "metodo",
          "dificultad", "preocupa", "funcion", "barrera", "piloto"]

TITULOS = {
    "visita": "Frecuencia de visita a áreas verdes",
    "seco": "Frecuencia con que observó terrenos secos (último año)",
    "lugar": "Dónde observó problemas de sequía o falta de riego",
    "problema": "Problema de sequía más importante de atender",
    "metodo": "Método de riego que ha observado",
    "dificultad": "Principal dificultad del riego convencional",
    "preocupa": "Preocupación por incendios en vegetación seca (1-5)",
    "funcion": "Función del sistema considerada más útil",
    "barrera": "Principal preocupación sobre la instalación",
    "piloto": "Apoyo a una prueba piloto en la universidad",
}

ORDEN = {
    "visita": ["Nunca", "Rara vez", "Una vez por semana", "Varias veces por semana", "Diariamente"],
    "seco": ["Nunca", "Rara vez", "Ocasionalmente", "Frecuentemente", "Muy frecuentemente"],
    "preocupa": ["1 — Ninguna preocupación", "2 — Poca preocupación", "3 — Preocupación moderada",
                 "4 — Bastante preocupación", "5 — Mucha preocupación"],
    "piloto": ["Definitivamente no", "Probablemente no", "No estoy seguro/a",
               "Probablemente sí", "Sí, definitivamente"],
}


def cargar(fuente=None) -> pd.DataFrame:
    """Lee el Excel (ruta o archivo subido). Las columnas se asignan por posición."""
    df = pd.read_excel(fuente or ARCHIVO)
    if df.shape[1] < len(CAMPOS):
        raise ValueError(f"Se esperaban {len(CAMPOS)} columnas y el archivo trae {df.shape[1]}.")
    df = df.iloc[:, :len(CAMPOS)].copy()
    df.columns = CAMPOS
    df["marca"] = pd.to_datetime(df["marca"], errors="coerce")
    for c in CAMPOS[1:]:
        df[c] = df[c].astype("string").str.strip()
    for c, orden in ORDEN.items():
        df[c] = pd.Categorical(df[c], categories=orden, ordered=True)
    df["preocupa_n"] = pd.to_numeric(df["preocupa"].astype("string").str[0], errors="coerce")
    return df.dropna(subset=["marca"]).reset_index(drop=True)


def frecuencias(df: pd.DataFrame, campo: str) -> pd.DataFrame:
    """Conteo y porcentaje sobre quienes respondieron esa pregunta."""
    s = df[campo].dropna()
    t = s.value_counts(sort=campo not in ORDEN).rename_axis("Respuesta").reset_index(name="Personas")
    if campo in ORDEN:
        t = t.set_index("Respuesta").reindex(ORDEN[campo]).reset_index()
        t["Personas"] = t["Personas"].fillna(0).astype(int)
    t["Porcentaje"] = (100 * t["Personas"] / max(len(s), 1)).round(1)
    return t


def porcentaje(df: pd.DataFrame, campo: str, valores) -> float:
    s = df[campo].dropna()
    if isinstance(valores, str):
        valores = [valores]
    return 100 * s.isin(valores).mean() if len(s) else 0.0
