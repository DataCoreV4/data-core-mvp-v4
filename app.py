import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import os
import unicodedata

# =====================================================
# CONFIG
# =====================================================
st.set_page_config("Data Core", layout="wide")

ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"
USERS_FILE = "users.csv"
CONTACT_EMAIL = "datacore.agrotech@gmail.com"

# =====================================================
# DRIVE MAP (NO SE TOCA)
# =====================================================
DRIVE_MAP = {  # ← exactamente igual, no se modifica
    "envios": {
        2021: {
            "uva": "https://drive.google.com/file/d/1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF/view",
            "mango": "https://drive.google.com/file/d/1k6CxjPufa0YF17e264BI8NYO1rFFZuc7/view",
            "arandano": "https://drive.google.com/file/d/1CyFQu-BdYNxFSoed9SGvKnkimrJjS2Q9/view",
            "limon": "https://drive.google.com/file/d/1--9cfYzrB2giYCy5khZmqXdXL_46Zuz8/view",
            "palta": "https://drive.google.com/file/d/1-BK3uEDMAMrTAdqxMJd-pIYCg0Rp-8kJ/view",
        },
        2022: {
            "uva": "https://drive.google.com/file/d/1wHxIXmn2stnjdFSnu8spnOSDw9Q45Dti/view",
            "mango": "https://drive.google.com/file/d/1kjtC1QVGe4w3GWEYhMmB9VD98eYjhvPh/view",
            "arandano": "https://drive.google.com/file/d/1tJRlp3FWvYZBr3LFPV1PFke3o6LZcOfa/view",
            "limon": "https://drive.google.com/file/d/1HfO0jh0yPXK99P8mQ080KLEevc4QVnLT/view",
            "palta": "https://drive.google.com/file/d/1IYS7yUDFmeCw3YyCIgKDbayZ63AORHvf/view",
        },
        2023: {
            "uva": "https://drive.google.com/file/d/1SZjCd3ANa4CF0N0lK_mnOQfzn0-ywTLs/view",
            "mango": "https://drive.google.com/file/d/1S5mMR3nG_DeH3ZpOqAvcjidzPQMW8kw_/view",
            "arandano": "https://drive.google.com/file/d/1JhAhZi3roOQpw5ejm3jnW5Av59De8wc2/view",
            "limon": "https://drive.google.com/file/d/1sGnvph11F431fg5v9c8qzoH-Yxytffti/view",
            "palta": "https://drive.google.com/file/d/1MCaBirErsv3PeJZ4soi2Fszw8QcJbg7w/view",
        },
        2024: {
            "uva": "https://drive.google.com/file/d/1csIY-AT7Uw6QFp49SANyHALHuZO3r65n/view",
            "mango": "https://drive.google.com/file/d/1In6_xnpKZwD1zTG4JrD3uhk7sYNKU4qF/view",
            "arandano": "https://drive.google.com/file/d/1CZSWhLV-STPw9k90cOVzQxJ0V2k7ZTUa/view",
            "limon": "https://drive.google.com/file/d/1XxGB8PGI4yh5K5mO5qGqRnSK_Fe2nPAX/view",
            "palta": "https://drive.google.com/file/d/1mLNGjAunM6HTiCnJIgEoaqZQEuegfSf9/view",
        },
        2025: {
            "uva": "https://drive.google.com/file/d/1iw-OafOHph_epXgf-6kreXhq2GxzNqyN/view",
            "mango": "https://drive.google.com/file/d/1-f5tlde1nBJnl_9BbRJkaDpGBleYtbyG/view",
            "arandano": "https://drive.google.com/file/d/1TxC9TwgFojnNRkQlOI27KJBzG0TK7tp7/view",
            "limon": "https://drive.google.com/file/d/1G8VbTnSeOcJJVDRkze9s12TRts5BvQx6/view",
            "palta": "https://drive.google.com/file/d/1Qt680UXFnKBh7bdV0iGqnJKKmc1suNVA/view",
        },
    },
    "campo": {
        2021: {
            "uva": "https://drive.google.com/file/d/1k6OMQxl7B3hVY9OVECc9UlYcytIjpN1A/view",
            "mango": "https://drive.google.com/file/d/1JX50r2NJYG3HjalUTZ5pCHmbD5DXQDUu/view",
            "arandano": "https://drive.google.com/file/d/1HOKP2FaW9UPRYyA7tIj0oSnGzUhkb3h4/view",
            "limon": "https://drive.google.com/file/d/12xOZVXqxvvepb97On1H8feKUoW_u1Qet/view",
            "palta": "https://drive.google.com/file/d/1ckjszJeuyPQS6oVNeWFd-FwoM8FTalHO/view",
        },
        2022: {
            "uva": "https://drive.google.com/file/d/1LS_80bCCgGE4flJ2BEzav1XeQQSrSX1y/view",
            "mango": "https://drive.google.com/file/d/16CDM3zQnH3S5n2SNjqwJmk0oUGkbxtJS/view",
            "arandano": "https://drive.google.com/file/d/1WTkBElLqv3aLQ8s2rkmlQqHM1zsKE33-/view",
            "limon": "https://drive.google.com/file/d/123wwsJLNrvlTxh2VRZQy1JpVOjI9Oj32/view",
            "palta": "https://drive.google.com/file/d/1uIs_MXnilSoPIGhtJtmOCv8N8un2VoFg/view",
        },
        2023: {
            "uva": "https://drive.google.com/file/d/11sb54WtgNe0poLSR4q-nEGvjMdbnjXiq/view",
            "mango": "https://drive.google.com/file/d/1qV3zoDQNnzeEvQR0eZ0FnrvxdkuruyUM/view",
            "arandano": "https://drive.google.com/file/d/1jdNrMyVcW2HV5PJI63_A_oxl6xLpapl7/view",
            "limon": "https://drive.google.com/file/d/1F708yJNg3mzrdHi53Dmw4RQZkTqUh4YH/view",
            "palta": "https://drive.google.com/file/d/1ZBXYrxS4iJ-lUBPKAMtr4ZIWGf6Wh6ED/view",
        },
        2024: {
            "uva": "https://drive.google.com/file/d/15CoNL-b9tONKTjbj2rIy8cthyeVhsD_F/view",
            "mango": "https://drive.google.com/file/d/1T6OVYHVN6j57Km9Z8zWrKYMlzTUIeRes/view",
            "arandano": "https://drive.google.com/file/d/1YejBbqWi383QjeJntU-AaICQw0TOJyaV/view",
            "limon": "https://drive.google.com/file/d/1JH6oXdDP5z-JAQgu9WvT-ej1pCjnX6WS/view",
            "palta": "https://drive.google.com/file/d/1fxh3QgnZXzjkuqmwG4w9h1YjhK6PPvX9/view",
        },
        2025: {
            "uva": "https://drive.google.com/file/d/15R-9ECTNpSQM1FC8tFPUs0emE16H8cHT/view",
            "mango": "https://drive.google.com/file/d/11IziWG98PfqkSyTaK5GvKwU4NEC9LwXJ/view",
            "arandano": "https://drive.google.com/file/d/15w2FG2TT_qPfxEksBgcGbfPu67yNbvYT/view",
            "limon": "https://drive.google.com/file/d/178kHRjqLgs-EFUmzCsNclBKq-nYmVJPO/view",
            "palta": "https://drive.google.com/file/d/1fo9HKY9DSKAjgLVKsx2H0Y7f_YU4DwRT/view",
        },
    }
}

