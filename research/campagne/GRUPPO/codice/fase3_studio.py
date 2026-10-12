"""Fase 3 (studio dei fallimenti) sui trade sommati salvati da gruppo.py: solo lettura dei trade di costruzione.

Uso: python3 -u fase3_studio.py ID [ID ...]   (legge campagne/GRUPPO/trade/<ID>_costruzione.jsonl)
Per ogni ID: R medio; costo stimato di un giro in R per trade = 2 x (commissione 0,05% + slippage della scheda) x
entrata / |entrata - stop| (stima: il motore applica i costi sui riempimenti veri); R medio al lordo di quel costo;
quota e R medio per esito (stop, segnale); R medio per durata; R medio per mese di uscita aggregato per giorno con
molte uscite (grappoli: giorni con almeno 10 uscite contro gli altri).
"""
import json
import sys
from collections import Counter, defaultdict

from comune import CARTELLA_GRUPPO, schede

COMMISSIONE = 0.0005
GIORNO = 86_400_000


def media(xs):
    return sum(xs) / len(xs) if xs else None


if __name__ == "__main__":
    slip = {s: v["slippage_per_lato"] for s, v in schede().items()}
    for ident in sys.argv[1:]:
        righe = [json.loads(x) for x in (CARTELLA_GRUPPO / "trade" / f"{ident}_costruzione.jsonl").read_text().splitlines() if x.strip()]
        costi = [2 * (COMMISSIONE + slip[t["simbolo"]]) * t["entrata"] / abs(t["entrata"] - t["stop"]) for t in righe]
        r = [t["r"] for t in righe]
        per_esito = defaultdict(list)
        for t in righe:
            per_esito[t["esito"]].append(t["r"])
        uscite_giorno = Counter(t["ts_uscita"] // GIORNO for t in righe)
        grappolo = [t["r"] for t in righe if uscite_giorno[t["ts_uscita"] // GIORNO] >= 10]
        sparsi = [t["r"] for t in righe if uscite_giorno[t["ts_uscita"] // GIORNO] < 10]
        print(json.dumps({
            "id": ident, "trade": len(r), "r_medio": round(media(r), 4),
            "costo_giro_r_medio_stimato": round(media(costi), 4),
            "r_medio_lordo_stimato": round(media(r) + media(costi), 4),
            "per_esito": {k: {"quota": round(len(v) / len(r), 3), "r_medio": round(media(v), 4)} for k, v in per_esito.items()},
            "giorni_con_almeno_10_uscite": {"trade": len(grappolo), "r_medio": round(media(grappolo), 4) if grappolo else None},
            "altri_giorni": {"trade": len(sparsi), "r_medio": round(media(sparsi), 4) if sparsi else None},
        }, ensure_ascii=False))
