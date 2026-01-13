import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

# ===============================
# CONFIGURACIÓN GENERAL
# ===============================
st.set_page_config(
    page_title="Data Core – Dashboard",
    layout="wide"
)

LOGO_PATH = "logotipo_datacore.jpg"
CONTACT_EMAIL = "datacore.agrotech@gmail.com"

# ===============================
# USUARIOS (CSV LOCAL)
# ===============================
USERS_FILE = "users.csv"

def load_users():
    try:
        return pd.read_csv(USERS_FILE)
    except:
        df = pd.DataFrame(columns=[
            "usuario","password","nombre","apellido",
            "dni","email","tipo"
        ])
        df.to_csv(USERS_FILE, index=False)
        return df

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

# ===============================
# ADMIN DEFAULT
# ===============================
def ensure_admin():
    users = load_users()
    if not (users["usuario"] == "DCADMIN").any():
        admin = pd.DataFrame([{
            "usuario":"DCADMIN",
            "password":"admindatacore123!",
            "nombre":"Data",
            "apellido":"Core",
            "dni":"00000000",
            "email":"admin@datacore.pe",
            "tipo":"admin"
        }])
        users = pd.concat([users, admin], ignore_index=True)
        save_users(users)

ensure_admin()

# ===============================
# GOOGLE DRIVE MAP
# ===============================
DRIVE_MAP = {
    ("envios","uva",2021): "1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF",
    ("envios","mango",2021): "1k6CxjPufa0YF17e264BI8NYO1rFFZuc7",
    ("envios","arandano",2021): "1CyFQu-BdYNxFSoed9SGvKnkimrJjS2Q9",
    ("envios","limon",2021): "1--9cfYzrB2giYCy5khZmqXdXL_46Zuz8",
    ("envios","palta",2021): "1-BK3uEDMAMrTAdqxMJd-pIYCg0Rp-8kJ",

    ("campo","uva",2021): "1k6OMQxl7B3hVY9OVECc9UlYcytIjpN1A",
    ("campo","mango",2021): "1JX50r2NJYG3HjalUTZ5pCHmbD5DXQDUu",
    ("campo","arandano",2021): "1HOKP2FaW9UPRYyA7tIj0oSnGzUhkb3h4",
    ("campo","limon",2021): "12xOZVXqxvvepb97On1H8feKUoW_u1Qet",
    ("campo","palta",2021): "1ckjszJeuyPQS6oVNeWFd-FwoM8FTalHO",

    # 👉 aquí puedes seguir agregando 2022–2025
}

# ===============================
# UTILIDADES
# ===============================
def drive_download_url(file_id):
    return f"https://drive.google.com/uc?id={file_id}"

def load_drive_csv(file_id):
    url = drive_download_url(file_id)
    r = requests.get(url)
    r.raise_for_status()
    return pd.read_csv(
        BytesIO(r.content),
        sep=",",
        encoding="utf-8",
        engine="python",
        on_bad_lines="skip",
        low_memory=False
    )

def normalize_month(val):
    if pd.isna(val):
        return None
    val = str(val).strip().lower()
    meses = {
        "ene":1,"feb":2,"mar":3,"abr":4,"may":5,"jun":6,
        "jul":7,"ago":8,"sep":9,"oct":10,"nov":11,"dic":12
    }
    if val.isdigit():
        return int(val)
    for k,v in meses.items():
        if val.startswith(k):
            return v
    return None

# ===============================
# AUTH SCREEN
# ===============================
def auth_screen():
    st.title("🔐 Data Core – Acceso")

    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

    with tab1:
        u = st.text_input("Usuario", key="login_user")
        p = st.text_input("Contraseña", type="password", key="login_pass")

        if st.button("Ingresar"):
            users = load_users()
            match = users[
                (users["usuario"] == u) &
                (users["password"] == p)
            ]
            if not match.empty:
                st.session_state.user = match.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

    with tab2:
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        dni = st.text_input("DNI")
        email = st.text_input("Correo electrónico")
        usuario = st.text_input("Usuario nuevo")
        password = st.text_input("Contraseña nueva", type="password")

        if st.button("Registrarse"):
            users = load_users()
            if (users["usuario"] == usuario).any():
                st.error("Usuario ya existe")
            else:
                nuevo = {
                    "usuario":usuario,
                    "password":password,
                    "nombre":nombre,
                    "apellido":apellido,
                    "dni":dni,
                    "email":email,
                    "tipo":"freemium"
                }
                users = pd.concat([users, pd.DataFrame([nuevo])])
                save_users(users)
                st.success("Registro exitoso. Ahora puedes ingresar.")

