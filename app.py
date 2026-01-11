import streamlit as st
import pandas as pd
import os

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Data Core",
    layout="wide"
)

# =========================
# CONSTANTS
# =========================
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

ENVIOS_FILES = [
    "datos_reales.csv",
    "data_arandano_1_6.csv",
    "data.csv"
]

CAMPO_FILES = [
    "data_campo_limon_2025.csv",
    "data_campo_arandano_2025.csv"
]

LOGO_FILE = "logo_datacore.jpg"

# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =========================
# LOGIN SCREEN
# =========================
def login_screen():
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, width=180)

    st.title("🌱 Data Core")
    st.subheader("Agroexport Intelligence Platform")

    user = st.text_input("User")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == ADMIN_USER and password == ADMIN_PASS:
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.rerun()
        else:
            st.error("Invalid credentials")

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# =========================
# DATA LOADING
# =========================
@st.cache_data
def load_csv(files):
    dfs = []
    for f in files:
        if os.path.exists(f):
            try:
                df = pd.read_csv(
                    f,
                    encoding="latin1",
                    sep=",",
                    on_bad_lines="skip"
                )
                df["__source_file"] = f
                dfs.append(df)
            except Exception as e:
                st.error(f"Error loading {f}: {e}")
        else:
            st.warning(f"File not found: {f}")

    if dfs:
        return pd.concat(dfs, ignore_index=True)

    return pd.DataFrame()

envios = load_csv(ENVIOS_FILES)
campos = load_csv(CAMPO_FILES)

# =========================
# SIDEBAR
# =========================
if os.path.exists(LOGO_FILE):
    st.sidebar.image(LOGO_FILE, width=140)

st.sidebar.success("Session active")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.is_admin = False
    st.rerun()

# =========================
# DASHBOARD
# =========================
st.title("📊 Data Core – Dashboard")

# =========================
# ENVIOS SECTION
# =========================
st.subheader("📦 Shipments")

if envios.empty:
    st.error("No shipment data loaded.")
else:
    st.success(f"Shipments loaded: {len(envios)} records")

    with st.expander("🧩 Detected shipment columns"):
        st.write(envios.columns.tolist())

    # Dynamic column detection
    col_product = next((c for c in envios.columns if "producto" in c.lower() or "product" in c.lower()), None)
    col_country = next((c for c in envios.columns if "pais" in c.lower() and "destino" in c.lower()), None)

    if col_product is None:
        st.error("Product column not found.")
    else:
        products = sorted(envios[col_product].dropna().unique())
        selected_product = st.selectbox("Product", products)

        df_filtered = envios[envios[col_product] == selected_product]

        if col_country:
            countries = sorted(df_filtered[col_country].dropna().unique())
            selected_country = st.selectbox(
                "Destination country",
                ["All"] + countries
            )

            if selected_country != "All":
                df_filtered = df_filtered[df_filtered[col_country] == selected_country]

        st.metric("Total shipments", len(df_filtered))

        if st.session_state.is_admin:
            st.dataframe(df_filtered, use_container_width=True)
        else:
            st.dataframe(df_filtered.head(3), use_container_width=True)
            st.info("Freemium view – limited rows")

# =========================
# CAMPOS SECTION
# =========================
st.subheader("🌾 Certified Fields")

if campos.empty:
    st.error("No certified field data loaded.")
else:
    st.success(f"Certified fields loaded: {len(campos)} records")

    with st.expander("🧩 Detected field columns"):
        st.write(campos.columns.tolist())

    if st.session_state.is_admin:
        st.dataframe(campos, use_container_width=True)
    else:
        st.dataframe(campos.head(3), use_container_width=True)
        st.info("Freemium view – limited rows")

# =========================
# FOOTER
# =========================
st.success("✅ Data Core MVP operational – stable version")
