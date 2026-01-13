import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import os

st.set_page_config(page_title="Data Core", layout="wide")

# =========================
# CONFIGURACIÓN GENERAL
# =========================
ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"
USERS_FILE = "users.csv"

# =========================
# MAPA DRIVE (CONFIRMADO)
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
}

# =========================
# UTILIDADES
# =========================
def drive_download(file_id):
    url = f"https://drive.google.com/uc?id={file_id}"
    r = requests.get(url)
    r.raise_for_status()
    return r.content

def load_csv_from_drive(file_id):
    try:
        content = drive_download(file_id)
        return pd.read_csv(BytesIO(content), sep=",", encoding="utf-8", engine="python")
    except Exception:
        try:
            return pd.read_csv(BytesIO(content), sep=";", encoding="latin1", engine="python")
        except Exception:
            return None

# =========================
# USUARIOS
# =========================
def load_users():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=[
            "usuario", "password", "rol",
            "nombre", "apellido", "dni",
            "correo", "celular", "empresa", "cargo"
        ])
        df.to_csv(USERS_FILE, index=False)

    return pd.read_csv(USERS_FILE)

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

def ensure_admin():
    df = load_users()
    if ADMIN_USER not in df["usuario"].values:
        admin = pd.DataFrame([{
            "usuario": ADMIN_USER,
            "password": ADMIN_PASS,
            "rol": "admin",
            "nombre": "Administrador",
            "apellido": "",
            "dni": "",
            "correo": "",
            "celular": "",
            "empresa": "Data Core",
            "cargo": "Admin"
        }])
        df = pd.concat([df, admin], ignore_index=True)
        save_users(df)

# =========================
# AUTH
# =========================
def auth_screen():
    st.title("🔐 Data Core – Acceso")

    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

    with tab1:
        u = st.text_input("Usuario", key="login_user")
        p = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Ingresar"):
            users = load_users()
            ok = users[(users.usuario == u) & (users.password == p)]
            if not ok.empty:
                st.session_state.user = ok.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    with tab2:
        st.subheader("Registro")
        data = {
            "usuario": st.text_input("Usuario"),
            "password": st.text_input("Contraseña", type="password"),
            "password2": st.text_input("Repetir contraseña", type="password"),
            "nombre": st.text_input("Nombre"),
            "apellido": st.text_input("Apellido"),
            "dni": st.text_input("DNI"),
            "correo": st.text_input("Correo electrónico"),
            "celular": st.text_input("Celular"),
            "empresa": st.text_input("Empresa (opcional)"),
            "cargo": st.text_input("Cargo (opcional)")
        }

        if st.button("Registrar"):
            if data["password"] != data["password2"]:
                st.error("Las contraseñas no coinciden")
                return

            users = load_users()
            if data["usuario"] in users.usuario.values:
                st.error("Usuario ya existe")
                return

            new = pd.DataFrame([{
                "usuario": data["usuario"],
                "password": data["password"],
                "rol": "freemium",
                "nombre": data["nombre"],
                "apellido": data["apellido"],
                "dni": data["dni"],
                "correo": data["correo"],
                "celular": data["celular"],
                "empresa": data["empresa"],
                "cargo": data["cargo"]
            }])

            users = pd.concat([users, new], ignore_index=True)
            save_users(users)
            st.success("Registro exitoso. Ahora puede ingresar.")

# =========================
# DASHBOARD
# =========================
def dashboard():
    user = st.session_state.user
    st.markdown(f"## 👋 Bienvenido, {user['nombre'] or user['usuario']}")

    colf = st.columns(3)
    producto = colf[0].selectbox("Producto", ["uva", "mango", "arandano", "limon", "palta"])
    año = colf[1].selectbox("Año", [2021, 2022, 2023, 2024, 2025])
    mes = colf[2].selectbox("Mes", ["Todos"] + list(range(1, 13)))

    col1, col2 = st.columns(2)

    # ========= ENVIOS =========
    with col1:
        st.subheader("📦 Envíos")
        key = (año, "envios", producto)
        if key not in DRIVE_MAP:
            st.info("📌 Información en proceso de mejora.")
        else:
            df = load_csv_from_drive(DRIVE_MAP[key])
            if df is None or df.empty:
                st.info("📌 Información en proceso de mejora.")
            else:
                if user["rol"] != "admin":
                    df = df.head(3)
                st.dataframe(df)
                if user["rol"] != "admin":
                    st.markdown("🔓 **Acceso completo: escribir a datacore.agrotech@gmail.com**")

    # ========= CAMPO =========
    with col2:
        st.subheader("🌾 Campos certificados")
        key = (año, "campo", producto)
        if key not in DRIVE_MAP:
            st.info("📌 Información de campos en proceso de mejora.")
        else:
            df = load_csv_from_drive(DRIVE_MAP[key])
            if df is None or df.empty:
                st.info("📌 Información de campos en proceso de mejora.")
            else:
                if user["rol"] != "admin":
                    df = df.head(3)
                st.dataframe(df)
                if user["rol"] != "admin":
                    st.markdown("🔓 **Acceso completo: escribir a datacore.agrotech@gmail.com**")

    # ========= ADMIN =========
    if user["rol"] == "admin":
        st.divider()
        st.subheader("🛠 Gestión de usuarios")
        users = load_users()
        st.dataframe(users[["usuario", "rol", "correo"]])
        sel = st.selectbox("Cambiar rol de usuario", users.usuario)
        new_role = st.selectbox("Nuevo rol", ["freemium", "premium"])
        if st.button("Actualizar rol"):
            users.loc[users.usuario == sel, "rol"] = new_role
            save_users(users)
            st.success("Rol actualizado")

# =========================
# MAIN
# =========================
ensure_admin()

if "user" not in st.session_state:
    auth_screen()
else:
    dashboard()
