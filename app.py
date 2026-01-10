import streamlit as st
import pandas as pd
import hashlib
import os

# ===============================
# CONFIGURACIÓN GENERAL
# ===============================
st.set_page_config(
    page_title="Data Core – Inteligencia Agroexportadora",
    layout="wide"
)

# ===============================
# FUNCIONES DE SEGURIDAD
# ===============================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ===============================
# CONFIGURACIÓN ADMIN
# ===============================
ADMIN_EMAIL = "admin@datacore.pe"
ADMIN_PASSWORD = hash_password("Admin2025!")

# ===============================
# USUARIOS
# ===============================
USERS_FILE = "usuarios.csv"

def cargar_usuarios():
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    return pd.DataFrame(columns=[
        "nombre","apellido","dni","correo",
        "celular","empresa","cargo","password"
    ])

def correo_existe(correo):
    return correo in cargar_usuarios()["correo"].values

def guardar_usuario(data):
    usuarios = cargar_usuarios()
    usuarios = pd.concat([usuarios, pd.DataFrame([data])], ignore_index=True)
    usuarios.to_csv(USERS_FILE, index=False)

def validar_login(correo, password):
    if correo == ADMIN_EMAIL and hash_password(password) == ADMIN_PASSWORD:
        st.session_state.admin = True
        return True

    usuarios = cargar_usuarios()
    pwd = hash_password(password)
    user = usuarios[
        (usuarios["correo"] == correo) &
        (usuarios["password"] == pwd)
    ]

    if not user.empty:
        st.session_state.admin = False
        return True

    return False

# ===============================
# SESIÓN
# ===============================
if "login" not in st.session_state:
    st.session_state.login = False

if "admin" not in st.session_state:
    st.session_state.admin = False

# ===============================
# PORTADA
# ===============================
if not st.session_state.login:

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if os.path.exists("logo_datacore.png"):
            try:
                st.image("logo_datacore.png", width=260)
            except:
                pass

        st.title("🌱 Data Core")
        st.subheader("Plataforma de inteligencia agroexportadora")
        st.markdown(
            "Análisis de **datos reales de certificaciones, inspecciones y exportaciones** "
            "para decisiones estratégicas del sector agroexportador."
        )

        opcion = st.radio("Acceso", ["Iniciar sesión", "Registrarse"])

        if opcion == "Iniciar sesión":
            correo = st.text_input("Correo electrónico")
            password = st.text_input("Contraseña", type="password")

            if st.button("Ingresar"):
                if validar_login(correo, password):
                    st.session_state.login = True
                    st.session_state.usuario = correo
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")

        else:
            st.markdown("### Registro")

            nombre = st.text_input("Nombre")
            apellido = st.text_input("Apellido")
            dni = st.text_input("DNI")
            correo = st.text_input("Correo electrónico")
            celular = st.text_input("Celular")
