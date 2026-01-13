import streamlit as st
import pandas as pd
import os
import hashlib

# =============================
# CONFIG GENERAL
# =============================
st.set_page_config(page_title="Data Core", layout="wide")

LOGO_PATH = "logo_datacore.jpg"
AUTH_DIR = "auth"
USERS_FILE = f"{AUTH_DIR}/users.csv"

ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"
CONTACT_EMAIL = "datacore.agrotech@gmail.com"

# =============================
# AUTH UTILITIES
# =============================
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def init_auth():
    os.makedirs(AUTH_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame([{
            "username": ADMIN_USER,
            "password": hash_pass(ADMIN_PASS),
            "role": "admin",
            "is_premium": True,
            "nombres": "Data",
            "apellidos": "Core",
            "dni": "00000000",
            "email": CONTACT_EMAIL
        }])
        df.to_csv(USERS_FILE, index=False)

def load_users():
    return pd.read_csv(USERS_FILE)

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

# =============================
# LOGIN / REGISTER
# =============================
def auth_screen():
    st.title("🔐 Data Core – Acceso")

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
        st.subheader("Registro de usuario")

        nombres = st.text_input("Nombres")
        apellidos = st.text_input("Apellidos")
        dni = st.text_input("DNI")
        email = st.text_input("Correo electrónico")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Registrar"):
            users = load_users()

            if username in users["username"].values:
                st.warning("El usuario ya existe")
                return

            new_user = pd.DataFrame([{
                "username": username,
                "password": hash_pass(password),
                "role": "user",
                "is_premium": False,
                "nombres": nombres,
                "apellidos": apellidos,
                "dni": dni,
                "email": email
            }])

            users = pd.concat([users, new_user], ignore_index=True)
            save_users(users)

            st.success("Registro exitoso. Ya puedes ingresar.")

# =============================
# SIDEBAR
# =============================
def sidebar():
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, use_container_width=True)

        st.markdown(
            f"### 👋 {st.session_state.user['nombres']} "
            f"{st.session_state.user['apellidos']}"
        )

        if st.session_state.user["role"] == "admin":
            st.caption("Administrador")
        else:
            st.caption(
                "Premium" if st.session_state.user["is_premium"] else "Freemium"
            )

        if st.button("Cerrar sesión"):
            st.session_state.clear()
            st.rerun()

# =============================
# FREEMIUM MESSAGE
# =============================
def freemium_cta():
    st.info(
        "🔓 **Acceso completo: Adquirir data completa aquí**\n\n"
        f"[Solicitar acceso](mailto:{CONTACT_EMAIL})"
    )

# =============================
# ACCESS CONTROL
# =============================
def apply_access(df):
    if st.session_state.user["role"] == "admin":
        return df

    if st.session_state.user["is_premium"]:
        return df

    freemium_cta()
    return df.head(3)

# =============================
# ADMIN PANEL
# =============================
def admin_panel():
    st.subheader("🛠 Gestión de usuarios")

    users = load_users()

    for i, row in users.iterrows():
        if row["role"] == "admin":
            continue

        c1, c2, c3 = st.columns([4, 2, 2])
        c1.write(f"{row['nombres']} {row['apellidos']}")
        c2.write("Premium" if row["is_premium"] else "Freemium")

        if c3.button("Cambiar estado", key=row["username"]):
            users.loc[i, "is_premium"] = not row["is_premium"]
            save_users(users)
            st.rerun()

# =============================
# MAIN APP
# =============================
init_auth()

if "user" not in st.session_state:
    auth_screen()
    st.stop()

sidebar()

# PANEL ADMIN
if st.session_state.user["role"] == "admin":
    admin_panel()

st.markdown("---")

# =============================
# ⬇⬇⬇ AQUÍ VA TU BLOQUE DE DATA
# =============================
# ⚠️ PEGA AQUÍ EXACTAMENTE
# EL BLOQUE QUE YA TE FUNCIONA:
#
# - Envíos
# - Campos certificados
# - Filtros
# - Carga desde Drive
#
# Y JUSTO ANTES DE MOSTRAR:
#   df = apply_access(df)
# =============================

st.caption("✅ Data Core – MVP estable | Escalable | Compatible con 13G")
