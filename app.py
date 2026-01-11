import streamlit as st
import pandas as pd
import os
import hashlib

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Data Core", layout="wide")

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

LOGO = "logo_datacore.jpg"

SHIPMENT_FILES = [
    "datos_reales.csv",
    "data_arandano_1_6.csv",
    "data.csv"
]

FIELD_FILES = [
    "data_campo_limon_2025.csv",
    "data_campo_arandano_2025.csv"
]

USERS_FILE = "users.csv"

# =========================
# UTILS
# =========================
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    return pd.DataFrame(columns=["user", "password", "role"])

def save_user(user, password, role="freemium"):
    users = load_users()
    users.loc[len(users)] = [user, hash_pass(password), role]
    users.to_csv(USERS_FILE, index=False)

def read_csv_smart(file):
    try:
        return pd.read_csv(file, sep=";", encoding="utf-8-sig", on_bad_lines="skip")
    except:
        return pd.read_csv(file, sep=",", encoding="latin1", on_bad_lines="skip")

# =========================
# SESSION
# =========================
if "logged" not in st.session_state:
    st.session_state.logged = False
if "role" not in st.session_state:
    st.session_state.role = None

# =========================
# AUTH UI
# =========================
def login_ui():
    if os.path.exists(LOGO):
        st.image(LOGO, width=180)

    st.title("🌱 Data Core")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        user = st.text_input("User")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            if user == ADMIN_USER and pwd == ADMIN_PASS:
                st.session_state.logged = True
                st.session_state.role = "admin"
                st.rerun()

            users = load_users()
            row = users[(users.user == user) & (users.password == hash_pass(pwd))]

            if not row.empty:
                st.session_state.logged = True
                st.session_state.role = row.iloc[0]["role"]
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        new_user = st.text_input("New user")
        new_pass = st.text_input("New password", type="password")
        new_pass2 = st.text_input("Repeat password", type="password")

        if st.button("Register"):
            if new_pass != new_pass2:
                st.error("Passwords do not match")
            else:
                save_user(new_user, new_pass)
                st.success("User registered. Please login.")

if not st.session_state.logged:
    login_ui()
    st.stop()

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data(files):
    dfs = []
    for f in files:
        if os.path.exists(f):
            df = read_csv_smart(f)
            df["__source"] = f
            dfs.append(df)
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()

shipments = load_data(SHIPMENT_FILES)
fields = load_data(FIELD_FILES)

# =========================
# SIDEBAR
# =========================
if os.path.exists(LOGO):
    st.sidebar.image(LOGO, width=140)

st.sidebar.success(f"Logged as: {st.session_state.role}")

if st.sidebar.button("Logout"):
    st.session_state.logged = False
    st.session_state.role = None
    st.rerun()

# =========================
# DASHBOARD
# =========================
st.title("📊 Data Core – Dashboard")

# =========================
# SHIPMENTS
# =========================
st.subheader("📦 Shipments")

if shipments.empty:
    st.error("No shipment data loaded")
else:
    st.success(f"Shipments loaded: {len(shipments)}")

    with st.expander("Detected columns"):
        st.write(list(shipments.columns))

    # Detect columns
    col_product = next((c for c in shipments.columns if "producto" in c.lower()), None)
    col_country = next((c for c in shipments.columns if "pais destino" in c.lower()), None)

    if not col_product:
        st.error("Product column not found")
    else:
        products = sorted(shipments[col_product].dropna().unique())
        product = st.selectbox("Product", products)

        dfp = shipments[shipments[col_product] == product]

        if col_country:
            countries = sorted(dfp[col_country].dropna().unique())
            country = st.selectbox("Destination country", ["All"] + countries)
            if country != "All":
                dfp = dfp[dfp[col_country] == country]

        st.metric("Total shipments", len(dfp))

        if st.session_state.role == "admin":
            st.dataframe(dfp, use_container_width=True)
        else:
            st.dataframe(dfp.head(3), use_container_width=True)
            st.info("Freemium view – upgrade to unlock full data")

# =========================
# FIELDS
# =========================
st.subheader("🌾 Certified Fields")

if fields.empty:
    st.error("No field data loaded")
else:
    st.success(f"Fields loaded: {len(fields)}")

    if st.session_state.role == "admin":
        st.dataframe(fields, use_container_width=True)
    else:
        st.dataframe(fields.head(3), use_container_width=True)
        st.info("Freemium view – upgrade to unlock full data")

st.success("✅ Data Core MVP – stable, functional, ProInnóvate-ready")
