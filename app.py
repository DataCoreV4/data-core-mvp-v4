import streamlit as st
import pandas as pd
import hashlib
import os

# ======================================================
# CONFIGURACIÓN
# ======================================================
st.set_page_config(page_title="Data Core – MVP", layout="wide")

USERS_FILE = "users.csv"

ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"

USER_COLUMNS = [
    "usuario", "password", "nombre", "apellido", "dni",
    "correo", "celular", "empresa", "cargo", "tipo"
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

    # normalizar estructura antigua
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

    admin_row = {
        "usuario": ADMIN_USER,
        "password": hash_pass(ADMIN_PASS),
        "nombre": "Administrador",
        "apellido": "Data Core",
        "dni": "",
        "correo": "admin@datacore.pe",
        "celular": "",
        "empresa": "Data Core",
        "cargo": "Administrador",
        "tipo": "admin"
    }

    if (df["usuario"] == ADMIN_USER).any():
        # ✅ asignación correcta columna por columna
        for col, val in admin_row.items():
            df.loc[df["usuario"] == ADMIN_USER, col] = val
    else:
        df = pd.concat([df, pd.DataFrame([admin_row])], ignore_index=True)

    save_users(df)

# ======================================================
# AUTENTICACIÓN
# ======================================================
def auth_screen():
    st.title("🔐 Data Core – Acceso")

    tab_login, tab_register = st.tabs(["Ingresar", "Registrarse"])

    # ---------- LOGIN ----------
    with tab_login:
        user = st.text_input("Usuario", key="login_user")
        pwd = st.text_input("Contraseña", type="password", key="login_pass")

        if st.button("Ingresar", key="login_btn"):
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
                st.success("Ingreso exitoso")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    # ---------- REGISTRO ----------
    with tab_register:
        st.subheader("Registro")

        r_user = st.text_input("Usuario", key="reg_user")
        r_pwd1 = st.text_input("Contraseña", type="password", key="reg_pass1")
        r_pwd2 = st.text_input("Repetir contraseña", type="password", key="reg_pass2")
        nombre = st.text_input("Nombre", key="reg_nombre")
        apellido = st.text_input("Apellido", key="reg_apellido")
        dni = st.text_input("DNI", key="reg_dni")
        correo = st.text_input("Correo electrónico", key="reg_correo")
        celular = st.text_input("Celular", key="reg_celular")
        empresa = st.text_input("Empresa (opcional)", key="reg_empresa")
        cargo = st.text_input("Cargo (opcional)", key="reg_cargo")

        if st.button("Registrarse", key="reg_btn"):
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
# DASHBOARD BASE (no toca data)
# ======================================================
def dashboard():
    st.markdown(f"### 👋 Bienvenido, **{st.session_state.nombre}**")
    st.info("Dashboard base estable. Data se reconecta después.")

    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

# ======================================================
# MAIN
# ======================================================
ensure_admin()

if "user" not in st.session_state:
    auth_screen()
else:
    dashboard()
