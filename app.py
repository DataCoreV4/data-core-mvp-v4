import streamlit as st
import pandas as pd
import hashlib
import os

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================
st.set_page_config(
    page_title="Data Core – Inteligencia Agroexportadora",
    layout="wide"
)

# =====================================================
# UTILIDADES
# =====================================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# =====================================================
# CONFIG ADMIN
# =====================================================
ADMIN_EMAIL = "admin@datacore.pe"
ADMIN_PASSWORD = hash_password("Admin2025!")

# =====================================================
# USUARIOS
# =====================================================
USERS_FILE = "usuarios.csv"

def cargar_usuarios():
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    return pd.DataFrame(columns=[
        "nombre","apellido","dni","correo",
        "celular","empresa","cargo","password"
    ])

def correo_existe(correo):
    return correo in cargar_usuarios()["correo"].values

def guardar_usuario(data):
    usuarios = cargar_usuarios()
    usuarios = pd.concat([usuarios, pd.DataFrame([data])], ignore_index=True)
    usuarios.to_csv(USERS_FILE, index=False)

def validar_login(correo, password):
    if correo == ADMIN_EMAIL and hash_password(password) == ADMIN_PASSWORD:
        st.session_state.admin = True
        return True

    usuarios = cargar_usuarios()
    pwd = hash_password(password)
    user = usuarios[
        (usuarios["correo"] == correo) &
        (usuarios["password"] == pwd)
    ]

    if not user.empty:
        st.session_state.admin = False
        return True

    return False

# =====================================================
# SESIÓN
# =====================================================
if "login" not in st.session_state:
    st.session_state.login = False

if "admin" not in st.session_state:
    st.session_state.admin = False

# =====================================================
# PORTADA
# =====================================================
if not st.session_state.login:

    col1, col2, col3 = st.columns([1,2,1])
    with col2:

        # LOGO (PNG o JPG)
        for logo in ["logotipo_datacore.jpg", "logo_datacore.png"]:
            if os.path.exists(logo):
                try:
                    st.image(logo, width=260)
                    break
                except:
                    pass

        st.title("🌱 Data Core")
        st.subheader("Plataforma de inteligencia agroexportadora")

        opcion = st.radio("Acceso", ["Iniciar sesión", "Registrarse"])

        if opcion == "Iniciar sesión":
            correo = st.text_input("Correo electrónico")
            password = st.text_input("Contraseña", type="password")

            if st.button("Ingresar"):
                if validar_login(correo, password):
                    st.session_state.login = True
                    st.session_state.usuario = correo
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")

        else:
            st.markdown("### Registro")

            nombre = st.text_input("Nombre")
            apellido = st.text_input("Apellido")
            dni = st.text_input("DNI")
            correo = st.text_input("Correo electrónico")
            celular = st.text_input("Celular")
            empresa = st.text_input("Empresa (opcional)")
            cargo = st.text_input("Cargo (opcional)")
            p1 = st.text_input("Contraseña", type="password")
            p2 = st.text_input("Repetir contraseña", type="password")

            if st.button("Registrarse"):
                if correo_existe(correo):
                    st.error("Correo ya registrado")
                elif p1 != p2:
                    st.error("Las contraseñas no coinciden")
                else:
                    guardar_usuario({
                        "nombre": nombre,
                        "apellido": apellido,
                        "dni": dni,
                        "correo": correo,
                        "celular": celular,
                        "empresa": empresa,
                        "cargo": cargo,
                        "password": hash_password(p1)
                    })
                    st.success("Registro exitoso. Inicie sesión.")

    st.stop()

# =====================================================
# SIDEBAR
# =====================================================
for logo in ["logotipo_datacore.jpg", "logo_datacore.png"]:
    if os.path.exists(logo):
        try:
            st.sidebar.image(logo, width=180)
            break
        except:
            pass

st.sidebar.markdown(f"👤 **{st.session_state.usuario}**")

if st.session_state.admin:
    st.sidebar.success("Administrador")
else:
    st.sidebar.info("Freemium")

if st.sidebar.button("Cerrar sesión"):
    st.session_state.login = False
    st.session_state.admin = False
    st.rerun()

# =====================================================
# DASHBOARD
# =====================================================
st.title("📊 Data Core – Dashboard")

# =====================================================
# CARGA DE DATOS (NOMBRES REALES)
# =====================================================
@st.cache_data
def cargar_envios():
    archivos = [
        "datos.csv",
        "datos_reales.csv",
        "datos_arandano_1_6.csv"
    ]
    dfs = []
    for f in archivos:
        if os.path.exists(f):
            try:
                df = pd.read_csv(f, low_memory=False)
                dfs.append(df)
            except:
                pass
    if dfs:
        df = pd.concat(dfs, ignore_index=True)
        df.columns = df.columns.str.lower()
        return df
    return pd.DataFrame()

@st.cache_data
def cargar_campos():
    archivos = [
        "datos_campo_limon_2025.csv",
        "datos_campo_arandano_2025.csv"
    ]
    dfs = []
    for f in archivos:
        if os.path.exists(f):
            try:
                df = pd.read_csv(f, low_memory=False)
                dfs.append(df)
            except:
                pass
    if dfs:
        df = pd.concat(dfs, ignore_index=True)
        df.columns = df.columns.str.lower()
        return df
    return pd.DataFrame()

envios = cargar_envios()
campos = cargar_campos()

# =====================================================
# ENVÍOS
# =====================================================
st.subheader("📦 Envíos")

if envios.empty:
    st.warning("No hay datos de envíos cargados.")
else:
    if "producto" not in envios.columns:
        st.error("No existe la columna 'producto' en los datos.")
    else:
        productos = sorted(envios["producto"].dropna().unique())

        if not productos:
            st.warning("No hay productos disponibles.")
        else:
            producto = st.selectbox("Producto", productos)
            dfp = envios[envios["producto"] == producto]

            st.metric("Total de envíos", len(dfp))

            if st.session_state.admin:
                st.dataframe(dfp, use_container_width=True)
            else:
                st.dataframe(dfp.head(3), use_container_width=True)
                st.info("Modo freemium – vista limitada")

# =====================================================
# CAMPOS
# =====================================================
st.subheader("🌾 Campos certificados")

if campos.empty:
    st.warning("No hay datos de campos certificados.")
else:
    if st.session_state.admin:
        st.dataframe(campos, use_container_width=True)
    else:
        st.dataframe(campos.head(3), use_container_width=True)
        st.info("Modo freemium – vista limitada")

st.success("✅ Data Core v1.0 – datos cargados correctamente")