# =====================================================
# UTILIDADES
# =====================================================
MESES_MAP = {
    "ene":1,"feb":2,"mar":3,"abr":4,"may":5,"jun":6,
    "jul":7,"ago":8,"sep":9,"oct":10,"nov":11,"dic":12
}

def normalize(text):
    return unicodedata.normalize("NFKD", text).encode("ascii","ignore").decode().lower()

def detect_mes_column(df):
    for c in df.columns:
        c_norm = normalize(c)
        if "mes" in c_norm:
            return c
    return None

def normalize_mes(val):
    if pd.isna(val):
        return None
    if isinstance(val, (int,float)):
        return int(val)
    v = str(val).lower()[:3]
    return MESES_MAP.get(v)

# =====================================================
# DRIVE
# =====================================================
def drive_download(url):
    file_id = url.split("/d/")[1].split("/")[0]
    return f"https://drive.google.com/uc?id={file_id}"

def load_csv(url):
    r = requests.get(drive_download(url))
    r.raise_for_status()
    return pd.read_csv(BytesIO(r.content), sep=";", encoding="latin1", on_bad_lines="skip", low_memory=False)

# =====================================================
# USUARIOS
# =====================================================
def init_users():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=["usuario","password","rol"]).to_csv(USERS_FILE, index=False)
    df = pd.read_csv(USERS_FILE)
    df = df[df.usuario != ADMIN_USER]
    df = pd.concat([df, pd.DataFrame([{
        "usuario": ADMIN_USER,
        "password": ADMIN_PASS,
        "rol": "admin"
    }])], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)

# =====================================================
# SESIÓN
# =====================================================
if "logged" not in st.session_state:
    st.session_state.logged = False
    st.session_state.role = ""
    st.session_state.user = ""

# =====================================================
# AUTH
# =====================================================
def auth():
    st.title("🔐 Data Core – Acceso")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        df = pd.read_csv(USERS_FILE)
        ok = df[(df.usuario==u)&(df.password==p)]
        if not ok.empty:
            st.session_state.logged=True
            st.session_state.role=ok.iloc[0].rol
            st.session_state.user=u
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# =====================================================
# DASHBOARD
# =====================================================
def dashboard():
    st.markdown(f"👋 **Bienvenido, {st.session_state.user}**")

    producto = st.selectbox("Producto", ["uva","mango","arandano","limon","palta"])
    anio = st.selectbox("Año", sorted(DRIVE_MAP["envios"].keys()))

    mes_sel = st.selectbox(
        "Mes",
        ["Todos"] + ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
    )

    # ---------------- ENVÍOS ----------------
    st.subheader("📦 Envíos")
    try:
        df = load_csv(DRIVE_MAP["envios"][anio][producto])
        col_mes = detect_mes_column(df)
        if col_mes and mes_sel!="Todos":
            df["_mes"] = df[col_mes].apply(normalize_mes)
            df = df[df["_mes"]==MESES_MAP[mes_sel.lower()[:3]]]
        st.dataframe(df if st.session_state.role=="admin" else df.head(3))
    except:
        st.info("📌 Información en proceso de mejora")

    # ---------------- CAMPOS ----------------
    st.subheader("🌾 Campos certificados")
    try:
        dfc = load_csv(DRIVE_MAP["campo"][anio][producto])
        col_mes = detect_mes_column(dfc)
        if col_mes and mes_sel!="Todos":
            dfc["_mes"] = dfc[col_mes].apply(normalize_mes)
            dfc = dfc[dfc["_mes"]==MESES_MAP[mes_sel.lower()[:3]]]
        st.dataframe(dfc if st.session_state.role=="admin" else dfc.head(3))
    except:
        st.info("📌 Información de campos en proceso de mejora")

# =====================================================
# MAIN
# =====================================================
init_users()

if not st.session_state.logged:
    auth()
else:
    dashboard()
