"""Cerca negli esame.json delle prove i casi con un solo anno negativo che e' il primo o l'ultimo (anni parziali). Sola lettura."""
import glob
import json
import math

REPO = "/home/user/agentic_trading_system/research"
files = sorted(glob.glob(f"{REPO}/programma7/risultati_*/esame.json") + glob.glob(f"{REPO}/programma6/risultati_*/esame.json")
               + glob.glob(f"{REPO}/programma7/risultati_*/risultati.json"))


def visita(x, percorso, out):
    if isinstance(x, dict):
        pa = x.get("per_anno")
        if isinstance(pa, dict) and pa and all(isinstance(v, (int, float)) for v in pa.values()):
            anni = sorted(pa, key=lambda a: int(str(a)[:4]))
            neg = [a for a in anni if not pa[a] > 0]
            intero = x.get("intero") if isinstance(x.get("intero"), dict) else x
            sh, st = intero.get("sharpe"), intero.get("settimane")
            t = x.get("t") if isinstance(x.get("t"), (int, float)) else (sh * math.sqrt(st / 52) if isinstance(sh, (int, float)) and isinstance(st, (int, float)) else None)
            out.append((percorso, anni, neg, sh, st, t, x.get("sharpe_corretto")))
        for k, v in x.items():
            visita(v, percorso + "/" + str(k), out)


out = []
for f in files:
    try:
        visita(json.load(open(f)), f.replace(REPO + "/", ""), out)
    except Exception as ex:
        print("errore", f, ex)
print("esami con per_anno:", len(out))
for p, anni, neg, sh, st, t, dsr in out:
    if len(neg) == 1 and neg[0] in (anni[0], anni[-1]) and isinstance(t, (int, float)) and t >= 2.5:
        print(f"{p[:110]:110s} anni {anni[0]}-{anni[-1]} negativo {neg} Sharpe {sh} sett {st} t {t:.2f} corretto {dsr}")
