import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# ======================================
# CONFIG
# ======================================
st.set_page_config(page_title="Data Core", layout="wide")

# ======================================
# USERS (MVP)
# ======================================
USERS = {
    "admin": {"password": "admin123", "role": "admin"}
}

# ======================================
# DATA MAP (Drive)
# ======================================
DATA_MAP = {
    (2021, "envios", "uva"): "1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF",
    (2021, "campo", "uva"): "1k6OMQxl7B3hVY9OVECc9UlYcytIjpN1A",
    # 👉 puedes seguir agregando todos
}

PRODUCTS = ["uva", "mango", "arandano", "limon", "palta"]
YEARS = [2021, 2022, 2023, 2024, 2025]

# ======================================
# GOOGLE DRIVE DOWNLOADER (CLAVE)
# ======================================
def download_from_gdrive(file_id):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()

    response = session.get(URL, params={"id": file_id}, stream=True)
    token = None

    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            token = value

    if token:
        response = session.get(
            URL, params={"id": file_id, "confirm": token}, stream=True
        )

    content = BytesIO()
    for chunk in response.iter_content(32768):
        if chunk:
            content.write(chunk)

    content.seek(0)
    return content

@st.cache_data(show_spinner=True)
def load_data(year, tipo, producto):
    file_id = DATA_MAP.get((year, tipo, producto))
    if not file_id:
        return None

    try:
        file_bytes = download_from_gdrive(file_id)
        df = pd.read_csv(file_bytes, sep=",", encoding="utf-8")
        return df
    except Exception as e:
        st.error(f"Error cargando data: {e}")
        return None

# ======================================
# LOGIN
# ======================================
def auth_screen():
    st.title("🔐 Data Core – Acceso")
    user = st.text_input("Usuario", key="login_user")
    pwd = st.text_input("Contraseña", type="password", key="login_pwd")

    if st.button("Ingresar"):
        if user in USERS and USERS[user]["password"] == pwd:
            st.session_state.user = user
            st.session_state.role = USERS[user]["role"]
            st.rerun()
        else:
            st.error("Credenciales incorrectas")

# ======================================
# DASHBOARD
# ======================================
def dashboard():
    st.sidebar.image("logo_datacore.jpg", width=160)
    st.sidebar.markdown("### Freemium")

    st.title("📊 Data Core – Dashboard")

    # ---------- ENVÍOS ----------
    st.header("📦 Envíos")

    c1, c2, c3 = st.columns(3)
    product = c1.selectbox("Producto", PRODUCTS)
    year = c2.selectbox("Año", YEARS)
    month = c3.selectbox("Mes", ["Todos"] + list(range(1, 13)))

    df = load_data(year, "envios", product)

    if df is None or df.empty:
        st.warning("📌 Información en proceso de mejora para este producto/año.")
    else:
        st.success(f"Datos cargados: {len(df)} registros")

        if st.session_state.role == "admin":
            st.dataframe(df)
        else:
            st.dataframe(df.head(3))
            st.markdown(
                "🔓 **Acceso completo:** "
                "[Adquirir data completa aquí](mailto:datacore.agrotech@gmail.com)"
            )

    # ---------- CAMPOS ----------
    st.header("🌾 Campos certificados")

    c4, c5, c6 = st.columns(3)
    product_c = c4.selectbox("Producto (campo)", PRODUCTS)
    year_c = c5.selectbox("Año (campo)", YEARS)
    month_c = c6.selectbox("Mes (campo)", ["Todos"] + list(range(1, 13)))

    dfc = load_data(year_c, "campo", product_c)

    if dfc is None or dfc.empty:
        st.warning("📌 Información de campos en proceso de mejora.")
    else:
        st.success(f"Datos de campo cargados: {len(dfc)} registros")

        if st.session_state.role == "admin":
            st.dataframe(dfc)
        else:
            st.dataframe(dfc.head(3))
            st.markdown(
                "🔓 **Acceso completo:** "
                "[Adquirir data completa aquí](mailto:datacore.agrotech@gmail.com)"
            )

    st.markdown("✅ **Data Core – MVP estable | Escalable | Compatible con 13G**")

# ======================================
# MAIN
# ======================================
if "user" not in st.session_state:
    auth_screen()
else:
    dashboard()
