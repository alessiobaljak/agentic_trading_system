"""Fase 4: le verifiche dei candidati della famiglia ETCUSDT-023 (short nell'ultima mezz'ora UTC).

Uso: python fase4.py <ID>   (ETCUSDT-033, ETCUSDT-036 o ETCUSDT-037)

Ogni verifica si registra nel log (tipo registrazione, tipo_test verifica, verifica_di) PRIMA di
eseguirla e il risultato va in una voce separata. Le verifiche non cambiano le regole del
candidato e non servono a sceglierne un altro (sezione Fase 4 del protocollo).

Regole di conversione scritte prima dei numeri:
* robustezza: ogni parametro numerico +-20%, uno alla volta; interi a round(0,8 x) e round(1,2 x)
  con le meta' verso l'alto, e se restano uguali -1 e +1. L'uscita a 1 barra resta 1 con +-20%:
  si prova 2 (+1); 0 barre non esiste come uscita e si dichiara (caso non eseguibile). Il filtro di
  volatilita' di 036 e 037 e' "distanza dello stop >= 2,5% del close": la distanza dello stop
  e' quella del parametro stop_atr, quindi spostare stop_atr sposta anche il filtro; la soglia del
  2,5% si sposta da sola.
* timeframe adiacenti: 15m e 1h. La mezz'ora finale del giorno resta la stessa durata dove si puo':
  15m segnale alla chiusura delle 23:30 (barra 23:15), uscita dopo 2 barre (30 minuti); 1h segnale
  alla chiusura delle 23:00 (barra 22:00), uscita dopo round(0,5) -> 1 barra (almeno 1). L'ATR a 14
  barre da 30 minuti (7 ore) diventa 28 barre a 15m e 7 a 1h; soglie in percentuale invariate.
"""
from __future__ import annotations

import sys
from dataclasses import replace

import numpy as np

import comune as C
import registro
import varianti as V
from comune import Variante

GIORNO, ORA = V.GIORNO, V.ORA
SEGNALE = {"15m": 23 * ORA + 15 * 60_000, "30m": 23 * ORA, "1h": 22 * ORA}
USCITA = {"15m": 2, "30m": 1, "1h": 1}
N_ATR = {"15m": 28, "30m": 14, "1h": 7}

CANDIDATI = {
    "ETCUSDT-033": {"soglia": -0.05, "filtro": None},
    "ETCUSDT-036": {"soglia": -0.03, "filtro": 0.025},
    "ETCUSDT-037": {"soglia": -0.05, "filtro": 0.025},
}


def costruisci(soglia, filtro, tf="30m", k=2.0, n_atr=None, uscita=None, nome="verifica"):
    n_atr = n_atr or N_ATR[tf]
    uscita = uscita if uscita is not None else USCITA[tf]
    off = SEGNALE[tf]

    def prepara(serie):
        ind = V._base(serie, n_atr)
        apertura = {c.ts: c.open for c in serie.candele if c.ts % GIORNO == 0}
        rg = [None] * serie.n
        for i, c in enumerate(serie.candele):
            if c.ts % GIORNO == off:
                a = apertura.get(c.ts - c.ts % GIORNO)
                if a:
                    rg[i] = c.close / a - 1
        ind["rg"] = rg
        ind["riscaldamento"] = V._riscaldamento(ind["atr"])
        return ind

    def ingresso(ind, i):
        if ind["rg"][i] is None or not ind["rg"][i] < soglia:
            return False
        return filtro is None or k * ind["atr"][i] / ind["c"][i] >= filtro

    return Variante(nome, tf, "short", prepara, ingresso, V._stop(k, "short"), max_barre=uscita)


def voce_base(vid):
    reg = [v for v in registro.voci() if v["id"] == vid and v["tipo"] == "registrazione"][0]
    ris = [v for v in registro.voci() if v["id"] == vid and v["tipo"] == "risultato"][0]
    return reg, ris


