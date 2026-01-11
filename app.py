import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Data Core", layout="wide")

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

LOGO_PATH = "logo_datacore.jpg"
MAIL_TO = "datacore.agrotech@gmail.com"

# --------------------------------------------------
# UTILIDADES
# --------------------------------------------------
def load_csv_safe(file):
    if os.path.exists(file):
        return pd.read_csv(file, encoding="latin1", sep=";")
    return None

def limit_df(df, is_admin):
    if is_admin:
        return df
    return df.head(3)

# --------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------
shipments_files = [
    "datos_reales.csv",
    "data_arandano_1_6.csv"
]

shipments = []
for f in shipments_files:
    df = load_csv_safe(f)
    if df is not None:
        df["__source_file"] = f
        shipments.append(df)

shipments = pd.concat(shipments, ignore_index=True) if shipments else pd.DataFrame()

campo_limon = load_csv_safe("datos_campo_limon_2025.csv")
campo_arandano = load_csv_safe("datos_campo_arandano_2025.csv")

# --------------------------------------------------
# AUTH
# --------------------------------------------------
def auth_screen():
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=180)

    st.title("Data Core – Agroexport Intelligence")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("User", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if u == ADMIN_USER and p == ADMIN_PASS:
                st.session_state.user = u
                st.session_state.role = "admin"
            elif u:
                st.session_state.user = u
                st.session_state.role = "freemium"

    with tab2:
        st.text_input("First Name")
        st.text_input("Last Name")
        st.text_input("DNI")
        st.text_input("Email")
        st.text_input("Phone")
        st.text_input("Company (optional)")
        st.text_input("Role (optional)")
        st.text_input("User ID")
        st.text_input("Password", type="password")
        st.text_input("Repeat Password", type="password")
        st.button("Register")

# --------------------------------------------------
# MAIN
# --------------------------------------------------
if "user" not in st.session_state:
    auth_screen()
    st.stop()

is_admin = st.session_state.role == "admin"

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
st.title("📊 Data Core – Dashboard")

# ---------------- SHIPMENTS ----------------
st.header("📦 Shipments")

if shipments.empty:
    st.warning("No shipment data available.")
else:
    col_product = "Producto"
    col_country = "Pais Destino"
    col_year = "Año Inspección"

    # Limpieza de columnas mal codificadas
    for c in shipments.columns:
        if "Producto" in c:
            col_product = c
        if "Pais" in c:
            col_country = c
        if "Año" in c:
            col_year = c

    product = st.selectbox(
        "Product",
        sorted(shipments[col_product].dropna().unique())
    )

    df_prod = shipments[shipments[col_product] == product]

    if col_year in df_prod.columns:
        year = st.selectbox(
            "Year",
            sorted(df_prod[col_year].dropna().unique())
        )
        df_prod = df_prod[df_prod[col_year] == year]

    country_options = ["All"] + sorted(df_prod[col_country].dropna().unique())
    country = st.selectbox("Destination country", country_options)

    if country != "All":
        df_prod = df_prod[df_prod[col_country] == country]

    st.dataframe(limit_df(df_prod, is_admin))

    # -------- CTA FREEMIUM --------
    if not is_admin:
        subject = f"Solicitud Data Completa – {product}"
        body = f"""
Usuario: {st.session_state.user}
Producto: {product}
Tipo de data: Envíos
Periodo: {year if col_year in df_prod.columns else 'No especificado'}
"""
        mailto = f"mailto:{MAIL_TO}?subject={subject}&body={body}"
        st.markdown(
            f"""
            🔓 **¿Quieres acceso completo y actualizado?**  
            <a href="{mailto}" target="_blank"><b>Adquirir data completa aquí</b></a>
            """,
            unsafe_allow_html=True
        )

# ---------------- CAMPOS ----------------
st.header("🌾 Certified Fields")

campo_df = pd.concat(
    [campo_limon, campo_arandano],
    ignore_index=True
) if campo_limon is not None and campo_arandano is not None else pd.DataFrame()

if campo_df.empty:
    st.warning("No certified field data available.")
else:
    prod_col = "producto"
    prod = st.selectbox(
        "Product (Fields)",
        sorted(campo_df[prod_col].dropna().unique())
    )

    df_campo = campo_df[campo_df[prod_col] == prod]
    st.dataframe(limit_df(df_campo, is_admin))

    if not is_admin:
        subject = f"Solicitud Data Campos – {prod}"
        body = f"""
Usuario: {st.session_state.user}
Producto: {prod}
Tipo de data: Campos certificados
"""
        mailto = f"mailto:{MAIL_TO}?subject={subject}&body={body}"
        st.markdown(
            f"""
            🔓 **Acceso completo a campos certificados**  
            <a href="{mailto}" target="_blank"><b>Adquirir data completa aquí</b></a>
            """,
            unsafe_allow_html=True
        )

st.markdown("---")
st.caption("✅ Data Core – MVP estable | Modelo de suscripción por producto")
