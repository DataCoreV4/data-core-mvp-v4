import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import os
import re

st.set_page_config(page_title="Data Core", layout="wide")

# ======================================================
# CONFIGURACIÓN GENERAL
# ======================================================
USERS_FILE = "users.csv"

ADMIN_USER = "DATACORE_ADMIN"
ADMIN_PASS = "DataCore@2025"

PRODUCTOS = ["uva", "mango", "arandano", "limon", "palta"]
MESES = ["Todos"] + list(range(1, 13))

# ======================================================
# TABLA MAESTRA (TAL CUAL TU DRIVE)
# ======================================================
RAW_TABLE = [
    # AÑO, BASE, TIPO, PRODUCTO, URL
    (2021,"envios","uva","1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF"),
    (2021,"envios","mango","1k6CxjPufa0YF17e264BI8NYO1rFFZuc7"),
    (2021,"envios","arandano","1CyFQu-BdYNxFSoed9SGvKnkimrJjS2Q9"),
    (2021,"envios","limon","1--9cfYzrB2giYCy5khZmqXdXL_46Zuz8"),
    (2021,"envios","palta","1-BK3uEDMAMrTAdqxMJd-pIYCg0Rp-8kJ"),

    (2021,"campo","uva","1k6OMQxl7B3hVY9OVECc9UlYcytIjpN1A"),
    (2021,"campo","mango","1JX50r2NJYG3HjalUTZ5pCHmbD5DXQDUu"),
    (2021,"campo","arandano","1HOKP2FaW9UPRYyA7tIj0oSnGzUhkb3h4"),
    (2021,"campo","limon","12xOZVXqxvvepb97On1H8feKUoW_u1Qet"),
    (2021,"campo","palta","1ckjszJeuyPQS6oVNeWFd-FwoM8FTalHO"),

    (2022,"envios","uva","1wHxIXmn2stnjdFSnu8spnOSDw9Q45Dti"),
    (2022,"envios","mango","1kjtC1QVGe4w3GWEYhMmB9VD98eYjhvPh"),
    (2022,"envios","arandano","1tJRlp3FWvYZBr3LFPV1PFke3o6LZcOfa"),
    (2022,"envios","limon","1HfO0jh0yPXK99P8mQ080KLEevc4QVnLT"),
    (2022,"envios","palta","1IYS7yUDFmeCw3YyCIgKDbayZ63AORHvf"),

    (2022,"campo","uva","1LS_80bCCgGE4flJ2BEzav1XeQQSrSX1y"),
    (2022,"campo","mango","16CDM3zQnH3S5n2SNjqwJmk0oUGkbxtJS"),
    (2022,"campo","arandano","1WTkBElLqv3aLQ8s2rkmlQqHM1zsKE33-"),
    (2022,"campo","limon","123wwsJLNrvlTxh2VRZQy1JpVOjI9Oj32"),
    (2022,"campo","palta","1uIs_MXnilSoPIGhtJtmOCv8N8un2VoFg"),

    (2023,"envios","uva","1SZjCd3ANa4CF0N0lK_mnOQfzn0-ywTLs"),
    (2023,"envios","mango","1S5mMR3nG_DeH3ZpOqAvcjidzPQMW8kw_"),
    (2023,"envios","arandano","1JhAhZi3roOQpw5ejm3jnW5Av59De8wc2"),
    (2023,"envios","limon","1sGnvph11F431fg5v9c8qzoH-Yxytffti"),
    (2023,"envios","palta","1MCaBirErsv3PeJZ4soi2Fszw8QcJbg7w"),

    (2023,"campo","uva","11sb54WtgNe0poLSR4q-nEGvjMdbnjXiq"),
    (2023,"campo","mango","1qV3zoDQNnzeEvQR0eZ0FnrvxdkuruyUM"),
    (2023,"campo","arandano","1jdNrMyVcW2HV5PJI63_A_oxl6xLpapl7"),
    (2023,"campo","limon","1F708yJNg3mzrdHi53Dmw4RQZkTqUh4YH"),
    (2023,"campo","palta","1ZBXYrxS4iJ-lUBPKAMtr4ZIWGf6Wh6ED"),

    (2024,"envios","uva","1csIY-AT7Uw6QFp49SANyHALHuZO3r65n"),
    (2024,"envios","mango","1In6_xnpKZwD1zTG4JrD3uhk7sYNKU4qF"),
    (2024,"envios","arandano","1CZSWhLV-STPw9k90cOVzQxJ0V2k7ZTUa"),
    (2024,"envios","limon","1XxGB8PGI4yh5K5mO5qGqRnSK_Fe2nPAX"),
    (2024,"envios","palta","1mLNGjAunM6HTiCnJIgEoaqZQEuegfSf9"),

    (2024,"campo","uva","15CoNL-b9tONKTjbj2rIy8cthyeVhsD_F"),
    (2024,"campo","mango","1T6OVYHVN6j57Km9Z8zWrKYMlzTUIeRes"),
    (2024,"campo","arandano","1YejBbqWi383QjeJntU-AaICQw0TOJyaV"),
    (2024,"campo","limon","1JH6oXdDP5z-JAQgu9WvT-ej1pCjnX6WS"),
    (2024,"campo","palta","1fxh3QgnZXzjkuqmwG4w9h1YjhK6PPvX9"),

    (2025,"envios","uva","1iw-OafOHph_epXgf-6kreXhq2GxzNqyN"),
    (2025,"envios","mango","1-f5tlde1nBJnl_9BbRJkaDpGBleYtbyG"),
    (2025,"envios","arandano","1TxC9TwgFojnNRkQlOI27KJBzG0TK7tp7"),
    (2025,"envios","limon","1G8VbTnSeOcJJVDRkze9s12TRts5BvQx6"),
    (2025,"envios","palta","1Qt680UXFnKBh7bdV0iGqnJKKmc1suNVA"),

    (2025,"campo","uva","15R-9ECTNpSQM1FC8tFPUs0emE16H8cHT"),
    (2025,"campo","mango","11IziWG98PfqkSyTaK5GvKwU4NEC9LwXJ"),
    (2025,"campo","arandano","15w2FG2TT_qPfxEksBgcGbfPu67yNbvYT"),
    (2025,"campo","limon","178kHRjqLgs-EFUmzCsNclBKq-nYmVJPO"),
    (2025,"campo","palta","1fo9HKY9DSKAjgLVKsx2H0Y7f_YU4DwRT"),
]

