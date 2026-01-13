import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import os
import unicodedata

# =====================================================
# CONFIG
# =====================================================
st.set_page_config("Data Core", layout="wide")

ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"
USERS_FILE = "users.csv"

# =====================================================
# DRIVE MAP (NO SE TOCA)
# =====================================================
DRIVE_MAP = { ... }  # 👈 EXACTAMENTE IGUAL, OMITIDO AQUÍ POR BREVEDAD
# (en tu archivo final DEBE IR COMPLETO, tal como lo pegaste)

# =====================================================
# FUNCIONES BASE (NO SE TOCAN)
# =====================================================
def drive_download(url):
    file_id = url.split("/d/")[1].split("/")[0]
    return f"https://drive.google.com/uc?id={file_id}"

def load_csv(url):
    r = requests.get(drive_download(url))
    r.raise_for_status()
    return pd.read_csv(
        BytesIO(r.content),
        sep=";",
        encoding="latin1",
        on_bad_lines="skip",
        low_memory=False
    )

# =====================================================
# UTILIDADES NUEVAS
# =====================================================
def normalize(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()

def detectar_columna_mes(df):
    for c in df.columns:
        n = normalize(c)
        if "mes" in n:
            return c
    return None

# =====================================================
# USUARIOS
# =====================================================
def init_users():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=[
            "usuario","password","rol",
            "nombre","apellido","dni",
            "correo","celular","empresa","cargo"
        ]).to_csv(USERS_FILE, index=False)

    df = pd.read_csv(USERS_FILE)
    df = df[df.usuario != ADMIN_USER]

    admin_row = {
        "usuario": ADMIN_USER,
        "password": ADMIN_PASS,
        "rol": "admin",
        "nombre": "Administrador",
        "apellido": "DataCore",
        "dni": "",
        "correo": "",
        "celular": "",
        "empresa": "",
        "cargo": ""
    }

    df = pd.concat([df, pd.DataFrame([admin_row])], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)

# =====================================================
# SESIÓN
# =====================================================
if "logged" not in st.session_state:
    st.session_state.logged = False
    st.session_state.role = ""
    st.session_state.user = ""

# =====================================================
# AUTH + REGISTRO (NUEVO)
# =====================================================
def auth():
    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

    with tab1:
        st.subheader("🔐 Acceso")
        u = st.text_input("Usuario", key="login_user")
        p = st.text_input("Contraseña", type="password", key="login_pass")

        if st.button("Ingresar"):
            df = pd.read_csv(USERS_FILE)
            ok = df[(df.usuario == u) & (df.password == p)]
            if not ok.empty:
                st.session_state.logged = True
                st.session_state.role = ok.iloc[0].rol
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    with tab2:
        st.subheader("📝 Registro")
        data = {}
        data["usuario"] = st.text_input("Usuario")
        data["password"] = st.text_input("Contraseña", type="password")
        rep = st.text_input("Repetir contraseña", type="password")
        data["nombre"] = st.text_input("Nombre")
        data["apellido"] = st.text_input("Apellido")
        data["dni"] = st.text_input("DNI")
        data["correo"] = st.text_input("Correo electrónico")
        data["celular"] = st.text_input("Celular")
        data["empresa"] = st.text_input("Empresa (opcional)")
        data["cargo"] = st.text_input("Cargo (opcional)")

        if st.button("Registrarse"):
            if data["password"] != rep:
                st.error("Las contraseñas no coinciden")
                return

            df = pd.read_csv(USERS_FILE)
            if data["usuario"] in df.usuario.values:
                st.error("Usuario ya existe")
                return

            data["rol"] = "freemium"
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
            df.to_csv(USERS_FILE, index=False)
            st.success("Registro exitoso. Ya puedes ingresar.")

# =====================================================
# DASHBOARD
# =====================================================
def dashboard():
    st.markdown(f"👋 **Bienvenido, {st.session_state.user}**")

    if st.button("🚪 Cerrar sesión"):
        st.session_state.logged = False
        st.rerun()

    producto = st.selectbox("Producto", ["uva","mango","arandano","limon","palta"])
    anios_disponibles = []

if isinstance(DRIVE_MAP, dict) and "envios" in DRIVE_MAP:
    if isinstance(DRIVE_MAP["envios"], dict):
        anios_disponibles = sorted(list(DRIVE_MAP["envios"].keys()))

if not anios_disponibles:
    st.error("❌ No se pudo leer la estructura de años desde DRIVE_MAP")
    st.stop()

anio = st.selectbox("Año", anios_disponibles)

    # =========================
    # ENVÍOS
    # =========================
    st.subheader("📦 Envíos")
    try:
        df = load_csv(DRIVE_MAP["envios"][anio][producto])
        col_mes = detectar_columna_mes(df)

        if col_mes:
            meses = sorted(df[col_mes].dropna().unique())
            mes_sel = st.selectbox("Mes (envíos)", ["Todos"] + list(meses))
            if mes_sel != "Todos":
                df = df[df[col_mes] == mes_sel]

        st.dataframe(df if st.session_state.role=="admin" else df.head(3))

        if st.session_state.role != "admin":
            st.markdown("🔓 **¿Necesitas acceso completo a la información de envíos?**")
            st.link_button(
                "📩 Solicitar acceso completo – Envíos",
                f"mailto:datacore.agrotech@gmail.com?subject=Acceso%20ENVÍOS%20{producto}%20{anio}"
            )
    except:
        st.info("📌 Información en proceso de mejora")

    # =========================
    # CAMPOS
    # =========================
    st.subheader("🌾 Campos certificados")
    try:
        dfc = load_csv(DRIVE_MAP["campo"][anio][producto])
        col_mes_c = detectar_columna_mes(dfc)

        if col_mes_c:
            meses = sorted(dfc[col_mes_c].dropna().unique())
            mes_sel = st.selectbox("Mes (campos)", ["Todos"] + list(meses))
            if mes_sel != "Todos":
                dfc = dfc[dfc[col_mes_c] == mes_sel]

        st.dataframe(dfc if st.session_state.role=="admin" else dfc.head(3))

        if st.session_state.role != "admin":
            st.markdown("🔓 **¿Necesitas acceso completo a la información de campos certificados?**")
            st.link_button(
                "📩 Solicitar acceso completo – Campos",
                f"mailto:datacore.agrotech@gmail.com?subject=Acceso%20CAMPOS%20{producto}%20{anio}"
            )
    except:
        st.info("📌 Información de campos en proceso de mejora")

    # =========================
    # GESTIÓN DE USUARIOS (ADMIN)
    # =========================
    if st.session_state.role == "admin":
        st.subheader("🛠 Gestión de usuarios")
        dfu = pd.read_csv(USERS_FILE)
        for i, r in dfu.iterrows():
            if r.usuario != ADMIN_USER:
                col1, col2 = st.columns([3,2])
                col1.write(r.usuario)
                nuevo = col2.selectbox(
                    "Rol",
                    ["freemium","premium_envios","premium_campo","premium_full"],
                    index=["freemium","premium_envios","premium_campo","premium_full"].index(r.rol),
                    key=f"rol_{i}"
                )
                dfu.loc[i,"rol"] = nuevo
        dfu.to_csv(USERS_FILE, index=False)

# =====================================================
# MAIN
# =====================================================
init_users()

if not st.session_state.logged:
    auth()
else:
    dashboard()
