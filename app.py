import streamlit as st
import pandas as pd
import hashlib
import os

# ===============================
# CONFIGURACIÓN GENERAL
# ===============================
st.set_page_config(
    page_title="Data Core – Inteligencia Agroexportadora",
    layout="wide"
)

# ===============================
# FUNCIONES DE USUARIOS
# ===============================
USERS_FILE = "usuarios.csv"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def cargar_usuarios():
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    else:
        return pd.DataFrame(columns=[
            "nombre", "apellido", "dni", "correo", "celular",
            "empresa", "cargo", "password"
        ])

def guardar_usuario(data):
    usuarios = cargar_usuarios()
    usuarios = pd.concat([usuarios, pd.DataFrame([data])], ignore_index=True)
    usuarios.to_csv(USERS_FILE, index=False)

def correo_existe(correo):
    usuarios = cargar_usuarios()
    return correo in usuarios["correo"].values

def validar_login(correo, password):
    usuarios = cargar_usuarios()
    pwd_hash = hash_password(password)
    user = usuarios[
        (usuarios["correo"] == correo) &
        (usuarios["password"] == pwd_hash)
    ]
    return not user.empty

# ===============================
# SESIÓN
# ===============================
if "login" not in st.session_state:
    st.session_state.login = False

# ===============================
# PORTADA / LOGIN / REGISTRO
# ===============================
if not st.session_state.login:

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if os.path.exists("logo_datacore.png"):
            st.image("logo_datacore.png", width=250)

        st.title("🌱 Data Core")
        st.subheader("Plataforma de inteligencia agroexportadora")
        st.markdown(
            "Análisis de datos reales de **certificaciones, inspecciones y envíos** "
            "para la toma de decisiones estratégicas."
        )

        opcion = st.radio("Acceso", ["Iniciar sesión", "Registrarse"])

        # -------- LOGIN --------
        if opcion == "Iniciar sesión":
            correo = st.text_input("Correo electrónico")
            password = st.text_input("Contraseña", type="password")

            if st.button("Ingresar"):
                if validar_login(correo, password):
                    st.session_state.login = True
                    st.session_state.usuario = correo
                    st.success("Acceso correcto")
                    st.rerun()
                else:
                    st.error("Correo o contraseña incorrectos")

        # -------- REGISTRO --------
        else:
            st.markdown("### Registro de usuario")

            nombre = st.text_input("Nombre")
            apellido = st.text_input("Apellido")
            dni = st.text_input("DNI")
            correo = st.text_input("Correo electrónico")
            celular = st.text_input("Celular")
            empresa = st.text_input("Empresa (opcional)")
            cargo = st.text_input("Cargo (opcional)")
            password = st.text_input("Contraseña", type="password")
            password2 = st.text_input("Repetir contraseña", type="password")

            if st.button("Registrarse"):
                if correo_existe(correo):
                    st.error("Este correo ya está registrado")
                elif password != password2:
                    st.error("Las contraseñas no coinciden")
                elif not nombre or not apellido or not dni or not correo:
                    st.error("Complete los campos obligatorios")
                else:
                    guardar_usuario({
                        "nombre": nombre,
                        "apellido": apellido,
                        "dni": dni,
                        "correo": correo,
                        "celular": celular,
                        "empresa": empresa,
                        "cargo": cargo,
                        "password": hash_password(password)
                    })
                    st.success("Registro exitoso. Ahora puede iniciar sesión.")

    st.stop()

# ===============================
# DASHBOARD (USUARIO LOGUEADO)
# ===============================
st.sidebar.image("logo_datacore.png", width=180)
st.sidebar.markdown(f"👤 Usuario: **{st.session_state.usuario}**")
st.sidebar.info("Modo: Freemium")

if st.sidebar.button("Cerrar sesión"):
    st.session_state.login = False
    st.rerun()

st.title("📊 Data Core – Dashboard")

# ===============================
# CARGA DE DATOS
# ===============================
@st.cache_data
def cargar_envios():
    dfs = []
    if os.path.exists("datos_reales.csv"):
        dfs.append(pd.read_csv("datos_reales.csv", low_memory=False))
    if os.path.exists("data_arandano_1_6.csv"):
        dfs.append(pd.read_csv("data_arandano_1_6.csv", low_memory=False))
    if dfs:
        df = pd.concat(dfs, ignore_index=True)
        df.columns = df.columns.str.lower()
        return df
    return pd.DataFrame()

@st.cache_data
def cargar_campos():
    dfs = []
    if os.path.exists("data_campo_limon_2025.csv"):
        dfs.append(pd.read_csv("data_campo_limon_2025.csv", low_memory=False))
    if os.path.exists("data_campo_arandano_2025.csv"):
        dfs.append(pd.read_csv("data_campo_arandano_2025.csv", low_memory=False))
    if dfs:
        df = pd.concat(dfs, ignore_index=True)
        df.columns = df.columns.str.lower()
        return df
    return pd.DataFrame()

envios = cargar_envios()
campos = cargar_campos()

if envios.empty:
    st.error("No se cargaron datos de envíos")
    st.stop()

# ===============================
# FILTROS
# ===============================
st.subheader("🔎 Filtros")

colf1, colf2, colf3, colf4 = st.columns(4)

with colf1:
    producto = st.selectbox(
        "Producto",
        sorted(envios["producto"].dropna().unique())
    )

dfp = envios[envios["producto"] == producto]

with colf2:
    if "aao_inspeccia3n" in dfp.columns:
        anio = st.selectbox(
            "Año",
            sorted(dfp["aao_inspeccia3n"].dropna().unique())
        )
        dfp = dfp[dfp["aao_inspeccia3n"] == anio]

with colf3:
    if "mes_inspeccia3n" in dfp.columns:
        mes = st.selectbox(
            "Mes",
            sorted(dfp["mes_inspeccia3n"].dropna().unique())
        )
        dfp = dfp[dfp["mes_inspeccia3n"] == mes]

with colf4:
    paises = sorted(dfp["pais_destino"].dropna().unique())
    pais = st.selectbox(
        "País destino",
        ["Todos"] + paises
    )
    if pais != "Todos":
        dfp = dfp[dfp["pais_destino"] == pais]

# ===============================
# RESULTADOS
# ===============================
st.subheader("📦 Envíos registrados")

st.metric("Total de envíos", len(dfp))

st.dataframe(dfp.head(3), use_container_width=True)

st.info("Modo freemium: solo se muestran las 3 primeras filas")

# ===============================
# CAMPOS CERTIFICADOS
# ===============================
if not campos.empty:
    st.subheader("🌾 Campos certificados")
    st.metric("Total de campos registrados", campos.shape[0])
    st.dataframe(campos.head(3), use_container_width=True)
    st.info("Modo freemium: vista limitada")

st.success("Plataforma operativa – Data Core v1.0")
