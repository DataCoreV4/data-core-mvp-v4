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
# CARGA DATOS DE CAMPO
# =================================================
@st.cache_data
def cargar_campo():
    archivos = {
        "limon": "datos_campo_limon_2025.csv",
        "arandano": "datos_campo_arandano_2025.csv"
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

campo = cargar_campo()

# =================================================
# APP PRINCIPAL
# =================================================
st.title("🌱 Data Core – Plataforma de Inteligencia Agroexportadora")
st.write("Análisis integral de envíos e infraestructura certificada")

# =================================================
# SIDEBAR – FILTROS
# =================================================
st.sidebar.header("🔍 Filtros")

producto_sel = st.sidebar.selectbox(
    "Producto",
    sorted(envios["producto"].unique())
)

df = envios[envios["producto"] == producto_sel]

# =================================================
# DETECTAR COLUMNAS
# =================================================
def detectar_columna(df, claves):
    for c in df.columns:
        for k in claves:
            if k in c:
                return c
    return None

col_pais = detectar_columna(df, ["pais_destino"])
col_mes = detectar_columna(df, ["mes_inspeccion"])

# =================================================
# FILTRO MES
# =================================================
orden_meses = [
    "enero","febrero","marzo","abril","mayo","junio",
    "julio","agosto","septiembre","octubre","noviembre","diciembre"
]

if col_mes:
    df[col_mes] = df[col_mes].astype(str).str.lower().str.strip()
    df[col_mes] = pd.Categorical(df[col_mes], categories=orden_meses, ordered=True)

    mes_sel = st.sidebar.selectbox(
        "Mes de inspección",
        ["Todos"] + orden_meses
    )

    if mes_sel != "Todos":
        df = df[df[col_mes] == mes_sel]

# =================================================
# FILTRO PAÍS (CON TODOS)
# =================================================
if col_pais:
    paises = sorted(df[col_pais].dropna().astype(str).unique())
    pais_sel = st.sidebar.selectbox(
        "País de destino",
        ["Todos los países"] + paises
    )

    if pais_sel != "Todos los países":
        df = df[df[col_pais].astype(str) == pais_sel]

# =================================================
# MÓDULO 1 – ENVÍOS
# =================================================
st.subheader("📦 Módulo 1: Envíos e inspecciones")

c1, c2 = st.columns(2)
c1.metric("Registros analizados", len(df))
c2.metric("Países destino", df[col_pais].nunique() if col_pais else 0)

if col_mes:
    st.markdown("**📈 Inspecciones por mes**")
    graf = df.groupby(col_mes).size()
    if not graf.empty:
        st.bar_chart(graf)
    else:
        st.warning("No hay datos para los filtros seleccionados.")

if col_pais:
    st.markdown("**🌍 Envíos por país destino**")
    ranking = df.groupby(col_pais).size().reset_index(name="envios")
    st.dataframe(ranking.sort_values("envios", ascending=False), use_container_width=True)

st.markdown("**📋 Detalle de envíos**")
st.dataframe(df, use_container_width=True, height=350)

# =================================================
# MÓDULO 2 – CAMPO (LUGARES CERTIFICADOS)
# =================================================
st.subheader("🌾 Módulo 2: Lugares de producción certificados")

campo_prod = campo[campo["producto"] == producto_sel]

col_lugar = detectar_columna(
    campo_prod,
    ["lugar_produccion", "lugar_de_produccion", "codigo_lugar", "predio"]
)

if col_lugar:
    total_lugares = campo_prod[col_lugar].nunique()

    c3, c4 = st.columns(2)
    c3.metric("Producto", producto_sel.upper())
    c4.metric("Lugares certificados", total_lugares)

    st.markdown("**📋 Base de campo certificada**")
    st.dataframe(campo_prod, use_container_width=True, height=300)
else:
    st.warning("No se pudo identificar la columna de lugar de producción.")

# =================================================
# MENSAJE FINAL
# =================================================
st.info(
    "La plataforma integra información de envíos e infraestructura productiva certificada, "
    "permitiendo evaluar capacidad, cobertura y desempeño por producto."
)
