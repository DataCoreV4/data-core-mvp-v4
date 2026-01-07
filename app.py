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
# INTERFAZ
# =================================================
st.title("🌱 Data Core – Inteligencia Agroexportadora")
st.write("Uso real de campos certificados según envíos registrados")

producto_sel = st.sidebar.selectbox(
    "Producto",
    sorted(envios["producto"].unique())
)

envios_p = envios[envios["producto"] == producto_sel]
campo_p = campo[campo["producto"] == producto_sel]

# =================================================
# DIAGNÓSTICO (YA CONFIRMADO, LO DEJAMOS)
# =================================================
with st.expander("🧩 Ver columnas detectadas"):
    st.write("📦 Envíos:", list(envios_p.columns))
    st.write("🌾 Campo:", list(campo_p.columns))

# =================================================
# DETECCIÓN REAL (AJUSTADA A TUS DATOS)
# =================================================
col_cod_envio = detectar_columna(
    envios_p,
    ["cod_lugar", "produccia3n"]
)

col_cod_campo = detectar_columna(
    campo_p,
    ["cod_lugar_prod"]
)

col_mes = detectar_columna(
    envios_p,
    ["mes_inspeccia3n", "mes_inspec"]
)

# =================================================
# VALIDACIÓN FINAL
# =================================================
if not col_cod_envio or not col_cod_campo or not col_mes:
    st.error("❌ No se pudieron vincular las columnas necesarias.")
    st.stop()

# =================================================
# CRUCE DE DATOS
# =================================================
envios_p[col_cod_envio] = envios_p[col_cod_envio].astype(str).str.strip()
campo_p[col_cod_campo] = campo_p[col_cod_campo].astype(str).str.strip()

df_cruce = envios_p.merge(
    campo_p[[col_cod_campo]],
    left_on=col_cod_envio,
    right_on=col_cod_campo,
    how="inner"
)

# =================================================
# ORDEN DE MESES
# =================================================
orden_meses = [
    "enero","febrero","marzo","abril","mayo","junio",
    "julio","agosto","septiembre","octubre","noviembre","diciembre"
]

df_cruce[col_mes] = (
    df_cruce[col_mes]
    .astype(str)
    .str.lower()
    .str.strip()
)

df_cruce[col_mes] = pd.Categorical(
    df_cruce[col_mes],
    categories=orden_meses,
    ordered=True
)

# =================================================
# AGRUPACIÓN
# =================================================
envios_campo_mes = (
    df_cruce
    .groupby([col_mes, col_cod_envio])
    .size()
    .reset_index(name="envios")
)

# =================================================
# VISUALIZACIÓN
# =================================================
st.subheader("📊 Envíos por campo certificado – evolución mensual")

campo_sel = st.selectbox(
    "Campo certificado",
    sorted(envios_campo_mes[col_cod_envio].unique())
)

df_plot = envios_campo_mes[
    envios_campo_mes[col_cod_envio] == campo_sel
]

st.bar_chart(df_plot.set_index(col_mes)["envios"])

st.markdown("### 📋 Detalle completo")
st.dataframe(envios_campo_mes, use_container_width=True)

# =================================================
# MENSAJE ESTRATÉGICO
# =================================================
st.info(
    "Este módulo vincula trazabilidad de envíos con campos certificados, "
    "permitiendo evaluar el uso real de cada unidad productiva y su evolución mensual."
)
