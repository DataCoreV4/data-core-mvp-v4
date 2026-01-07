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
# APLICACIÓN PRINCIPAL
# ---------------------------
st.title("🌱 Data Core – Plataforma de Inteligencia Agroexportadora")
st.write("MVP funcional – Análisis y trazabilidad de certificaciones fitosanitarias")

# ---------------------------
# CARGA DE DATOS
# ---------------------------
data = pd.read_csv("datos_limon.csv")

# Limpieza básica
data.columns = data.columns.str.strip()
data["Producto"] = data["Producto"].str.strip().str.lower()

# ---------------------------
# FILTROS
# ---------------------------
st.sidebar.header("🔍 Filtros")

producto = st.sidebar.selectbox(
    "Producto",
    sorted(data["Producto"].unique())
)

pais_destino = st.sidebar.multiselect(
    "País Destino",
    sorted(data["Pais Destino"].dropna().unique())
)

df = data[data["Producto"] == producto]

if pais_destino:
    df = df[df["Pais Destino"].isin(pais_destino)]

# ---------------------------
# MÉTRICAS CLAVE
# ---------------------------
st.subheader("📊 Indicadores clave")

col1, col2, col3 = st.columns(3)

col1.metric("Registros analizados", len(df))
col2.metric("Certificados generados", df["Certificados Generados"].sum())
col3.metric("Peso Neto Total", round(df["Peso Neto"].sum(), 2))

# ---------------------------
# TABLA COMPLETA (CORE)
# ---------------------------
st.subheader("📋 Base de datos detallada")

st.dataframe(
    df,
    use_container_width=True,
    height=500
)

# ---------------------------
# MENSAJE TÉCNICO
# ---------------------------
st.info(
    "La plataforma Data Core integra, filtra y analiza grandes volúmenes de información "
    "relacionada a certificaciones, inspecciones y exportaciones agrícolas, "
    "permitiendo trazabilidad y análisis para la toma de decisiones."
)
