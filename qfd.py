"""Casa de la calidad: la importancia de cada requisito sale de la encuesta."""
import numpy as np
import pandas as pd
from datos import porcentaje

FUNCION_FUEGO = ["Detección temprana de posibles incendios y alertas", "Ambas funciones por igual"]
FUNCION_RIEGO = ["Riego automático según la humedad del suelo", "Ambas funciones por igual"]

# (requisito, campo, respuestas que lo respaldan)
REQUISITOS = [
    ("Detectar incendios y avisar", "funcion", FUNCION_FUEGO),
    ("Regar según la humedad del suelo", "funcion", FUNCION_RIEGO),
    ("Sensores precisos y confiables", "barrera", "Precisión y confiabilidad de los sensores"),
    ("Bajo costo de instalación", "barrera", "Costo de instalación"),
    ("Mantenimiento sencillo", "barrera", "Dificultad de mantenimiento"),
    ("Bajo consumo de agua y energía", "barrera", "Consumo de agua o energía"),
    ("Poca supervisión humana", "dificultad", "Requieren supervisión o intervención constante"),
    ("Riego en el momento necesario", "dificultad", "El riego no siempre se realiza cuando es necesario"),
]

TECNICAS = [  # nombre, dirección, meta
    ("Tiempo de detección", "↓", "≤ 120 s"),
    ("Eficiencia hídrica", "↑", "≥ 30 % de ahorro"),
    ("Autonomía energética", "↑", "≥ 7 días sin sol"),
    ("Protección IP", "↑", "IP65"),
    ("Costo por nodo", "↓", "≤ 250 USD"),
    ("Alcance de comunicación", "↑", "≥ 5 km"),
    ("Área cubierta por nodo", "↑", "≥ 5 ha"),
    ("Tiempo entre fallas", "↑", "≥ 12 meses"),
    ("Precisión del sensor", "↑", "± 3 % humedad"),
]

RELACIONES = np.array([
    [9, 0, 3, 1, 0, 9, 3, 3, 9],
    [0, 9, 1, 0, 1, 3, 3, 1, 9],
    [3, 3, 1, 3, 3, 0, 0, 9, 9],
    [1, 1, 3, 3, 9, 3, 9, 3, 3],
    [0, 1, 3, 3, 1, 0, 0, 9, 1],
    [0, 9, 9, 0, 3, 1, 0, 1, 1],
    [3, 3, 3, 1, 1, 9, 1, 9, 3],
    [3, 9, 1, 0, 0, 3, 3, 3, 9],
])

# techo: (i, j, signo) con i<j
TECHO = [(0, 5, "+"), (0, 4, "−"), (0, 2, "−"), (0, 8, "+"), (1, 8, "+"), (2, 4, "−"),
         (3, 4, "−"), (4, 6, "−"), (4, 8, "−"), (2, 5, "−"), (5, 6, "+"), (3, 7, "+"), (2, 7, "+")]


def importancias(df: pd.DataFrame) -> pd.DataFrame:
    """Importancia 1-5 proporcional al % de personas que respalda el requisito."""
    filas = [(n, porcentaje(df, c, v)) for n, c, v in REQUISITOS]
    t = pd.DataFrame(filas, columns=["Requisito", "Respaldo (%)"])
    mx = t["Respaldo (%)"].max() or 1
    t["Importancia"] = (1 + 4 * t["Respaldo (%)"] / mx).round(1)
    return t


def prioridades(imp: np.ndarray, rel: np.ndarray) -> pd.DataFrame:
    pts = imp @ rel
    t = pd.DataFrame({
        "Característica técnica": [x[0] for x in TECNICAS],
        "Dirección": [x[1] for x in TECNICAS],
        "Meta": [x[2] for x in TECNICAS],
        "Puntos": pts.round(1),
    })
    t["Peso (%)"] = (100 * t["Puntos"] / t["Puntos"].sum()).round(1)
    t["Ranking"] = t["Puntos"].rank(ascending=False, method="min").astype(int)
    return t


def techo_svg(w=84) -> str:
    n = len(TECNICAS)
    alto = n * w / 2 + 6
    s = [f'<svg viewBox="0 0 {n * w} {alto}" width="100%" style="max-width:720px" role="img" aria-label="Techo de correlaciones">']
    for i in range(n):
        for j in range(i + 1, n):
            cx, cy = (i + j + 1) / 2 * w, alto - 3 - (j - i) / 2 * w
            signo = next((x[2] for x in TECHO if x[0] == i and x[1] == j), "")
            col = "#2F6B4F" if signo == "+" else "#C2410C"
            s.append(f'<path d="M{cx} {cy - w / 2}L{cx + w / 2} {cy}L{cx} {cy + w / 2}L{cx - w / 2} {cy}Z" '
                     f'fill="#FFFFFF" stroke="#BFC8BA"/>')
            if signo:
                s.append(f'<text x="{cx}" y="{cy + 7}" text-anchor="middle" font-size="22" '
                         f'font-weight="700" fill="{col}">{signo}</text>')
    s.append("</svg>")
    return "".join(s)
