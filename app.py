import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import os

# =====================================================
# CONFIG
# =====================================================
st.set_page_config("Data Core", layout="wide")

ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"
USERS_FILE = "users.csv"

# =====================================================
# DRIVE MAP (EXPLÍCITO – COMO YA FUNCIONABA)
# =====================================================
DRIVE_MAP = {
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
    }
}

# =====================================================
# UTILIDADES
# =====================================================
def drive_download(url):
    file_id = url.split("/d/")[1].split("/")[0]
    return f"https://drive.google.com/uc?id={file_id}"

def load_csv(url):
    r = requests.get(drive_download(url))
    r.raise_for_status()
    return pd.read_csv(BytesIO(r.content), encoding="latin1", on_bad_lines="skip", low_memory=False)

# =====================================================
# USUARIOS
# =====================================================
def init_users():
    cols = ["usuario","password","rol","nombre","apellido","dni","email","celular","empresa","cargo"]
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=cols).to_csv(USERS_FILE, index=False)

    df = pd.read_csv(USERS_FILE)
    df = df[df.usuario != ADMIN_USER]

    admin = {
        "usuario": ADMIN_USER,
        "password": ADMIN_PASS,
        "rol": "admin",
        "nombre": "Administrador",
        "apellido": "DataCore",
        "dni":"","email":"","celular":"","empresa":"","cargo":""
    }
    df = pd.concat([df, pd.DataFrame([admin])], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)

# =====================================================
# SESIÓN
# =====================================================
if "logged" not in st.session_state:
    st.session_state.logged = False
    st.session_state.user = ""
    st.session_state.role = ""

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
            st.session_state.logged = True
            st.session_state.user = u
            st.session_state.role = ok.iloc[0].rol
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# =====================================================
# DASHBOARD
# =====================================================
def dashboard():
    st.success(f"👋 Bienvenido, {st.session_state.user}")

    producto = st.selectbox("Producto", ["uva","mango","arandano","limon","palta"])
    anio = st.selectbox("Año", sorted(DRIVE_MAP["envios"].keys()))
    mes = st.selectbox("Mes", ["Todos"])

    st.subheader("📦 Envíos")
    try:
        df = load_csv(DRIVE_MAP["envios"][anio][producto])
        st.dataframe(df if st.session_state.role=="admin" else df.head(3))
    except Exception:
        st.info("📌 Información en proceso de mejora")

    st.subheader("🌾 Campos certificados")
    try:
        dfc = load_csv(DRIVE_MAP["campo"][anio][producto])
        st.dataframe(dfc if st.session_state.role=="admin" else dfc.head(3))
    except Exception:
        st.info("📌 Información de campos en proceso de mejora")

# =====================================================
# MAIN
# =====================================================
init_users()

if not st.session_state.logged:
    auth()
else:
    dashboard()
