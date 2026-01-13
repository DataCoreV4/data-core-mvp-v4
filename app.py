import streamlit as st
import pandas as pd
import re
from io import BytesIO

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Data Core – MVP", layout="wide")

# =========================
# GOOGLE DRIVE → CSV
# =========================
def load_drive_csv(file_id):
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    try:
        df = pd.read_csv(
            url,
            sep=None,
            engine="python",
            encoding="utf-8",
            on_bad_lines="skip"
        )
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error cargando data: {e}")
        return None

# =========================
# NORMALIZADORES
# =========================
MESES = {
    "1": 1, "01": 1, "ene": 1, "enero": 1,
    "2": 2, "feb": 2, "febrero": 2,
    "3": 3, "mar": 3, "marzo": 3,
    "4": 4, "abr": 4, "abril": 4,
    "5": 5, "may": 5, "mayo": 5,
    "6": 6, "jun": 6, "junio": 6,
    "7": 7, "jul": 7, "julio": 7,
    "8": 8, "ago": 8, "agosto": 8,
    "9": 9, "sep": 9, "set": 9, "septiembre": 9,
    "10": 10, "oct": 10, "octubre": 10,
    "11": 11, "nov": 11, "noviembre": 11,
    "12": 12, "dic": 12, "diciembre": 12,
}

def normalize_mes(value):
    if pd.isna(value):
        return None
    v = str(value).strip().lower()
    return MESES.get(v)

def find_column(df, keywords):
    for col in df.columns:
        for k in keywords:
            if k in col:
                return col
    return None

