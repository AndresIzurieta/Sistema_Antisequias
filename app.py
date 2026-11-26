import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from datos import cargar, frecuencias, porcentaje, TITULOS, ORDEN
import qfd

VERDE, FUEGO, SUELO, TINTA = "#2F6B4F", "#C2410C", "#E6EBDF", "#1D2B24"
SECUENCIA = ["#C2410C", "#E8883A", "#C9CFC6", "#7DB59A", "#2F6B4F"]  # de menos a más (divergente)

st.set_page_config(page_title="Riego inteligente y prevención de incendios", page_icon="🔥", layout="wide")
st.markdown(f"""
<style>
html, body, [class*="css"] {{ font-family: "Source Sans 3", "Segoe UI", sans-serif; }}
h1, h2, h3 {{ font-family: "Archivo Narrow", "Arial Narrow", Arial, sans-serif; color:{TINTA}; letter-spacing:-.01em; }}
.block-container {{ padding-top: 2rem; max-width: 1180px; }}
div[data-testid="stMetric"] {{ background:#fff; border:1px solid #C9CFC6; border-left:5px solid {VERDE};
  padding:14px 16px; border-radius:6px; }}
div[data-testid="stMetric"] label {{ color:#5D6B64; }}
button[data-baseweb="tab"] {{ font-weight:600; }}
.nota {{ color:#5D6B64; font-size:.9rem; max-width:75ch; }}
.hallazgo {{ background:#fff; border:1px solid #C9CFC6; border-left:5px solid {FUEGO}; padding:12px 16px;
  border-radius:6px; margin:6px 0; max-width:80ch; }}
</style>""", unsafe_allow_html=True)


def estilo(fig, alto=380):
    fig.update_layout(height=alto, margin=dict(l=8, r=8, t=48, b=8), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", font=dict(color=TINTA), title_font_size=16,
                      legend_title_text="")
    fig.update_xaxes(gridcolor="#DDE2D8"); fig.update_yaxes(gridcolor="#DDE2D8")
    return fig


def barras(df, campo, color=VERDE, secuencia=False):
    t = frecuencias(df, campo)
    t["Etiqueta"] = t["Respuesta"].astype(str).str.wrap(38).str.replace("\n", "<br>")
    t = t.iloc[::-1] if campo not in ORDEN else t.iloc[::-1]
    fig = px.bar(t, x="Porcentaje", y="Etiqueta", orientation="h", text=t["Porcentaje"].map("{:.0f} %".format),
                 title=TITULOS[campo], hover_data={"Personas": True, "Etiqueta": False})
    fig.update_traces(marker_color=color, textposition="outside", cliponaxis=False)
    fig.update_yaxes(title=""); fig.update_xaxes(title="% de quienes respondieron", range=[0, t["Porcentaje"].max() * 1.2])
    return estilo(fig, 120 + 52 * len(t))


# ---------- datos ----------
with st.sidebar:
    st.header("Datos")
    subido = st.file_uploader("Actualizar con un Excel nuevo", type=["xlsx"],
                              help="Mismo formato de Google Forms: 11 columnas, la primera es la marca temporal.")
    st.caption("Sin archivo, se usa encuesta_respuestas.xlsx del repositorio.")

try:
    df = cargar(subido)
except Exception as e:
    st.error(f"No se pudo leer el Excel: {e}")
    st.stop()

n = len(df)
st.title("Riego inteligente con detección de incendios")
st.caption(f"Encuesta a {n} personas · {df.marca.min():%d/%m/%Y} al {df.marca.max():%d/%m/%Y} · Proyecto de Diseño de Máquinas")

alta = porcentaje(df, "preocupa", ORDEN["preocupa"][3:])
ambas = porcentaje(df, "funcion", "Ambas funciones por igual")
piloto = porcentaje(df, "piloto", ORDEN["piloto"][3:])
vio_seco = porcentaje(df, "seco", ORDEN["seco"][2:])
c = st.columns(4)
c[0].metric("Respuestas", n)
c[1].metric("Preocupación alta por incendios", f"{alta:.0f} %", help="Respondieron 4 o 5 en la escala de 1 a 5")
c[2].metric("Quieren ambas funciones", f"{ambas:.0f} %")
c[3].metric("Apoyan una prueba piloto", f"{piloto:.0f} %", help="«Probablemente sí» o «Sí, definitivamente»")

