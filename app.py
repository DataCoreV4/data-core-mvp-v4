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
# CARGA MULTIARCHIVO
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
st.write("Análisis comparativo de inspecciones y destinos")

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
# NORMALIZAR MES (CLAVE PARA LA GRÁFICA)
# =================================================
orden_meses = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]

if col_mes:
    df[col_mes] = (
        df[col_mes]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    df[col_mes] = pd.Categorical(
        df[col_mes],
        categories=orden_meses,
        ordered=True
    )

# =================================================
# FILTRO MES
# =================================================
if col_mes:
    mes_sel = st.sidebar.selectbox(
        "Mes de inspección",
        ["Todos"] + orden_meses
    )
    if mes_sel != "Todos":
        df = df[df[col_mes] == mes_sel]

# =================================================
# FILTRO PAÍS
# =================================================
if col_pais:
    pais_sel = st.sidebar.multiselect(
        "País de destino (comparación)",
        sorted(df[col_pais].dropna().astype(str).unique()),
        default=sorted(df[col_pais].dropna().astype(str).unique())
    )
    if pais_sel:
        df = df[df[col_pais].astype(str).isin(pais_sel)]

# =================================================
# INDICADORES
# =================================================
st.subheader("📊 Indicadores")

c1, c2 = st.columns(2)
c1.metric("Registros analizados", len(df))
c2.metric("Países comparados", df[col_pais].nunique() if col_pais else 0)

# =================================================
# GRÁFICA A) INSPECCIONES POR MES
# =================================================
if col_mes:
    st.subheader("📈 Inspecciones por mes")

    graf_mes = (
        df.groupby(col_mes)
        .size()
        .reset_index(name="inspecciones")
        .dropna()
    )

    if not graf_mes.empty:
        st.bar_chart(
            graf_mes.set_index(col_mes)["inspecciones"]
        )
    else:
        st.warning("No hay datos para graficar con los filtros seleccionados.")

# =================================================
# COMPARACIÓN B) PAÍSES DESTINO (EJ. EE.UU. vs PAÍSES BAJOS)
# =================================================
if col_pais:
    st.subheader("🌍 Comparación de países destino")

    comparacion = (
        df.groupby(col_pais)
        .size()
        .reset_index(name="inspecciones")
        .sort_values("inspecciones", ascending=False)
    )

    st.dataframe(comparacion, use_container_width=True)

# =================================================
# TABLA FINAL
# =================================================
st.subheader("📋 Datos detallados")
st.dataframe(df, use_container_width=True, height=450)

# =================================================
# MENSAJE FINAL
# =================================================
st.info(
    "El sistema permite comparar envíos por producto, mes y país destino, "
    "identificando mercados prioritarios y patrones operativos."
)
