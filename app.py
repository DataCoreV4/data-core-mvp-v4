import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import os
import hashlib

st.set_page_config(page_title="Data Core", layout="wide")

# =========================
# CONFIGURACIÓN GENERAL
# =========================
ADMIN_USER = "DCADMIN"
ADMIN_PASS = hashlib.sha256("admindatacore123!".encode()).hexdigest()
USERS_FILE = "usuarios.csv"

# =========================
# MAPA GOOGLE DRIVE
# =========================
DRIVE_MAP = {
    (2021, "envios", "uva"): "1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF",
    (2021, "envios", "mango"): "1k6CxjPufa0YF17e264BI8NYO1rFFZuc7",
    (2021, "envios", "arandano"): "1CyFQu-BdYNxFSoed9SGvKnkimrJjS2Q9",
    (2021, "envios", "limon"): "1--9cfYzrB2giYCy5khZmqXdXL_46Zuz8",
    (2021, "envios", "palta"): "1-BK3uEDMAMrTAdqxMJd-pIYCg0Rp-8kJ",

    (2021, "campo", "uva"): "1k6OMQxl7B3hVY9OVECc9UlYcytIjpN1A",
    (2021, "campo", "mango"): "1JX50r2NJYG3HjalUTZ5pCHmbD5DXQDUu",
    (2021, "campo", "arandano"): "1HOKP2FaW9UPRYyA7tIj0oSnGzUhkb3h4",
    (2021, "campo", "limon"): "12xOZVXqxvvepb97On1H8feKUoW_u1Qet",
    (2021, "campo", "palta"): "1ckjszJeuyPQS6oVNeWFd-FwoM8FTalHO",

    (2022, "envios", "uva"): "1wHxIXmn2stnjdFSnu8spnOSDw9Q45Dti",
    (2022, "envios", "mango"): "1kjtC1QVGe4w3GWEYhMmB9VD98eYjhvPh",
    (2022, "envios", "arandano"): "1tJRlp3FWvYZBr3LFPV1PFke3o6LZcOfa",
    (2022, "envios", "limon"): "1HfO0jh0yPXK99P8mQ080KLEevc4QVnLT",
    (2022, "envios", "palta"): "1IYS7yUDFmeCw3YyCIgKDbayZ63AORHvf",

    (2022, "campo", "uva"): "1LS_80bCCgGE4flJ2BEzav1XeQQSrSX1y",
    (2022, "campo", "mango"): "16CDM3zQnH3S5n2SNjqwJmk0oUGkbxtJS",
    (2022, "campo", "arandano"): "1WTkBElLqv3aLQ8s2rkmlQqHM1zsKE33-",
    (2022, "campo", "limon"): "123wwsJLNrvlTxh2VRZQy1JpVOjI9Oj32",
    (2022, "campo", "palta"): "1uIs_MXnilSoPIGhtJtmOCv8N8un2VoFg",

    # (2023–2025 exactamente igual, ya puedes completarlos si deseas)
}

# =========================
# UTILIDADES
# =========================
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def load_drive_csv(file_id):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    r = requests.get(url)
    r.raise_for_status()
    return pd.read_csv(BytesIO(r.content), sep=",", encoding="utf-8", engine="python")

def normalize_month(m):
    if pd.isna(m):
        return None
    m = str(m).strip().lower()
    meses = {
        "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
        "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12
    }
    if m.isdigit():
        return int(m)
    return meses.get(m[:3])

# =========================
# USUARIOS
# =========================
def ensure_users():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame([{
            "usuario": ADMIN_USER,
            "password": ADMIN_PASS,
            "rol": "admin",
            "estado": "premium",
            "nombre": "Administrador"
        }])
        df.to_csv(USERS_FILE, index=False)

def load_users():
    ensure_users()
    return pd.read_csv(USERS_FILE)

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

# =========================
# AUTH
# =========================
def auth_screen():
    st.title("🔐 Data Core – Acceso")

    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

    users = load_users()

    with tab1:
        u = st.text_input("Usuario", key="login_user")
        p = st.text_input("Contraseña", type="password", key="login_pass")

        if st.button("Ingresar"):
            h = hash_pass(p)
            row = users[(users.usuario == u) & (users.password == h)]
            if not row.empty:
                st.session_state.user = row.iloc[0].to_dict()
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    with tab2:
        ru = st.text_input("Usuario", key="r_user")
        rp = st.text_input("Contraseña", type="password", key="r_pass")
        rpr = st.text_input("Repetir contraseña", type="password", key="r_pass2")
        rn = st.text_input("Nombre")
        ra = st.text_input("Apellido")
        rd = st.text_input("DNI")
        re = st.text_input("Correo electrónico")

        if st.button("Registrar"):
            if rp != rpr:
                st.error("Las contraseñas no coinciden")
            elif ru in users.usuario.values:
                st.error("Usuario ya existe")
            else:
                users.loc[len(users)] = {
                    "usuario": ru,
                    "password": hash_pass(rp),
                    "rol": "user",
                    "estado": "freemium",
                    "nombre": rn
                }
                save_users(users)
                st.success("Usuario registrado correctamente")

# =========================
# DASHBOARD
# =========================
def dashboard():
    user = st.session_state.user
    st.subheader(f"👋 Bienvenido, {user['nombre']}")

    producto = st.selectbox("Producto", ["uva", "mango", "arandano", "limon", "palta"])
    año = st.selectbox("Año", [2021, 2022, 2023, 2024, 2025])
    mes = st.selectbox("Mes", ["Todos"] + list(range(1, 13)))

    col1, col2 = st.columns(2)

    # -------- ENVÍOS --------
    with col1:
        st.markdown("### 📦 Envíos")
        key = (año, "envios", producto)
        if key in DRIVE_MAP:
            try:
                df = load_drive_csv(DRIVE_MAP[key])
                if mes != "Todos":
                    df["mes_norm"] = df.iloc[:, 0].apply(normalize_month)
                    df = df[df["mes_norm"] == mes]
                st.dataframe(df.head(3 if user["estado"] == "freemium" else None))
            except:
                st.info("📌 Información en proceso de mejora para este producto/año.")
        else:
            st.info("📌 Información en proceso de mejora para este producto/año.")

    # -------- CAMPOS --------
    with col2:
        st.markdown("### 🌾 Campos certificados")
        key = (año, "campo", producto)
        if key in DRIVE_MAP:
            try:
                df = load_drive_csv(DRIVE_MAP[key])
                if mes != "Todos":
                    df["mes_norm"] = df.iloc[:, 0].apply(normalize_month)
                    df = df[df["mes_norm"] == mes]
                st.dataframe(df.head(3 if user["estado"] == "freemium" else None))
            except:
                st.info("📌 Información de campos en proceso de mejora.")
        else:
            st.info("📌 Información de campos en proceso de mejora.")

    if user["estado"] == "freemium":
        st.warning("🔓 Para acceder a toda la data escribe a datacore.agrotech@gmail.com")

    if user["rol"] == "admin":
        st.markdown("### 🛠 Gestión de usuarios")
        st.dataframe(load_users())

# =========================
# MAIN
# =========================
ensure_users()

if "user" not in st.session_state:
    auth_screen()
else:
    dashboard()
