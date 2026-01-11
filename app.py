import streamlit as st
import pandas as pd
import os
import hashlib

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(page_title="Data Core", layout="wide")

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

LOGO = "logo_datacore.jpg"
USERS_FILE = "users.csv"

SHIPMENT_FILES = [
    "datos_reales.csv",
    "data_arandano_1_6.csv",
    "data.csv"
]

FIELD_FILES = [
    "data_campo_limon_2025.csv",
    "data_campo_arandano_2025.csv"
]

# =========================
# UTILIDADES
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
        "user","password","role","name","lastname","dni",
        "email","phone","company","position"
    ])

def save_user(data):
    users = load_users()
    users.loc[len(users)] = data
    users.to_csv(USERS_FILE, index=False)

# =========================
# SESIÓN
# =========================
if "logged" not in st.session_state:
    st.session_state.logged = False
if "role" not in st.session_state:
    st.session_state.role = None

# =========================
# LOGIN / REGISTRO
# =========================
def auth_screen():
    if os.path.exists(LOGO):
        st.image(LOGO, width=180)

    st.title("🌱 Data Core")
    st.subheader("Agroexport Intelligence Platform")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # ---------- LOGIN ----------
    with tab1:
        user = st.text_input("User")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            if user == ADMIN_USER and pwd == ADMIN_PASS:
                st.session_state.logged = True
                st.session_state.role = "admin"
                st.rerun()

            users = load_users()
            row = users[
                (users.user == user) &
                (users.password == hash_pass(pwd))
            ]

            if not row.empty:
                st.session_state.logged = True
                st.session_state.role = row.iloc[0]["role"]
                st.rerun()
            else:
                st.error("Invalid credentials")

    # ---------- REGISTRO ----------
    with tab2:
        name = st.text_input("Name")
        lastname = st.text_input("Last name")
        dni = st.text_input("DNI")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        company = st.text_input("Company (optional)")
        position = st.text_input("Position (optional)")
        user = st.text_input("User ID")
        pwd1 = st.text_input("Password", type="password")
        pwd2 = st.text_input("Repeat password", type="password")

        if st.button("Register"):
            if pwd1 != pwd2:
                st.error("Passwords do not match")
            elif user == "" or email == "":
                st.error("User and email are required")
            else:
                save_user([
                    user,
                    hash_pass(pwd1),
                    "freemium",
                    name,
                    lastname,
                    dni,
                    email,
                    phone,
                    company,
                    position
                ])
                st.success("Registration successful. Please login.")

if not st.session_state.logged:
    auth_screen()
    st.stop()

# =========================
# CARGA DE DATOS
# =========================
@st.cache_data
def load_data(files):
    dfs = []
    for f in files:
        if os.path.exists(f):
            df = smart_read_csv(f)
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

st.sidebar.success(f"Role: {st.session_state.role}")

if st.sidebar.button("Logout"):
    st.session_state.logged = False
    st.session_state.role = None
    st.rerun()

# =========================
# DASHBOARD
# =========================
st.title("📊 Data Core – Dashboard")

# =========================
# ENVÍOS
# =========================
st.subheader("📦 Shipments")

if shipments.empty:
    st.error("No shipment data loaded")
else:
    st.success(f"Shipments loaded: {len(shipments)}")

    with st.expander("Detected columns"):
        st.write(list(shipments.columns))

    # Detección robusta de columnas
    col_product = next((c for c in shipments.columns if "producto" in c.lower()), None)
    col_country = next((c for c in shipments.columns if "pais destino" in c.lower()), None)
    col_year = next((c for c in shipments.columns if "año inspe" in c.lower() or "aao_inspeccia3n" in c.lower()), None)

    if not col_product:
        st.error("Product column not found")
    else:
        product = st.selectbox(
            "Product",
            sorted(shipments[col_product].dropna().unique())
        )

        df = shipments[shipments[col_product] == product]

        # Filtro país
        if col_country:
            country = st.selectbox(
                "Destination country",
                ["All"] + sorted(df[col_country].dropna().unique())
            )
            if country != "All":
                df = df[df[col_country] == country]

        # Filtro año
        if col_year:
            years = sorted(df[col_year].dropna().unique())
            year = st.selectbox("Inspection year", ["All"] + list(years))
            if year != "All":
                df = df[df[col_year] == year]

        st.metric("Total shipments", len(df))

        if st.session_state.role == "admin":
            st.dataframe(df, use_container_width=True)
        else:
            st.dataframe(df.head(3), use_container_width=True)
            st.info("Freemium view – limited data")

# =========================
# CAMPOS
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
        st.info("Freemium view – limited data")

# =========================
# FOOTER
# =========================
st.success("✅ Data Core MVP – stable version ready for ProInnóvate")