def sintesi(r):
    m = r["metriche"]
    return {"trade": m["trade"], "r_medio": m["r_medio"], "profit_factor": m["profit_factor"],
            "t_b": r.get("baseline_b", {}).get("t"), "netta_b": r.get("baseline_b", {}).get("netta"),
            "media_b": r.get("baseline_b", {}).get("media"), "t_a": r.get("baseline_a", {}).get("t"),
            "netta_a": r.get("baseline_a", {}).get("netta"), "valutabile": r.get("valutabile")}


def verifica(vid, nome, descrizione, criterio, var, parametri=C.PARAMETRI, conta=True):
    """Registra, conta (se serve), esegue, scrive il risultato. Ritorna la sintesi o None (sotto i minimi)."""
    stima = C.conta(var) if conta else None
    reg = {"id": f"{vid}-V-{nome}", "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": vid,
           "verifica": descrizione, "criterio_successo": criterio, "periodo": "costruzione",
           "trade_stimati": stima["trade"] if stima else None, "timeframe": var.tf}
    registro.scrivi(reg)
    if stima and stima["trade"] < C.TRADE_MINIMI_COSTRUZIONE:
        registro.scrivi({"id": reg["id"], "tipo": "risultato", "esito": "sotto i trade minimi di costruzione: non conta",
                         "trade": stima["trade"]})
        C.stampa(reg["id"], "sotto i minimi", stima["trade"])
        return None
    r = C.esame(var, parametri=parametri)
    s = sintesi(r)
    registro.scrivi({"id": reg["id"], "tipo": "risultato", **s, "metriche": r["metriche"],
                     "n_violazioni_liquidazione": r["metriche"].get("n_violazioni_liquidazione")})
    C.stampa(reg["id"], s)
    return s


