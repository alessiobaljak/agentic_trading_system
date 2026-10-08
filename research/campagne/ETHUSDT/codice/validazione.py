"""Validazione (dopo la Fase 5): ogni candidato gira UNA volta sul periodo di validazione.

La serie va dall'inizio della costruzione al 2023-12-31 (indicatori caldi) e contano solo
i trade entrati dal 2022-10-19 00:00 UTC (Fase 0, punto 1). La (b) di validazione ha gli
ingressi casuali solo dove il trade entrerebbe in validazione: sono vietate le barre di
segnale il cui ingresso (la barra dopo) cade in costruzione. Il p-value dell'asticella e'
il campo ``p_value`` di ``contro_baseline`` contro questa (b) (sezione 8).

Questo modulo NON si usa prima della Fase 5.
"""

from typing import Dict

import comune
from research.src import motore, statistica


def valida(V, kw: dict, tf: str) -> Dict[str, object]:
    p = comune.parametri()
    s = comune.carica(tf, "tutto")
    ris = motore.esegui(s.last, None, s.mark, s.funding, comune.fabbrica(V, kw, s)(), p)
    trades = sorted([t for t in ris.trades if t.ts_entrata >= comune.INIZIO_VALIDAZIONE_TS], key=lambda t: t.ts_uscita)
    out: Dict[str, object] = {"metriche": comune._metriche(None, trades), "trade_validazione": len(trades)}
    if len(trades) < 30:
        out.update({"esito": "sotto i trade minimi di validazione (30): non si sa", "p_value": 1.0})
        return out
    r = [t.r for t in trades]
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    # barre di segnale con ingresso in costruzione: vietate alla (b) di validazione
    primo = next(i for i, c in enumerate(s.last) if c.ts >= comune.INIZIO_VALIDAZIONE_TS)
    vietate_costruzione = [(0, max(0, primo - 1))]
    base_b = comune.baseline_b(V, kw, s, trades, p, vietate_extra=vietate_costruzione)
    out["blocco"] = blocco
    if "errore" in base_b:
        out.update({"esito": "non valutabile contro la (b) di validazione", "errore": base_b["errore"], "p_value": 1.0})
        return out
    cmp_b = statistica.contro_baseline(r, blocco, base_b, comune.BOOTSTRAP_N, comune.BOOTSTRAP_SEME)
    out["baseline_b"] = dict(comune._sintesi_confronto(cmp_b), media=base_b["media"],
                             trade_per_simulazione_medio=sum(base_b["trade_per_simulazione"]) / len(base_b["trade_per_simulazione"]),
                             durata_media_barre=base_b["durata_media_barre"])
    out["p_value"] = cmp_b["p_value"]
    out["percentile_caso"] = statistica.percentile_del_candidato(sum(r) / len(r), base_b["valori"])
    return out
