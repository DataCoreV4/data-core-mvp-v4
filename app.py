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
USERS_FILE = "users.csv"

SHIPMENT_FILES = ["datos_reales.csv","data_arandano_1_6.csv","data.csv"]
FIELD_FILES = ["data_campo_limon_2025.csv","data_campo_arandano_2025.csv"]

# =========================
# UTILS
# =========================
def hash_pass(text):
    return hashlib.sha256(text.encode()).hexdigest()

def smart_read_csv(file):
    try:
        return pd.read_csv(file, sep=";", encoding="utf-8-sig", on_bad_lines="skip")
    except:
        return pd.read_csv(file, sep=",", encoding="latin1", on_bad_lines="skip")

def load_users():
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    return pd.DataFrame(columns=[
        "user","password","role",
        "name","lastname","dni",
        "email","phone","company","position"
    ])

# =========================
# SESSION
# =========================
if "logged" not in st.session_state:
    st.session_state.logged = False
if "role" not in st.session_state:
    st.session_state.role = None
if "user" not in st.session_state:
    st.session_state.user = None

# =========================
# AUTH
# =========================
def auth():
    if os.path.exists(LOGO):
        st.image(LOGO, width=160)

    tab1, tab2 = st.tabs(["Login","Register"])

    with tab1:
        u = st.text_input("User", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            if u == ADMIN_USER and p == ADMIN_PASS:
                st.session_state.logged = True
                st.session_state.role = "admin"
                st.session_state.user = u
                st.rerun()

            users = load_users()
            row = users[(users.user==u)&(users.password==hash_pass(p))]
            if not row.empty:
                st.session_state.logged = True
                st.session_state.role = row.iloc[0]["role"]
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        name = st.text_input("Name")
        lastname = st.text_input("Last name")
        dni = st.text_input("DNI")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        company = st.text_input("Company (optional)")
        position = st.text_input("Position (optional)")
        user = st.text_input("User ID")
        p1 = st.text_input("Password", type="password")
        p2 = st.text_input("Repeat password", type="password")

        if st.button("Register"):
            if p1 != p2:
                st.error("Passwords do not match")
            else:
                users = load_users()
                users.loc[len(users)] = [
                    user, hash_pass(p1), "freemium",
                    name, lastname, dni,
                    email, phone, company, position
                ]
                users.to_csv(USERS_FILE, index=False)
                st.success("Registered successfully")

if not st.session_state.logged:
    auth()
    st.stop()

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data(files):
    dfs = []
    for f in files:
        if os.path.exists(f):
            dfs.append(smart_read_csv(f))
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

shipments = load_data(SHIPMENT_FILES)
fields = load_data(FIELD_FILES)

# =========================
# SIDEBAR
# =========================
if os.path.exists(LOGO):
    st.sidebar.image(LOGO, width=130)

st.sidebar.write(f"User: **{st.session_state.user}**")
st.sidebar.write(f"Role: **{st.session_state.role}**")

if st.sidebar.button("Logout"):
    st.session_state.logged = False
    st.session_state.role = None
    st.session_state.user = None
    st.rerun()

# =========================
# DASHBOARD
# =========================
st.title("📊 Data Core – Dashboard")

# =========================
# SHIPMENTS
# =========================
st.subheader("📦 Shipments")

col_product = next(c for c in shipments.columns if "producto" in c.lower())
col_country = next(c for c in shipments.columns if "pais destino" in c.lower())
col_year = next(c for c in shipments.columns if "año inspe" in c.lower() or "aao_inspeccia3n" in c.lower())

products = sorted(
    shipments[col_product]
    .dropna()
    .astype(str)
    .unique()
)

years = sorted(
    shipments[col_year]
    .dropna()
    .astype(str)
    .unique()
)

product = st.selectbox("Product", products)
year = st.selectbox("Inspection year", years)

filtered = shipments[
    (shipments[col_product].astype(str) == product) &
    (shipments[col_year].astype(str) == year)
]

st.metric("Total shipments", len(filtered))

if st.session_state.role == "admin":
    st.dataframe(filtered)
else:
    st.dataframe(filtered.head(3))

# =========================
# FIELDS
# =========================
st.subheader("🌾 Certified Fields")

if st.session_state.role == "admin":
    st.dataframe(fields)
else:
    st.dataframe(fields.head(3))

st.success("✅ Data Core v1.0 – stable and operational")
