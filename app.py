import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import os
import re

st.set_page_config(page_title="Data Core", layout="wide")

# =========================
# CONFIG USUARIOS
# =========================
USERS_FILE = "users.csv"

ADMIN_USER = "DATACORE_ADMIN"
ADMIN_PASS = "DataCore@2025"

# =========================
# TABLA MAESTRA DRIVE
# =========================
RAW_TABLE = [
    # AÑO, BASE, TIPO, PRODUCTO, URL
    (2021,"BASE","envios","uva","https://drive.google.com/file/d/1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF/view"),
    (2021,"BASE","envios","mango","https://drive.google.com/file/d/1k6CxjPufa0YF17e264BI8NYO1rFFZuc7/view"),
    (2021,"BASE","envios","arandano","https://drive.google.com/file/d/1CyFQu-BdYNxFSoed9SGvKnkimrJjS2Q9/view"),
    (2021,"BASE","envios","limon","https://drive.google.com/file/d/1--9cfYzrB2giYCy5khZmqXdXL_46Zuz8/view"),
    (2021,"BASE","envios","palta","https://drive.google.com/file/d/1-BK3uEDMAMrTAdqxMJd-pIYCg0Rp-8kJ/view"),

    (2021,"BASE","campo","uva","https://drive.google.com/file/d/1k6OMQxl7B3hVY9OVECc9UlYcytIjpN1A/view"),
    (2021,"BASE","campo","mango","https://drive.google.com/file/d/1JX50r2NJYG3HjalUTZ5pCHmbD5DXQDUu/view"),
    (2021,"BASE","campo","arandano","https://drive.google.com/file/d/1HOKP2FaW9UPRYyA7tIj0oSnGzUhkb3h4/view"),
    (2021,"BASE","campo","limon","https://drive.google.com/file/d/12xOZVXqxvvepb97On1H8feKUoW_u1Qet/view"),
    (2021,"BASE","campo","palta","https://drive.google.com/file/d/1ckjszJeuyPQS6oVNeWFd-FwoM8FTalHO/view"),

    (2022,"BASE","envios","uva","https://drive.google.com/file/d/1wHxIXmn2stnjdFSnu8spnOSDw9Q45Dti/view"),
    (2022,"BASE","envios","mango","https://drive.google.com/file/d/1kjtC1QVGe4w3GWEYhMmB9VD98eYjhvPh/view"),
    (2022,"BASE","envios","arandano","https://drive.google.com/file/d/1tJRlp3FWvYZBr3LFPV1PFke3o6LZcOfa/view"),
    (2022,"BASE","envios","limon","https://drive.google.com/file/d/1HfO0jh0yPXK99P8mQ080KLEevc4QVnLT/view"),
    (2022,"BASE","envios","palta","https://drive.google.com/file/d/1IYS7yUDFmeCw3YyCIgKDbayZ63AORHvf/view"),

    (2022,"BASE","campo","uva","https://drive.google.com/file/d/1LS_80bCCgGE4flJ2BEzav1XeQQSrSX1y/view"),
    (2022,"BASE","campo","mango","https://drive.google.com/file/d/16CDM3zQnH3S5n2SNjqwJmk0oUGkbxtJS/view"),
    (2022,"BASE","campo","arandano","https://drive.google.com/file/d/1WTkBElLqv3aLQ8s2rkmlQqHM1zsKE33-/view"),
    (2022,"BASE","campo","limon","https://drive.google.com/file/d/123wwsJLNrvlTxh2VRZQy1JpVOjI9Oj32/view"),
    (2022,"BASE","campo","palta","https://drive.google.com/file/d/1uIs_MXnilSoPIGhtJtmOCv8N8un2VoFg/view"),

    (2023,"BASE","envios","uva","https://drive.google.com/file/d/1SZjCd3ANa4CF0N0lK_mnOQfzn0-ywTLs/view"),
    (2023,"BASE","envios","mango","https://drive.google.com/file/d/1S5mMR3nG_DeH3ZpOqAvcjidzPQMW8kw_/view"),
    (2023,"BASE","envios","arandano","https://drive.google.com/file/d/1JhAhZi3roOQpw5ejm3jnW5Av59De8wc2/view"),
    (2023,"BASE","envios","limon","https://drive.google.com/file/d/1sGnvph11F431fg5v9c8qzoH-Yxytffti/view"),
    (2023,"BASE","envios","palta","https://drive.google.com/file/d/1MCaBirErsv3PeJZ4soi2Fszw8QcJbg7w/view"),

    (2023,"BASE","campo","uva","https://drive.google.com/file/d/11sb54WtgNe0poLSR4q-nEGvjMdbnjXiq/view"),
    (2023,"BASE","campo","mango","https://drive.google.com/file/d/1qV3zoDQNnzeEvQR0eZ0FnrvxdkuruyUM/view"),
    (2023,"BASE","campo","arandano","https://drive.google.com/file/d/1jdNrMyVcW2HV5PJI63_A_oxl6xLpapl7/view"),
    (2023,"BASE","campo","limon","https://drive.google.com/file/d/1F708yJNg3mzrdHi53Dmw4RQZkTqUh4YH/view"),
    (2023,"BASE","campo","palta","https://drive.google.com/file/d/1ZBXYrxS4iJ-lUBPKAMtr4ZIWGf6Wh6ED/view"),

    (2024,"BASE","envios","uva","https://drive.google.com/file/d/1csIY-AT7Uw6QFp49SANyHALHuZO3r65n/view"),
    (2024,"BASE","envios","mango","https://drive.google.com/file/d/1In6_xnpKZwD1zTG4JrD3uhk7sYNKU4qF/view"),
    (2024,"BASE","envios","arandano","https://drive.google.com/file/d/1CZSWhLV-STPw9k90cOVzQxJ0V2k7ZTUa/view"),
    (2024,"BASE","envios","limon","https://drive.google.com/file/d/1XxGB8PGI4yh5K5mO5qGqRnSK_Fe2nPAX/view"),
    (2024,"BASE","envios","palta","https://drive.google.com/file/d/1mLNGjAunM6HTiCnJIgEoaqZQEuegfSf9/view"),

    (2024,"BASE","campo","uva","https://drive.google.com/file/d/15CoNL-b9tONKTjbj2rIy8cthyeVhsD_F/view"),
    (2024,"BASE","campo","mango","https://drive.google.com/file/d/1T6OVYHVN6j57Km9Z8zWrKYMlzTUIeRes/view"),
    (2024,"BASE","campo","arandano","https://drive.google.com/file/d/1YejBbqWi383QjeJntU-AaICQw0TOJyaV/view"),
    (2024,"BASE","campo","limon","https://drive.google.com/file/d/1JH6oXdDP5z-JAQgu9WvT-ej1pCjnX6WS/view"),
    (2024,"BASE","campo","palta","https://drive.google.com/file/d/1fxh3QgnZXzjkuqmwG4w9h1YjhK6PPvX9/view"),

    (2025,"BASE","envios","uva","https://drive.google.com/file/d/1iw-OafOHph_epXgf-6kreXhq2GxzNqyN/view"),
    (2025,"BASE","envios","mango","https://drive.google.com/file/d/1-f5tlde1nBJnl_9BbRJkaDpGBleYtbyG/view"),
    (2025,"BASE","envios","arandano","https://drive.google.com/file/d/1TxC9TwgFojnNRkQlOI27KJBzG0TK7tp7/view"),
    (2025,"BASE","envios","limon","https://drive.google.com/file/d/1G8VbTnSeOcJJVDRkze9s12TRts5BvQx6/view"),
    (2025,"BASE","envios","palta","https://drive.google.com/file/d/1Qt680UXFnKBh7bdV0iGqnJKKmc1suNVA/view"),

    (2025,"BASE","campo","uva","https://drive.google.com/file/d/15R-9ECTNpSQM1FC8tFPUs0emE16H8cHT/view"),
    (2025,"BASE","campo","mango","https://drive.google.com/file/d/11IziWG98PfqkSyTaK5GvKwU4NEC9LwXJ/view"),
    (2025,"BASE","campo","arandano","https://drive.google.com/file/d/15w2FG2TT_qPfxEksBgcGbfPu67yNbvYT/view"),
    (2025,"BASE","campo","limon","https://drive.google.com/file/d/178kHRjqLgs-EFUmzCsNclBKq-nYmVJPO/view"),
    (2025,"BASE","campo","palta","https://drive.google.com/file/d/1fo9HKY9DSKAjgLVKsx2H0Y7f_YU4DwRT/view"),
]

