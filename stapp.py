# app.py

import streamlit as st
from api_helper import ShoonyaApiPy
import pyotp
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)

# Credentials
TOKEN = "H74CCFV4A72D2525FX5454HN3W534J7J"
USER = "FA424139"
PWD = "Amex@12345"
VC = "FA424139_U"
APP_KEY = "ce7eca6d33d988335b63b98bfbab817a"
IMEI = "abc1234"

EXCHANGE = 'NFO'

TOKENS = [
    "46620", "103951", "93402", "89878", "100528", "96876", "90994", "94330", "117597"
    # Add more tokens as needed...
]

# Shoonya API Init
api = ShoonyaApiPy()

# Login only once
@st.cache_resource
def login():
    return api.login(
        userid=USER,
        password=PWD,
        twoFA=pyotp.TOTP(TOKEN).now(),
        vendor_code=VC,
        api_secret=APP_KEY,
        imei=IMEI
    )

# Fetch data
def fetch_data(sort_by="tsym"):
    rows = []

    for token in TOKENS:
        try:
            quote = api.get_quotes(exchange=EXCHANGE, token=token)
            if quote.get('stat') == 'Ok':
                tsym = quote.get('tsym', 'N/A')
                ls = float(quote.get('ls', '0'))
                lp = quote.get('lp', 'N/A')
                bid = quote.get('bp1', '0')
                ask = quote.get('sp1', '0')
                bidamt = float(bid) * ls
                askamt = float(ask) * ls
                strk = api.get_security_info("NFO", token).get('strprc', '0')

                stocklp = api.get_quotes(quote.get('und_exch', 'NSE'), quote.get('und_tk', '22')).get('lp', '0')
                contract = float(strk) * float(ls)
                lowup = api.get_quotes(quote.get('und_exch', 'NSE'), quote.get('und_tk', '22')).get('wk52_l', '0')
                lowup_dist = round(float(lowup) / float(stocklp) - 1, 2)

                try:
                    distance = 100 * (float(strk) / float(stocklp) - 1)
                    distance = round(distance, 2)
                    chng = round(float(lp) / float(quote.get('o', '0')) - 1, 2)
                except:
                    distance = 'N/A'
                    chng = 'N/A'

                rows.append({
                    "TSYM": tsym,
                    "LS": ls,
                    "LP": lp,
                    "BID": bid,
                    "ASK": ask,
                    "BIDAMT": bidamt,
                    "ASKAMT": askamt,
                    "CHNG": chng,
                    "STOCKLP": stocklp,
                    "DISTANCE": distance,
                    "CONTRACT": contract,
                    "LOWUP": lowup,
                    "LOWUP_DIST": lowup_dist,
                    "TOKEN": token
                })
        except Exception as e:
            rows.append({"TSYM": f"Error: {token}", "TOKEN": token})

    if sort_by == "tsym":
        rows.sort(key=lambda x: x["TSYM"])
    else:
        rows.sort(key=lambda x: x.get("BIDAMT", 0), reverse=True)

    return rows

# Streamlit UI
st.title("Shoonya Token Quotes")

sort_option = st.radio("Sort by", ["tsym", "bidamt"])

if login():
    if st.button("Fetch Quotes"):
        data = fetch_data(sort_option)
        st.dataframe(data)
else:
    st.error("Login failed")
