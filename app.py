import streamlit as st
import pandas as pd
import os

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Data Core", layout="wide")

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"
LOGO_PATH = "logo_datacore.jpg"
MAIL_TO = "datacore.agrotech@gmail.com"

# --------------------------------------------------
# FUNCIONES
# --------------------------------------------------
def load_csv(file):
    if os.path.exists(file):
        return pd.read_csv(file, sep=";", encoding="latin1", low_memory=False)
    return pd.DataFrame()

def limit_rows(df, is_admin):
    return df if is_admin else df.head(3)

def find_col(df, keyword):
    for c in df.columns:
        if keyword.lower() in c.lower():
            return c
    return None

# --------------------------------------------------
# AUTH
# --------------------------------------------------
def auth_screen():
    st.image(LOGO_PATH, width=180)
    st.title("Data Core – Agroexport Intelligence")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        user = st.text_input("User", key="login_user")
        pwd = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login"):
            if user == ADMIN_USER and pwd == ADMIN_PASS:
                st.session_state.user = user
                st.session_state.role = "ADMIN"
            elif user:
                st.session_state.user = user
                st.session_state.role = "FREEMIUM"

    with tab2:
        st.text_input("First name")
        st.text_input("Last name")
        st.text_input("DNI")
        st.text_input("Email")
        st.text_input("Phone")
        st.text_input("Company (optional)")
        st.text_input("Position (optional)")
        st.text_input("User ID")
        st.text_input("Password", type="password")
        st.text_input("Repeat password", type="password")
        st.button("Register")

# --------------------------------------------------
# LOGIN CHECK
# --------------------------------------------------
if "user" not in st.session_state:
    auth_screen()
    st.stop()

is_admin = st.session_state.role == "ADMIN"

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.image(LOGO_PATH, width=160)
    st.markdown(f"**User:** {st.session_state.user}")
    st.markdown(f"**Role:** {st.session_state.role}")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
shipments = pd.concat([
    load_csv("datos_reales.csv"),
    load_csv("data_arandano_1_6.csv")
], ignore_index=True)

campo = pd.concat([
    load_csv("datos_campo_limon_2025.csv"),
    load_csv("datos_campo_arandano_2025.csv")
], ignore_index=True)

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
st.title("📊 Data Core – Dashboard")

# ================== SHIPMENTS ==================
st.header("📦 Shipments")

if shipments.empty:
    st.warning("No shipment data loaded.")
else:
    col_product = find_col(shipments, "producto")
    col_country = find_col(shipments, "pais")
    col_month = find_col(shipments, "mes")
    col_year = find_col(shipments, "año")

    product = st.selectbox(
        "Product",
        sorted(shipments[col_product].dropna().unique())
    )

    df = shipments[shipments[col_product] == product]

    if col_year:
        year = st.selectbox(
            "Year",
            sorted(df[col_year].dropna().unique())
        )
        df = df[df[col_year] == year]

    if col_month:
        month = st.selectbox(
            "Month",
            sorted(df[col_month].dropna().unique())
        )
        df = df[df[col_month] == month]

    if col_country:
        country = st.selectbox(
            "Destination country",
            ["All"] + sorted(df[col_country].dropna().unique())
        )
        if country != "All":
            df = df[df[col_country] == country]

    st.dataframe(limit_rows(df, is_admin))

    if not is_admin:
        mailto = f"mailto:{MAIL_TO}?subject=Solicitud Data Envíos – {product}"
        st.markdown(
            f"🔓 **Acceso completo:** <a href='{mailto}' target='_blank'>Adquirir data completa aquí</a>",
            unsafe_allow_html=True
        )

# ================== CAMPOS ==================
st.header("🌾 Certified Fields")

if campo.empty:
    st.warning("No field data loaded.")
else:
    col_prod_campo = find_col(campo, "producto")
    product_c = st.selectbox(
        "Product (Fields)",
        sorted(campo[col_prod_campo].dropna().unique())
    )

    df_campo = campo[campo[col_prod_campo] == product_c]
    st.dataframe(limit_rows(df_campo, is_admin))

    if not is_admin:
        mailto = f"mailto:{MAIL_TO}?subject=Solicitud Data Campos – {product_c}"
        st.markdown(
            f"🔓 **Acceso completo:** <a href='{mailto}' target='_blank'>Adquirir data completa aquí</a>",
            unsafe_allow_html=True
        )

st.markdown("---")
st.caption("✅ Data Core – MVP estable | Suscripción por producto")
