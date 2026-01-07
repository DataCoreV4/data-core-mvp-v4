import streamlit as st
import pandas as pd
import unicodedata

# ---------------------------------
# CONFIGURACIÓN
# ---------------------------------
st.set_page_config(
    page_title="Data Core | Inteligencia Agroexportadora",
    layout="wide"
)

# ---------------------------------
# LOGIN SIMPLE
# ---------------------------------
def login():
    st.title("🔐 Acceso a Data Core")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if usuario == "admin" and password == "datacore123":
            st.session_state["auth"] = True
        else:
            st.error("Usuario o contraseña incorrectos")

if "auth" not in st.session_state:
    login()
    st.stop()

# ---------------------------------
# APP PRINCIPAL
# ---------------------------------
st.title("🌱 Data Core – Plataforma de Inteligencia Agroexportadora")
st.write("MVP funcional – análisis de certificaciones y simulación de riesgo")

# ---------------------------------
# CARGA DE DATOS
# ---------------------------------
data = pd.read_csv(
    "datos_reales.csv",
    sep=";",
    encoding="latin1",
    on_bad_lines="skip"
)

# ---------------------------------
# NORMALIZAR ENCABEZADOS
# ---------------------------------
def normalizar(texto):
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = texto.replace(" ", "_")
    return texto

data.columns = [normalizar(c) for c in data.columns]

# ---------------------------------
# NORMALIZAR PRODUCTO
# -------------------------
