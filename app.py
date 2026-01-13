import streamlit as st
import pandas as pd

# =============================
# CONFIGURACIÓN
# =============================
st.set_page_config(
    page_title="Data Core – Inteligencia Agroexportadora",
    layout="wide"
)

# =============================
# USUARIOS (MVP)
# =============================
USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin"
    }
}

# =============================
# MAPA DE ARCHIVOS (Drive)
# =============================
DATA_MAP = {
    (2025, "envio", "uva"): "1iw-OafOHph_epXgf-6kreXhq2GxzNqyN",
    (2025, "envio", "mango"): "1-f5tlde1nBJnl_9BbRJkaDpGBleYtbyG",
    (2025, "envio", "arandano"): "1TxC9TwgFojnNRkQlOI27KJBzG0TK7tp7",
    (2025, "envio", "limon"): "1G8VbTnSeOcJJVDRkze9s12TRts5BvQx6",
    (2025, "envio", "palta"): "1Qt680UXFnKBh7bdV0iGqnJKKmc1suNVA",

    (2025, "campo", "uva"): "15R-9ECTNpSQM1FC8tFPUs0emE16H8cHT",
    (2025, "campo", "mango"): "11IziWG98PfqkSyTaK5GvKwU4NEC9LwXJ",
    (2025, "campo", "arandano"): "15w2FG2TT_qPfxEksBgcGbfPu67yNbvYT",
    (2025, "campo", "limon"): "178kHRjqLgs-EFUmzCsNclBKq-nYmVJPO",
    (2025, "campo", "palta"): "1fo9HKY9DSKAjgLVKsx2H0Y7f_YU4DwRT",
}

PRODUCTS = ["uva", "mango", "arandano", "limon", "palta"]
YEARS = [2021, 2022, 2023, 2024, 2025]

# =============================
# UTILIDADES
# =============================
MONTH_MAP = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12
}

def normalize_month(val):
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return int(val)
    val = str(val).strip().lower()
    if val.isdigit():
        return int(val)
    return MONTH_MAP.get(val[:3])

def find_column(df, keywords):
    for col in df.columns:
        c = col.lower()
        if any(k in c for k in keywords):
            return col
    return None

@st.cache_data(show_spinner=False)
def load_data(year, tipo, producto):
    file_id = DATA_MAP.get((year, tipo, producto))
    if not file_id:
        return None
    url = f"https://drive.google.com/uc?id={file_id}"
    try:
        return pd.read_csv(url)
    except Exception:
        return None

# =============================
# LOGIN
# =============================
def auth_screen():
    st.markdown("## 🔐 Data Core – Acceso")
    try:
        st.image("logo_datacore.jpg", width=200)
    except:
        pass

    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if user in USERS and USERS[user]["password"] == pwd:
            st.session_state.user = user
            st.session_state.role = USERS[user]["role"]
            st.experimental_rerun()
        else:
            st.error("Credenciales incorrectas")

# =============================
# DASHBOARD
# =============================
def dashboard():
    st.sidebar.image("logo_datacore.jpg", width=160)
    st.sidebar.markdown("### Freemium")

    st.title("📊 Data Core – Dashboard")

    # =====================
    # ENVÍOS
    # =====================
    st.header("📦 Envíos")

    c1, c2, c3 = st.columns(3)
    product = c1.selectbox("Producto", PRODUCTS)
    year = c2.selectbox("Año", YEARS)
    month = c3.selectbox("Mes", ["Todos"] + list(range(1, 13)))

    df = load_data(year, "envio", product)

    if df is None or df.empty:
        st.warning("📌 Información en proceso de mejora para este producto/año.")
    else:
        col_month = find_column(df, ["mes"])
        col_country = find_column(df, ["pais", "destino"])

        if col_month:
            df["mes_norm"] = df[col_month].apply(normalize_month)
            if month != "Todos":
                df = df[df["mes_norm"] == month]

        if col_country:
            country = st.selectbox(
                "País destino",
                ["Todos"] + sorted(df[col_country].dropna().unique())
            )
            if country != "Todos":
                df = df[df[col_country] == country]

        if st.session_state.role != "admin":
            st.dataframe(df.head(3))
            st.markdown(
                "🔓 **Acceso completo:** "
                "[Adquirir data completa aquí](mailto:datacore.agrotech@gmail.com)"
            )
        else:
            st.dataframe(df)

    # =====================
    # CAMPOS
    # =====================
    st.header("🌾 Campos certificados")

    c4, c5, c6 = st.columns(3)
    product_c = c4.selectbox("Producto (campo)", PRODUCTS)
    year_c = c5.selectbox("Año (campo)", YEARS)
    month_c = c6.selectbox("Mes (campo)", ["Todos"] + list(range(1, 13)))

    dfc = load_data(year_c, "campo", product_c)

    if dfc is None or dfc.empty:
        st.warning("📌 Información de campos en proceso de mejora.")
    else:
        col_crop = find_column(dfc, ["cultivo"])
        col_month_c = find_column(dfc, ["mes"])

        if col_crop:
            dfc = dfc[dfc[col_crop].str.lower() == product_c]

        if col_month_c:
            dfc["mes_norm"] = dfc[col_month_c].apply(normalize_month)
            if month_c != "Todos":
                dfc = dfc[dfc["mes_norm"] == month_c]

        if st.session_state.role != "admin":
            st.dataframe(dfc.head(3))
            st.markdown(
                "🔓 **Acceso completo:** "
                "[Adquirir data completa aquí](mailto:datacore.agrotech@gmail.com)"
            )
        else:
            st.dataframe(dfc)

    st.markdown("✅ **Data Core – MVP estable | Escalable | Compatible con 13G**")

# =============================
# APP FLOW
# =============================
if "user" not in st.session_state:
    auth_screen()
else:
    dashboard()
