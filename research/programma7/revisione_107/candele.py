import sys, json, datetime as dt
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma5.strumenti import motore5 as m5
from research.programma6 import quarta as qa
from research.programma6 import esecuzione as es
from research.programma6 import dati as d6

def orev(s):
    file = sorted((qa.DATI / s / "ore").glob("*.zip"))
    if not file: return pd.DataFrame()
    df = pd.concat([m5._csv_da_zip(p, m5.KLINE) for p in file], ignore_index=True)
    df["ora"] = m5._ms(df["open_time"]) // 3_600_000
    df = df.drop_duplicates("ora", keep="last").set_index("ora").sort_index()
    return df[["open","high","low","close","volume","quote_volume","count"]].astype(float)

f = lambda h: dt.datetime.utcfromtimestamp(h*3600).strftime('%Y-%m-%d %H:%M')
