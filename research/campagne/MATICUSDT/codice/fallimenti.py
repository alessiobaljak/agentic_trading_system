"""Fase 3: dove una variante fallisce (solo dati di costruzione, solo i trade del candidato).

Uso: python research/campagne/MATICUSDT/codice/fallimenti.py V33
Scrive esiti/<ID>_fallimenti.json: R medio e numero di trade per gruppi noti all'ingresso
(anno, tendenza rispetto alla media di 50 giorni, rendimento di BTCUSDT delle 24 ore prima,
ora UTC, mese di ingresso, esito dell'uscita).
"""
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import quadro  # noqa: E402
import varianti  # noqa: E402

vid = sys.argv[1]
tf = varianti.TIMEFRAME[vid]
s = quadro.carica(tf)
reg = getattr(varianti, vid)(s)
from research.src import motore  # noqa: E402

ris = motore.esegui(s.candele, None, s.mark, s.funding, reg.crea(), quadro.parametri())
barre_giorno = 86_400_000 // s.ms_barra
m50 = quadro.sma(s.c, 50 * barre_giorno)
btc24 = quadro.rendimento(s.btc_c, barre_giorno)
gruppi = defaultdict(list)
for t in ris.trades:
    k = s.indice_di_ts[t.ts_entrata] - 1  # barra di segnale
    d = datetime.fromtimestamp(t.ts_entrata / 1000, tz=timezone.utc)
    gruppi[f"anno {d.year}"].append(t.r)
    gruppi[f"mese {d.year}-{d.month:02d}"].append(t.r)
    if not np.isnan(m50[k]):
        gruppi["sopra la media di 50 giorni" if s.c[k] > m50[k] else "sotto la media di 50 giorni"].append(t.r)
    if not np.isnan(btc24[k]):
        gruppi["BTC 24h > 0" if btc24[k] > 0 else "BTC 24h <= 0"].append(t.r)
    gruppi[f"ora {d.hour // 6 * 6:02d}-{d.hour // 6 * 6 + 5:02d}"].append(t.r)
    gruppi[f"esito {t.esito}"].append(t.r)
out = {g: {"trade": len(v), "r_medio": round(float(np.mean(v)), 4)} for g, v in sorted(gruppi.items())}
(Path(__file__).resolve().parents[1] / "esiti" / f"{vid}_fallimenti.json").write_text(json.dumps(out, indent=0, ensure_ascii=False))
print(json.dumps(out, ensure_ascii=False))
