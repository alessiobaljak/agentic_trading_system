"""Fase 2 (baseline) sui dati di costruzione, per una variante ammessa.

Uso: python -m research.campagne.SOLUSDT.codice.fase2 registra NOME...   (scrive le registrazioni, con id e variante_n)
     python -m research.campagne.SOLUSDT.codice.fase2 esegui NOME ID      (esegue e scrive il risultato con quell'id)

Il risultato porta: metriche del motore, R per anno, le tre baseline della
sezione 8 [(a) stessa uscita su barre qualsiasi, (b) entrate casuali con la
stessa uscita, (c) buy and hold e opposto], il giudizio «nettamente» e il
controllo «e' solo BTC» (R residuo dopo beta x BTC nelle stesse finestre).
"""
import json
import sys
from pathlib import Path

import numpy as np

from research.src import motore, statistica
from research.campagne.SOLUSDT.codice import campagna as cp, strategie as st
from research.campagne.SOLUSDT.codice.varianti import VARIANTI, regola

sys.path.insert(0, str(Path(__file__).resolve().parent))
import log  # noqa: E402

FONTI = {
    "I-01": "Time Series Momentum, Moskowitz, Ooi, Pedersen, Journal of Financial Economics 104(2), 2012; Risks and Returns of Cryptocurrency, Liu, Tsyvinski, Review of Financial Studies 34(6), 2021",
    "I-03": "Bitcoin time-of-day, day-of-week and month-of-year effects in returns and trading volume, Baur, Cahill, Godfrey, Liu, Finance Research Letters 31, 2019",
    "I-04": "Seasonality in cryptocurrencies, Kaiser, Finance Research Letters 31, 2019; Baur, Cahill, Godfrey, Liu 2019",
    "I-05": "Price overreactions in the cryptocurrency market, Caporale, Plastun, Journal of Economic Studies 46(5), 2019; Market Liquidity and Funding Liquidity, Brunnermeier, Pedersen, Review of Financial Studies 22(6), 2009",
    "I-06": "Does the Stock Market Overreact?, De Bondt, Thaler, Journal of Finance 40(3), 1985; Brunnermeier, Pedersen 2009",
    "I-07": "Way of the Turtle, Curtis M. Faith, McGraw-Hill, 2007 (regola del canale di Donchian)",
    "I-08": "Bollinger on Bollinger Bands, John Bollinger, McGraw-Hill, 2001",
    "I-09": "Simple Technical Trading Rules and the Stochastic Properties of Stock Returns, Brock, Lakonishok, LeBaron, Journal of Finance 47(5), 1992",
    "I-13": "Order imbalance and individual stock returns: Theory and evidence, Chordia, Subrahmanyam, Journal of Financial Economics 72(3), 2004",
    "I-10": "Virtual relationships: Short- and long-run evidence from BitCoin and altcoin markets, Ciaian, Rajcaniova, Kancs, Journal of International Financial Markets, Institutions and Money 52, 2018",
}
MECCANISMI = {
    "I-01": "inseguimento della tendenza dai flussi al dettaglio e diffusione lenta delle informazioni",
    "I-03": "flussi concentrati nelle ore di mercato americane",
    "I-04": "segno sistematico dei rendimenti del fine settimana a liquidita' bassa",
    "I-05": "spirale di liquidita': liquidazioni a catena nella direzione dello shock",
    "I-06": "esaurimento della spirale e ritorno verso il prezzo precedente",
    "I-07": "ordini di stop e inseguimento oltre i massimi/minimi recenti",
    "I-08": "eccesso di breve periodo e fornitura di liquidita'",
    "I-09": "acquisti sui ribassi dentro una tendenza riconosciuta",
    "I-13": "persistenza del flusso degli ordini a mercato spezzati su piu' ore",
    "I-10": "diffusione del movimento di BTC alle altcoin con ritardo",
}
PREVISIONI = {
    "I-01-4h-long": "R medio 0,05-0,20, profit factor 1,1-1,4, win rate sotto il 50% con vincite lunghe; vantaggio dominato dal 2021",
    "I-01-4h-short": "R medio vicino a zero o negativo, profit factor sotto 1,1",
    "I-03-1h-long": "R medio 0,00-0,05, non netto rispetto alle entrate casuali; segno dell'anno",
    "I-04-4h-segno-long": "R medio 0,00-0,05, non netto; segno dell'anno",
    "I-05-1h-long": "R medio circa zero, molti stop",
    "I-05-1h-short": "R medio 0,05-0,15, molti stop per la volatilita' dopo lo shock",
    "I-06-1h-short-2.5s": "R medio circa zero (il ritorno dopo shock positivo e' il caso meno frequente)",
    "I-07-1h-long": "profit factor 1,0-1,3, win rate 35-45%, R medio 0,00-0,15, dominato dal 2021",
    "I-07-1h-short": "R medio circa zero",
    "I-08-1h-long": "win rate 55-65%, R medio vicino a zero, profit factor 0,9-1,1",
    "I-08-1h-short": "win rate 55-65%, R medio vicino a zero, profit factor 0,9-1,1",
    "I-09-1h-long": "R medio 0,00-0,10, non netto rispetto all'entrata casuale condizionata alla tendenza",
    "I-09-1h-short": "R medio circa zero",
    "I-10-1h-long": "R medio circa zero",
    "I-10-1h-short": "R medio circa zero",
    "I-13-1h-long": "R medio circa zero",
    "I-13-1h-short": "R medio circa zero; se c'e' qualcosa e' qui (le vendite forzate persistono piu' degli acquisti)",
}
STIME = {
    "I-01-4h-long": {"grezzi": 160, "non_sovrapposti": 105}, "I-01-4h-short": {"grezzi": 161, "non_sovrapposti": 101},
    "I-03-1h-long": {"grezzi": 518, "non_sovrapposti": 518}, "I-04-4h-segno-long": {"grezzi": 103, "non_sovrapposti": 103},
    "I-05-1h-long": {"grezzi": 178, "non_sovrapposti": 133}, "I-05-1h-short": {"grezzi": 129, "non_sovrapposti": 103},
    "I-06-1h-short-2.5s": {"grezzi": 158, "non_sovrapposti": 122},
    "I-07-1h-long": {"grezzi": 910, "non_sovrapposti": 325}, "I-07-1h-short": {"grezzi": 804, "non_sovrapposti": 310},
    "I-08-1h-long": {"grezzi": 1075, "non_sovrapposti": 299}, "I-08-1h-short": {"grezzi": 1126, "non_sovrapposti": 293},
    "I-09-1h-long": {"grezzi": 1069, "non_sovrapposti": 170}, "I-09-1h-short": {"grezzi": 1228, "non_sovrapposti": 176},
    "I-10-1h-long": {"grezzi": 271, "non_sovrapposti": 136}, "I-10-1h-short": {"grezzi": 188, "non_sovrapposti": 107},
    "I-13-1h-long": {"grezzi": 1021, "non_sovrapposti": 473}, "I-13-1h-short": {"grezzi": 1095, "non_sovrapposti": 458},
}
CRITERIO = ("sui dati di costruzione: almeno 100 trade; profit factor dopo costi sopra 1; R medio sopra il 90° percentile "
            "degli R medi di 200 entrate casuali con la stessa uscita; differenza dalla simulazione casuale mediana oltre 2 "
            "errori standard (bootstrap a blocchi); R residuo dopo beta x BTC ancora positivo")


