import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from fredapi import Fred
from sklearn.ensemble import IsolationForest

st.title("Price anomaly detector")

SERIES = {"Brent oil": "DCOILBRENTEU", "WTI oil": "DCOILWTICO",
          "Natural gas (Henry Hub)": "DHHNGSP"}
name = st.selectbox("Choose a price series", list(SERIES))
pct = st.slider("Share of days to flag (%)", 0.5, 5.0, 1.0, 0.5)

@st.cache_data
def load(code):
    fred = Fred(api_key=os.environ["FRED_API_KEY"])
    return fred.get_series(code, observation_start="2015-01-01").dropna()

prices = load(SERIES[name])
prices = prices[prices > 0]            # oil went negative once in 2020 and breaks % change
change = prices.pct_change() * 100

X = pd.DataFrame({
    "change": change,
    "abs_change": change.abs(),
    "vol_20d": change.rolling(20).std(),
    "move_5d": prices.pct_change(5) * 100,
}).dropna()

model = IsolationForest(contamination=pct / 100, random_state=0)
X["flag"] = model.fit_predict(X) == -1

def explain(row):
    parts = []
    if abs(row["change"]) > 5:
        parts.append("price moved %.1f%% in one day" % row["change"])
    if row["vol_20d"] > 4:
        parts.append("last 20 days very volatile (%.1f%% typical swing)" % row["vol_20d"])
    if abs(row["move_5d"]) > 15:
        parts.append("price moved %.0f%% over 5 days" % row["move_5d"])
    return "; ".join(parts) if parts else "unusual mix of signals"

flagged = X[X["flag"]].copy()
flagged["why"] = flagged.apply(explain, axis=1)

st.write("Flagged **%d** days out of %d" % (len(flagged), len(X)))

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(X.index, X["change"], color="lightgray")
ax.plot(flagged.index, flagged["change"], "ro")
ax.set_ylabel("daily change (%)")
st.pyplot(fig)

st.dataframe(flagged[["change", "vol_20d", "move_5d", "why"]].round(1))
st.download_button("Download flagged days (CSV)",
                   flagged.to_csv(index_label="date"), "flagged_days.csv")