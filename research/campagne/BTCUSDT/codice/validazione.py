"""Validazione (dopo la Fase 5): ogni candidato gira UNA volta sul periodo di validazione.

La serie va dall'inizio della costruzione al 2023-12-31 (indicatori caldi); contano solo i
trade ENTRATI dopo la fine della costruzione. La (b) ha ingressi casuali solo nelle barre di
validazione; la (a) e' la variante senza condizione sulla stessa serie, con i trade entrati
in validazione. p-value dell'asticella da contro_baseline contro la (b) di validazione.
Uso: python validazione.py V10 [...]   (registra prima, esegue, scrive il risultato)
"""
import sys

import numpy as np

import quadro
import varianti
from comune import PERIODI, SIMBOLO, aggiungi_log, motore, parametri, voci_log
from research.src import statistica

INIZIO_V = PERIODI["inizio_validazione_ts"]


def costruzione_trade(vid):
    r = [v for v in voci_log() if v.get("id") == f"{SIMBOLO}-{vid}" and v.get("tipo") == "risultato"][-1]
    return r["metriche"]["trade"]


def valida(vid):
    lid = f"{SIMBOLO}-{vid}-VAL"
    if any(v.get("id") == lid and v.get("tipo") == "risultato" for v in voci_log()):
        raise SystemExit(f"{vid}: la validazione ha gia' un risultato; si fa una volta sola")
    n_c = costruzione_trade(vid)
    if not any(v.get("id") == lid for v in voci_log()):
        aggiungi_log({"id": lid, "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": f"{SIMBOLO}-{vid}",
                  "verifica": "validazione", "periodo": "validazione (2022-10-19 -> 2023-12-31)",
                  "trade_stimati": round(n_c * 30 / 70), "trade_stimati_nota": f"stima proporzionale {n_c} x 30/70, non conta_trade",
                  "criterio_successo": "almeno 30 trade in validazione e asticella di Benjamini-Hochberg al 10% sul p-value contro la (b) di validazione (esito provvisorio, lo conferma il coordinamento al Passo 4)"})
    v = varianti.TUTTE[vid]()
    par = parametri()
    candele, mark, funding = quadro.tutto_insample(v.tf)
    ris = motore.esegui(candele, None, mark, funding, v.fabbrica(candele)(), par)
    trades = sorted([t for t in ris.trades if t.ts_entrata >= INIZIO_V], key=lambda t: t.ts_uscita)
    m = quadro.metriche_trade(trades)
    # drawdown e rendimento sui soli trade di validazione, dal capitale iniziale
    cap, picco, dd = par.capitale_iniziale, par.capitale_iniziale, 0.0
    for t in trades:
        cap += t.pnl_pct * cap
        picco = max(picco, cap)
        dd = max(dd, (picco - cap) / picco)
    m["drawdown_max"] = round(dd, 4)
    m["rendimento_totale_composto"] = round(cap / par.capitale_iniziale - 1, 4)
    out = {"id": lid, "tipo": "risultato", "metriche": m}
    if len(trades) < 30:
        out.update({"esito": "non si sa: sotto i 30 trade di validazione", "p_value": 1.0})
        aggiungi_log(out)
        print(out)
        return
    r = [t.r for t in trades]
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    out["blocco"] = blocco
    # (a)
    ris_a = motore.esegui(candele, None, mark, funding, v.fabbrica_a(candele)(), par)
    ta = sorted([t for t in ris_a.trades if t.ts_entrata >= INIZIO_V], key=lambda t: t.ts_uscita)
    blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in ta], [t.ts_uscita for t in ta])
    base_a = statistica.baseline_da_trade([t.r for t in ta], blocco_a)
    out["baseline_a"] = dict(media=round(base_a["media"], 5), n_trade=base_a["n_trade"],
                             **quadro._ridotto(statistica.contro_baseline(r, blocco, base_a), quadro.CHIAVI_CONFRONTO))
    # (b) con ingressi solo nelle barre di validazione
    primo = next(i for i, c in enumerate(candele) if c.ts >= INIZIO_V)
    vietate = [(0, primo)] + motore.barre_vietate_segnale_non_valido(candele, v.fabbrica_segnale(candele), par)
    durata = motore.durata_media_barre(trades, quadro.MS[v.tf])
    base_b = motore.simula_baseline_casuale(candele, v.fabbrica_casuale(candele), len(trades), durata, par,
                                            None, mark, funding, vietate, n_simulazioni=200)
    cmp_b = statistica.contro_baseline(r, blocco, base_b)
    out["baseline_b"] = dict(media=round(base_b["media"], 5), n_simulazioni=base_b["n_simulazioni"],
                             trade_per_simulazione_medio=round(float(np.mean(base_b["trade_per_simulazione"])), 2),
                             durata_media_barre=durata, **quadro._ridotto(cmp_b, quadro.CHIAVI_CONFRONTO))
    out["percentile_caso"] = round(statistica.percentile_del_candidato(float(np.mean(r)), base_b["valori"]), 2)
    out["p_value"] = cmp_b["p_value"]
    giorni = [c for c in candele if c.ts >= INIZIO_V]
    out["buy_and_hold_per_anno"] = quadro.buy_and_hold_per_anno(giorni, par)
    aggiungi_log(out)
    print({k: out[k] for k in ("metriche", "baseline_a", "baseline_b", "p_value", "percentile_caso")})


if __name__ == "__main__":
    for vid in sys.argv[1:]:
        valida(vid)