DRIVE_MAP = {(y,t,p):fid for y,t,p,fid in RAW_TABLE}
YEARS = sorted({y for y,_,_,_ in RAW_TABLE})

# ======================================================
# UTILIDADES
# ======================================================
def load_drive_csv(file_id):
    try:
        url = f"https://drive.google.com/uc?id={file_id}"
        r = requests.get(url)
        r.raise_for_status()
        return pd.read_csv(BytesIO(r.content), engine="python")
    except:
        return None

# ======================================================
# USUARIOS
# ======================================================
def load_users():
    cols = ["usuario","password","rol","nombre","apellido","dni","correo","celular","empresa","cargo"]
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=cols).to_csv(USERS_FILE, index=False)
    df = pd.read_csv(USERS_FILE)
    return df[cols]

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

def ensure_admin():
    df = load_users()
    df = df[df.usuario != ADMIN_USER]
    admin = pd.DataFrame([{
        "usuario": ADMIN_USER,
        "password": ADMIN_PASS,
        "rol": "admin",
        "nombre": "Administrador",
        "apellido": "",
        "dni": "",
        "correo": "",
        "celular": "",
        "empresa": "Data Core",
        "cargo": "Admin"
    }])
    df = pd.concat([df, admin], ignore_index=True)
    save_users(df)

