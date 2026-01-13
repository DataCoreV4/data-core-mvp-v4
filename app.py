import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import os

# =====================================================
# CONFIG
# =====================================================
st.set_page_config("Data Core", layout="wide")

ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"
USERS_FILE = "users.csv"

# 🔴 CAMBIA SOLO ESTO (link directo al index.csv en Drive)
INDEX_URL = "https://drive.google.com/uc?id=REEMPLAZA_ID_DEL_INDEX"

# =====================================================
# UTILIDADES
# =====================================================
def drive_download(url):
    file_id = url.split("/d/")[1].split("/")[0] if "/d/" in url else url.split("id=")[-1]
    return f"https://drive.google.com/uc?id={file_id}"

def read_drive_csv(url):
    r = requests.get(drive_download(url))
    r.raise_for_status()
    return pd.read_csv(BytesIO(r.content), encoding="latin1", on_bad_lines="skip", low_memory=False)

def normalize_cols(df):
    df.columns = (
        df.columns.str.lower()
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("ó","o").str.replace("í","i")
        .str.replace("á","a").str.replace("é","e")
        .str.replace("ú","u").str.replace("ñ","n")
    )
    return df

def normalize_month(v):
    if pd.isna(v): return None
    m = str(v).lower().strip()
    mapa = {
        "ene":1,"enero":1,"1":1,"feb":2,"febrero":2,"2":2,
        "mar":3,"marzo":3,"3":3,"abr":4,"abril":4,"4":4,
        "may":5,"mayo":5,"5":5,"jun":6,"6":6,
        "jul":7,"7":7,"ago":8,"8":8,
        "sep":9,"set":9,"9":9,"oct":10,"10":10,
        "nov":11,"11":11,"dic":12,"12":12
    }
    return mapa.get(m)

# =====================================================
# USUARIOS
# =====================================================
def init_users():
    cols = ["usuario","password","rol","nombre","apellido","dni","email","celular","empresa","cargo"]
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=cols).to_csv(USERS_FILE, index=False)

    df = pd.read_csv(USERS_FILE)
    df = df[df.usuario != ADMIN_USER]

    admin = {
        "usuario": ADMIN_USER,
        "password": ADMIN_PASS,
        "rol": "admin",
        "nombre": "Administrador",
        "apellido": "DataCore",
        "dni": "","email":"","celular":"","empresa":"","cargo":""
    }
    df = pd.concat([df, pd.DataFrame([admin])], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)

# =====================================================
# SESIÓN
# =====================================================
if "logged" not in st.session_state:
    st.session_state.logged = False
    st.session_state.user = ""
    st.session_state.role = ""

# =====================================================
# AUTH
# =====================================================
def auth():
    st.title("🔐 Data Core – Acceso")
    t1, t2 = st.tabs(["Ingresar","Registrarse"])

    with t1:
        u = st.text_input("Usuario", key="lu")
        p = st.text_input("Contraseña", type="password", key="lp")
        if st.button("Ingresar"):
            df = pd.read_csv(USERS_FILE)
            ok = df[(df.usuario==u)&(df.password==p)]
            if not ok.empty:
                st.session_state.logged = True
                st.session_state.user = u
                st.session_state.role = ok.iloc[0].rol
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    with t2:
        with st.form("reg"):
            data = {}
            data["usuario"] = st.text_input("Usuario")
            data["password"] = st.text_input("Contraseña", type="password")
            rep = st.text_input("Repetir contraseña", type="password")
            data["nombre"] = st.text_input("Nombre")
            data["apellido"] = st.text_input("Apellido")
            data["dni"] = st.text_input("DNI")
            data["email"] = st.text_input("Correo electrónico")
            data["celular"] = st.text_input("Celular")
            data["empresa"] = st.text_input("Empresa (opcional)")
            data["cargo"] = st.text_input("Cargo (opcional)")
            if st.form_submit_button("Registrarse"):
                if data["password"]!=rep:
                    st.error("Contraseñas no coinciden"); return
                df = pd.read_csv(USERS_FILE)
                if data["usuario"] in df.usuario.values:
                    st.error("Usuario ya existe"); return
                data["rol"] = "freemium"
                df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
                df.to_csv(USERS_FILE, index=False)
                st.success("Registro exitoso")

# =====================================================
# DASHBOARD (DRIVE)
# =====================================================
def dashboard():
    st.success(f"👋 Bienvenido, {st.session_state.user}")

    try:
        index = read_drive_csv(INDEX_URL)
        index = normalize_cols(index)
    except Exception:
        st.error("No se pudo cargar el índice de datos")
        return

    productos = sorted(index.producto.unique())
    anios = sorted(index.anio.unique())

    producto = st.selectbox("Producto", productos)
    anio = st.selectbox("Año", anios)
    mes = st.selectbox("Mes", ["Todos"] + list(range(1,13)))

    # ================= ENVÍOS =================
    st.subheader("📦 Envíos")
    env = index[(index.tipo=="envios")&(index.producto==producto)&(index.anio==anio)]

    if env.empty:
        st.info("📌 Información en proceso de mejora")
    else:
        try:
            df = normalize_cols(read_drive_csv(env.iloc[0].url))
            if mes!="Todos":
                mcol = [c for c in df.columns if "mes" in c][0]
                df["mes_n"]=df[mcol].apply(normalize_month)
                df=df[df.mes_n==mes]

            if st.session_state.role!="admin":
                st.dataframe(df.head(3))
                st.warning("🔓 Adquirir acceso completo – Envíos")
            else:
                st.dataframe(df)
        except Exception:
            st.info("📌 Información en proceso de mejora")

    # ================= CAMPOS =================
    st.subheader("🌾 Campos certificados")
    cam = index[(index.tipo=="campo")&(index.producto==producto)&(index.anio==anio)]

    if cam.empty:
        st.info("📌 Información de campos en proceso de mejora")
    else:
        try:
            dfc = normalize_cols(read_drive_csv(cam.iloc[0].url))
            if mes!="Todos":
                mcol=[c for c in dfc.columns if "mes" in c][0]
                dfc["mes_n"]=dfc[mcol].apply(normalize_month)
                dfc=dfc[dfc.mes_n==mes]

            if st.session_state.role!="admin":
                st.dataframe(dfc.head(3))
                st.warning("🔓 Adquirir acceso completo – Campos")
            else:
                st.dataframe(dfc)
        except Exception:
            st.info("📌 Información de campos en proceso de mejora")

    if st.button("Cerrar sesión"):
        st.session_state.logged=False
        st.rerun()

# =====================================================
# MAIN
# =====================================================
init_users()

if not st.session_state.logged:
    auth()
else:
    dashboard()

