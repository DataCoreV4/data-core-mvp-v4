import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import os
import unicodedata

# ================= CONFIG =================
st.set_page_config(page_title="Data Core", layout="wide")

LOGO_PATH = "logotipo_datacore.jpg"
USERS_FILE = "users.csv"
ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"
CONTACT_EMAIL = "datacore.agrotech@gmail.com"

# ================= UTILIDADES =================
def normalize(text):
    if pd.isna(text):
        return ""
    text = str(text)
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.lower().strip()

def ensure_users_file():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame([{
            "usuario": ADMIN_USER,
            "password": ADMIN_PASS,
            "nombre": "Administrador",
            "apellido": "DataCore",
            "correo": CONTACT_EMAIL,
            "tipo": "admin"
        }])
        df.to_csv(USERS_FILE, index=False)

def load_users():
    ensure_users_file()
    return pd.read_csv(USERS_FILE)

def save_user(row):
    df = load_users()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)

def is_admin():
    return st.session_state.get("user_tipo") == "admin"

# ================= DRIVE MAP =================
DRIVE_MAP = {
    ("envios","uva",2021):"1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF",
    ("envios","mango",2021):"1k6CxjPufa0YF17e264BI8NYO1rFFZuc7",
    ("envios","arandano",2021):"1CyFQu-BdYNxFSoed9SGvKnkimrJjS2Q9",
    ("envios","limon",2021):"1--9cfYzrB2giYCy5khZmqXdXL_46Zuz8",
    ("envios","palta",2021):"1-BK3uEDMAMrTAdqxMJd-pIYCg0Rp-8kJ",
    ("campo","uva",2021):"1k6OMQxl7B3hVY9OVECc9UlYcytIjpN1A",
    ("campo","mango",2021):"1JX50r2NJYG3HjalUTZ5pCHmbD5DXQDUu",
    ("campo","arandano",2021):"1HOKP2FaW9UPRYyA7tIj0oSnGzUhkb3h4",
    ("campo","limon",2021):"12xOZVXqxvvepb97On1H8feKUoW_u1Qet",
    ("campo","palta",2021):"1ckjszJeuyPQS6oVNeWFd-FwoM8FTalHO",
    # 👉 (El resto YA FUNCIONA igual, puedes seguir ampliando aquí)
}

def load_drive_csv(file_id):
    url = f"https://drive.google.com/uc?id={file_id}"
    r = requests.get(url)
    return pd.read_csv(
        BytesIO(r.content),
        sep=",",
        encoding="utf-8",
        on_bad_lines="skip",
        low_memory=False
    )

# ================= AUTH =================
def auth_screen():
    st.title("🔐 Data Core – Acceso")

    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

    with tab1:
        user = st.text_input("Usuario", key="login_user")
        pwd = st.text_input("Contraseña", type="password", key="login_pass")

        if st.button("Ingresar"):
            users = load_users()
            match = users[(users.usuario == user) & (users.password == pwd)]
            if not match.empty:
                st.session_state["logged"] = True
                st.session_state["user"] = user
                st.session_state["user_tipo"] = match.iloc[0]["tipo"]
                st.session_state["nombre"] = match.iloc[0]["nombre"]
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

    with tab2:
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        correo = st.text_input("Correo")
        usuario = st.text_input("Usuario nuevo")
        password = st.text_input("Contraseña", type="password")

        if st.button("Registrarse"):
            save_user({
                "usuario": usuario,
                "password": password,
                "nombre": nombre,
                "apellido": apellido,
                "correo": correo,
                "tipo": "freemium"
            })
            st.success("Registro exitoso. Ya puedes ingresar.")

# ================= DASHBOARD =================
def dashboard():
    st.image(LOGO_PATH, width=140)
    st.markdown(f"### 👋 Bienvenido, **{st.session_state['nombre']}**")

    productos = ["uva","mango","arandano","limon","palta"]
    años = [2021,2022,2023,2024,2025]

    producto = normalize(st.selectbox("Producto", productos))
    año = st.selectbox("Año", años)
    mes = st.selectbox("Mes", ["Todos"] + list(range(1,13)))

    col1, col2 = st.columns(2)

    # ===== ENVIOS =====
    with col1:
        st.subheader("📦 Envíos")
        key = ("envios", producto, año)

        if key not in DRIVE_MAP:
            st.info("📌 Información en proceso de mejora.")
        else:
            try:
                df = load_drive_csv(DRIVE_MAP[key])
                df.columns = [normalize(c) for c in df.columns]

                if mes != "Todos":
                    for c in df.columns:
                        if "mes" in c:
                            df = df[df[c] == mes]

                if not is_admin():
                    df = df.head(3)

                st.dataframe(df, use_container_width=True)

                if not is_admin():
                    st.markdown(
                        f"🔓 **Acceso completo:** "
                        f"[Adquirir data completa aquí](mailto:{CONTACT_EMAIL})"
                    )
            except:
                st.error("Error cargando data")

    # ===== CAMPO =====
    with col2:
        st.subheader("🌾 Campos certificados")
        key = ("campo", producto, año)

        if key not in DRIVE_MAP:
            st.info("📌 Información de campos en proceso de mejora.")
        else:
            try:
                df = load_drive_csv(DRIVE_MAP[key])
                df.columns = [normalize(c) for c in df.columns]

                if mes != "Todos":
                    for c in df.columns:
                        if "mes" in c:
                            df = df[df[c] == mes]

                if not is_admin():
                    df = df.head(3)

                st.dataframe(df, use_container_width=True)

                if not is_admin():
                    st.markdown(
                        f"🔓 **Acceso completo:** "
                        f"[Adquirir data completa aquí](mailto:{CONTACT_EMAIL})"
                    )
            except:
                st.error("Error cargando data")

    if is_admin():
        st.divider()
        st.subheader("🛠 Gestión de usuarios")
        st.dataframe(load_users())

# ================= MAIN =================
ensure_users_file()

if "logged" not in st.session_state:
    st.session_state["logged"] = False

if not st.session_state["logged"]:
    auth_screen()
else:
    dashboard()

st.markdown("✅ **Data Core – MVP estable | Escalable | Compatible con 13G**")
