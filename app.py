import streamlit as st
import pandas as pd
import hashlib
import os
import requests
from io import BytesIO

# ======================================================
# CONFIGURACIÓN GENERAL
# ======================================================
st.set_page_config(
    page_title="Data Core – MVP",
    layout="wide"
)

USERS_FILE = "users.csv"
ADMIN_USER = "DCADMIN"
ADMIN_PASS = "admindatacore123!"
CONTACT_EMAIL = "datacore.agrotech@gmail.com"

# ======================================================
# MAPA DE ARCHIVOS EN GOOGLE DRIVE
# ======================================================
DRIVE_MAP = {
    # ENVÍOS
    (2021, "envios", "uva"): "1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF",
    (2021, "envios", "mango"): "1k6CxjPufa0YF17e264BI8NYO1rFFZuc7",
    (2021, "envios", "arandano"): "1CyFQu-BdYNxFSoed9SGvKnkimrJjS2Q9",
    (2021, "envios", "limon"): "1--9cfYzrB2giYCy5khZmqXdXL_46Zuz8",
    (2021, "envios", "palta"): "1-BK3uEDMAMrTAdqxMJd-pIYCg0Rp-8kJ",
    # CAMPOS
    (2021, "campo", "uva"): "1k6OMQxl7B3hVY9OVECc9UlYcytIjpN1A",
    (2021, "campo", "mango"): "1JX50r2NJYG3HjalUTZ5pCHmbD5DXQDUu",
    (2021, "campo", "arandano"): "1HOKP2FaW9UPRYyA7tIj0oSnGzUhkb3h4",
    (2021, "campo", "limon"): "12xOZVXqxvvepb97On1H8feKUoW_u1Qet",
    (2021, "campo", "palta"): "1ckjszJeuyPQS6oVNeWFd-FwoM8FTalHO",
    # 👉 El resto de años YA está soportado automáticamente
}

# ======================================================
# UTILIDADES
# ======================================================
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=[
            "usuario","password","nombre","apellido","dni",
            "correo","celular","empresa","cargo","tipo"
        ])
        df.to_csv(USERS_FILE, index=False)
    return pd.read_csv(USERS_FILE)

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

def ensure_admin():
    df = load_users()
    if "usuario" not in df.columns:
        df = pd.DataFrame(columns=[
            "usuario","password","nombre","apellido","dni",
            "correo","celular","empresa","cargo","tipo"
        ])
    if not (df["usuario"] == ADMIN_USER).any():
        df.loc[len(df)] = [
            ADMIN_USER,
            hash_pass(ADMIN_PASS),
            "Administrador",
            "Data Core",
            "",
            CONTACT_EMAIL,
            "",
            "Data Core",
            "Admin",
            "admin"
        ]
        save_users(df)

def load_drive_csv(file_id):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
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
    months = {
        "ene":1,"feb":2,"mar":3,"abr":4,"may":5,"jun":6,
        "jul":7,"ago":8,"sep":9,"oct":10,"nov":11,"dic":12
    }
    if val.isdigit():
        return int(val)
    for k,v in months.items():
        if k in val:
            return v
    return None

# ======================================================
# AUTENTICACIÓN
# ======================================================
def auth_screen():
    st.title("🔐 Data Core – Acceso")

    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

    with tab1:
        user = st.text_input("Usuario", key="login_user")
        pwd = st.text_input("Contraseña", type="password", key="login_pwd")
        if st.button("Ingresar"):
            users = load_users()
            hp = hash_pass(pwd)
            ok = users[
                (users["usuario"]==user) &
                (users["password"]==hp)
            ]
            if not ok.empty:
                st.session_state.user = user
                st.session_state.tipo = ok.iloc[0]["tipo"]
                st.session_state.nombre = ok.iloc[0]["nombre"]
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

    with tab2:
        st.subheader("Registro")
        r_user = st.text_input("Usuario", key="reg_user")
        r_pwd1 = st.text_input("Contraseña", type="password", key="reg_pwd1")
        r_pwd2 = st.text_input("Repetir contraseña", type="password", key="reg_pwd2")
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        dni = st.text_input("DNI")
        correo = st.text_input("Correo electrónico")
        celular = st.text_input("Celular")
        empresa = st.text_input("Empresa (opcional)")
        cargo = st.text_input("Cargo (opcional)")

        if st.button("Registrarse"):
            if r_pwd1 != r_pwd2:
                st.error("Las contraseñas no coinciden")
                return
            users = load_users()
            if (users["usuario"]==r_user).any():
                st.error("Usuario ya existe")
                return
            users.loc[len(users)] = [
                r_user,
                hash_pass(r_pwd1),
                nombre,
                apellido,
                dni,
                correo,
                celular,
                empresa,
                cargo,
                "freemium"
            ]
            save_users(users)
            st.success("Registro exitoso. Ya puedes ingresar.")

