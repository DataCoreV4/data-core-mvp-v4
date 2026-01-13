import streamlit as st
import pandas as pd

# ======================================
# CONFIGURACIÓN GENERAL
# ======================================
st.set_page_config(
    page_title="Data Core – Inteligencia Agroexportadora",
    layout="wide"
)

# ======================================
# USUARIOS (MVP)
# ======================================
USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin"
    }
}

# ======================================
# MAPA DE DATA (Drive)
# CLAVE: (AÑO, TIPO, PRODUCTO)
# TIPO = envios | campo
# ======================================
DATA_MAP = {
    # ---------------- ENVÍOS ----------------
    (2021, "envios", "uva"): "1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF",
    (2021, "envios", "mango"): "1k6CxjPufa0YF17e264BI8NYO1rFFZuc7",
    (2021, "envios", "arandano"): "1CyFQu-BdYNxFSoed9SGvKnkimrJjS2Q9",
    (2021, "envios", "limon"): "1--9cfYzrB2giYCy5khZmqXdXL_46Zuz8",
    (2021, "envios", "palta"): "1-BK3uEDMAMrTAdqxMJd-pIYCg0Rp-8kJ",

    (2022, "envios", "uva"): "1wHxIXmn2stnjdFSnu8spnOSDw9Q45Dti",
    (2022, "envios", "mango"): "1kjtC1QVGe4w3GWEYhMmB9VD98eYjhvPh",
    (2022, "envios", "arandano"): "1tJRlp3FWvYZBr3LFPV1PFke3o6LZcOfa",
    (2022, "envios", "limon"): "1HfO0jh0yPXK99P8mQ080KLEevc4QVnLT",
    (2022, "envios", "palta"): "1IYS7yUDFmeCw3YyCIgKDbayZ63AORHvf",

    (2023, "envios", "uva"): "1SZjCd3ANa4CF0N0lK_mnOQfzn0-ywTLs",
    (2023, "envios", "mango"): "1S5mMR3nG_DeH3ZpOqAvcjidzPQMW8kw_",
    (2023, "envios", "arandano"): "1JhAhZi3roOQpw5ejm3jnW5Av59De8wc2",
    (2023, "envios", "limon"): "1sGnvph11F431fg5v9c8qzoH-Yxytffti",
    (2023, "envios", "palta"): "1MCaBirErsv3PeJZ4soi2Fszw8QcJbg7w",

    (2024, "envios", "uva"): "1csIY-AT7Uw6QFp49SANyHALHuZO3r65n",
    (2024, "envios", "mango"): "1In6_xnpKZwD1zTG4JrD3uhk7sYNKU4qF",
    (2024, "envios", "arandano"): "1CZSWhLV-STPw9k90cOVzQxJ0V2k7ZTUa",
    (2024, "envios", "limon"): "1XxGB8PGI4yh5K5mO5qGqRnSK_Fe2nPAX",
    (2024, "envios", "palta"): "1mLNGjAunM6HTiCnJIgEoaqZQEuegfSf9",

    (2025, "envios", "uva"): "1iw-OafOHph_epXgf-6kreXhq2GxzNqyN",
    (2025, "envios", "mango"): "1-f5tlde1nBJnl_9BbRJkaDpGBleYtbyG",
    (2025, "envios", "arandano"): "1TxC9TwgFojnNRkQlOI27KJBzG0TK7tp7",
    (2025, "envios", "limon"): "1G8VbTnSeOcJJVDRkze9s12TRts5BvQx6",
    (2025, "envios", "palta"): "1Qt680UXFnKBh7bdV0iGqnJKKmc1suNVA",

    # ---------------- CAMPO ----------------
    (2021, "campo", "uva"): "1k6OMQxl7B3hVY9OVECc9UlYcytIjpN1A",
    (2021, "campo", "mango"): "1JX50r2NJYG3HjalUTZ5pCHmbD5DXQDUu",
    (2021, "campo", "arandano"): "1HOKP2FaW9UPRYyA7tIj0oSnGzUhkb3h4",
    (2021, "campo", "limon"): "12xOZVXqxvvepb97On1H8feKUoW_u1Qet",
    (2021, "campo", "palta"): "1ckjszJeuyPQS6oVNeWFd-FwoM8FTalHO",

    (2022, "campo", "uva"): "1LS_80bCCgGE4flJ2BEzav1XeQQSrSX1y",
    (2022, "campo", "mango"): "16CDM3zQnH3S5n2SNjqwJmk0oUGkbxtJS",
    (2022, "campo", "arandano"): "1WTkBElLqv3aLQ8s2rkmlQqHM1zsKE33-",
    (2022, "campo", "limon"): "123wwsJLNrvlTxh2VRZQy1JpVOjI9Oj32",
    (2022, "campo", "palta"): "1uIs_MXnilSoPIGhtJtmOCv8N8un2VoFg",

    (2023, "campo", "uva"): "11sb54WtgNe0poLSR4q-nEGvjMdbnjXiq",
    (2023, "campo", "mango"): "1qV3zoDQNnzeEvQR0eZ0FnrvxdkuruyUM",
    (2023, "campo", "arandano"): "1jdNrMyVcW2HV5PJI63_A_oxl6xLpapl7",
    (2023, "campo", "limon"): "1F708yJNg3mzrdHi53Dmw4RQZkTqUh4YH",
    (2023, "campo", "palta"): "1ZBXYrxS4iJ-lUBPKAMtr4ZIWGf6Wh6ED",

    (2024, "campo", "uva"): "15CoNL-b9tONKTjbj2rIy8cthyeVhsD_F",
    (2024, "campo", "mango"): "1T6OVYHVN6j57Km9Z8zWrKYMlzTUIeRes",
    (2024, "campo", "arandano"): "1YejBbqWi383QjeJntU-AaICQw0TOJyaV",
    (2024, "campo", "limon"): "1JH6oXdDP5z-JAQgu9WvT-ej1pCjnX6WS",
    (2024, "campo", "palta"): "1fxh3QgnZXzjkuqmwG4w9h1YjhK6PPvX9",

    (2025, "campo", "uva"): "15R-9ECTNpSQM1FC8tFPUs0emE16H8cHT",
    (2025, "campo", "mango"): "11IziWG98PfqkSyTaK5GvKwU4NEC9LwXJ",
    (2025, "campo", "arandano"): "15w2FG2TT_qPfxEksBgcGbfPu67yNbvYT",
    (2025, "campo", "limon"): "178kHRjqLgs-EFUmzCsNclBKq-nYmVJPO",
    (2025, "campo", "palta"): "1fo9HKY9DSKAjgLVKsx2H0Y7f_YU4DwRT",
}

