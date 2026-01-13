import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import os
import hashlib

st.set_page_config(page_title="Data Core", layout="wide")

USERS_FILE = "users.csv"
ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"

# ======================
# UTILIDADES BÁSICAS
# ======================
def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def init_users():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=[
            "usuario","password","nombre","apellido","dni",
            "correo","celular","empresa","cargo","rol"
        ])
        df.loc[0] = [
            ADMIN_USER, hash_pwd(ADMIN_PASS),
            "Administrador","DataCore","-","-","-","-","-","admin"
        ]
        df.to_csv(USERS_FILE, index=False)

def load_users():
    return pd.read_csv(USERS_FILE)

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

# ======================
# GOOGLE DRIVE
# ======================
def drive_download(url):
    file_id = url.split("/d/")[1].split("/")[0]
    download_url = f"https://drive.google.com/uc?id={file_id}"
    r = requests.get(download_url)
    r.raise_for_status()
    return BytesIO(r.content)

def read_csv_drive_safe(url):
    try:
        return pd.read_csv(
            drive_download(url),
            sep=None,              # ← DETECTA DELIMITADOR
            engine="python",       # ← MÁS ROBUSTO
            encoding="utf-8",
            on_bad_lines="skip"
        )
    except Exception:
        try:
            return pd.read_csv(
                drive_download(url),
                sep=None,
                engine="python",
                encoding="latin1",
                on_bad_lines="skip"
            )
        except Exception as e:
            return None

def normalize_columns(df):
    df.columns = (
        df.columns.str.lower()
        .str.strip()
        .str.replace("á","a").str.replace("é","e")
        .str.replace("í","i").str.replace("ó","o")
        .str.replace("ú","u").str.replace("ñ","n")
    )
    return df

def normalize_mes(val):
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return int(val)
    val = str(val).strip().lower()
    meses = {
        "ene":1,"feb":2,"mar":3,"abr":4,"may":5,"jun":6,
        "jul":7,"ago":8,"sep":9,"oct":10,"nov":11,"dic":12
    }
    if val.isdigit():
        return int(val)
    return meses.get(val[:3], None)

# ======================
# DRIVE MAP (AMPLIABLE)
# ======================
DRIVE_MAP = {
    ("envios","uva",2021): "https://drive.google.com/file/d/1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF/view",
    ("campo","uva",2021): "https://drive.google.com/file/d/1k6OMQxl7B3hVY9OVECc9UlYcytIjpN1A/view",
    # 👉 EL RESTO LO VAS AGREGANDO SIN TOCAR EL CÓDIGO
}

# ======================
# LOGIN / REGISTRO
# ======================
def auth_screen():
    st.title("🔐 Data Core – Acceso")

    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

    with tab1:
        u = st.text_input("Usuario", key="login_user")
        p = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Ingresar"):
            users = load_users()
            ok = users[
                (users["usuario"] == u) &
                (users["password"] == hash_pwd(p))
            ]
            if len(ok) > 0:
                st.session_state.user = u
                st.session_state.rol = ok.iloc[0]["rol"]
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    with tab2:
        data = {}
        fields = ["usuario","password","nombre","apellido","dni","correo","celular","empresa","cargo"]
        for f in fields:
            data[f] = st.text_input(
                f.capitalize(),
                type="password" if f=="password" else "default",
                key=f"reg_{f}"
            )
        if st.button("Registrarse"):
            users = load_users()
            if data["usuario"] in users["usuario"].values:
                st.error("Usuario ya existe")
            else:
                users.loc[len(users)] = [
                    data["usuario"], hash_pwd(data["password"]),
                    data["nombre"], data["apellido"], data["dni"],
                    data["correo"], data["celular"],
                    data["empresa"], data["cargo"], "freemium"
                ]
                save_users(users)
                st.success("Registro exitoso")

# ======================
# DASHBOARD
# ======================
def dashboard():
    st.markdown(f"👋 **Bienvenido, {st.session_state.user}**")

    f1,f2,f3 = st.columns(3)
    producto = f1.selectbox("Producto", ["uva","mango","arandano","limon","palta"])
    anio = f2.selectbox("Año", [2021,2022,2023,2024,2025])
    mes = f3.selectbox("Mes", ["Todos"] + list(range(1,13)))

    # -------- ENVÍOS --------
    st.subheader("📦 Envíos")
    key = ("envios", producto, anio)
    if key in DRIVE_MAP:
        df = read_csv_drive_safe(DRIVE_MAP[key])
        if df is not None:
            df = normalize_columns(df)
            mes_col = next((c for c in df.columns if "mes" in c), None)
            if mes_col:
                df["mes_norm"] = df[mes_col].apply(normalize_mes)
                if mes != "Todos":
                    df = df[df["mes_norm"] == mes]
            if st.session_state.rol != "admin":
                df = df.head(3)
            st.dataframe(df)
            if st.session_state.rol != "admin":
                st.markdown("🔓 [Adquirir acceso completo – Envíos](mailto:datacore.agrotech@gmail.com)")
        else:
            st.info("📌 Información en proceso de mejora")
    else:
        st.info("📌 Información en proceso de mejora")

    st.divider()

    # -------- CAMPOS --------
    st.subheader("🌾 Campos certificados")
    key = ("campo", producto, anio)
    if key in DRIVE_MAP:
        dfc = read_csv_drive_safe(DRIVE_MAP[key])
        if dfc is not None:
            dfc = normalize_columns(dfc)
            mes_col = next((c for c in dfc.columns if "mes" in c), None)
            if mes_col:
                dfc["mes_norm"] = dfc[mes_col].apply(normalize_mes)
                if mes != "Todos":
                    dfc = dfc[dfc["mes_norm"] == mes]
            if st.session_state.rol != "admin":
                dfc = dfc.head(3)
            st.dataframe(dfc)
            if st.session_state.rol != "admin":
                st.markdown("🔓 [Adquirir acceso completo – Campos](mailto:datacore.agrotech@gmail.com)")
        else:
            st.info("📌 Información de campos en proceso de mejora")
    else:
        st.info("📌 Información de campos en proceso de mejora")

    # -------- ADMIN --------
    if st.session_state.rol == "admin":
        st.divider()
        st.subheader("🛠 Gestión de usuarios")
        users = load_users()
        for i,r in users.iterrows():
            if r.usuario != ADMIN_USER:
                c1,c2 = st.columns([3,2])
                c1.write(r.usuario)
                users.loc[i,"rol"] = c2.selectbox(
                    "Rol", ["freemium","premium"],
                    index=0 if r.rol=="freemium" else 1,
                    key=f"rol_{i}"
                )
        save_users(users)

# ======================
# MAIN
# ======================
init_users()

if "user" not in st.session_state:
    auth_screen()
else:
    dashboard()