# ======================================================
# AUTH
# ======================================================
def auth_screen():
    st.title("🔐 Data Core – Acceso")
    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

    # ---------- LOGIN ----------
    with tab1:
        u = st.text_input("Usuario", key="login_user")
        p = st.text_input("Contraseña", type="password", key="login_pass")

        if st.button("Ingresar", key="login_btn"):
            df = load_users()
            row = df[(df.usuario == u) & (df.password == p)]
            if not row.empty:
                st.session_state.user = row.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    # ---------- REGISTRO ----------
    with tab2:
        reg_usuario = st.text_input("Usuario", key="reg_usuario")
        reg_pass = st.text_input("Contraseña", type="password", key="reg_pass")
        reg_pass2 = st.text_input("Repetir contraseña", type="password", key="reg_pass2")
        reg_nombre = st.text_input("Nombre", key="reg_nombre")
        reg_apellido = st.text_input("Apellido", key="reg_apellido")
        reg_dni = st.text_input("DNI", key="reg_dni")
        reg_correo = st.text_input("Correo electrónico", key="reg_correo")
        reg_celular = st.text_input("Celular", key="reg_celular")
        reg_empresa = st.text_input("Empresa (opcional)", key="reg_empresa")
        reg_cargo = st.text_input("Cargo (opcional)", key="reg_cargo")

        if st.button("Registrar", key="reg_btn"):
            if reg_pass != reg_pass2:
                st.error("Las contraseñas no coinciden")
                return

            df = load_users()
            if reg_usuario in df.usuario.values:
                st.error("El usuario ya existe")
                return

            new = {
                "usuario": reg_usuario,
                "password": reg_pass,
                "rol": "freemium",
                "nombre": reg_nombre,
                "apellido": reg_apellido,
                "dni": reg_dni,
                "correo": reg_correo,
                "celular": reg_celular,
                "empresa": reg_empresa,
                "cargo": reg_cargo
            }

            df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
            save_users(df)
            st.success("Registro exitoso. Ahora puede ingresar.")

# ======================================================
# DASHBOARD
# ======================================================
def dashboard():
    u = st.session_state.user
    st.markdown(f"## 👋 Bienvenido, {u['nombre'] or u['usuario']}")

    c1,c2,c3 = st.columns(3)
    prod = c1.selectbox("Producto", PRODUCTOS)
    year = c2.selectbox("Año", YEARS)
    mes = c3.selectbox("Mes", MESES)

    colA,colB = st.columns(2)

    with colA:
        st.subheader("📦 Envíos")
        key = (year,"envios",prod)
        df = load_drive_csv(DRIVE_MAP[key]) if key in DRIVE_MAP else None
        if df is None:
            st.info("📌 Información en proceso de mejora")
        else:
            if u["rol"] == "freemium":
                st.dataframe(df.head(3))
                st.markdown("🔓 **Adquirir data completa:** datacore.agrotech@gmail.com")
            else:
                st.dataframe(df)

    with colB:
        st.subheader("🌾 Campos certificados")
        key = (year,"campo",prod)
        df = load_drive_csv(DRIVE_MAP[key]) if key in DRIVE_MAP else None
        if df is None:
            st.info("📌 Información en proceso de mejora")
        else:
            if u["rol"] == "freemium":
                st.dataframe(df.head(3))
                st.markdown("🔓 **Adquirir data completa:** datacore.agrotech@gmail.com")
            else:
                st.dataframe(df)

    if u["rol"] == "admin":
        st.divider()
        st.subheader("🛠 Gestión de usuarios")
        users = load_users()
        st.dataframe(users[["usuario","rol","correo"]])
        sel = st.selectbox("Usuario", users.usuario)
        new_role = st.selectbox("Nuevo rol", ["freemium","premium"])
        if st.button("Actualizar rol"):
            users.loc[users.usuario == sel, "rol"] = new_role
            save_users(users)
            st.success("Rol actualizado")

# ======================================================
# MAIN
# ======================================================
ensure_admin()

if "user" not in st.session_state:
    auth_screen()
else:
    dashboard()