PRODUCTS = ["uva", "mango", "arandano", "limon", "palta"]
YEARS = [2021, 2022, 2023, 2024, 2025]

# ======================================
# UTILIDADES
# ======================================
MONTH_MAP = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12
}

def normalize_month(val):
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return int(val)
    v = str(val).strip().lower()
    if v.isdigit():
        return int(v)
    return MONTH_MAP.get(v[:3])

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
        return pd.read_csv(url, encoding="utf-8")
    except Exception:
        return None

# ======================================
# LOGIN
# ======================================
def auth_screen():
    st.title("🔐 Data Core – Acceso")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")

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

    # ---------------- ENVÍOS ----------------
    st.header("📦 Envíos")

    c1, c2, c3 = st.columns(3)
    product = c1.selectbox("Producto", PRODUCTS)
    year = c2.selectbox("Año", YEARS)
    month = c3.selectbox("Mes", ["Todos"] + list(range(1, 13)))

    df = load_data(year, "envios", product)

    if df is None or df.empty:
        st.warning("📌 Información en proceso de mejora para este producto/año.")
    else:
        col_month = find_column(df, ["mes"])
        col_country = find_column(df, ["pais", "destino"])

        if col_country:
            country = st.selectbox(
                "País destino",
                ["Todos"] + sorted(df[col_country].dropna().unique())
            )
            if country != "Todos":
                df = df[df[col_country] == country]

        if col_month:
            df["mes_norm"] = df[col_month].apply(normalize_month)
            if month != "Todos":
                df = df[df["mes_norm"] == month]

        if df.empty:
            st.warning("📌 Información en proceso de mejora para este filtro.")
        else:
            if st.session_state.role == "admin":
                st.dataframe(df)
            else:
                st.dataframe(df.head(3))
                st.markdown(
                    "🔓 **Acceso completo:** "
                    "[Adquirir data completa aquí](mailto:datacore.agrotech@gmail.com)"
                )

    # ---------------- CAMPO ----------------
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

        if dfc.empty:
            st.warning("📌 Información de campos en proceso de mejora.")
        else:
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
# FLUJO PRINCIPAL
# ======================================
if "user" not in st.session_state:
    auth_screen()
else:
    dashboard()
