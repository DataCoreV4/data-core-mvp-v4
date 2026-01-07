import streamlit as st
import pandas as pd
import unicodedata

# =================================================
# CONFIGURACIÓN
# =================================================
st.set_page_config(
    page_title="Data Core | Inteligencia Agroexportadora",
    layout="wide"
)

# =================================================
# LOGIN
# =================================================
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

# =================================================
# NORMALIZADOR
# =================================================
def normalizar(texto):
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = texto.replace(" ", "_")
    return texto

# =================================================
# CARGA MULTIARCHIVO (ESCALABLE)
# =================================================
@st.cache_data
def cargar_datos():
    archivos = {
        "limon": "datos_reales.csv",
        "arandano": "data_arandano_1_6.csv"
    }

    dfs = []

    for producto, archivo in archivos.items():
        df = pd.read_csv(
            archivo,
            sep=";",
            encoding="latin1",
            on_bad_lines="skip"
        )
        df.columns = [normalizar(c) for c in df.columns]
        df["producto"] = producto
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)

data = cargar_datos()

# =================================================
# APP PRINCIPAL
# =================================================
st.title("🌱 Data Core – Plataforma de Inteligencia Agroexportadora")
st.write("MVP funcional – análisis de certificaciones y simulación de riesgo")

# =================================================
# FILTROS
# =================================================
st.sidebar.header("🔍 Filtros")

producto_sel = st.sidebar.selectbox(
    "Producto",
    sorted(data["producto"].unique())
)

df = data[data["producto"] == producto_sel]

# =================================================
# PARÁMETROS MANUALES
# =================================================
st.sidebar.header("⚙️ Parámetros del modelo")

rechazo_manual = st.sidebar.slider(
    "Porcentaje de rechazos estimado (%)",
    0,
    100,
    20
)

# =================================================
# SCORING
# =================================================
def calcular_score(row, rechazo):
    score = 100
    score -= rechazo * 0.6

    if "estado_certificado" in row:
        if str(row["estado_certificado"]).upper() != "APROBADO":
            score -= 20

    if "certificacion_electronica" in row:
        if str(row["certificacion_electronica"]).upper() == "NO":
            score -= 10

    return max(round(score, 1), 0)

df["score_riesgo"] = df.apply(
    lambda r: calcular_score(r, rechazo_manual),
    axis=1
)

def clasificar(score):
    if score >= 80:
        return "🟢 Bajo Riesgo"
    elif score >= 60:
        return "🟡 Riesgo Medio"
    else:
        return "🔴 Alto Riesgo"

df["nivel_riesgo"] = df["score_riesgo"].apply(clasificar)

# =================================================
# MÉTRICAS
# =================================================
st.subheader("📊 Indicadores")

c1, c2, c3 = st.columns(3)
c1.metric("Registros analizados", len(df))
c2.metric("Rechazo simulado (%)", rechazo_manual)
c3.metric("Score promedio", round(df["score_riesgo"].mean(), 1))

# =================================================
# TABLA
# =================================================
st.subheader("📋 Información del producto seleccionado")
st.dataframe(df, use_container_width=True, height=500)

# =================================================
# MENSAJE FINAL
# =================================================
st.info(
    f"Análisis correspondiente al producto: {producto_sel.upper()} | "
    "Datos reales integrados para simulación de riesgo y apoyo a decisiones."
)
