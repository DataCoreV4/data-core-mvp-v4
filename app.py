import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import os
import hashlib

st.set_page_config(page_title="Data Core", layout="wide")

# ======================
# CONSTANTES
# ======================
USERS_FILE = "users.csv"
ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"

PRODUCTOS = ["uva", "mango", "arandano", "limon", "palta"]
ANIOS = [2021, 2022, 2023, 2024, 2025]
MESES = ["Todos"] + list(range(1, 13))

# ======================
# SEGURIDAD
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
            "Administrador","DataCore","-",
            "-","-","-","-","admin"
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
    return BytesIO(
        requests.get(f"https://drive.google.com/uc?id={file_id}").content
    )

def read_csv_drive(url):
    try:
        return pd.read_csv(
            drive_download(url),
            sep=None,
            engine="python",
            on_bad_lines="skip"
        )
    except:
        return None

def normalize(df):
    df.columns = (
        df.columns.str.lower()
        .str.replace("á","a").str.replace("é","e")
        .str.replace("í","i").str.replace("ó","o")
        .str.replace("ú","u").str.replace("ñ","n")
        .str.strip()
    )
    return df

def normalize_mes(val):
    if pd.isna(val):
        return None
    if str(val).isdigit():
        return int(val)
    meses = {
        "ene":1,"feb":2,"mar":3,"abr":4,"may":5,"jun":6,
        "jul":7,"ago":8,"sep":9,"oct":10,"nov":11,"dic":12
    }
    return meses.get(str(val).lower()[:3])

# ======================
# DRIVE MAP (EJEMPLO 2021)
# ======================
DRIVE_MAP = {
    "envios": {
        2021: {
            "uva": "https://drive.google.com/file/d/1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF/view",
            "mango": "https://drive.google.com/file/d/1k6CxjPufa0YF17e264BI8NYO1rFFZuc7/view",
            "arandano": "https://drive.google.com/file/d/1CyFQu-BdYNxFSoed9SGvKnkimrJjS2Q9/view",
            "limon": "https://drive.google.com/file/d/1--9cfYzrB2giYCy5khZmqXdXL_46Zuz8/view",
            "palta": "https://drive.google.com/file/d/1-BK3uEDMAMrTAdqxMJd-pIYCg0Rp-8kJ/view"
        }
    },
    "campo": {
        2021: {
            "uva": "https://drive.google.com/file/d/1k6OMQxl7B3hVY9OVECc9UlYcytIjpN1A/view",
            "mango": "https://drive.google.com/file/d/1JX50r2NJYG3HjalUTZ5pCHmbD5DXQDUu/view",
            "arandano": "https://drive.google.com/file/d/1HOKP2FaW9UPRYyA7tIj0oSnGzUhkb3h4/view",
            "limon": "https://drive.google.com/file/d/12xOZVXqxvvepb97On1H8feKUoW_u1Qet/view",
            "palta": "https://drive.google.com/file/d/1ckjszJeuyPQS6oVNeWFd-FwoM8FTalHO/view"
        }
    }
}

# ======================
# LOGIN / REGISTRO
# ======================
def auth():
    st.title("🔐 Data Core – Acceso")
    t1, t2 = st.tabs(["Ingresar", "Registrarse"])

    with t1:
        u = st.text_input("Usuario", key="login_user")
        p = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Ingresar"):
            users = load_users()
            ok = users[(users.usuario == u) & (users.password == hash_pwd(p))]
            if len(ok):
                st.session_state.user = u
                st.session_state.rol = ok.iloc[0].rol
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    with t2:
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
            if data["usuario"] in users.usuario.values:
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

    c1,c2,c3 = st.columns(3)
    producto = c1.selectbox("Producto", PRODUCTOS)
    anio = c2.selectbox("Año", ANIOS)
    mes = c3.selectbox("Mes", MESES)

    for tipo, titulo in [("envios","📦 Envíos"), ("campo","🌾 Campos certificados")]:
        st.subheader(titulo)
        link = DRIVE_MAP.get(tipo, {}).get(anio, {}).get(producto)

        if not link:
            st.info("📌 Información en proceso de mejora")
            continue

        df = read_csv_drive(link)
        if df is None:
            st.error("Error cargando data")
            continue

        df = normalize(df)

        mes_col = next((c for c in df.columns if "mes" in c), None)
        if mes_col:
            df["mes_norm"] = df[mes_col].apply(normalize_mes)
            if mes != "Todos":
                df = df[df.mes_norm == mes]

        # 🔴 SOLO FREEMIUM LIMITADO
        if st.session_state.rol != "admin":
            df = df.head(3)

        st.dataframe(df)

        if st.session_state.rol != "admin":
            st.markdown("🔓 [Adquirir acceso premium](mailto:datacore.agrotech@gmail.com)")

    # ======================
    # ADMIN USERS
    # ======================
    if st.session_state.rol == "admin":
        st.divider()
        st.subheader("🛠 Gestión de usuarios")
        users = load_users()
        for i, r in users.iterrows():
            if r.usuario != ADMIN_USER:
                col1, col2 = st.columns([3,2])
                col1.write(r.usuario)
                users.loc[i,"rol"] = col2.selectbox(
                    "Rol",
                    ["freemium","premium"],
                    index=0 if r.rol=="freemium" else 1,
                    key=f"rol_{i}"
                )
        save_users(users)

# ======================
# MAIN
# ======================
init_users()

if "user" not in st.session_state:
    auth()
else:
    dashboard()
