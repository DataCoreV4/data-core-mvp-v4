import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Data Core | Inteligencia Agroexportadora",
    layout="wide"
)

st.title("🌱 Data Core – Motor de Inteligencia Agroexportadora")
st.write("MVP – Plataforma de Scoring y Decisión para Compra de Fruta")

data = pd.read_csv("datos_reales.csv")
st.write("Vista previa de los datos cargados:")
st.dataframe(data)

st.sidebar.header("🔍 Filtros de análisis")

cultivo = st.sidebar.selectbox(
    "Selecciona el cultivo",
    data["cultivo"].unique()
)

mercado = st.sidebar.selectbox(
    "Selecciona mercado destino",
    ["UE", "EEUU", "Mercado Nacional"]
)

df = data[data["cultivo"] == cultivo]

def calcular_score(row):
    score = 0
    score += (100 - row["rechazos_pct"]) * 0.4
    score += row["certificacion"] * 30
    score += row["rendimiento"] * 0.3
    return round(score, 1)

df["score"] = df.apply(calcular_score, axis=1)

def clasificar(score):
    if score >= 80:
        return "🟢 Bajo Riesgo"
    elif score >= 60:
        return "🟡 Riesgo Medio"
    else:
        return "🔴 Alto Riesgo"

df["riesgo"] = df["score"].apply(clasificar)

st.subheader("📊 Resultados del análisis")

st.dataframe(
    df[["campo", "score", "riesgo", "rechazos_pct", "rendimiento"]],
    use_container_width=True
)

st.subheader("⚙️ Recomendación del sistema")

mejor_campo = df.sort_values("score", ascending=False).iloc[0]

st.success(
    f"""
    ✅ Campo recomendado: **{mejor_campo['campo']}**  
    📈 Score: **{mejor_campo['score']}**  
    🌍 Mercado sugerido: **{mercado}**
    """
)

st.info(
    "Resultado generado automáticamente por el motor de scoring de Data Core."
)
