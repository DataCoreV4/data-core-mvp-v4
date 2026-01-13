import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import hashlib
import os

st.set_page_config(page_title="Data Core", layout="wide")

# ======================
# CONFIG
# ======================
USERS_FILE = "users.csv"
INDEX_FILE = "resumen de field.xlsx"  # ← índice LOCAL adjunto
ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"

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
            "Administrador","DataCore","-","-","-","-","-","admin"
        ]
        df.to_csv(USERS_FILE, index=False)

def load_users():
    return pd.read_csv(USERS_FILE)

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

# ======================
# DRIVE
# ======================
def download_drive(url):
    file_id = url.split("/d/")[1].split("/")[0]
    return BytesIO(
        requests.get(f"https://drive.google.com/uc?id={file_id}").content
    )

def read_csv_drive(url):
    try:
        return pd.read_csv(
            download_drive(url),
            sep=None,
            engine="python",
            on_bad_lines="skip",
            low_memory=False
        )
    except Exception:
        return None

def normalize_cols(df):
    df.columns = (
        df.columns.str.lower()
        .str.replace("á","a").str.replace("é","e")
        .str.replace("í","i").str.replace("ó","o")
        .str.replace("ú","u").str.replace("ñ","n")
        .str.strip()
    )
    return df

def norm_mes(val):
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
# ÍNDICE LOCAL (EXCEL)
# ======================
@st.cache_data
def load_index():
    if not os.path.exists(INDEX_FILE):
        return None
    idx = pd.read_excel(INDEX_FILE)
    idx = normalize_cols(idx)

    # normalizar nombres esperados
    rename_map = {}
    for c in idx.columns:
        if "ano" in c:
            rename_map[c] = "anio"
        if c in ["field id", "field_id", "url", "link"]:
            rename_map[c] = "url"
        if "producto" in c:
            rename_map[c] = "producto"
        if "tipo" in c:
            rename_map[c] = "tipo"
    idx = idx.rename(columns=rename_map)

    # normalizar valores
    idx["producto"] = idx["producto"].str.lower().str.strip()
    idx["tipo"] = idx["tipo"].str.lower().str.strip()

    return idx[["anio","tipo","producto","url"]]

# ======================
# AUTH
# ======================
def auth():
    st.title("🔐 Data Core – Acceso")
    t1, t2 = st.tabs(["Ingresar","Registrarse"])

    with t1:
        u = st.text_input("Usuario", key="login_user")
        p = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Ingresar"):
            users = load_users()
            ok = users[(users.usuario==u) & (users.password==hash_pwd(p))]
            if len(ok):
                st.session_state.user = u
                st.session_state.rol = ok.iloc[0].rol
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    with t2:
        fields = ["usuario","password","nombre","apellido","dni","correo","celular","empresa","cargo"]
        data = {}
        for f in fields:
            data[f] = st.text_input(
                f.capitalize(),
                key=f"reg_{f}",
                type="password" if f=="password" else "default"
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

    idx = load_index()
    if idx is None or idx.empty:
        st.error("No se pudo cargar el índice de datos")
        return

    productos = sorted(idx.producto.unique())
    anios = sorted(idx.anio.unique())

    f1,f2,f3 = st.columns(3)
    producto = f1.selectbox("Producto", productos)
    anio = f2.selectbox("Año", anios)
    mes = f3.selectbox("Mes", ["Todos"] + list(range(1,13)))

    for tipo, titulo in [("envios","📦 Envíos"),("campo","🌾 Campos certificados")]:
        st.subheader(titulo)

        fila = idx[
            (idx.tipo == tipo) &
            (idx.producto == producto) &
            (idx.anio == anio)
        ]

        if fila.empty:
            st.info("📌 Información en proceso de mejora")
            continue

        df = read_csv_drive(fila.iloc[0].url)
        if df is None:
            st.error("Error cargando data")
            continue

        df = normalize_cols(df)

        mes_col = next((c for c in df.columns if "mes" in c), None)
        if mes_col:
            df["mes_norm"] = df[mes_col].apply(norm_mes)
            if mes != "Todos":
                df = df[df.mes_norm == mes]

        # 🔒 LÍMITE SOLO PARA FREEMIUM
        if st.session_state.rol != "admin":
            df = df.head(3)

        st.dataframe(df)

        if st.session_state.rol != "admin":
            st.markdown("🔓 [Adquirir acceso premium](mailto:datacore.agrotech@gmail.com)")

    # ===== ADMIN =====
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
    auth()
else:
    dashboard()
