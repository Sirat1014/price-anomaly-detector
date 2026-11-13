# Price Anomaly Detector

Finds unusual days in public commodity prices (Brent oil, WTI oil, natural gas)
using Isolation Forest, and explains each flagged day in plain English.

## Methods compared
The app uses Isolation Forest. I compared it with two simple statistical
rules, which I used as baselines while building it.

| Method | Finds | Misses |
|---|---|---|
| Whole-history rule (3 std), baseline | Biggest crises | Quiet-time surprises |
| Rolling 60-day rule, baseline | Surprises vs the recent past | Long wild periods |
| Isolation Forest (used in the app) | Abnormal periods, using several clues | Single-day shocks in calm years |

## Limitation
There are no true labels, so I can't measure accuracy. I checked the flags
against known events such as the 2020 oil crash.

## Run it
```
pip install -r requirements.txt
streamlit run app.py
```
Set your free FRED API key as the environment variable `FRED_API_KEY`.

Data: FRED (Federal Reserve Bank of St. Louis)
Built by Subhsirat Kaur Sehra