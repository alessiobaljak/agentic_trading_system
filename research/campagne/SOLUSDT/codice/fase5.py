"""Fase 5: sfida alla conclusione. Per i tre quasi-passaggi della Fase 2 ripete la baseline
delle entrate casuali con un altro seme e piu' simulazioni (500) e aggiunge la versione a un
campione del giudizio «nettamente» (errore standard dal solo bootstrap del candidato, contro la
MEDIA degli R medi casuali). E' una prova INFORMATIVA: il criterio della Fase 2 era registrato
prima dei test e questa prova non puo' promuovere una variante. Serve a dire quanto il giudizio
dipende dal confronto con UNA sola simulazione casuale (lezione di metodo).

Uso: python -m research.campagne.SOLUSDT.codice.fase5 registra NOME... | esegui NOME ID
"""
import sys
from pathlib import Path

import numpy as np

from research.src import motore, statistica
from research.campagne.SOLUSDT.codice import campagna as cp, strategie as st
from research.campagne.SOLUSDT.codice.varianti import VARIANTI, regola

sys.path.insert(0, str(Path(__file__).resolve().parent))
import log  # noqa: E402


def registra(nomi):
    ids = {}
    for line in log.leggi():
        if line.get("tipo") == "registrazione" and line.get("tipo_test") == "variante":
            ids[line["variante"]] = line["id"]
    for nome in nomi:
        v = log.scrivi({"id": f"SOLUSDT-{log.prossimo_numero():03d}", "tipo": "registrazione", "tipo_test": "verifica",
                        "verifica_di": ids[nome], "variante": nome, "verifica": "baseline_casuale_altro_seme", "fase": "5",
                        "cosa": "500 entrate casuali con la stessa uscita, seme 1000; percentile del candidato; 'netta' a un campione (bootstrap del candidato contro la media degli R medi casuali)",
                        "periodo": "costruzione",
                        "criterio_successo": "nessuno: prova informativa che non puo' promuovere la variante (il criterio della Fase 2 era registrato). Previsione: il percentile resta sopra 90 per tutte e tre; la versione a un campione di 'netta' e' vera per I-09 short e I-05 long e falsa per I-01 long (3 trade)"})
        print(v["id"], nome)


def esegui(nome, idv):
    idea, tf, direzione, _, _ = VARIANTI[nome]
    periodo = cp.COSTRUZIONE
    r = regola(nome)
    ris = cp.esegui(st.fabbrica(r, direzione), tf, periodo)
    last, mark, fund, _ = cp.carica(tf, periodo)
    tr = ris.trades
    passo = last[1].ts - last[0].ts
    durata = max(1, round(sum(t.ts_uscita - t.ts_entrata + 1 for t in tr) / len(tr) / passo))
    vietate = [(0, 250)]
    if idea == "I-09":
        r.precalcola(last)
        mask = np.array([r.in_tendenza(i) != direzione for i in range(len(last))])
        i = 0
        while i < len(mask):
            if mask[i]:
                j = i
                while j < len(mask) and mask[j]:
                    j += 1
                vietate.append((i, j)); i = j
            else:
                i += 1
    medie = []
    for k in range(500):
        idx = statistica.entrate_casuali(len(last) - 1, len(tr), durata, 1000 + k, barre_vietate=vietate)
        rr = motore.esegui(last, None, mark, fund, st.fabbrica_casuale(r, direzione, idx)(last), cp.PARAMETRI)
        rs = [t.r for t in rr.trades]
        medie.append(float(np.mean(rs)) if rs else 0.0)
    medie = np.array(medie)
    r_c = cp.r_ordinati(ris)
    blocco = cp.lunghezza_blocco(ris, tf)
    bs = statistica.bootstrap_blocchi(r_c, blocco, 2000, 7)
    media_c = float(np.mean(r_c))
    diff = media_c - float(medie.mean())
    log.scrivi({"id": idv, "tipo": "risultato", "variante": nome, "simulazioni": 500, "seme": 1000,
                "r_medio_candidato": round(media_c, 3), "r_medio_caso_media": round(float(medie.mean()), 3),
                "r_medio_caso_p90": round(float(np.percentile(medie, 90)), 3), "r_medio_caso_p99": round(float(np.percentile(medie, 99)), 3),
                "percentile_candidato": round(float((medie < media_c).mean() * 100), 1),
                "netta_un_campione": {"differenza": round(diff, 3), "errore_standard_candidato": round(float(bs["errore_standard"]), 3),
                                      "margine": round(2 * float(bs["errore_standard"]), 3), "netta": bool(diff > 2 * bs["errore_standard"]),
                                      "blocco": blocco, "n_blocchi": int(bs["n_blocchi"])}})
    print("fatto", nome)


if __name__ == "__main__":
    if sys.argv[1] == "registra":
        registra(sys.argv[2:])
    else:
        esegui(sys.argv[2], sys.argv[3])