def principale(vid):
    cfg = CANDIDATI[vid]
    reg, ris = voce_base(vid)
    base_t = ris["baseline_b"]["t"]
    media_b = ris["baseline_b"]["media"]
    esiti = {}

    # 8. costi doppi
    s = verifica(vid, "costi-doppi", "costi doppi (commissioni, slippage e funding quando e' un costo, x2)",
                 "batte nettamente la (b) ricalcolata a costi doppi e R medio a costi doppi > 0",
                 costruisci(cfg["soglia"], cfg["filtro"]), replace(C.PARAMETRI, moltiplicatore_costi=2.0))
    esiti["costi_doppi"] = bool(s and s["netta_b"] and s["r_medio"] > 0)

    # 6. ritardo di una barra
    s = verifica(vid, "ritardo", "esecuzione ritardata di una barra",
                 "t contro la (b) ricalcolata col ritardo > 0 e almeno la meta' del t senza ritardo",
                 costruisci(cfg["soglia"], cfg["filtro"]), replace(C.PARAMETRI, ritardo_barre=1), conta=False)
    esiti["ritardo"] = bool(s and s["t_b"] is not None and s["t_b"] > 0 and s["t_b"] >= 0.5 * base_t)

    # 5. regola intra-barra opposta
    s = verifica(vid, "intrabarra-opposta", "riempimento intra-barra opposto (target prima)",
                 "si dichiara la differenza (la variante non ha target: atteso identico)",
                 costruisci(cfg["soglia"], cfg["filtro"]), replace(C.PARAMETRI, riempimento_intrabarra="target_prima"),
                 conta=False)
    esiti["intrabarra_differenza_r"] = (s["r_medio"] - ris["metriche"]["r_medio"]) if s else None

    # 1. robustezza
    casi = [("soglia-0.8", dict(soglia=cfg["soglia"] * 0.8)), ("soglia-1.2", dict(soglia=cfg["soglia"] * 1.2)),
            ("stop-0.8", dict(k=1.6)), ("stop-1.2", dict(k=2.4)),
            ("atr-0.8", dict(n_atr=11)), ("atr-1.2", dict(n_atr=17)),
            ("uscita+1", dict(uscita=2))]
    if cfg["filtro"]:
        casi += [("filtro-0.8", dict(filtro=cfg["filtro"] * 0.8)), ("filtro-1.2", dict(filtro=cfg["filtro"] * 1.2))]
    contati, positivi, netti = 0, 0, 0
    for nome, mod in casi:
        p = dict(soglia=cfg["soglia"], filtro=cfg["filtro"])
        p.update({k: v for k, v in mod.items() if k in ("soglia", "filtro")})
        kw = {k: v for k, v in mod.items() if k not in ("soglia", "filtro")}
        s = verifica(vid, f"robustezza-{nome}", f"robustezza: {nome} {mod}",
                     "nei casi che contano t contro la (b) > 0 e in almeno meta' netta; casi sotto i minimi non contano",
                     costruisci(p["soglia"], p["filtro"], **kw))
        if s is None:
            continue
        contati += 1
        if s["valutabile"] and s["t_b"] > 0:
            positivi += 1
        if s["valutabile"] and s["netta_b"]:
            netti += 1
    previsti = len(casi) + 1  # +1: l'uscita a 0 barre, prevista dalla regola e non eseguibile
    esiti["robustezza"] = {"casi_previsti": previsti, "contati": contati, "t_positivo": positivi, "netti": netti,
                           "superata": bool(contati >= previsti / 2 and positivi == contati and netti >= contati / 2)}

    # 2. timeframe adiacenti
    adiac = {}
    for tf in ("15m", "1h"):
        s = verifica(vid, f"timeframe-{tf}", f"timeframe adiacente {tf} (parametri convertiti in tempo)",
                     "t contro la (b) ricalcolata > 0; sotto i minimi non conta; non valutabile = fallita",
                     costruisci(cfg["soglia"], cfg["filtro"], tf=tf))
        adiac[tf] = None if s is None else bool(s["valutabile"] and s["t_b"] > 0)
    esiti["timeframe_adiacenti"] = {"esiti": adiac, "superata": all(v is not False for v in adiac.values())}

    # 4. stabilita' temporale e trade estremi (dal risultato del candidato, gia' nel log)
    m = ris["metriche"]
    anni = {a: r for a, r in m["r_medio_per_anno"].items() if m["trade_per_anno"][a] >= 10}
    sopra = sum(1 for r in anni.values() if r > media_b)
    esiti["stabilita"] = {"anni_con_10_trade": anni, "media_b": media_b, "anni_sopra": sopra,
                          "superata": bool(anni and sopra > len(anni) / 2)}
    esiti["senza_3_migliori"] = {"r": m["r_medio_senza_3_migliori"], "media_b": media_b,
                                 "superata": bool(m["r_medio_senza_3_migliori"] is not None
                                                  and m["r_medio_senza_3_migliori"] > media_b)}
    esiti["liquidazione"] = {"violazioni": m.get("n_violazioni_liquidazione"),
                             "superata": m.get("n_violazioni_liquidazione") == 0}
    esiti["trade_ridotti_tetto_leva"] = m.get("n_ridotti_tetto_leva")
    tutte = (esiti["costi_doppi"] and esiti["ritardo"] and esiti["robustezza"]["superata"]
             and esiti["timeframe_adiacenti"]["superata"] and esiti["stabilita"]["superata"]
             and esiti["senza_3_migliori"]["superata"] and esiti["liquidazione"]["superata"])
    registro.scrivi({"id": f"{vid}-FASE4", "tipo": "nota", "testo": f"Esito delle verifiche di Fase 4 di {vid}: "
                     + ("tutte superate" if tutte else "almeno una NON superata: il candidato e' scartato"),
                     "esiti": esiti, "superato": bool(tutte)})
    C.stampa("ESITO FASE 4", vid, tutte, esiti)


if __name__ == "__main__":
    principale(sys.argv[1])
