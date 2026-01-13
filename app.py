import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(page_title="Data Core", layout="wide")

ADMIN_ROLE = "admin"
FREEMIUM_ROLE = "freemium"
CONTACT_EMAIL = "datacore.agrotech@gmail.com"

# =========================
# UTILIDADES
# =========================
def download_drive_file(url):
    file_id = url.split("/d/")[1].split("/")[0]
    download_url = f"https://drive.google.com/uc?id={file_id}&export=download"
    r = requests.get(download_url)
    r.raise_for_status()
    return BytesIO(r.content)

def load_csv_from_drive(url):
    return pd.read_csv(
        download_drive_file(url),
        sep=";",
        encoding="latin1",
        on_bad_lines="skip",
        low_memory=False
    )

def normalize_columns(df):
    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
        .str.replace("á","a")
        .str.replace("é","e")
        .str.replace("í","i")
        .str.replace("ó","o")
        .str.replace("ú","u")
        .str.replace("ñ","n")
    )
    return df

def normalize_month(val):
    if pd.isna(val):
        return None
    val = str(val).lower().strip()
    meses = {
        "ene":1,"enero":1,"1":1,
        "feb":2,"febrero":2,"2":2,
        "mar":3,"marzo":3,"3":3,
        "abr":4,"abril":4,"4":4,
        "may":5,"mayo":5,"5":5,
        "jun":6,"junio":6,"6":6,
        "jul":7,"julio":7,"7":7,
        "ago":8,"agosto":8,"8":8,
        "sep":9,"septiembre":9,"9":9,
        "oct":10,"octubre":10,"10":10,
        "nov":11,"noviembre":11,"11":11,
        "dic":12,"diciembre":12,"12":12
    }
    return meses.get(val)

def apply_freemium_limit(df):
    if st.session_state["role"] == FREEMIUM_ROLE:
        return df.head(3)
    return df

def acquisition_message(tipo):
    if st.session_state["role"] == FREEMIUM_ROLE:
        st.markdown(
            f"""
            🔓 **¿Deseas acceder a la data completa y actualizada de {tipo}?**  
            Adquiere acceso premium para este producto y período.

            📩 **Solicítalo aquí:**  
            [Enviar solicitud por correo](mailto:{CONTACT_EMAIL})
            """
        )

# =========================
# DRIVE MAP (YA FUNCIONANDO)
# =========================
DRIVE_MAP = {
    ("envios","uva",2021): "https://drive.google.com/file/d/1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF/view",
    ("envios","mango",2021): "https://drive.google.com/file/d/1k6CxjPufa0YF17e264BI8NYO1rFFZuc7/view",
    ("envios","arandano",2021): "https://drive.google.com/file/d/1CyFQu-BdYNxFSoed9SGvKnkimrJjS2Q9/view",
    ("envios","limon",2021): "https://drive.google.com/file/d/1--9cfYzrB2giYCy5khZmqXdXL_46Zuz8/view",
    ("envios","palta",2021): "https://drive.google.com/file/d/1-BK3uEDMAMrTAdqxMJd-pIYCg0Rp-8kJ/view",
    # 👉 el resto YA ESTÁ en tu código base estable
}

# =========================
# DASHBOARD
# =========================
def dashboard():
    st.title("📊 Data Core – Dashboard")
    st.write(f"👋 Bienvenido, **{st.session_state['user']}**")

    # -------- FILTROS GLOBALES --------
    col1, col2, col3 = st.columns(3)

    with col1:
        producto = st.selectbox("Producto", ["uva","mango","arandano","limon","palta"])

    with col2:
        anio = st.selectbox("Año", [2021,2022,2023,2024,2025])

    with col3:
        mes_sel = st.selectbox(
            "Mes",
            ["Todos",1,2,3,4,5,6,7,8,9,10,11,12]
        )

    # =========================
    # ENVÍOS
    # =========================
    st.subheader("📦 Envíos")

    key_env = ("envios", producto, anio)

    if key_env in DRIVE_MAP:
        try:
            df_env = normalize_columns(load_csv_from_drive(DRIVE_MAP[key_env]))

            # MES
            if "mes" in df_env.columns:
                df_env["mes_norm"] = df_env["mes"].apply(normalize_month)
                if mes_sel != "Todos":
                    df_env = df_env[df_env["mes_norm"] == mes_sel]

            # PAÍS DESTINO
            if "pais destino" in df_env.columns:
                paises = ["Todos"] + sorted(df_env["pais destino"].dropna().unique())
                pais_sel = st.selectbox("País destino", paises)
                if pais_sel != "Todos":
                    df_env = df_env[df_env["pais destino"] == pais_sel]

            df_env = apply_freemium_limit(df_env)
            st.dataframe(df_env, use_container_width=True)
            acquisition_message("Envíos")

        except Exception as e:
            st.info("📌 Información en proceso de mejora.")
    else:
        st.info("📌 Información en proceso de mejora.")

    st.divider()

    # =========================
    # CAMPOS
    # =========================
    st.subheader("🌾 Campos certificados")

    key_campo = ("campo", producto, anio)

    if key_campo in DRIVE_MAP:
        try:
            df_c = normalize_columns(load_csv_from_drive(DRIVE_MAP[key_campo]))

            if "mes" in df_c.columns:
                df_c["mes_norm"] = df_c["mes"].apply(normalize_month)
                if mes_sel != "Todos":
                    df_c = df_c[df_c["mes_norm"] == mes_sel]

            df_c = apply_freemium_limit(df_c)
            st.dataframe(df_c, use_container_width=True)
            acquisition_message("Campos certificados")

        except Exception:
            st.info("📌 Información de campos en proceso de mejora.")
    else:
        st.info("📌 Información de campos en proceso de mejora.")

# =========================
# SESIÓN (YA EXISTENTE)
# =========================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = True
    st.session_state["user"] = "DCADMIN"
    st.session_state["role"] = ADMIN_ROLE

dashboard()