def parametri_regola(nome):
    r = regola(nome)
    return {k: v for k, v in r.p.items() if k not in ("funding", "btc")}


def registra(nomi):
    n_var = max([v.get("variante_n", 0) for v in log.leggi() if v.get("tipo_test") == "variante"] + [0])
    for nome in nomi:
        idea, tf, direzione, _, _ = VARIANTI[nome]
        n_var += 1
        voce = {"id": f"SOLUSDT-{log.prossimo_numero():03d}", "tipo": "registrazione", "tipo_test": "variante",
                "variante": nome, "idea": idea, "fonte": FONTI[idea], "meccanismo": MECCANISMI[idea],
                "timeframe": tf, "direzione": direzione, "parametri": parametri_regola(nome), "periodo": "costruzione",
                "fase": "2", "previsione": PREVISIONI[nome], "criterio_successo": CRITERIO,
                "trade_stimati": STIME[nome], "variante_n": n_var}
        log.scrivi(voce)
        print(voce["id"], nome, "variante_n", n_var)


def beta_sol_btc(tf, periodo):
    last = cp.carica(tf, periodo)[0]
    btc = {c.ts: c.close for c in cp.carica_riferimento(tf, periodo)}
    xs, ys = [], []
    for a, b in zip(last, last[1:]):
        if a.ts in btc and b.ts in btc:
            xs.append(btc[b.ts] / btc[a.ts] - 1); ys.append(b.close / a.close - 1)
    xs, ys = np.array(xs), np.array(ys)
    return float(np.cov(xs, ys)[0, 1] / xs.var())


def r_residuo(ris, tf, periodo, beta):
    """R di ogni trade meno la parte spiegata da beta x movimento di BTC nella stessa finestra."""
    btc = cp.carica_riferimento(tf, periodo)
    ts = np.array([c.ts for c in btc]); cl = np.array([c.close for c in btc]); op = np.array([c.open for c in btc])
    out = []
    for t in ris.trades:
        i0 = int(np.searchsorted(ts, t.ts_entrata)); i1 = int(np.searchsorted(ts, t.ts_uscita, side="right") - 1)
        if i0 >= len(ts) or i1 < i0:
            out.append(t.r); continue
        mossa = cl[i1] / op[i0] - 1
        segno = 1 if t.direzione == "long" else -1
        dist = abs(t.entrata - t.stop) / t.entrata
        out.append(t.r - segno * beta * mossa / dist)
    return out