tabs = st.tabs(["Resumen", "Resultados", "Cruces", "Casa de la calidad", "Datos", "Método"])

# ---------- Resumen ----------
with tabs[0]:
    top_problema = frecuencias(df, "problema").sort_values("Porcentaje", ascending=False).iloc[0]
    top_barrera = frecuencias(df[~df.barrera.isin(["No estoy seguro/a", "No tendría preocupaciones importantes"])],
                              "barrera").sort_values("Porcentaje", ascending=False).iloc[0]
    st.subheader("Lo que dicen los datos")
    for txt in [
        f"<b>{alta:.0f} %</b> siente preocupación alta (4 o 5) por incendios en vegetación seca; el promedio es <b>{df.preocupa_n.mean():.1f} de 5</b>.",
        f"<b>{ambas:.0f} %</b> prefiere que el sistema haga ambas cosas, detectar incendios y regar, antes que solo una de las dos.",
        f"El problema que más personas quieren atender es «{top_problema.Respuesta.lower()}» ({top_problema.Porcentaje:.0f} %), seguido muy de cerca por los demás.",
        f"La mayor barrera para instalarlo es el <b>{top_barrera.Respuesta.lower()}</b> ({top_barrera.Porcentaje:.0f} % del total de respuestas).",
        f"<b>{piloto:.0f} %</b> apoyaría una prueba piloto en la universidad; solo {porcentaje(df, 'piloto', ORDEN['piloto'][:2]):.0f} % está en contra.",
    ]:
        st.markdown(f'<div class="hallazgo">{txt}</div>', unsafe_allow_html=True)
    a, b = st.columns(2)
    a.plotly_chart(barras(df, "funcion", FUEGO), width="stretch")
    b.plotly_chart(barras(df, "piloto", VERDE), width="stretch")

# ---------- Resultados ----------
with tabs[1]:
    st.caption("Cada gráfico usa solo a quienes contestaron esa pregunta; por eso los totales pueden variar en una o dos personas.")
    for campo in ["visita", "seco", "lugar", "problema", "metodo", "dificultad", "preocupa", "funcion", "barrera", "piloto"]:
        color = FUEGO if campo in ("preocupa", "problema", "funcion") else VERDE
        st.plotly_chart(barras(df, campo, color), width="stretch", key=f"b_{campo}")

# ---------- Cruces ----------
with tabs[2]:
    st.subheader("Preocupación por incendios y función preferida")
    d = df.dropna(subset=["preocupa", "funcion"])
    m = pd.crosstab(d["funcion"], d["preocupa"], normalize="index").mul(100).round(0)
    fig = px.imshow(m, text_auto=".0f", aspect="auto", color_continuous_scale=["#F6F4EC", "#E8883A", "#C2410C"],
                    labels=dict(color="% de la fila"), title="% dentro de cada función preferida")
    fig.update_xaxes(title="Preocupación por incendios", side="bottom"); fig.update_yaxes(title="")
    st.plotly_chart(estilo(fig, 360), width="stretch")
    st.markdown('<p class="nota">Cada fila suma 100 %. Con pocas personas en algunas filas, léelo como tendencia y no como prueba.</p>', unsafe_allow_html=True)

    st.subheader("Apoyo a la prueba piloto según lo observado")
    d = df.dropna(subset=["seco", "piloto"])
    m = pd.crosstab(d["seco"], d["piloto"]).reindex(index=ORDEN["seco"], columns=ORDEN["piloto"], fill_value=0)
    pct = m.div(m.sum(axis=1).replace(0, np.nan), axis=0).mul(100)
    fig = go.Figure()
    for col, color in zip(ORDEN["piloto"], SECUENCIA):
        fig.add_bar(y=pct.index, x=pct[col], name=col, orientation="h", marker_color=color)
    fig.update_layout(barmode="stack", title="Frecuencia con que vio terrenos secos vs. apoyo al piloto")
    fig.update_xaxes(title="% dentro de cada grupo", range=[0, 100]); fig.update_yaxes(title="", autorange="reversed")
    st.plotly_chart(estilo(fig, 380), width="stretch")