# =========================
# HELPERS
# =========================
def extract_id(url):
    m = re.search(r"/d/([^/]+)", url)
    return m.group(1) if m else None

DRIVE_MAP = {}
for y,b,t,p,u in RAW_TABLE:
    DRIVE_MAP[(y,t,p)] = extract_id(u)

def load_drive_csv(fid):
    try:
        url = f"https://drive.google.com/uc?id={fid}"
        r = requests.get(url)
        r.raise_for_status()
        return pd.read_csv(BytesIO(r.content))
    except:
        return None

# =========================
# DASHBOARD
# =========================
st.title("📊 Data Core – Dashboard")

prod = st.selectbox("Producto", ["uva","mango","arandano","limon","palta"])
year = st.selectbox("Año", sorted({y for y,_,_,_,_ in RAW_TABLE}))

c1, c2 = st.columns(2)

with c1:
    st.subheader("📦 Envíos")
    key = (year,"envios",prod)
    df = load_drive_csv(DRIVE_MAP[key]) if key in DRIVE_MAP else None
    st.dataframe(df) if df is not None else st.info("Información en proceso de mejora")

with c2:
    st.subheader("🌾 Campos certificados")
    key = (year,"campo",prod)
    df = load_drive_csv(DRIVE_MAP[key]) if key in DRIVE_MAP else None
    st.dataframe(df) if df is not None else st.info("Información en proceso de mejora")
