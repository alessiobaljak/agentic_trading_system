"""Fase 3 per BTCUSDT-V08-long: studio dei fallimenti (quando l'effetto NON si verifica).

Riesegue la variante in costruzione (stessi parametri) e scompone i trade per:
anno, livello del funding al segnale (quanto sotto il 10° percentile), stato del
trend (close sopra/sotto la media a 50 barre), giorno della settimana, con la
quota del funding incassato sul pnl. NON cambia la variante: serve a capire se
i fallimenti hanno una forma prevedibile in anticipo. Esito in
risultati/BTCUSDT-V08-long.fase3.json.
"""
from __future__ import annotations
import json, sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import dati_btc as d
import strumenti as s
from varianti import VARIANTI

v = VARIANTI["BTCUSDT-V08-long"]
serie = s.Serie("8h")
entra, uscita = v["entra"](serie), v["uscita"](serie)
ris, last = s.esegui_su_periodo(serie, s.strategia_da_regole(serie, entra, uscita), d.COSTRUZIONE)
f = serie.funding_ultimo()
sma50 = s.sma(serie.c, 50)
out = {}

def gruppo(chiave_fn, nome):
    g = defaultdict(list)
    for t in ris.trades:
        i = serie.idx[t.ts_entrata] - 1  # barra del segnale
        g[chiave_fn(i, t)].append(t)
    out[nome] = {str(k): {"n": len(ts), "r_medio": round(float(np.mean([t.r for t in ts])), 3), "win": round(float(np.mean([t.pnl > 0 for t in ts])), 2),
                          "pnl": round(sum(t.pnl for t in ts), 2), "funding": round(-sum(t.funding_pagato for t in ts), 2)} for k, ts in sorted(g.items(), key=lambda kv: str(kv[0]))}

gruppo(lambda i, t: datetime.fromtimestamp(t.ts_entrata/1000, tz=timezone.utc).year, "per_anno")
gruppo(lambda i, t: "funding<0" if f[i] < 0 else ("0<=funding<0.0001" if f[i] < 0.0001 else "funding>=0.0001"), "per_livello_funding")
gruppo(lambda i, t: "sopra_sma50" if serie.c[i] > sma50[i] else "sotto_sma50", "per_trend")
gruppo(lambda i, t: int(serie.giorno_settimana[i]), "per_giorno_settimana")
gruppo(lambda i, t: int(serie.ora[i]), "per_ora_segnale")
gruppo(lambda i, t: t.esito, "per_esito")
pnl = sum(t.pnl for t in ris.trades)
fund = -sum(t.funding_pagato for t in ris.trades)
prezzo = sum(t.pnl_lordo for t in ris.trades)
costi = sum(t.commissioni + t.slippage_costo for t in ris.trades)
out["scomposizione_pnl"] = {"pnl_netto": round(pnl, 2), "pnl_prezzo_lordo": round(prezzo, 2), "funding_incassato": round(fund, 2), "commissioni_e_slippage": round(costi, 2),
                            "quota_funding_su_netto": round(fund / pnl, 3) if pnl else None}
rs = sorted(t.r for t in ris.trades)
out["distribuzione_r"] = {"min": round(rs[0], 3), "p10": round(rs[len(rs)//10], 3), "mediana": round(rs[len(rs)//2], 3), "p90": round(rs[-len(rs)//10], 3), "max": round(rs[-1], 3),
                          "r_medio_senza_i_5_migliori": round(float(np.mean(rs[:-5])), 4), "r_medio_senza_i_5_peggiori": round(float(np.mean(rs[5:])), 4)}
# sequenze: segnali consecutivi (cluster) -> primo trade del cluster vs successivi
primi, successivi = [], []
ultimo_uscita = None
for t in ris.trades:
    (successivi if (ultimo_uscita is not None and t.ts_entrata - ultimo_uscita <= 8*3600*1000) else primi).append(t)
    ultimo_uscita = t.ts_uscita
out["cluster"] = {"primo_del_cluster": {"n": len(primi), "r_medio": round(float(np.mean([t.r for t in primi])), 3)},
                  "successivo_nel_cluster": {"n": len(successivi), "r_medio": round(float(np.mean([t.r for t in successivi])), 3) if successivi else None}}
# rendimento a 3 barre su TUTTE le barre con funding < soglia vs tutte le altre (effetto grezzo senza stop)
r3 = serie.c / s.shift(serie.c, 3) - 1  # (non usato: guarda avanti) -> costruiamo forward
fwd3 = np.full(serie.n, np.nan); fwd3[:-3] = serie.c[3:] / serie.o[1:-2] - 1
i0, i1 = serie.idx[int(last[0].ts)], serie.idx[int(last[-1].ts)]
seg = [i for i in range(i0, i1 - 3) if entra(i) == "long"]
alt = [i for i in range(i0, i1 - 3) if entra(i) is None]
out["rendimento_3_barre_grezzo"] = {"segnale": {"n": len(seg), "medio_pct": round(float(np.nanmean(fwd3[seg]))*100, 3)}, "altre_barre": {"n": len(alt), "medio_pct": round(float(np.nanmean(fwd3[alt]))*100, 3)}}
p = Path(__file__).resolve().parent / "risultati" / "BTCUSDT-V08-long.fase3.json"
p.write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps(out, indent=1, ensure_ascii=False))