# ===============================
# DASHBOARD
# ===============================
def dashboard():
    user = st.session_state.user

    st.image(LOGO_PATH, width=120)
    st.markdown(f"👋 **Bienvenido, {user['nombre']} {user['apellido']}**")

    colf1, colf2, colf3 = st.columns(3)
    producto = colf1.selectbox("Producto", ["uva","mango","arandano","limon","palta"])
    año = colf2.selectbox("Año", list(range(2021, 2026)))
    mes = colf3.selectbox("Mes", ["Todos"] + list(range(1,13)))

    # ===============================
    # ENVÍOS
    # ===============================
    st.subheader("📦 Envíos")

    key_env = ("envios", producto, año)
    if key_env in DRIVE_MAP:
        try:
            df = load_drive_csv(DRIVE_MAP[key_env])

            # columna producto
            if "Producto" in df.columns:
                df = df[df["Producto"].str.lower() == producto]

            # mes
            for c in df.columns:
                if "mes" in c.lower():
                    df["_mes"] = df[c].apply(normalize_month)
                    break

            if mes != "Todos" and "_mes" in df:
                df = df[df["_mes"] == mes]

            # país destino
            pais_col = next((c for c in df.columns if "pais" in c.lower()), None)
            if pais_col:
                pais = st.selectbox("País Destino", ["Todos"] + sorted(df[pais_col].dropna().unique()))
                if pais != "Todos":
                    df = df[df[pais_col] == pais]

            if user["tipo"] == "freemium":
                st.dataframe(df.head(3))
                st.info("🔓 Acceso completo: Adquirir data completa aquí")
                st.markdown(f"[Enviar solicitud](mailto:{CONTACT_EMAIL})")
            else:
                st.dataframe(df)

        except Exception as e:
            st.error(f"Error cargando data: {e}")
            st.info("📌 Información en proceso de mejora.")
    else:
        st.info("📌 Información en proceso de mejora.")

    # ===============================
    # CAMPO
    # ===============================
    st.subheader("🌾 Campos certificados")

    key_cam = ("campo", producto, año)
    if key_cam in DRIVE_MAP:
        try:
            dfc = load_drive_csv(DRIVE_MAP[key_cam])

            # columna cultivo
            if "CULTIVO" in dfc.columns:
                dfc = dfc[dfc["CULTIVO"].str.lower() == producto]

            for c in dfc.columns:
                if "mes" in c.lower():
                    dfc["_mes"] = dfc[c].apply(normalize_month)
                    break

            if mes != "Todos" and "_mes" in dfc:
                dfc = dfc[dfc["_mes"] == mes]

            if user["tipo"] == "freemium":
                st.dataframe(dfc.head(3))
                st.info("🔓 Acceso completo: Adquirir data completa aquí")
                st.markdown(f"[Enviar solicitud](mailto:{CONTACT_EMAIL})")
            else:
                st.dataframe(dfc)

        except Exception as e:
            st.error(f"Error cargando data: {e}")
            st.info("📌 Información de campos en proceso de mejora.")
    else:
        st.info("📌 Información de campos en proceso de mejora.")

    # ===============================
    # ADMIN PANEL
    # ===============================
    if user["tipo"] == "admin":
        st.subheader("🛠 Gestión de usuarios")
        users = load_users()
        for i, r in users.iterrows():
            colA, colB = st.columns([4,1])
            colA.write(f"{r['usuario']} – {r['tipo']}")
            if r["tipo"] == "freemium":
                if colB.button("Hacer Premium", key=f"up_{i}"):
                    users.at[i,"tipo"] = "premium"
                    save_users(users)
                    st.rerun()

    st.markdown("✅ **Data Core – MVP estable | Escalable | Compatible con 13G**")

# ===============================
# MAIN
# ===============================
if "user" not in st.session_state:
    auth_screen()
else:
    dashboard()
