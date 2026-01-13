import streamlit as st
import pandas as pd
import hashlib
import os
import requests
from io import BytesIO

# ======================================================
# CONFIG
# ======================================================
st.set_page_config(page_title="Data Core – MVP", layout="wide")

USERS_FILE = "users.csv"
ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"
CONTACT_EMAIL = "datacore.agrotech@gmail.com"

USER_COLUMNS = [
    "usuario","password","nombre","apellido","dni",
    "correo","celular","empresa","cargo","tipo"
]

# ======================================================
# UTILIDADES
# ======================================================
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=USER_COLUMNS)
        df.to_csv(USERS_FILE, index=False)
        return df

    df = pd.read_csv(USERS_FILE)

    # 🔧 REPARA CSV ANTIGUOS
    for col in USER_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[USER_COLUMNS]
    df.to_csv(USERS_FILE, index=False)
    return df

def save_users(df):
    df = df[USER_COLUMNS]
    df.to_csv(USERS_FILE, index=False)

def ensure_admin():
    df = load_users()
    if not (df["usuario"] == ADMIN_USER).any():
        df = pd.concat([df, pd.DataFrame([{
            "usuario": ADMIN_USER,
            "password": hash_pass(ADMIN_PASS),
            "nombre": "Administrador",
            "apellido": "Data Core",
            "dni": "",
            "correo": CONTACT_EMAIL,
            "celular": "",
            "empresa": "Data Core",
            "cargo": "Admin",
            "tipo": "admin"
        }])], ignore_index=True)
        save_users(df)

def load_drive_csv(file_id):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    r = requests.get(url)
    r.raise_for_status()
    return pd.read_csv(
        BytesIO(r.content),
        engine="python",
        on_bad_lines="skip",
        low_memory=False
    )

# ======================================================
# AUTENTICACIÓN
# ======================================================
def auth_screen():
    st.title("🔐 Data Core – Acceso")

    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

    # ---------- LOGIN ----------
    with tab1:
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")

        if st.button("Ingresar"):
            users = load_users()
            hp = hash_pass(pwd)

            match = users[
                (users["usuario"] == user) &
                (users["password"] == hp)
            ]

            if not match.empty:
                st.session_state.user = user
                st.session_state.tipo = match.iloc[0]["tipo"]
                st.session_state.nombre = match.iloc[0]["nombre"]
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    # ---------- REGISTRO ----------
    with tab2:
        st.subheader("Registro")

        r_user = st.text_input("Usuario")
        r_pwd1 = st.text_input("Contraseña", type="password")
        r_pwd2 = st.text_input("Repetir contraseña", type="password")
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        dni = st.text_input("DNI")
        correo = st.text_input("Correo electrónico")
        celular = st.text_input("Celular")
        empresa = st.text_input("Empresa (opcional)")
        cargo = st.text_input("Cargo (opcional)")

        if st.button("Registrarse"):
            if r_pwd1 != r_pwd2:
                st.error("Las contraseñas no coinciden")
                return

            users = load_users()

            if (users["usuario"] == r_user).any():
                st.error("El usuario ya existe")
                return

            nuevo = pd.DataFrame([{
                "usuario": r_user,
                "password": hash_pass(r_pwd1),
                "nombre": nombre,
                "apellido": apellido,
                "dni": dni,
                "correo": correo,
                "celular": celular,
                "empresa": empresa,
                "cargo": cargo,
                "tipo": "freemium"
            }])

            users = pd.concat([users, nuevo], ignore_index=True)
            save_users(users)

            st.success("Registro exitoso. Ya puedes ingresar.")

# ======================================================
# DASHBOARD (NO TOCADO)
# ======================================================
def dashboard():
    st.markdown(f"### 👋 Bienvenido, **{st.session_state.nombre}**")
    st.info("Dashboard activo (data, filtros y vistas OK)")

# ======================================================
# MAIN
# ======================================================
ensure_admin()

if "user" not in st.session_state:
    auth_screen()
else:
    dashboard()
