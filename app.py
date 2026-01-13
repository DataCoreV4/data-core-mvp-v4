import streamlit as st
import pandas as pd
import os

# =============================
# CONFIGURACIÓN GENERAL
# =============================
st.set_page_config(page_title="Data Core – Acceso", layout="centered")

USERS_FILE = "users.csv"

ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"

# =============================
# UTILIDADES
# =============================

def init_users_file():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=[
            "usuario", "password", "rol",
            "nombre", "apellido", "dni",
            "email", "celular", "empresa", "cargo"
        ])
        df.to_csv(USERS_FILE, index=False)

def load_users():
    return pd.read_csv(USERS_FILE)

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

def ensure_admin():
    df = load_users()
    if ADMIN_USER not in df["usuario"].values:
        admin_row = {
            "usuario": ADMIN_USER,
            "password": ADMIN_PASS,
            "rol": "admin",
            "nombre": "Administrador",
            "apellido": "DataCore",
            "dni": "",
            "email": "",
            "celular": "",
            "empresa": "",
            "cargo": ""
        }
        df = pd.concat([df, pd.DataFrame([admin_row])], ignore_index=True)
        save_users(df)

# =============================
# SESIÓN
# =============================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None

# =============================
# LOGIN / REGISTRO
# =============================

def auth_screen():
    st.title("🔐 Data Core – Acceso")

    tab_login, tab_register = st.tabs(["Ingresar", "Registrarse"])

    # -------- LOGIN --------
    with tab_login:
        username = st.text_input("Usuario", key="login_user")
        password = st.text_input("Contraseña", type="password", key="login_pass")

        if st.button("Ingresar"):
            df = load_users()
            match = df[
                (df["usuario"] == username) &
                (df["password"] == password)
            ]

            if not match.empty:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.session_state.role = match.iloc[0]["rol"]
                st.success("Ingreso exitoso")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    # -------- REGISTRO --------
    with tab_register:
        with st.form("register_form"):
            usuario = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            password2 = st.text_input("Repetir contraseña", type="password")

            nombre = st.text_input("Nombre")
            apellido = st.text_input("Apellido")
            dni = st.text_input("DNI")
            email = st.text_input("Correo electrónico")
            celular = st.text_input("Celular")
            empresa = st.text_input("Empresa (opcional)")
            cargo = st.text_input("Cargo (opcional)")

            submit = st.form_submit_button("Registrarse")

            if submit:
                if password != password2:
                    st.error("Las contraseñas no coinciden")
                    return

                df = load_users()
                if usuario in df["usuario"].values:
                    st.error("El usuario ya existe")
                    return

                new_user = {
                    "usuario": usuario,
                    "password": password,
                    "rol": "freemium",
                    "nombre": nombre,
                    "apellido": apellido,
                    "dni": dni,
                    "email": email,
                    "celular": celular,
                    "empresa": empresa,
                    "cargo": cargo
                }

                df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
                save_users(df)
                st.success("Registro exitoso. Ahora puedes ingresar.")

# =============================
# DASHBOARD BASE (VACÍO)
# =============================

def dashboard():
    st.success(f"👋 Bienvenido, {st.session_state.user}")

    if st.session_state.role == "admin":
        st.info("Modo administrador activo")
    else:
        st.info("Modo usuario freemium")

    st.warning("Dashboard base estable. Data se conectará en la siguiente capa.")

    if st.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.role = None
        st.rerun()

# =============================
# MAIN
# =============================

init_users_file()
ensure_admin()

if not st.session_state.logged_in:
    auth_screen()
else:
    dashboard()
