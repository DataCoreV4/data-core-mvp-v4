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
st.write("Análisis operativo de inspecciones, destinos y riesgo por producto")

# =================================================
# FILTROS PRINCIPALES
# =================================================
st.sidebar.header("🔍 Filtros")

producto_sel = st.sidebar.selectbox(
    "Producto",
    sorted(data["producto"].unique())
)

df = data[data["producto"] == producto_sel]

# =================================================
# DETECTAR COLUMNAS CLAVE
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
# FILTRO PAÍS
# =================================================
if col_pais:
    pais_sel = st.sidebar.selectbox(
        "País de destino",
        ["Todos"] + sorted(df[col_pais].dropna().astype(str).unique())
    )
    if pais_sel != "Todos":
        df = df[df[col_pais].astype(str) == pais_sel]

# =================================================
# FILTRO MES
# =================================================
if col_mes:
    mes_sel = st.sidebar.selectbox(
        "Mes de inspección",
        ["Todos"] + sorted(df[col_mes].dropna().astype(str).unique())
    )
    if mes_sel != "Todos":
        df = df[df[col_mes].astype(str) == mes_sel]

# =================================================
# PARÁMETRO MANUAL
# =================================================
st.sidebar.header("⚙️ Simulación")

rechazo_manual = st.sidebar.slider(
    "Porcentaje de rechazos (%)",
    0, 100, 20
)

# =================================================
# SCORING DIFERENCIADO POR PRODUCTO (D)
# =================================================
def calcular_score(row, rechazo, producto):
    score = 100

    if producto == "limon":
        score -= rechazo * 0.7
        if "estado_certificado" in row and str(row["estado_certificado"]).upper() != "APROBADO":
            score -= 25
    elif producto == "arandano":
        score -= rechazo * 0.5
        if "estado_certificado" in row and str(row["estado_certificado"]).upper() != "APROBADO":
            score -= 15

    if "certificacion_electronica" in row:
        if str(row["certificacion_electronica"]).upper() == "NO":
            score -= 10

    return max(round(score, 1), 0)

df["score_riesgo"] = df.apply(
    lambda r: calcular_score(r, rechazo_manual, producto_sel),
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
# INDICADORES
# =================================================
st.subheader("📊 Indicadores clave")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Registros", len(df))
c2.metric("Rechazo simulado (%)", rechazo_manual)
c3.metric("Score promedio", round(df["score_riesgo"].mean(), 1))
c4.metric("Inspecciones", len(df))

# =================================================
# A) GRÁFICO INSPECCIONES POR MES
# =================================================
if col_mes:
    st.subheader("📈 Inspecciones por mes")

    graf_mes = (
        df.groupby(col_mes)
        .size()
        .reset_index(name="inspecciones")
        .sort_values(col_mes)
    )

    st.bar_chart(
        graf_mes.set_index(col_mes)["inspecciones"]
    )

# =================================================
# B) RANKING PAÍSES DESTINO
# =================================================
if col_pais:
    st.subheader("🌍 Ranking de países destino")

    ranking = (
        df.groupby(col_pais)
        .size()
        .reset_index(name="inspecciones")
        .sort_values("inspecciones", ascending=False)
    )

    st.dataframe(ranking, use_container_width=True)

# =================================================
# TABLA FINAL
# =================================================
st.subheader("📋 Base de datos filtrada")
st.dataframe(df, use_container_width=True, height=450)

# =================================================
# MENSAJE FINAL
# =================================================
st.info(
    f"Análisis avanzado para el producto {producto_sel.upper()}, "
    "integrando comportamiento mensual, destinos prioritarios y "
    "scoring de riesgo diferenciado."
)
