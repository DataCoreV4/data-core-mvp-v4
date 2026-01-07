import streamlit as st
import pandas as pd

# ---------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------
st.set_page_config(
    page_title="Data Core | Inteligencia Agroexportadora",
    layout="wide"
)

# ---------------------------
# LOGIN SIMPLE (MVP)
# ---------------------------
def login():
    st.title("🔐 Acceso a Data Core")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if usuario == "admin" and password == "datacore123":
            st.session_state["autenticado"] = True
        else:
            st.error("Usuario o contraseña incorrectos")

if "autenticado" not in st.session_state:
    login()
    st.stop()

# ---------------------------
# APP PRINCIPAL
# ---------------------------
st.title("🌱 Data Core – Plataforma de Inteligencia Agroexportadora")
st.write("MVP – Análisis, trazabilidad y simulación de decisiones")

# ---------------------------
# CARGA DE DATOS
# ---------------------------
import unicodedata

data = pd.read_csv(
    "datos_reales.csv",
    sep=";",
    encoding="latin1",
    on_bad_lines="skip"
)

# -------- NORMALIZAR ENCABEZADOS --------
def normalizar(texto):
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = texto.replace(" ", "_")
    return texto

data.columns = [normalizar(c) for c in data.columns]

data.columns = data.columns.str.strip()

# Normalización
data["producto"] = data["producto"].astype(str).str.strip().str.lower()

# ---------------------------
# FILTROS
# ---------------------------
st.sidebar.header("🔍 Filtros")

producto = st.sidebar.selectbox(
    "Producto",
    sorted(data["producto"].unique())
)

pais_destino = st.sidebar.multiselect(
    "País Destino",
    sorted(data["Pais Destino"].dropna().unique())
)

df = data[data["producto"] == producto]

if pais_destino:
    df = df[df["Pais Destino"].isin(pais_destino)]

# ---------------------------
# INPUT MANUAL DE RECHAZOS
# ---------------------------
st.sidebar.header("⚙️ Parámetros del modelo")

rechazo_manual = st.sidebar.slider(
    "Porcentaje de rechazos estimado (%)",
    min_value=0,
    max_value=100,
    value=20
)

# ---------------------------
# SCORING (CONTROLADO POR TI)
# ---------------------------
def calcular_score(row, rechazo):
    score = 100
    score -= rechazo * 0.6

    if "estado_certificado" in row and str(row["estado_certificado"]).upper() != "APROBADO":
        score -= 20

    if "certificacion_electronica" in row and str(row["certificacion_electronica"]).upper() == "NO":
        score -= 10

    return max(round(score, 1), 0)

)

def clasificar(score):
    if score >= 80:
        return "🟢 Bajo Riesgo"
    elif score >= 60:
        return "🟡 Riesgo Medio"
    else:
        return "🔴 Alto Riesgo"

df["Nivel Riesgo"] = df["Score Riesgo"].apply(clasificar)

# ---------------------------
# MÉTRICAS
# ---------------------------
st.subheader("📊 Indicadores clave")

col1, col2, col3 = st.columns(3)

col1.metric("Registros evaluados", len(df))
col2.metric("Rechazo simulado (%)", rechazo_manual)
col3.metric("Score promedio", round(df["Score Riesgo"].mean(), 1))

# ---------------------------
# TABLA FINAL
# ---------------------------
st.subheader("📋 Resultados del análisis")

st.dataframe(
    df,
    use_container_width=True,
    height=500
)

# ---------------------------
# MENSAJE FINAL
# ---------------------------
st.info(
    "El motor de Data Core permite simular escenarios de rechazo y evaluar su impacto "
    "en el riesgo de certificación y exportación, apoyando la toma de decisiones."
)