def esegui(nome, id_voce):
    idea, tf, direzione, _, _ = VARIANTI[nome]
    periodo = cp.COSTRUZIONE
    r = regola(nome)
    fab = st.fabbrica(r, direzione)
    ris = cp.esegui(fab, tf, periodo)
    rs = cp.riassunto(ris)
    last, mark, fund, scartate = cp.carica(tf, periodo)
    risultato = {"id": id_voce, "tipo": "risultato", "variante": nome, "periodo": "costruzione", "metriche": rs,
                 "barre_scartate_allineamento": scartate}
    if ris.trades:
        # (a) stessa uscita su barre qualsiasi: ingresso a ogni barra libera
        tutti = list(range(len(last) - 1))
        ris_a = motore.esegui(last, None, mark, fund, st.fabbrica_casuale(r, direzione, tutti)(last), cp.PARAMETRI)
        rsa = cp.riassunto(ris_a)
        blocco = cp.lunghezza_blocco(ris, tf)
        risultato["baseline_a_barre_qualsiasi"] = {"trade": rsa["trade"], "r_medio": rsa["r_medio"], "profit_factor": rsa["profit_factor"],
                                                   "nettamente": cp.nettamente(cp.r_ordinati(ris), cp.r_ordinati(ris_a), blocco)}
        # (b) entrate casuali con la stessa uscita (per I-09 condizionate alla tendenza)
        vietate = ()
        if idea == "I-09":
            r.precalcola(last)
            mask = np.array([r.in_tendenza(i) != direzione for i in range(len(last))])
            vietate = _intervalli(mask)
        risultato["baseline_b_entrate_casuali"] = _baseline_b(ris, r, direzione, tf, periodo, vietate)
        # (c) buy and hold
        risultato["baseline_c_buy_and_hold"] = cp.buy_and_hold(tf, periodo)
        # e' solo BTC?
        beta = beta_sol_btc(tf, periodo)
        rres = r_residuo(ris, tf, periodo, beta)
        risultato["solo_btc"] = {"beta_sol_su_btc": round(beta, 3), "r_residuo_medio": round(float(np.mean(rres)), 3),
                                 "r_residuo_mediano": round(float(np.median(rres)), 3)}
        # pochi trade estremi
        rr = sorted(t.r for t in ris.trades)
        risultato["senza_3_migliori"] = {"r_medio": round(float(np.mean(rr[:-3])), 3) if len(rr) > 3 else None}
    log.scrivi(risultato)
    print(json.dumps(risultato, ensure_ascii=False)[:3000])


def _intervalli(mask):
    out = []; i = 0; n = len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j < n and mask[j]:
                j += 1
            out.append((i, j)); i = j
        else:
            i += 1
    return out


def _baseline_b(ris, r, direzione, tf, periodo, vietate, n_sim=200, seme=1):
    last, mark, fund, _ = cp.carica(tf, periodo)
    tr = ris.trades
    passo = last[1].ts - last[0].ts
    durata = max(1, round(sum(t.ts_uscita - t.ts_entrata + 1 for t in tr) / len(tr) / passo))
    medie, serie = [], []
    riscaldamento = 250
    viet = [(0, riscaldamento)] + list(vietate)
    for k in range(n_sim):
        try:
            idx = statistica.entrate_casuali(len(last) - 1, len(tr), durata, seme + k, barre_vietate=viet)
        except ValueError as e:
            return {"errore": str(e)}
        rr = motore.esegui(last, None, mark, fund, st.fabbrica_casuale(r, direzione, idx)(last), cp.PARAMETRI)
        rs = cp.r_ordinati(rr)
        medie.append(float(np.mean(rs)) if rs else 0.0); serie.append(rs)
    medie = np.array(medie)
    r_c = cp.r_ordinati(ris)
    media_c = float(np.mean(r_c))
    mediana = int(np.argsort(medie)[len(medie) // 2])
    blocco = cp.lunghezza_blocco(ris, tf)
    return {"simulazioni": n_sim, "trade_per_simulazione": len(tr), "durata_barre": durata,
            "r_medio_candidato": round(media_c, 3), "r_medio_caso_media": round(float(medie.mean()), 3),
            "r_medio_caso_p50": round(float(np.percentile(medie, 50)), 3), "r_medio_caso_p90": round(float(np.percentile(medie, 90)), 3),
            "r_medio_caso_p95": round(float(np.percentile(medie, 95)), 3), "percentile_candidato": round(float((medie < media_c).mean() * 100), 1),
            "blocco": blocco, "nettamente_vs_mediana": cp.nettamente(r_c, serie[mediana], blocco),
            "p_value_vs_mediana": round(statistica.p_value_bootstrap_vs_caso(r_c, serie[mediana], blocco, 2000, seme), 4)}


if __name__ == "__main__":
    if sys.argv[1] == "registra":
        registra(sys.argv[2:])
    else:
        esegui(sys.argv[2], sys.argv[3])
