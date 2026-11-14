# G1 nei periodi di mercato che sale a lungo: mesi, finestre di 90 giorni e i mesi intorno all'halving del 20 aprile 2024.
# Uso: python3 -W ignore research/programma7/misure_g1/g1_nei_rialzi.py (domanda del proprietario del 14 novembre 2026 sul mercato che sale e sull halving)
import numpy as np, pandas as pd
exec(open("research/programma7/misure_g1/g1_e_il_mercato.py", encoding="utf-8").read().split("def riga")[0])
d = pd.DataFrame({"g1": n, "mercato": ew, "btc": btc}, index=pd.to_datetime(gg * 86400, unit="s"))
m = d.resample("ME").sum()                          # somme mensili (non composte)
print(f"mesi {len(m)}; correlazione mensile G1-mercato {m.corr().loc['g1','mercato']:+.2f}")
for lo, hi, nome in ((0.20, 9, "mercato oltre +20% nel mese"), (0.05, 0.20, "mercato fra +5% e +20%"), (-0.05, 0.05, "mercato fra −5% e +5%"),
                     (-9, -0.05, "mercato sotto −5%")):
    k = (m["mercato"] > lo) & (m["mercato"] <= hi)
    print(f"{nome}: {k.sum()} mesi, G1 in media {100*m.loc[k,'g1'].mean():+.1f}% al mese, mesi di G1 positivi {int((m.loc[k,'g1']>0).sum())}")
# finestre di 90 giorni: quanto fa G1 quando il mercato è salito nei 90 giorni (tendenza)
r90 = d["mercato"].rolling(90).sum().shift(1)
q = r90.quantile([0.2, 0.8])
for nome, k in (("dopo 90 giorni di forte rialzo (20% più alto)", r90 >= q[0.8]), ("dopo 90 giorni di forte ribasso (20% più basso)", r90 <= q[0.2])):
    print(f"{nome}: G1 {100*d.loc[k,'g1'].mean():+.3f}% al giorno ({100*365*d.loc[k,'g1'].mean():+.0f}% l'anno), giorni {int(k.sum())}")
print(f"tutti i giorni: G1 {100*d['g1'].mean():+.3f}% al giorno")
h = d.loc["2023-10-01":"2024-12-31"].resample("ME").sum()
print("intorno all'halving del 20 aprile 2024 (mese: G1 / mercato / Bitcoin, somme in %):")
print("  " + "; ".join(f"{i:%Y-%m} {100*r.g1:+.0f}/{100*r.mercato:+.0f}/{100*r.btc:+.0f}" for i, r in h.iterrows()))
