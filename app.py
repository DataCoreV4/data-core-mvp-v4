import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import os

# ===============================
# CONFIG
# ===============================
st.set_page_config(
    page_title="Data Core",
    layout="wide"
)

ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"
UPSELL_EMAIL = "datacore.agrotech@gmail.com"
USERS_FILE = "users.csv"

# ===============================
# GOOGLE DRIVE MAP (BASE)
# ===============================
DRIVE_MAP = {
    ("envios", "uva", 2021): "1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF",
    ("campo", "uva", 2021): "1k6OMQxl7B3hVY9OVECc9UlYcytIjpN1A",
}

# ===============================
# HELPERS
# ===============================
def show_logo():
    for f in ["logo.png", "logo.jpg", "logo.jpeg"]:
        if os.path.exists(f):
            st.image(f, width=140)
            return

def load_drive_csv(file_id):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    r = requests.get(url)
    try:
        return pd.read_csv(
            BytesIO(r.content),
            sep=None,
            engine="python",
            encoding="utf-8",
            on_bad_lines="skip"
        )
    except Exception as e:
        st.error(f"Error cargando data: {e}")
        return pd.DataFrame()

def normalize_month(val):
    if pd.isna(val):
        return None
    m = str(val).strip().lower()
    months = {
        "ene": 1, "feb": 2, "mar": 3, "abr": 4,
        "may": 5, "jun": 6, "jul": 7, "ago": 8,
        "sep": 9, "oct": 10, "nov": 11, "dic": 12
    }
    if m.isdigit():
        return int(m)
    for k, v in months.items():
        if m.startswith(k):
            return v
    return None

def init_users():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=[
            "usuario", "password", "nombre",
            "apellido", "dni", "correo", "tipo"
        ])
        df.to_csv(USERS_FILE, index=False)

def load_users():
    return pd.read_csv(USERS_FILE)

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

# ===============================
# AUTH
# ===============================
def auth_screen():
    show_logo()
    st.markdown("## 🔐 Data Core – Acceso")

    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

    with tab1:
        u = st.text_input("Usuario", key="login_user")
        p = st.text_input("Contraseña", type="password", key="login_pass")

        if st.button("Ingresar"):
            if u == ADMIN_USER and p == ADMIN_PASS:
                st.session_state.user = u
                st.session_state.tipo = "admin"
                st.rerun()

            users = load_users()
            match = users[(users.usuario == u) & (users.password == p)]
            if not match.empty:
                st.session_state.user = u
                st.session_state.tipo = match.iloc[0]["tipo"]
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

    with tab2:
        st.subheader("Registro")
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        dni = st.text_input("DNI")
        correo = st.text_input("Correo electrónico")
        usuario = st.text_input("Usuario nuevo")
        password = st.text_input("Contraseña", type="password")

        if st.button("Registrar"):
            users = load_users()
            if usuario in users.usuario.values:
                st.error("Usuario ya existe")
            else:
                new = {
                    "usuario": usuario,
                    "password": password,
                    "nombre": nombre,
                    "apellido": apellido,
                    "dni": dni,
                    "correo": correo,
                    "tipo": "freemium"
                }
                users = pd.concat([users, pd.DataFrame([new])])
                save_users(users)
                st.success("Registro exitoso")

# ===============================
# DATA SECTIONS
# ===============================
def show_section(tipo, producto, year, mes, is_admin):
    key = (tipo, producto, year)

    if key not in DRIVE_MAP:
        st.info("📌 Información en proceso de mejora.")
        return

    df = load_drive_csv(DRIVE_MAP[key])
    if df.empty:
        st.info("📌 Información en proceso de mejora.")
        return

    df.columns = [c.lower() for c in df.columns]

    if "mes" in df.columns and mes != "Todos":
        df["mes_norm"] = df["mes"].apply(normalize_month)
        df = df[df["mes_norm"] == mes]

    if not is_admin:
        st.dataframe(df.head(3))
        st.warning(
            f"🔓 Acceso completo escribiendo a {UPSELL_EMAIL}"
        )
    else:
        st.dataframe(df)

# ===============================
# DASHBOARD
# ===============================
def dashboard():
    show_logo()
    st.markdown(f"### 👋 Bienvenido, **{st.session_state.user}**")

    producto = st.selectbox(
        "Producto", ["uva", "mango", "arandano", "limon", "palta"]
    )
    year = st.selectbox(
        "Año", [2021, 2022, 2023, 2024, 2025]
    )
    mes = st.selectbox(
        "Mes", ["Todos"] + list(range(1, 13))
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Envíos")
        show_section(
            "envios", producto, year, mes,
            st.session_state.tipo == "admin"
        )

    with col2:
        st.subheader("🌾 Campos certificados")
        show_section(
            "campo", producto, year, mes,
            st.session_state.tipo == "admin"
        )

    if st.session_state.tipo == "admin":
        st.subheader("🛠 Gestión de usuarios")
        users = load_users()
        for i, r in users.iterrows():
            colA, colB = st.columns([3, 1])
            colA.write(f"{r.usuario} – {r.tipo}")
            if r.tipo == "freemium":
                if colB.button("Hacer Premium", key=f"p{i}"):
                    users.at[i, "tipo"] = "premium"
                    save_users(users)
                    st.rerun()

# ===============================
# MAIN
# ===============================
init_users()

if "user" not in st.session_state:
    auth_screen()
else:
    dashboard()

st.markdown("✅ Data Core – MVP estable | Escalable | Compatible con 13G")
