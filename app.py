import streamlit as st
import pandas as pd
import unicodedata
import os

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
            st.success("Acceso correcto")
        else:
            st.error("Usuario o contraseña incorrectos")

if "auth" not in st.session_state:
    login()
    st.stop()

if not st.session_state.get("auth", False):
    st.stop()

# =================================================
# FUNCIONES
# =================================================
def normalizar(texto):
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = texto.replace(" ", "_")
    return texto

def detectar_columna(df, claves):
    for c in df.columns:
        for k in claves:
            if k in c:
                return c
    return None

# =================================================
# CARGA ENVÍOS
# =================================================
@st.cache_data
def cargar_envios():
    archivos = {
        "limon": "datos_reales.csv",
        "arandano": "data_arandano_1_6.csv"
    }

    dfs = []
    for producto, archivo in archivos.items():
        if not os.path.exists(archivo):
            continue

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

envios = cargar_envios()

# =================================================
# CARGA CAMPO
# =================================================
@st.cache_data
def cargar_campo():
    archivos = {
        "limon": "data_campo_limon_2025.csv",
        "arandano": "data_campo_arandano_2025.csv"
    }

    dfs = []
    for producto, archivo in archivos.items():
        if not os.path.exists(archivo):
            continue

        df = pd.read_csv(
            archivo,
            sep=";",
            encoding="latin1",
            on_bad_lines="skip"
        )
        df.columns = [normalizar(c) for c in df.columns]
        df["producto"] = producto
        dfs.append(df)

    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()

campo = cargar_campo()

# =================================================
# INTERFAZ
# =================================================
st.title("🌱 Data Core – Plataforma de Inteligencia Agroexportadora")
st.write("Análisis estratégico de envíos vs capacidad productiva certificada")

# =================================================
# FILTRO PRODUCTO
# =================================================
producto_sel = st.sidebar.selectbox(
    "Producto",
    sorted(envios["producto"].unique())
)

envios_p = envios[envios["producto"] == producto_sel]
campo_p = campo[campo["producto"] == producto_sel]

# =================================================
# MÉTRICAS BASE
# =================================================
total_envios = len(envios_p)

col_lugar = detectar_columna(
    campo_p,
    ["lugar_produccion", "codigo_lugar", "predio", "campo"]
)

total_lugares = campo_p[col_lugar].nunique() if col_lugar else 0

# =================================================
# INDICADOR ESTRELLA
# =================================================
st.subheader("⭐ Indicador estratégico: Uso de capacidad productiva")

c1, c2, c3 = st.columns(3)
c1.metric("📦 Envíos registrados", total_envios)
c2.metric("🌾 Lugares certificados", total_lugares)

if total_lugares > 0:
    ratio = round(total_envios / total_lugares, 2)
else:
    ratio = 0

c3.metric("⚖️ Envíos por lugar", ratio)

# =================================================
# INTERPRETACIÓN AUTOMÁTICA
# =================================================
if ratio < 1:
    st.error("🔴 Capacidad productiva subutilizada")
    st.write("Existe infraestructura certificada que no está siendo aprovechada comercialmente.")
elif 1 <= ratio <= 3:
    st.warning("🟡 Uso equilibrado de la capacidad productiva")
    st.write("La relación entre producción certificada y exportaciones es adecuada.")
else:
    st.success("🟢 Alta intensidad exportadora")
    st.write("Alta presión exportadora sobre la infraestructura certificada.")

# =================================================
# VISUALIZACIÓN
# =================================================
st.markdown("### 📊 Comparación visual")

grafico = pd.DataFrame({
    "Indicador": ["Envíos", "Lugares certificados"],
    "Cantidad": [total_envios, total_lugares]
})

st.bar_chart(grafico.set_index("Indicador"))

# =================================================
# DETALLE
# =================================================
st.markdown("### 📋 Detalle de envíos")
st.dataframe(envios_p, use_container_width=True, height=300)

st.markdown("### 🌾 Detalle de lugares de producción")
if not campo_p.empty:
    st.dataframe(campo_p, use_container_width=True, height=300)
else:
    st.info("No hay datos de campo disponibles para este producto.")

# =================================================
# CIERRE
# =================================================
st.info(
    "Este indicador permite evaluar brechas entre capacidad productiva certificada "
    "y actividad exportadora real, apoyando decisiones de inversión, articulación comercial "
    "y planificación sectorial."
)
