import streamlit as st
import pandas as pd
import os

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(page_title="Data Core – MVP", layout="wide")

USERS_FILE = "usuarios.csv"

ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"
ADMIN_NOMBRE = "Administrador"

PRODUCTOS = ["uva", "mango", "arandano", "limon", "palta"]
ANIOS = [2021, 2022, 2023, 2024, 2025]
MESES = ["Todos"] + list(range(1, 13))


# ---------------- UTILIDADES ----------------
def load_users():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=[
            "usuario", "password", "nombre", "apellido",
            "dni", "correo", "celular",
            "empresa", "cargo", "tipo"
        ])
        df.to_csv(USERS_FILE, index=False)
    return pd.read_csv(USERS_FILE)


def save_users(df):
    df.to_csv(USERS_FILE, index=False)


def ensure_admin():
    df = load_users()
    if "usuario" not in df.columns:
        return

    if not (df["usuario"] == ADMIN_USER).any():
        admin_row = pd.DataFrame([{
            "usuario": ADMIN_USER,
            "password": ADMIN_PASS,
            "nombre": ADMIN_NOMBRE,
            "apellido": "",
            "dni": "",
            "correo": "",
            "celular": "",
            "empresa": "",
            "cargo": "",
            "tipo": "admin"
        }])
        df = pd.concat([df, admin_row], ignore_index=True)
        save_users(df)


# ---------------- AUTENTICACIÓN ----------------
def auth_screen():
    st.title("🔐 Data Core – Acceso")

    tab_login, tab_register = st.tabs(["Ingresar", "Registrarse"])

    with tab_login:
        username = st.text_input("Usuario", key="login_user")
        password = st.text_input("Contraseña", type="password", key="login_pass")

        if st.button("Ingresar"):
            users = load_users()
            match = users[
                (users["usuario"] == username) &
                (users["password"] == password)
            ]

            if not match.empty:
                st.session_state.auth = True
                st.session_state.user = username
                st.session_state.tipo = match.iloc[0]["tipo"]
                st.session_state.nombre = match.iloc[0]["nombre"]
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    with tab_register:
        st.subheader("Registro")

        r_user = st.text_input("Usuario", key="reg_user")
        r_pass = st.text_input("Contraseña", type="password", key="reg_pass")
        r_pass2 = st.text_input("Repetir contraseña", type="password", key="reg_pass2")
        r_nombre = st.text_input("Nombre")
        r_apellido = st.text_input("Apellido")
        r_dni = st.text_input("DNI")
        r_correo = st.text_input("Correo electrónico")
        r_cel = st.text_input("Celular")
        r_empresa = st.text_input("Empresa (opcional)")
        r_cargo = st.text_input("Cargo (opcional)")

        if st.button("Registrar"):
            if r_pass != r_pass2:
                st.error("Las contraseñas no coinciden")
                return

            users = load_users()

            if (users["usuario"] == r_user).any():
                st.error("El usuario ya existe")
                return

            new_row = pd.DataFrame([{
                "usuario": r_user,
                "password": r_pass,
                "nombre": r_nombre,
                "apellido": r_apellido,
                "dni": r_dni,
                "correo": r_correo,
                "celular": r_cel,
                "empresa": r_empresa,
                "cargo": r_cargo,
                "tipo": "freemium"
            }])

            users = pd.concat([users, new_row], ignore_index=True)
            save_users(users)
            st.success("Registro exitoso. Ahora puedes ingresar.")


# ---------------- DASHBOARD ----------------
def dashboard():
    st.markdown(f"### 👋 Bienvenido, **{st.session_state.nombre}**")

    # -------- FILTROS GENERALES --------
    col1, col2, col3 = st.columns(3)

    with col1:
        producto = st.selectbox("Producto", PRODUCTOS)
    with col2:
        anio = st.selectbox("Año", ANIOS)
    with col3:
        mes = st.selectbox("Mes", MESES)

    st.divider()

    # -------- SECCIÓN ENVÍOS --------
    st.subheader("📦 Envíos")

    st.info("📌 Información en proceso de mejora para este producto/año.")

    # -------- SECCIÓN CAMPOS --------
    st.subheader("🌾 Campos certificados")

    st.info("📌 Información de campos en proceso de mejora.")

    # -------- FREEMIUM --------
    if st.session_state.tipo != "admin":
        st.warning(
            "🔒 Acceso limitado. "
            "Para ver la data completa, escríbenos a "
            "**datacore.agrotech@gmail.com**"
        )

    # -------- ADMIN --------
    if st.session_state.tipo == "admin":
        st.divider()
        st.subheader("🛠 Gestión de usuarios")

        users = load_users()
        st.dataframe(users, use_container_width=True)


# ---------------- MAIN ----------------
ensure_admin()

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    auth_screen()
else:
    dashboard()