# =========================
# DATA MAP (COMPLETO)
# =========================
DATA_MAP = {
    (2021,"envios","uva"):"1I-g0aN3KIgKRzCoT5cR24djQUwakhJxF",
    (2021,"envios","mango"):"1k6CxjPufa0YF17e264BI8NYO1rFFZuc7",
    (2021,"envios","arandano"):"1CyFQu-BdYNxFSoed9SGvKnkimrJjS2Q9",
    (2021,"envios","limon"):"1--9cfYzrB2giYCy5khZmqXdXL_46Zuz8",
    (2021,"envios","palta"):"1-BK3uEDMAMrTAdqxMJd-pIYCg0Rp-8kJ",

    (2021,"campo","uva"):"1k6OMQxl7B3hVY9OVECc9UlYcytIjpN1A",
    (2021,"campo","mango"):"1JX50r2NJYG3HjalUTZ5pCHmbD5DXQDUu",
    (2021,"campo","arandano"):"1HOKP2FaW9UPRYyA7tIj0oSnGzUhkb3h4",
    (2021,"campo","limon"):"12xOZVXqxvvepb97On1H8feKUoW_u1Qet",
    (2021,"campo","palta"):"1ckjszJeuyPQS6oVNeWFd-FwoM8FTalHO",

    (2022,"envios","uva"):"1wHxIXmn2stnjdFSnu8spnOSDw9Q45Dti",
    (2022,"envios","mango"):"1kjtC1QVGe4w3GWEYhMmB9VD98eYjhvPh",
    (2022,"envios","arandano"):"1tJRlp3FWvYZBr3LFPV1PFke3o6LZcOfa",
    (2022,"envios","limon"):"1HfO0jh0yPXK99P8mQ080KLEevc4QVnLT",
    (2022,"envios","palta"):"1IYS7yUDFmeCw3YyCIgKDbayZ63AORHvf",

    (2022,"campo","uva"):"1LS_80bCCgGE4flJ2BEzav1XeQQSrSX1y",
    (2022,"campo","mango"):"16CDM3zQnH3S5n2SNjqwJmk0oUGkbxtJS",
    (2022,"campo","arandano"):"1WTkBElLqv3aLQ8s2rkmlQqHM1zsKE33-",
    (2022,"campo","limon"):"123wwsJLNrvlTxh2VRZQy1JpVOjI9Oj32",
    (2022,"campo","palta"):"1uIs_MXnilSoPIGhtJtmOCv8N8un2VoFg",

    (2023,"envios","uva"):"1SZjCd3ANa4CF0N0lK_mnOQfzn0-ywTLs",
    (2023,"envios","mango"):"1S5mMR3nG_DeH3ZpOqAvcjidzPQMW8kw_",
    (2023,"envios","arandano"):"1JhAhZi3roOQpw5ejm3jnW5Av59De8wc2",
    (2023,"envios","limon"):"1sGnvph11F431fg5v9c8qzoH-Yxytffti",
    (2023,"envios","palta"):"1MCaBirErsv3PeJZ4soi2Fszw8QcJbg7w",

    (2023,"campo","uva"):"11sb54WtgNe0poLSR4q-nEGvjMdbnjXiq",
    (2023,"campo","mango"):"1qV3zoDQNnzeEvQR0eZ0FnrvxdkuruyUM",
    (2023,"campo","arandano"):"1jdNrMyVcW2HV5PJI63_A_oxl6xLpapl7",
    (2023,"campo","limon"):"1F708yJNg3mzrdHi53Dmw4RQZkTqUh4YH",
    (2023,"campo","palta"):"1ZBXYrxS4iJ-lUBPKAMtr4ZIWGf6Wh6ED",

    (2024,"envios","uva"):"1csIY-AT7Uw6QFp49SANyHALHuZO3r65n",
    (2024,"envios","mango"):"1In6_xnpKZwD1zTG4JrD3uhk7sYNKU4qF",
    (2024,"envios","arandano"):"1CZSWhLV-STPw9k90cOVzQxJ0V2k7ZTUa",
    (2024,"envios","limon"):"1XxGB8PGI4yh5K5mO5qGqRnSK_Fe2nPAX",
    (2024,"envios","palta"):"1mLNGjAunM6HTiCnJIgEoaqZQEuegfSf9",

    (2024,"campo","uva"):"15CoNL-b9tONKTjbj2rIy8cthyeVhsD_F",
    (2024,"campo","mango"):"1T6OVYHVN6j57Km9Z8zWrKYMlzTUIeRes",
    (2024,"campo","arandano"):"1YejBbqWi383QjeJntU-AaICQw0TOJyaV",
    (2024,"campo","limon"):"1JH6oXdDP5z-JAQgu9WvT-ej1pCjnX6WS",
    (2024,"campo","palta"):"1fxh3QgnZXzjkuqmwG4w9h1YjhK6PPvX9",

    (2025,"envios","uva"):"1iw-OafOHph_epXgf-6kreXhq2GxzNqyN",
    (2025,"envios","mango"):"1-f5tlde1nBJnl_9BbRJkaDpGBleYtbyG",
    (2025,"envios","arandano"):"1TxC9TwgFojnNRkQlOI27KJBzG0TK7tp7",
    (2025,"envios","limon"):"1G8VbTnSeOcJJVDRkze9s12TRts5BvQx6",
    (2025,"envios","palta"):"1Qt680UXFnKBh7bdV0iGqnJKKmc1suNVA",

    (2025,"campo","uva"):"15R-9ECTNpSQM1FC8tFPUs0emE16H8cHT",
    (2025,"campo","mango"):"11IziWG98PfqkSyTaK5GvKwU4NEC9LwXJ",
    (2025,"campo","arandano"):"15w2FG2TT_qPfxEksBgcGbfPu67yNbvYT",
    (2025,"campo","limon"):"178kHRjqLgs-EFUmzCsNclBKq-nYmVJPO",
    (2025,"campo","palta"):"1fo9HKY9DSKAjgLVKsx2H0Y7f_YU4DwRT",
}

# =========================
# UI
# =========================
st.title("📊 Data Core – MVP Agroexportador")

productos = ["uva","mango","arandano","limon","palta"]
anios = sorted(set([k[0] for k in DATA_MAP.keys()]))

col1,col2,col3 = st.columns(3)
producto = col1.selectbox("Producto", productos)
anio = col2.selectbox("Año", anios)
mes = col3.selectbox("Mes", ["Todos"] + list(range(1,13)))

# =========================
# RENDER DATA
# =========================
def render(tipo, emoji, titulo):
    st.subheader(f"{emoji} {titulo}")
    key = (anio, tipo, producto)

    if key not in DATA_MAP:
        st.info("📌 Información en proceso de mejora.")
        return

    df = load_drive_csv(DATA_MAP[key])
    if df is None or df.empty:
        st.info("📌 Información en proceso de mejora.")
        return

    col_mes = find_column(df, ["mes"])
    if col_mes and mes != "Todos":
        df[col_mes] = df[col_mes].apply(normalize_mes)
        df = df[df[col_mes] == mes]

    if df.empty:
        st.info("📌 Información en proceso de mejora.")
    else:
        st.dataframe(df, use_container_width=True)

render("envios","📦","Envíos")
render("campo","🌾","Campos certificados")

st.success("✅ Data Core – MVP estable | Escalable | Compatible con 13G")

