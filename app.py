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
    texto = texto.replace(" ", "_").replace(".", "")
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
# INTERFAZ PRINCIPAL
# =================================================
st.title("🌱 Data Core – Plataforma de Inteligencia Agroexportadora")
st.write(
    "MVP funcional para visualización de envíos agroexportadores "
    "y campos de producción certificados."
)

# =================================================
# SIDEBAR – FILTROS
# =================================================
st.sidebar.header("🔍 Filtros")

producto_sel = st.sidebar.selectbox(
    "Producto",
    sorted(envios["producto"].unique())
)

envios_p = envios[envios["producto"] == producto_sel]
campo_p = campo[campo["producto"] == producto_sel]

# Filtro país destino
col_pais = detectar_columna(envios_p, ["pais_destino"])

if col_pais:
    paises = sorted(envios_p[col_pais].dropna().astype(str).unique())
    pais_sel = st.sidebar.selectbox(
        "País de destino",
        ["Todos"] + paises
    )
    if pais_sel != "Todos":
        envios_p = envios_p[envios_p[col_pais].astype(str) == pais_sel]

# =================================================
# MÉTRICAS RESUMEN
# =================================================
c1, c2 = st.columns(2)
c1.metric("📦 Total de envíos", len(envios_p))
c2.metric("🌾 Campos certificados", len(campo_p))

# =================================================
# TABLA ENVÍOS
# =================================================
st.subheader("📦 Envíos registrados")
st.dataframe(
    envios_p,
    use_container_width=True,
    height=350
)

# =================================================
# TABLA CAMPO
# =================================================
st.subheader("🌾 Campos de producción certificados")
if not campo_p.empty:
    st.dataframe(
        campo_p,
        use_container_width=True,
        height=350
    )
else:
    st.info("No hay datos de campo disponibles para este producto.")

# =================================================
# MENSAJE FINAL
# =================================================
st.info(
    "Data Core integra información de envíos agroexportadores y campos "
    "de producción certificados, permitiendo análisis por producto y "
    "país de destino como base para inteligencia comercial y trazabilidad."
)
