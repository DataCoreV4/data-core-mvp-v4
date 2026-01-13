import streamlit as st
import pandas as pd
import os
import hashlib

# =============================
# CONFIGURACIÓN GENERAL
# =============================
st.set_page_config(page_title="Data Core", layout="wide")

LOGO_PATH = "logo_datacore.jpg"
AUTH_DIR = "auth"
USERS_FILE = f"{AUTH_DIR}/users.csv"

ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"

CONTACT_EMAIL = "datacore.agrotech@gmail.com"

# =============================
# UTILIDADES AUTH
# =============================
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def init_auth():
    os.makedirs(AUTH_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame([
            {
                "username": ADMIN_USER,
                "password": hash_pass(ADMIN_PASS),
                "role": "admin",
                "is_premium": True
            }
        ])
        df.to_csv(USERS_FILE, index=False)

def load_users():
    return pd.read_csv(USERS_FILE)

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

# =============================
# LOGIN / REGISTRO
# =============================
def login_screen():
    st.title("🔐 Acceso a Data Core")

    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

    with tab1:
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            users = load_users()
            row = users[users["username"] == u]
            if not row.empty and row.iloc[0]["password"] == hash_pass(p):
                st.session_state.user = row.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

    with tab2:
        nu = st.text_input("Nuevo usuario")
        np = st.text_input("Nueva contraseña", type="password")
        if st.button("Registrarse"):
            users = load_users()
            if nu in users["username"].values:
                st.warning("Usuario ya existe")
            else:
                users = pd.concat([
                    users,
                    pd.DataFrame([{
                        "username": nu,
                        "password": hash_pass(np),
                        "role": "user",
                        "is_premium": False
                    }])
                ])
                save_users(users)
                st.success("Usuario creado. Ya puedes ingresar.")

# =============================
# SIDEBAR
# =============================
def sidebar():
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, use_container_width=True)

        st.markdown(f"### 👤 {st.session_state.user['username']}")
        st.caption(
            "Administrador" if st.session_state.user["role"] == "admin"
            else "Usuario"
        )

        if st.button("Cerrar sesión"):
            st.session_state.clear()
            st.rerun()

# =============================
# MENSAJE FREEMIUM
# =============================
def freemium_message():
    st.info(
        "🔓 **Acceso completo: Adquirir data completa aquí**\n\n"
        f"[Escríbenos a {CONTACT_EMAIL}](mailto:{CONTACT_EMAIL})"
    )

# =============================
# AQUÍ VA TU LÓGICA ACTUAL DE DATA
# (NO LA TOCO – SOLO LA USO)
# =============================

# ⚠️
# PEGA AQUÍ EXACTAMENTE
# EL BLOQUE DE CARGA DE DATA
# QUE YA TE FUNCIONA
# (DATA_MAP, load_csv_from_drive, filtros, etc.)
# ⚠️

# =============================
# APLICAR FREEMIUM
# =============================
def apply_access_control(df):
    if st.session_state.user["role"] == "admin":
        return df

    if st.session_state.user.get("is_premium", False):
        return df

    freemium_message()
    return df.head(3)

# =============================
# PANEL ADMIN
# =============================
def admin_panel():
    st.subheader("🛠 Gestión de usuarios")
    users = load_users()

    for i, row in users.iterrows():
        if row["role"] == "admin":
            continue

        col1, col2, col3 = st.columns([3, 2, 2])
        col1.write(row["username"])
        col2.write("Premium" if row["is_premium"] else "Freemium")

        if col3.button(
            "Cambiar estado",
            key=row["username"]
        ):
            users.loc[i, "is_premium"] = not row["is_premium"]
            save_users(users)
            st.rerun()

# =============================
# MAIN
# =============================
init_auth()

if "user" not in st.session_state:
    login_screen()
    st.stop()

sidebar()

if st.session_state.user["role"] == "admin":
    admin_panel()

st.markdown("---")
st.caption("✅ Data Core – MVP estable | Escalable | Compatible con 13G")
