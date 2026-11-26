# Riego inteligente con detección de incendios

Panel en Streamlit con los resultados de la encuesta sobre sequías, riego inteligente y prevención de incendios, y la casa de la calidad del proyecto de Diseño de Máquinas.

## Ejecutar
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
Abre http://localhost:8501. En PyCharm: Module name = `streamlit`, Parameters = `run app.py`.

## Actualizar los datos
Reemplaza `encuesta_respuestas.xlsx` (mismo formato de Google Forms, 11 columnas) y haz commit. También puedes subir un Excel desde el panel lateral para verlo sin guardarlo.

## Archivos
- `app.py`: interfaz, gráficos y casa de la calidad.
- `datos.py`: lectura y limpieza del Excel.
- `qfd.py`: requisitos, matriz, techo y cálculo de prioridades.
- `.streamlit/config.toml`: tema.
