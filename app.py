import streamlit as st
import pandas as pd
import os

# ==================================================
# CONFIGURACIÓN GENERAL
# ==================================================
st.set_page_config(page_title="Data Core", layout="wide")

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

LOGO_PATH = "logo_datacore.jpg"
MAIL_TO = "datacore.agrotech@gmail.com"

# ==================================================
# FUNCIONES AUXILIARES
# ==================================================
def load_csv(file):
    if not os.path.exists(file):
        return pd.DataFrame()

    try:
        df = pd.read_csv(file, sep=";", encoding="latin1", low_memory=False)
        if df.shape[1] == 1:
            df = pd.read_csv(file, sep=",", encoding="latin1", low_memory=False)
        return df
    except Exception:
        return pd.DataFrame()


def limit_rows(df, is_admin):
    return df if is_admin else df.head(3)


def find_col(df, keywords):
    if isinstance(keywords, str):
        keywords = [keywords]

    for key in keywords:
        for c in df.columns:
            if key.lower() in c.lower():
                return c
    return None

# ==================================================
# AUTENTICACIÓN
# ==================================================
def auth_screen():
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=180)

    st.title("Data Core – Agroexport Intelligence")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        user = st.text_input("User", key="login_user")
        pwd = st.text_input("Password", type="password", key="login_pwd")

        if st.button("Login"):
            if user == ADMIN_USER and pwd == ADMIN_PASS:
                st.session_state.user = user
                st.session_state.role = "ADMIN"
            elif user:
                st.session_state.user = user
                st.session_state.role = "FREEMIUM"

    with tab_register:
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

# ==================================================
# CONTROL DE SESIÓN
# ==================================================
if "user" not in st.session_state:
    auth_screen()
    st.stop()

is_admin = st.session_state.role == "ADMIN"

# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=160)

    st.markdown(f"**User:** {st.session_state.user}")
    st.markdown(f"**Role:** {st.session_state.role}")

# ==================================================
# CARGA DE DATOS
# ==================================================
shipments = pd.concat(
    [
        load_csv("datos_reales.csv"),
        load_csv("data_arandano_1_6.csv"),
    ],
    ignore_index=True
)

campo = pd.concat(
    [
        load_csv("data_campo_limon_2025.csv"),
        load_csv("data_campo_arandano_2025.csv"),
    ],
    ignore_index=True
)

# ==================================================
# DASHBOARD
# ==================================================
st.title("📊 Data Core – Dashboard")

# ==================================================
# ENVÍOS
# ==================================================
st.header("📦 Shipments")

if not shipments.empty:
    col_product = find_col(shipments, "producto")
    col_country = find_col(shipments, "pais")
    col_month = find_col(shipments, "mes")
    col_year = find_col(shipments, "año")

    product = st.selectbox(
        "Product",
        sorted(shipments[col_product].dropna().unique())
    )

    df_ship = shipments[shipments[col_product] == product]

    if col_year:
        year = st.selectbox("Year", sorted(df_ship[col_year].dropna().unique()))
        df_ship = df_ship[df_ship[col_year] == year]

    if col_month:
        month = st.selectbox("Month", sorted(df_ship[col_month].dropna().unique()))
        df_ship = df_ship[df_ship[col_month] == month]

    if col_country:
        country = st.selectbox(
            "Destination country",
            ["All"] + sorted(df_ship[col_country].dropna().unique())
        )
        if country != "All":
            df_ship = df_ship[df_ship[col_country] == country]

    st.dataframe(limit_rows(df_ship, is_admin))

    if not is_admin:
        st.markdown(
            f"🔓 **Acceso completo:** "
            f"<a href='mailto:{MAIL_TO}?subject=Solicitud Data Envíos – {product}' target='_blank'>"
            f"Adquirir data completa aquí</a>",
            unsafe_allow_html=True
        )

# ==================================================
# CAMPOS CERTIFICADOS
# ==================================================
st.header("🌾 Certified Fields")

if not campo.empty:
    col_cultivo = find_col(campo, ["cultivo", "producto", "cientifico"])
    col_year_c = find_col(campo, ["año certificacion", "año"])
    col_month_c = find_col(campo, ["mes certificacion", "mes"])

    df_campo = campo.copy()

    if col_cultivo:
        cultivo = st.selectbox(
            "Crop / Product",
            sorted(df_campo[col_cultivo].dropna().unique())
        )
        df_campo = df_campo[df_campo[col_cultivo] == cultivo]

    if col_year_c:
        year_c = st.selectbox(
            "Certification Year",
            sorted(df_campo[col_year_c].dropna().unique())
        )
        df_campo = df_campo[df_campo[col_year_c] == year_c]

    if col_month_c:
        month_c = st.selectbox(
            "Certification Month",
            sorted(df_campo[col_month_c].dropna().unique())
        )
        df_campo = df_campo[df_campo[col_month_c] == month_c]

    st.dataframe(limit_rows(df_campo, is_admin))

    if not is_admin:
        st.markdown(
            f"🔓 **Acceso completo:** "
            f"<a href='mailto:{MAIL_TO}?subject=Solicitud Data Campos Certificados' target='_blank'>"
            f"Adquirir data completa aquí</a>",
            unsafe_allow_html=True
        )

# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
st.caption("✅ Data Core – MVP estable | Suscripción por producto")