# ---------- Casa de la calidad ----------
with tabs[3]:
    st.subheader("Casa de la calidad")
    st.markdown('<p class="nota">La importancia de cada requisito se calcula con la encuesta: es proporcional al porcentaje de personas que lo respalda (de 1 a 5). Cambia las relaciones en la matriz (0, 1, 3 o 9) y la prioridad se recalcula.</p>', unsafe_allow_html=True)
    imp = qfd.importancias(df)
    tec = [t[0] for t in qfd.TECNICAS]
    st.markdown("**Correlaciones entre características técnicas** (+ se apoyan, − se contraponen)")
    st.markdown(qfd.techo_svg(), unsafe_allow_html=True)
    mat = pd.DataFrame(qfd.RELACIONES, columns=tec, index=imp["Requisito"])
    mat.insert(0, "Importancia", imp["Importancia"].values)
    editada = st.data_editor(
        mat, key="matriz", width="stretch",
        disabled=["Importancia"],
        column_config={"Importancia": st.column_config.NumberColumn(format="%.1f", help="Calculada con la encuesta"),
                       **{t: st.column_config.SelectboxColumn(t, options=[0, 1, 3, 9], required=True) for t in tec}})
    res = qfd.prioridades(editada["Importancia"].to_numpy(float), editada[tec].to_numpy(float))
    st.dataframe(res, hide_index=True, width="stretch")
    fig = px.bar(res.sort_values("Puntos"), x="Puntos", y="Característica técnica", orientation="h",
                 text="Ranking", title="Prioridad técnica (el número es el ranking)")
    fig.update_traces(marker_color=VERDE, texttemplate="%{text}°", textposition="outside", cliponaxis=False)
    fig.update_yaxes(title="")
    st.plotly_chart(estilo(fig, 420), width="stretch")
    st.markdown('<p class="nota">Las metas son valores de partida para el diseño; confírmalas con tu docente y con las pruebas del prototipo.</p>', unsafe_allow_html=True)
    with st.expander("De dónde sale la importancia"):
        st.dataframe(imp, hide_index=True, width="stretch")

# ---------- Datos ----------
with tabs[4]:
    vista = df.rename(columns={**TITULOS, "marca": "Marca temporal"}).drop(columns=["preocupa_n"])
    st.dataframe(vista, hide_index=True, width="stretch")
    buf = io.BytesIO(); vista.to_excel(buf, index=False)
    a, b = st.columns(2)
    a.download_button("Descargar CSV", vista.to_csv(index=False).encode("utf-8-sig"), "encuesta.csv", "text/csv")
    b.download_button("Descargar Excel", buf.getvalue(), "encuesta.xlsx",
                      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ---------- Método ----------
with tabs[5]:
    st.markdown(f"""
**Muestra.** {n} respuestas voluntarias de un formulario en línea. No es una muestra aleatoria: describe a quienes respondieron, no a toda la población de Quito.

**Preguntas sin respuesta.** Algunas personas dejaron preguntas en blanco. Cada porcentaje se calcula solo sobre quienes contestaron esa pregunta.

**Preocupación.** Escala de 1 (ninguna) a 5 (mucha). «Alta» significa 4 o 5.

**Casa de la calidad.** Importancia = 1 + 4 × (respaldo del requisito ÷ respaldo máximo). Los requisitos de función salen de una pregunta de selección múltiple implícita (ambas funciones suman a las dos) y los de preocupación de una pregunta de una sola opción, por eso las funciones pesan más; es una simplificación. Las relaciones 0/1/3/9 y las metas técnicas son criterio de diseño y se pueden editar.

**Actualizar los datos.** Reemplaza `encuesta_respuestas.xlsx` en el repositorio, o sube un Excel nuevo desde el panel lateral para verlo sin guardarlo.
""")
