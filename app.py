import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import os, hashlib

st.set_page_config(page_title="Data Core", layout="wide")

USERS_FILE = "users.csv"
ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"

# =======================
# SEGURIDAD
# =======================
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

# =======================
# DRIVE
# =======================
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

def norm_mes(x):
    if pd.isna(x): return None
    if str(x).isdigit(): return int(x)
    m = {"ene":1,"feb":2,"mar":3,"abr":4,"may":5,"jun":6,
         "jul":7,"ago":8,"sep":9,"oct":10,"nov":11,"dic":12}
    return m.get(str(x).lower()[:3])

# =======================
# DRIVE MAP COMPLETO
# =======================
DRIVE_MAP = {
    "envios": {
        2021: {
            "uva": "https://drive.google.com/file/d/1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF/view",
            "mango": "https://drive.google.com/file/d/1k6CxjPufa0YF17e264BI8NYO1rFFZuc7/view",
            "arandano": "https://drive.google.com/file/d/1CyFQu-BdYNxFSoed9SGvKnkimrJjS2Q9/view",
            "limon": "https://drive.google.com/file/d/1--9cfYzrB2giYCy5khZmqXdXL_46Zuz8/view",
            "palta": "https://drive.google.com/file/d/1-BK3uEDMAMrTAdqxMJd-pIYCg0Rp-8kJ/view"
        }
        # AGREGA 2022–2025 AQUÍ
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

# =======================
# AUTH
# =======================
def auth():
    st.title("🔐 Data Core – Acceso")
    t1,t2 = st.tabs(["Ingresar","Registrarse"])

    with t1:
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            users = load_users()
            ok = users[(users.usuario==u) & (users.password==hash_pwd(p))]
            if len(ok):
                st.session_state.user = u
                st.session_state.rol = ok.iloc[0].rol
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

    with t2:
        d={}
        for f in ["usuario","password","nombre","apellido","dni","correo","celular","empresa","cargo"]:
            d[f]=st.text_input(f.capitalize(), type="password" if f=="password" else "default")
        if st.button("Registrar"):
            users = load_users()
            if d["usuario"] in users.usuario.values:
                st.error("Usuario existe")
            else:
                users.loc[len(users)] = [
                    d["usuario"],hash_pwd(d["password"]),
                    d["nombre"],d["apellido"],d["dni"],
                    d["correo"],d["celular"],d["empresa"],d["cargo"],"freemium"
                ]
                save_users(users)
                st.success("Registro exitoso")

# =======================
# DASHBOARD
# =======================
def dashboard():
    st.markdown(f"👋 **Bienvenido, {st.session_state.user}**")

    c1,c2,c3 = st.columns(3)
    prod = c1.selectbox("Producto", ["uva","mango","arandano","limon","palta"])
    year = c2.selectbox("Año", sorted(DRIVE_MAP["envios"].keys()))
    mes = c3.selectbox("Mes", ["Todos"]+list(range(1,13)))

    for tipo,titulo in [("envios","📦 Envíos"),("campo","🌾 Campos certificados")]:
        st.subheader(titulo)
        link = DRIVE_MAP.get(tipo,{}).get(year,{}).get(prod)
        if not link:
            st.info("📌 Información en proceso de mejora")
            continue

        df = read_csv_drive(link)
        if df is None:
            st.error("Error cargando data")
            continue

        df = normalize(df)
        mcol = next((c for c in df.columns if "mes" in c), None)
        if mcol:
            df["mes_norm"] = df[mcol].apply(norm_mes)
            if mes!="Todos":
                df = df[df.mes_norm==mes]

        if st.session_state.rol!="admin":
            df = df.head(3)

        st.dataframe(df)

        if st.session_state.rol!="admin":
            st.markdown("🔓 [Adquirir acceso premium](mailto:datacore.agrotech@gmail.com)")

# =======================
# MAIN
# =======================
init_users()
if "user" not in st.session_state:
    auth()
else:
    dashboard()
