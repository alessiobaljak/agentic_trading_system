"""Fase 3: studio dei fallimenti di una variante gia' testata, solo sui dati di costruzione.

Uso: python fallimenti.py <modulo> <ID>. Rigira la variante (stesse regole) e scrive in
data/insample/MASKUSDT/risultati/fallimenti_<ID>.json l'R medio per gruppi di trade:
esito, anno, ora UTC d'ingresso, rendimento di BTC nella barra del segnale (stesso segno o no),
ampiezza del segnale (rendimento della barra in deviazioni), volume relativo, funding all'ingresso,
regime (close sopra o sotto la media di 200 barre).
"""
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import quadro  # noqa: E402
from indicatori import deviazione_precedente, rendimento, sma  # noqa: E402
from research.src import motore  # noqa: E402


def gruppi(trades, chiave):
    out = {}
    for t in trades:
        out.setdefault(chiave(t), []).append(t["r"])
    return {str(k): {"n": len(v), "r_medio": round(float(np.mean(v)), 4)} for k, v in sorted(out.items(), key=lambda x: str(x[0]))}


def main():
    mod = importlib.import_module(sys.argv[1])
    vid = sys.argv[2]
    classe, _ = mod.VARIANTI[vid]
    var = classe()
    per = quadro.periodo(var.tf)
    crea, _, _, _ = quadro.fabbriche(var, per)
    ris = motore.esegui(per.candele, None, per.mark, per.funding, crea(), quadro.parametri())
    ts = [c.ts for c in per.candele]
    c = np.array([x.close for x in per.candele])
    r1 = rendimento(c, 1)
    sd = deviazione_precedente(r1, 168)
    m200 = sma(c, 200)
    bc = np.array([b.close if b else np.nan for b in per.btc])
    rb = rendimento(bc, 1)
    sdb = deviazione_precedente(rb, 168)
    vol = np.array([v if v is not None else np.nan for v in per.volume_usdt])
    fts = [t for t, _ in per.funding]
    righe = []
    for t in ris.trades:
        ie = ts.index(t.ts_entrata)
        i = ie - 1  # barra del segnale
        f_idx = int(np.searchsorted(fts, per.candele[i].close_ts, side="right")) - 1
        vr = vol[i] / np.nanmean(vol[max(0, i - 168):i]) if i > 0 else np.nan
        righe.append({
            "r": t.r, "esito": t.esito, "anno": datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc).year,
            "ora": datetime.fromtimestamp(t.ts_entrata / 1000, tz=timezone.utc).hour,
            "dev_barra": r1[i] / sd[i] if sd[i] > 0 else np.nan,
            "btc_dev": rb[i] / sdb[i] if sdb[i] > 0 else np.nan,
            "vol_rel": vr, "funding": per.funding[f_idx][1] if f_idx >= 0 else np.nan,
            "sopra_media200": bool(c[i] > m200[i]) if not np.isnan(m200[i]) else None,
        })
    out = {
        "id": vid, "trade": len(righe), "r_medio": float(np.mean([x["r"] for x in righe])),
        "per_esito": gruppi(righe, lambda x: x["esito"]),
        "per_anno": gruppi(righe, lambda x: x["anno"]),
        "per_fascia_oraria_utc": gruppi(righe, lambda x: f"{(x['ora'] // 6) * 6:02d}-{(x['ora'] // 6) * 6 + 5:02d}"),
        "per_btc_dev": gruppi(righe, lambda x: "nan" if np.isnan(x["btc_dev"]) else ("btc<-1" if x["btc_dev"] < -1 else ("btc>+1" if x["btc_dev"] > 1 else "btc fra -1 e +1"))),
        "per_dev_barra": gruppi(righe, lambda x: "nan" if np.isnan(x["dev_barra"]) else ("|dev|>=5" if abs(x["dev_barra"]) >= 5 else ("|dev| 4-5" if abs(x["dev_barra"]) >= 4 else "|dev|<4"))),
        "per_volume_relativo": gruppi(righe, lambda x: "nan" if np.isnan(x["vol_rel"]) else ("vol>=5" if x["vol_rel"] >= 5 else ("vol 2.5-5" if x["vol_rel"] >= 2.5 else "vol<2.5"))),
        "per_funding": gruppi(righe, lambda x: "nan" if np.isnan(x["funding"]) else ("f<0" if x["funding"] < 0 else ("f=base" if abs(x["funding"] - 0.0001) < 1e-9 else ("f>base" if x["funding"] > 0.0001 else "0<=f<base")))),
        "per_regime_media200": gruppi(righe, lambda x: x["sopra_media200"]),
    }
    p = quadro.RADICE_REPO / "research" / "data" / "insample" / "MASKUSDT" / "risultati" / f"fallimenti_{vid}.json"
    p.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