# ======================================================
# DASHBOARD
# ======================================================
def dashboard():
    st.markdown(f"### 👋 Bienvenido, **{st.session_state.nombre}**")

    productos = ["uva","mango","arandano","limon","palta"]
    years = sorted({k[0] for k in DRIVE_MAP.keys()})

    colf1,colf2,colf3 = st.columns(3)
    producto = colf1.selectbox("Producto", productos)
    year = colf2.selectbox("Año", years)
    mes = colf3.selectbox("Mes", ["Todos"] + list(range(1,13)))

    col1, col2 = st.columns(2)

    # ================= ENVIOS =================
    with col1:
        st.subheader("📦 Envíos")
        key = (year,"envios",producto)
        if key not in DRIVE_MAP:
            st.info("📌 Información en proceso de mejora.")
        else:
            try:
                df = load_drive_csv(DRIVE_MAP[key])
                df.columns = [c.lower() for c in df.columns]

                # Año
                year_cols = [c for c in df.columns if "año" in c]
                if year_cols:
                    df = df[df[year_cols[0]] == year]

                # Mes
                mes_cols = [c for c in df.columns if "mes" in c]
                if mes != "Todos" and mes_cols:
                    df["__mes"] = df[mes_cols[0]].apply(normalize_month)
                    df = df[df["__mes"] == mes]

                # País destino
                pais_cols = [c for c in df.columns if "pais destino" in c]
                if pais_cols:
                    paises = sorted(df[pais_cols[0]].dropna().unique())
                    pais_sel = st.selectbox("Pais Destino", ["Todos"]+paises)
                    if pais_sel != "Todos":
                        df = df[df[pais_cols[0]]==pais_sel]

                if df.empty:
                    st.info("📌 Información en proceso de mejora.")
                else:
                    if st.session_state.tipo != "admin":
                        st.dataframe(df.head(3))
                        st.warning("🔓 Acceso limitado (Freemium)")
                        st.markdown(
                            f"[Adquirir data completa aquí](mailto:{CONTACT_EMAIL}?subject=Acceso%20Envíos%20{producto})"
                        )
                    else:
                        st.dataframe(df)

            except Exception as e:
                st.error("Error cargando data")

    # ================= CAMPOS =================
    with col2:
        st.subheader("🌾 Campos certificados")
        key = (year,"campo",producto)
        if key not in DRIVE_MAP:
            st.info("📌 Información de campos en proceso de mejora.")
        else:
            try:
                df = load_drive_csv(DRIVE_MAP[key])
                df.columns = [c.lower() for c in df.columns]

                year_cols = [c for c in df.columns if "año" in c]
                if year_cols:
                    df = df[df[year_cols[0]] == year]

                mes_cols = [c for c in df.columns if "mes" in c]
                if mes != "Todos" and mes_cols:
                    df["__mes"] = df[mes_cols[0]].apply(normalize_month)
                    df = df[df["__mes"] == mes]

                if df.empty:
                    st.info("📌 Información de campos en proceso de mejora.")
                else:
                    if st.session_state.tipo != "admin":
                        st.dataframe(df.head(3))
                        st.warning("🔓 Acceso limitado (Freemium)")
                        st.markdown(
                            f"[Adquirir data completa aquí](mailto:{CONTACT_EMAIL}?subject=Acceso%20Campos%20{producto})"
                        )
                    else:
                        st.dataframe(df)

            except Exception:
                st.error("Error cargando data")

    st.markdown("---")
    st.caption("✅ Data Core – MVP estable | Escalable | Compatible con 13G")

# ======================================================
# MAIN
# ======================================================
ensure_admin()

if "user" not in st.session_state:
    auth_screen()
else:
    dashboard()
