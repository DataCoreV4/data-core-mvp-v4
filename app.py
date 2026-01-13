import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# ======================================
# CONFIGURACIÓN GENERAL
# ======================================
st.set_page_config(
    page_title="Data Core – Dashboard",
    layout="wide"
)

LOGO_PATH = "logotipo_datacore.jpg"
CONTACT_EMAIL = "datacore.agrotech@gmail.com"
USERS_FILE = "users.csv"

# ======================================
# USUARIOS – CARGA SEGURA
# ======================================
EXPECTED_COLUMNS = [
    "usuario", "password", "nombre", "apellido",
    "dni", "email", "tipo"
]

def load_users():
    try:
        df = pd.read_csv(USERS_FILE)

        # Si faltan columnas → reconstruir
        if not set(EXPECTED_COLUMNS).issubset(df.columns):
            raise ValueError("Estructura inválida")

        return df

    except Exception:
        df = pd.DataFrame(columns=EXPECTED_COLUMNS)
        df.to_csv(USERS_FILE, index=False)
        return df

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

# ======================================
# ADMIN SEGURO
# ======================================
def ensure_admin():
    users = load_users()

    if "usuario" not in users.columns:
        users = pd.DataFrame(columns=EXPECTED_COLUMNS)

    if not (users["usuario"].str.upper() == "DCADMIN").any():
        admin = pd.DataFrame([{
            "usuario": "DCADMIN",
            "password": "admindatacore123!",
            "nombre": "Data",
            "apellido": "Core",
            "dni": "00000000",
            "email": "admin@datacore.pe",
            "tipo": "admin"
        }])
        users = pd.concat([users, admin], ignore_index=True)
        save_users(users)

ensure_admin()

# ======================================
# GOOGLE DRIVE MAP
# ======================================
DRIVE_MAP = {
    ("envios","uva",2021): "1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF",
    ("campo","uva",2021): "1k6OMQxl7B3hVY9OVECc9UlYcytIjpN1A",
    # 👉 sigue agregando aquí sin romper nada
}

# ======================================
# UTILIDADES
# ======================================
def drive_url(file_id):
    return f"https://drive.google.com/uc?id={file_id}"

def load_drive_csv(file_id):
    r = requests.get(drive_url(file_id))
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
    val = str(val).lower().strip()
    months = {
        "ene":1,"feb":2,"mar":3,"abr":4,"may":5,"jun":6,
        "jul":7,"ago":8,"sep":9,"oct":10,"nov":11,"dic":12
    }
    if val.isdigit():
        return int(val)
    for k,v in months.items():
        if val.startswith(k):
            return v
    return None

# ======================================
# AUTH
# ======================================
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
        password = st.text_input("Contraseña", type="password")

        if st.button("Registrarse"):
            users = load_users()
            if (users["usuario"] == usuario).any():
                st.error("Usuario ya existe")
            else:
                nuevo = {
                    "usuario": usuario,
                    "password": password,
                    "nombre": nombre,
                    "apellido": apellido,
                    "dni": dni,
                    "email": email,
                    "tipo": "freemium"
                }
                users = pd.concat([users, pd.DataFrame([nuevo])])
                save_users(users)
                st.success("Registro exitoso. Ya puedes ingresar.")

# ======================================
# DASHBOARD
# ======================================
def dashboard():
    user = st.session_state.user

    st.image(LOGO_PATH, width=120)
    st.markdown(f"👋 **Bienvenido, {user['nombre']}**")

    col1, col2, col3 = st.columns(3)
    producto = col1.selectbox("Producto", ["uva","mango","arandano","limon","palta"])
    año = col2.selectbox("Año", list(range(2021, 2026)))
    mes = col3.selectbox("Mes", ["Todos"] + list(range(1,13)))

    # ===============================
    # ENVÍOS
    # ===============================
    st.subheader("📦 Envíos")
    key = ("envios", producto, año)

    if key in DRIVE_MAP:
        df = load_drive_csv(DRIVE_MAP[key])

        for c in df.columns:
            if "mes" in c.lower():
                df["_mes"] = df[c].apply(normalize_month)
                break

        if mes != "Todos":
            df = df[df["_mes"] == mes]

        if user["tipo"] == "freemium":
            st.dataframe(df.head(3))
            st.info("🔓 Acceso completo: Adquirir data completa aquí")
            st.markdown(f"[Enviar solicitud](mailto:{CONTACT_EMAIL})")
        else:
            st.dataframe(df)
    else:
        st.info("📌 Información en proceso de mejora.")

    # ===============================
    # CAMPO
    # ===============================
    st.subheader("🌾 Campos certificados")
    key = ("campo", producto, año)

    if key in DRIVE_MAP:
        dfc = load_drive_csv(DRIVE_MAP[key])

        for c in dfc.columns:
            if "mes" in c.lower():
                dfc["_mes"] = dfc[c].apply(normalize_month)
                break

        if mes != "Todos":
            dfc = dfc[dfc["_mes"] == mes]

        if user["tipo"] == "freemium":
            st.dataframe(dfc.head(3))
            st.info("🔓 Acceso completo: Adquirir data completa aquí")
            st.markdown(f"[Enviar solicitud](mailto:{CONTACT_EMAIL})")
        else:
            st.dataframe(dfc)
    else:
        st.info("📌 Información de campos en proceso de mejora.")

    # ===============================
    # ADMIN
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

# ======================================
# MAIN
# ======================================
if "user" not in st.session_state:
    auth_screen()
else:
    dashboard()
