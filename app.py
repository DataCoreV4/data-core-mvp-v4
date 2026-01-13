import streamlit as st
import pandas as pd
import hashlib
import requests
from io import BytesIO

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Data Core", layout="wide")

ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"

USERS_FILE = "users.csv"
CONTACT_EMAIL = "datacore.agrotech@gmail.com"

# =========================
# DRIVE MAP
# =========================
DRIVE_MAP = {
    ("envios", "uva", 2021): "1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF",
    ("campo", "uva", 2021): "1k6OMQxl7B3hVY9OVECc9UlYcytIjpN1A",
    # 👉 aquí puedes seguir agregando TODOS
}

# =========================
# HELPERS
# =========================
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def load_users():
    try:
        return pd.read_csv(USERS_FILE)
    except:
        admin = pd.DataFrame([{
            "username": ADMIN_USER,
            "password": hash_pass(ADMIN_PASS),
            "role": "admin",
            "is_premium": True,
            "nombres": "Administrador",
            "apellidos": "Data Core",
            "dni": "",
            "email": CONTACT_EMAIL
        }])
        admin.to_csv(USERS_FILE, index=False)
        return admin

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

def load_drive_csv(file_id):
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    r = requests.get(url)
    return pd.read_csv(BytesIO(r.content), sep=",", encoding="utf-8", low_memory=False)

def normalize_month(x):
    if pd.isna(x): return None
    m = str(x).strip().lower()
    meses = {
        "ene":1,"feb":2,"mar":3,"abr":4,"may":5,"jun":6,
        "jul":7,"ago":8,"sep":9,"oct":10,"nov":11,"dic":12
    }
    if m.isdigit(): return int(m)
    for k,v in meses.items():
        if k in m: return v
    return None

# =========================
# AUTH
# =========================
def auth_screen():
    st.title("🔐 Data Core – Acceso")

    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

    with tab1:
        u = st.text_input("Usuario", key="login_u").strip().upper()
        p = st.text_input("Contraseña", type="password", key="login_p")

        if st.button("Ingresar"):
            users = load_users()
            row = users[users.username == u]
            if not row.empty and row.iloc[0]["password"] == hash_pass(p):
                st.session_state.user = row.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

    with tab2:
        st.subheader("Registro")
        nombres = st.text_input("Nombres")
        apellidos = st.text_input("Apellidos")
        dni = st.text_input("DNI")
        email = st.text_input("Correo electrónico")
        u = st.text_input("Usuario").strip().upper()
        p = st.text_input("Contraseña", type="password")

        if st.button("Registrar"):
            users = load_users()
            if u in users.username.values:
                st.warning("Usuario ya existe")
                return
            new = pd.DataFrame([{
                "username": u,
                "password": hash_pass(p),
                "role": "user",
                "is_premium": False,
                "nombres": nombres,
                "apellidos": apellidos,
                "dni": dni,
                "email": email
            }])
            save_users(pd.concat([users, new], ignore_index=True))
            st.success("Registro exitoso")

# =========================
# DASHBOARD
# =========================
def dashboard():
    u = st.session_state.user

    with st.sidebar:
        st.image("logo_datacore.jpg", width=180)
        st.markdown(f"### 👤 {u['nombres']}")
        st.markdown("🟢 Admin" if u["role"]=="admin" else "🟡 Freemium")

        if st.button("Cerrar sesión"):
            st.session_state.clear()
            st.rerun()

    st.title("📊 Data Core – Dashboard")

    col1, col2 = st.columns(2)

    # ================= ENVÍOS =================
    with col1:
        st.subheader("📦 Envíos")

        producto = st.selectbox("Producto", ["uva","mango","limon","palta","arandano"])
        año = st.selectbox("Año", [2021,2022,2023,2024,2025])
        mes = st.selectbox("Mes", ["Todos"] + list(range(1,13)))

        key = ("envios", producto, año)
        if key not in DRIVE_MAP:
            st.info("📌 Información en proceso de mejora para este producto/año.")
        else:
            df = load_drive_csv(DRIVE_MAP[key])

            df.columns = [c.lower() for c in df.columns]
            if "mes" in df.columns:
                df["mes"] = df["mes"].apply(normalize_month)
                if mes!="Todos":
                    df = df[df["mes"]==mes]

            if "pais destino" in df.columns:
                pais = st.selectbox("País destino", ["Todos"] + sorted(df["pais destino"].dropna().unique()))
                if pais!="Todos":
                    df = df[df["pais destino"]==pais]

            if u["role"]!="admin":
                st.dataframe(df.head(3))
                st.markdown(f"🔓 **Acceso completo:** [Adquirir data completa aquí](mailto:{CONTACT_EMAIL})")
            else:
                st.dataframe(df)

    # ================= CAMPOS =================
    with col2:
        st.subheader("🌾 Campos certificados")

        producto = st.selectbox("Producto (campo)", ["uva","mango","limon","palta","arandano"], key="pc")
        año = st.selectbox("Año (campo)", [2021,2022,2023,2024,2025], key="ac")
        mes = st.selectbox("Mes (campo)", ["Todos"] + list(range(1,13)), key="mc")

        key = ("campo", producto, año)
        if key not in DRIVE_MAP:
            st.info("📌 Información de campos en proceso de mejora.")
        else:
            df = load_drive_csv(DRIVE_MAP[key])
            df.columns = [c.lower() for c in df.columns]

            if "mes certificacion" in df.columns:
                df["mes certificacion"] = df["mes certificacion"].apply(normalize_month)
                if mes!="Todos":
                    df = df[df["mes certificacion"]==mes]

            if u["role"]!="admin":
                st.dataframe(df.head(3))
                st.markdown(f"🔓 **Acceso completo:** [Adquirir data completa aquí](mailto:{CONTACT_EMAIL})")
            else:
                st.dataframe(df)

    st.markdown("✅ **Data Core – MVP estable | Escalable | Compatible con 13G**")

# =========================
# MAIN
# =========================
if "user" not in st.session_state:
    auth_screen()
else:
    dashboard()
