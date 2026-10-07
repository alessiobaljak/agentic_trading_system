"""Fase 4: le otto verifiche sui dati di COSTRUZIONE per un candidato sopravvissuto alle fasi 1-3.

Uso: python3 fase4_verifiche.py <IDEA> <long|short> <ID della variante nel log>
Ogni verifica si registra nel log PRIMA di eseguirla (tipo_test verifica, verifica_di = id
della variante) e il suo risultato subito dopo. Le verifiche non consumano budget.

1. robustezza: k_atr in {1,5; 2; 3} e H in {H/2; H; 2H} (area stabile, non picco);
2. timeframe adiacenti: la stessa regola sui timeframe vicini ammessi (solo per verificare);
3. direzione: gia' separata per costruzione (le varianti sono per direzione);
4. stabilita' temporale: R medio e somma R per anno (gia' nel risultato) e senza i 2 mesi migliori;
5. dipendenza dai dati: senza il 5 % dei trade migliori; regola intra-barra opposta;
6. ritardo di una barra;
7. liquidazione: violazioni (gia' nel risultato: n_violazioni_liquidazione);
8. costi doppi.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import comune  # noqa: E402
import strategie  # noqa: E402
from comune import Uscita  # noqa: E402
from log import aggiungi, prossimo_id  # noqa: E402

ADIACENTI = {"15m": ["30m"], "30m": ["15m", "1h"], "1h": ["30m", "2h"], "2h": ["1h", "4h"], "4h": ["2h", "6h"],
             "6h": ["4h", "8h"], "8h": ["6h", "12h"], "12h": ["8h", "1d"], "1d": ["12h"]}


def corri(codice: str, direzione: int, intervallo: str, k_atr=None, h_barre=None, parametri=None):
    idea = strategie.IDEE[codice]
    s = comune.serie(intervallo, comune.INIZIO_DATI, comune.FINE_COSTRUZIONE, con_btc=idea.con_btc)
    segn_tutti, uscita, riscaldamento = idea.costruisci(s)
    segn = strategie.solo(segn_tutti, direzione)
    if k_atr is not None or h_barre is not None:
        uscita = Uscita(k_atr=k_atr if k_atr is not None else uscita.k_atr,
                        h_barre=h_barre if h_barre is not None else uscita.h_barre,
                        rr_target=uscita.rr_target, chiusura_segnale=uscita.chiusura_segnale)
    strat = comune.costruisci_strategia(s, segn, uscita, comune.atr(s, 14), riscaldamento, len(s.ts))
    ris = comune.esegui(s, strat, parametri)
    return ris, comune.riassunto(ris, s), uscita


def senza_migliori(ris, quota=0.05):
    r = sorted((t.r for t in ris.trades), reverse=True)
    n_tolti = int(np.ceil(len(r) * quota))
    resto = r[n_tolti:]
    return {"n_tolti": n_tolti, "r_medio_senza": round(float(np.mean(resto)), 4) if resto else None,
            "somma_r_senza": round(float(np.sum(resto)), 2) if resto else None}


def senza_mesi_migliori(ris, n_mesi=2):
    per_mese = defaultdict(float)
    for t in ris.trades:
        d = datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc)
        per_mese[f"{d.year}-{d.month:02d}"] += t.r
    migliori = sorted(per_mese.items(), key=lambda kv: kv[1], reverse=True)[:n_mesi]
    tolti = {m for m, _ in migliori}
    resto = [t.r for t in ris.trades if f"{datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc).year}-{datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc).month:02d}" not in tolti]
    return {"mesi_tolti": [f"{m} (somma R {v:.1f})" for m, v in migliori], "r_medio_senza": round(float(np.mean(resto)), 4) if resto else None,
            "somma_r_senza": round(float(np.sum(resto)), 2) if resto else None, "n_senza": len(resto)}


def verifica(codice, nome_dir, id_variante, nome, previsione, criterio, esegui):
    id_v = prossimo_id()
    aggiungi({"id": id_v, "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": id_variante, "idea": codice,
              "direzione": nome_dir, "verifica": nome, "periodo": "costruzione", "previsione": previsione, "criterio_successo": criterio})
    esito = esegui()
    aggiungi({"id": id_v, "tipo": "risultato", "verifica": nome, "verifica_di": id_variante, **esito})
    print(nome, json.dumps(esito, ensure_ascii=False, default=str)[:600], flush=True)
    return esito


def tutte(codice: str, nome_dir: str, id_variante: str, note: dict):
    idea = strategie.IDEE[codice]
    direzione = 1 if nome_dir == "long" else -1
    base, m0, uscita0 = corri(codice, direzione, idea.timeframe)
    riepilogo = {"base": {"n": m0["n_trade"], "pf": m0["profit_factor"], "r": m0["r_medio"]}}

    # 1. robustezza
    def rob():
        griglia = {}
        for k in (1.5, 2.0, 3.0):
            for h in sorted({max(1, uscita0.h_barre // 2), uscita0.h_barre, uscita0.h_barre * 2}):
                _, m, _ = corri(codice, direzione, idea.timeframe, k_atr=k, h_barre=h)
                griglia[f"k{k}_h{h}"] = {"n": m["n_trade"], "pf": m["profit_factor"], "r": m["r_medio"]}
        positivi = sum(1 for v in griglia.values() if isinstance(v["pf"], float) and v["pf"] > 1.0)
        return {"griglia": griglia, "combinazioni_con_pf_sopra_1": positivi, "su": len(griglia)}
    riepilogo["robustezza"] = verifica(codice, nome_dir, id_variante, "robustezza (k_atr e H)", note["robustezza"],
                                       "almeno 7 combinazioni su 9 con profit factor sopra 1 e R medio dello stesso segno", rob)

    # 2. timeframe adiacenti
    def adj():
        out = {}
        for tf in ADIACENTI[idea.timeframe]:
            try:
                _, m, _ = corri(codice, direzione, tf)
                out[tf] = {"n": m["n_trade"], "pf": m["profit_factor"], "r": m["r_medio"]}
            except Exception as e:  # noqa: BLE001
                out[tf] = {"errore": str(e)[:200]}
        return {"adiacenti": out}
    riepilogo["adiacenti"] = verifica(codice, nome_dir, id_variante, "timeframe adiacenti", note["adiacenti"],
                                      "profit factor sopra 1 e R medio dello stesso segno su entrambi gli adiacenti", adj)

    # 4. stabilita' temporale
    riepilogo["stabilita"] = verifica(codice, nome_dir, id_variante, "stabilita' temporale (per anno e senza i 2 mesi migliori)", note["stabilita"],
                                      "R medio positivo in almeno 2 anni su 3 e ancora positivo senza i 2 mesi migliori",
                                      lambda: {"r_per_anno": m0["r_per_anno"], **senza_mesi_migliori(base)})

    # 5. dipendenza dai dati
    def dip():
        ris_opp, m_opp, _ = corri(codice, direzione, idea.timeframe, parametri=comune.parametri_motore(riempimento="target_prima"))
        return {"senza_5pct_migliori": senza_migliori(base), "intrabarra_opposta": {"n": m_opp["n_trade"], "pf": m_opp["profit_factor"], "r": m_opp["r_medio"]}}
    riepilogo["dipendenza"] = verifica(codice, nome_dir, id_variante, "dipendenza dai dati (5 % migliori; regola intra-barra opposta)", note["dipendenza"],
                                       "R medio ancora positivo senza il 5 % migliore; regola opposta cambia il profit factor di meno di 0,05", dip)

    # 6. ritardo
    def rit():
        _, m1, _ = corri(codice, direzione, idea.timeframe, parametri=comune.parametri_motore(ritardo_barre=1))
        return {"ritardo_1_barra": {"n": m1["n_trade"], "pf": m1["profit_factor"], "r": m1["r_medio"]}, "base": {"pf": m0["profit_factor"], "r": m0["r_medio"]}}
    riepilogo["ritardo"] = verifica(codice, nome_dir, id_variante, "ritardo di una barra", note["ritardo"],
                                    "peggiora gradualmente (R medio resta dello stesso segno o cala di meno della meta'), non crolla a zero", rit)

    # 7. liquidazione
    riepilogo["liquidazione"] = verifica(codice, nome_dir, id_variante, "liquidazione", "nessuna violazione: con leva 2 la liquidazione dista circa il 47 %",
                                         "zero violazioni", lambda: {"n_violazioni_liquidazione": m0["n_violazioni_liquidazione"], "n_ridotti": m0["n_ridotti"], "n_stop_oltre_6pct": m0.get("n_stop_oltre_6pct")})

    # 8. costi doppi
    def cd():
        _, m2, _ = corri(codice, direzione, idea.timeframe, parametri=comune.parametri_motore(moltiplicatore_costi=2.0))
        return {"costi_doppi": {"n": m2["n_trade"], "pf": m2["profit_factor"], "r": m2["r_medio"], "rendimento_totale": m2["rendimento_totale"]}}
    riepilogo["costi_doppi"] = verifica(codice, nome_dir, id_variante, "costi doppi", note["costi_doppi"],
                                        "profit factor sopra 1 e R medio positivo anche a costi doppi", cd)
    return riepilogo


if __name__ == "__main__":
    codice, nome_dir, id_variante, file_note = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    note = json.loads(Path(file_note).read_text(encoding="utf-8"))
    r = tutte(codice, nome_dir, id_variante, note)
    (QUI.parent / "risultati" / f"{id_variante}_verifiche.json").write_text(json.dumps(r, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
