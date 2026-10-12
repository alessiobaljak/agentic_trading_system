"""Fase 5: prove dello scettico sul candidato FILUSDT-025 (solo dati di costruzione).

S1 — «e' solo la struttura dello stop». Le baseline del protocollo usano lo stesso stop del
candidato (l'apertura del giorno): un ingresso casuale col close appena sopra l'apertura ha uno
stop vicinissimo e costi enormi in R. Qui il candidato si confronta con ingressi casuali long
nelle ore 00-22 UTC, uscita alla fine del giorno come il candidato, ma con lo stop a distanza
FISSA pari alla distanza media del candidato (in %): gli R casuali non sono piu' gonfiati dai
costi degli stop vicini. Stessi strumenti: simula_baseline_casuale (200 semi) e contro_baseline.

S2 — «e' solo il mercato». I trade del candidato divisi per il segno del rendimento di BTC dalla
mezzanotte alla barra del segnale, e la stessa regola applicata a BTC (rottura di BTC sopra la
sua apertura + 0,6 x escursione del giorno prima) per vedere quanti segnali coincidono.

Uso: python scettico.py S1 | S2
"""
from __future__ import annotations

import json
import sys

import numpy as np

import comune
import quadro as q
import varianti
from registro import _pulisci
from research.src import motore, statistica


def s1():
    s = q.carica("1h", "costruzione")
    cand = varianti.TUTTE["FILUSDT-025"]()
    k = q.calcola(cand, s)
    par = comune.parametri()
    ris = motore.esegui(s.candele, None, s.mark, s.funding, q.fabbrica_strategia(k)(), par)
    trades = sorted(ris.trades, key=lambda t: t.ts_uscita)
    r = np.array([t.r for t in trades])
    d_media = float(np.mean([abs(t.entrata - t.stop) / t.entrata for t in trades]))
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    ultima = varianti._ultima_barra_del_giorno(s)

    finta = q.Variante("S1", "1h", "long", ingresso=lambda s_: np.zeros(len(s_.c), dtype=bool),
                       stop=lambda s_: s_.c * (1 - d_media), uscita=lambda s_: varianti._ultima_barra_del_giorno(s_))
    kf = q.calcola(finta, s)
    vietata = ultima.copy()  # nessun ingresso sull'ultima barra del giorno, come il candidato
    durata = motore.durata_media_barre(trades, q.MS["1h"])
    base = motore.simula_baseline_casuale(s.candele, q.fabbrica_casuale(kf), len(trades), durata, par,
                                         candele_mark=s.mark, funding=s.funding,
                                         barre_vietate=q.intervalli_da_maschera(vietata))
    conf = statistica.contro_baseline(r, blocco, base)
    out = {"trade": len(trades), "r_medio": float(r.mean()), "distanza_stop_media": d_media, "blocco": blocco,
           "durata_media_barre": durata, "baseline_s1_media": base["media"],
           "baseline_s1_trade_per_sim": float(np.mean(base["trade_per_simulazione"])),
           "t": conf["t"], "soglia": conf["soglia"], "netta": conf["netta"], "p_value": conf["p_value"],
           "percentile": statistica.percentile_del_candidato(float(r.mean()), base["valori"])}
    return out


def s2():
    s = q.carica("1h", "costruzione")
    cand = varianti.TUTTE["FILUSDT-025"]()
    k = q.calcola(cand, s)
    par = comune.parametri()
    ris = motore.esegui(s.candele, None, s.mark, s.funding, q.fabbrica_strategia(k)(), par)
    giorno = s.ts // 86_400_000
    # apertura di BTC del giorno: close della barra precedente la prima barra del giorno
    btc_ap = np.full(len(s.c), np.nan)
    primo = {}
    for i in range(len(s.c)):
        d = int(giorno[i])
        if d not in primo:
            primo[d] = s.btc_c[i - 1] if i > 0 and s.ts[i] - s.ts[i - 1] == 3_600_000 else np.nan
        btc_ap[i] = primo[d]
    btc_dal_giorno = s.btc_c / btc_ap - 1
    su, giu = [], []
    for t in ris.trades:
        i = s.indice_ts[t.ts_entrata] - 1
        (su if btc_dal_giorno[i] > 0 else giu).append(t.r)
    # stessa regola su BTC: serve high/low di BTC, che il quadro non carica: si leggono i file
    from research.src import dati
    btc = dati.carica_candele("BTCUSDT", "1h", comune.PERIODI["inizio"], comune.PERIODI["fine_costruzione"])
    per_ts = {b.ts: b for b in btc}
    alto, basso, ap = {}, {}, {}
    segnali_btc = set()
    for b in btc:
        d = b.ts // 86_400_000
        if d not in ap:
            ap[d], alto[d], basso[d] = b.open, b.high, b.low
        else:
            alto[d], basso[d] = max(alto[d], b.high), min(basso[d], b.low)
        if d - 1 in alto and (b.ts // 3_600_000) % 24 < 23 and d not in {x // 86_400_000 for x in []}:
            if b.close > ap[d] + 0.6 * (alto[d - 1] - basso[d - 1]):
                segnali_btc.add(d)
    giorni_cand = {t.ts_entrata // 86_400_000 for t in ris.trades}
    comuni = giorni_cand & segnali_btc
    r_comuni = [t.r for t in ris.trades if t.ts_entrata // 86_400_000 in segnali_btc]
    r_solo_fil = [t.r for t in ris.trades if t.ts_entrata // 86_400_000 not in segnali_btc]
    return {"trade": len(ris.trades),
            "btc_su_dalla_mezzanotte": {"n": len(su), "r_medio": float(np.mean(su)) if su else None},
            "btc_giu_dalla_mezzanotte": {"n": len(giu), "r_medio": float(np.mean(giu)) if giu else None},
            "giorni_con_rottura_anche_di_btc": {"n": len(comuni), "r_medio": float(np.mean(r_comuni)) if r_comuni else None},
            "giorni_con_rottura_solo_di_fil": {"n": len(r_solo_fil), "r_medio": float(np.mean(r_solo_fil)) if r_solo_fil else None},
            "giorni_con_rottura_di_btc_in_costruzione": len(segnali_btc)}


if __name__ == "__main__":
    prova = sys.argv[1]
    out = s1() if prova == "S1" else s2()
    (comune.CARTELLA_DATI / "esiti" / f"FILUSDT-025_{prova}.json").write_text(json.dumps(_pulisci(out), indent=1))
    print(json.dumps(_pulisci(out), indent=1))
