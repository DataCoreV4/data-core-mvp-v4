import streamlit as st
import pandas as pd
import os

# =========================================
# CONFIGURACIÓN
# =========================================
st.set_page_config(page_title="Data Core – Acceso", layout="centered")

USERS_FILE = "users.csv"

ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"

# =========================================
# INICIALIZACIÓN DE USUARIOS
# =========================================
def init_users():
    columns = [
        "usuario", "password", "rol",
        "nombre", "apellido", "dni",
        "email", "celular", "empresa", "cargo"
    ]

    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=columns)
        df.to_csv(USERS_FILE, index=False)

    df = pd.read_csv(USERS_FILE)

    # 🔥 FORZAR ADMIN SIEMPRE
    df = df[df["usuario"] != ADMIN_USER]

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
    df.to_csv(USERS_FILE, index=False)

# =========================================
# SESIÓN
# =========================================
if "logged" not in st.session_state:
    st.session_state.logged = False
    st.session_state.user = ""
    st.session_state.role = ""

# =========================================
# LOGIN / REGISTRO
# =========================================
def auth():
    st.title("🔐 Data Core – Acceso")

    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

    # ---------- LOGIN ----------
    with tab1:
        user = st.text_input("Usuario", key="login_user")
        pwd = st.text_input("Contraseña", type="password", key="login_pass")

        if st.button("Ingresar"):
            df = pd.read_csv(USERS_FILE)
            ok = df[(df.usuario == user) & (df.password == pwd)]

            if not ok.empty:
                st.session_state.logged = True
                st.session_state.user = user
                st.session_state.role = ok.iloc[0]["rol"]
                st.success("Ingreso exitoso")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    # ---------- REGISTRO ----------
    with tab2:
        with st.form("register"):
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

                df = pd.read_csv(USERS_FILE)

                if usuario in df.usuario.values:
                    st.error("El usuario ya existe")
                    return

                new = {
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

                df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
                df.to_csv(USERS_FILE, index=False)

                st.success("Registro exitoso. Ya puedes ingresar.")

# =========================================
# DASHBOARD BASE
# =========================================
def dashboard():
    st.success(f"👋 Bienvenido, {st.session_state.user}")

    if st.session_state.role == "admin":
        st.info("Acceso administrador completo")
    else:
        st.info("Acceso freemium (limitado)")

    st.divider()

    st.warning("Dashboard base estable. La conexión con Drive y filtros avanzados se activarán en la siguiente capa.")

    if st.button("Cerrar sesión"):
        st.session_state.logged = False
        st.session_state.user = ""
        st.session_state.role = ""
        st.rerun()

# =========================================
# MAIN
# =========================================
init_users()

if not st.session_state.logged:
    auth()
else:
    dashboard()
