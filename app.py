import streamlit as st
import pandas as pd
import unicodedata

# =================================================
# CONFIGURACIÓN GENERAL
# =================================================
st.set_page_config(
    page_title="Data Core | Inteligencia Agroexportadora",
    layout="wide"
)

# =================================================
# LOGIN SIMPLE (MVP)
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
# APP PRINCIPAL
# =================================================
st.title("🌱 Data Core – Plataforma de Inteligencia Agroexportadora")
st.write("MVP funcional – análisis de certificaciones y simulación de riesgo")

# =================================================
# CARGA DE DATOS
# =================================================
data = pd.read_csv(
    "datos_reales.csv",
    sep=";",
    encoding="latin1",
    on_bad_lines="skip"
)

# =================================================
# NORMALIZAR ENCABEZADOS
# =================================================
def normalizar(texto):
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = texto.replace(" ", "_")
    return texto

data.columns = [normalizar(c) for c in data.columns]

# =================================================
# DETECTAR COLUMNA PRODUCTO (AUTOMÁTICO)
# =================================================
col_producto = None
for c in data.columns:
    if "producto" in c:
        col_producto = c
        break

if col_producto is None:
    st.error("No se pudo identificar la columna de producto.")
    st.write("Columnas detectadas:", list(data.columns))
    st.stop()

data["producto"] = data[col_producto].astype(str).str.strip().str.lower()

# =================================================
# FILTROS
# =================================================
st.sidebar.header("🔍 Filtros")

producto = st.sidebar.selectbox(
    "Producto",
    sorted(data["producto"].unique())
)

df = data[data["producto"] == producto]

# =================================================
# PARÁMETROS MANUALES (TÚ DECIDES)
# =================================================
st.sidebar.header("⚙️ Parámetros del modelo")

rechazo_manual = st.sidebar.slider(
    "Porcentaje de rechazos estimado (%)",
    0,
    100,
    20
)

# =================================================
# SCORING DE RIESGO
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
# TABLA COMPLETA
# =================================================
st.subheader("📋 Base de datos completa")

st.dataframe(
    df,
    use_container_width=True,
    height=500
)

# =================================================
# MENSAJE FINAL
# =================================================
st.info(
    "Data Core integra información real de certificaciones fitosanitarias, "
    "permitiendo simular escenarios de rechazo y apoyar la toma de decisiones "
    "en procesos de exportación agroalimentaria."
)

