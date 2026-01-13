import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import os

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Data Core", layout="wide")

LOGO_PATH = "logotipo_datacore.jpg"
USERS_FILE = "data/users.csv"
ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"
CONTACT_EMAIL = "datacore.agrotech@gmail.com"

os.makedirs("data", exist_ok=True)

# =========================
# DRIVE MAP (ENVÍOS / CAMPO)
# =========================
DRIVE_MAP = {
    # ejemplo (completo según tu tabla)
    ("envios", "uva", 2021): "1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF",
    ("campo", "uva", 2021): "1k6OMQxl7B3hVY9OVECc9UlYcytIjpN1A",
    # ⚠️ aquí va TODA la tabla que ya definimos
}

# =========================
# UTILIDADES
# =========================
def load_drive_csv(file_id):
    url = f"https://drive.google.com/uc?id={file_id}"
    r = requests.get(url)
    r.raise_for_status()
    return pd.read_csv(
        BytesIO(r.content),
        sep=None,
        engine="python",
        encoding="utf-8",
        low_memory=False,
    )

def normalize_month(val):
    if pd.isna(val):
        return None
    m = str(val).strip().lower()
    months = {
        "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
        "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12
    }
    if m.isdigit():
        return int(m)
    for k, v in months.items():
        if k in m:
            return v
    return None

# =========================
# USERS
# =========================
def ensure_admin():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame([{
            "usuario": ADMIN_USER,
            "password": ADMIN_PASS,
            "rol": "admin",
            "nombre": "Data",
            "apellido": "Core",
            "dni": "",
            "email": ""
        }])
        df.to_csv(USERS_FILE, index=False)
        return

    df = pd.read_csv(USERS_FILE)
    if "usuario" not in df.columns:
        df = pd.DataFrame(columns=["usuario","password","rol","nombre","apellido","dni","email"])
    if not (df["usuario"] == ADMIN_USER).any():
        df.loc[len(df)] = [ADMIN_USER, ADMIN_PASS, "admin", "Data", "Core", "", ""]
        df.to_csv(USERS_FILE, index=False)

ensure_admin()

# =========================
# AUTH
# =========================
def auth_screen():
    st.markdown("## 🔐 Data Core – Acceso")
    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

    with tab1:
        u = st.text_input("Usuario", key="login_user")
        p = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Ingresar"):
            df = pd.read_csv(USERS_FILE)
            user = df[(df.usuario == u) & (df.password == p)]
            if not user.empty:
                st.session_state.user = user.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

    with tab2:
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        dni = st.text_input("DNI")
        email = st.text_input("Correo electrónico")
        usuario = st.text_input("Usuario nuevo")
        password = st.text_input("Contraseña", type="password")

        if st.button("Registrarse"):
            df = pd.read_csv(USERS_FILE)
            if usuario in df.usuario.values:
                st.error("Usuario ya existe")
            else:
                df.loc[len(df)] = [usuario, password, "freemium", nombre, apellido, dni, email]
                df.to_csv(USERS_FILE, index=False)
                st.success("Registro exitoso. Ya puedes ingresar.")

# =========================
# DASHBOARD
# =========================
def dashboard():
    user = st.session_state.user

    col1, col2 = st.columns([1, 6])
    with col1:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=120)
    with col2:
        st.markdown(f"### 👋 Bienvenido, **{user['usuario']}**")

    producto = st.selectbox("Producto", ["uva","mango","palta","arandano","limon"])
    año = st.selectbox("Año", [2021,2022,2023,2024,2025])
    mes = st.selectbox("Mes", ["Todos"] + list(range(1,13)))

    colA, colB = st.columns(2)

    def render(tipo, col, filtro_pais=False):
        with col:
            st.subheader("📦 Envíos" if tipo=="envios" else "🌾 Campos certificados")
            key = (tipo, producto, año)
            if key not in DRIVE_MAP:
                st.info("📌 Información en proceso de mejora.")
                return

            try:
                df = load_drive_csv(DRIVE_MAP[key])

                # normalizar meses
                for c in df.columns:
                    if "mes" in c.lower():
                        df["MES_STD"] = df[c].apply(normalize_month)

                if mes != "Todos" and "MES_STD" in df:
                    df = df[df["MES_STD"] == mes]

                if filtro_pais:
                    pais_col = [c for c in df.columns if "pais" in c.lower()]
                    if pais_col:
                        pais = st.selectbox("País Destino", ["Todos"] + sorted(df[pais_col[0]].dropna().unique()))
                        if pais != "Todos":
                            df = df[df[pais_col[0]] == pais]

                if df.empty:
                    st.info("📌 Información en proceso de mejora.")
                    return

                if user["rol"] != "admin":
                    st.dataframe(df.head(3))
                    st.warning(f"🔒 Acceso limitado. Para adquirir data completa escribir a {CONTACT_EMAIL}")
                else:
                    st.dataframe(df)

            except Exception as e:
                st.error("Error cargando data")

    render("envios", colA, filtro_pais=True)
    render("campo", colB)

# =========================
# MAIN
# =========================
if "user" not in st.session_state:
    auth_screen()
else:
    dashboard()
