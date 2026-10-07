"""Verifiche della Fase 4 su una variante sopravvissuta alla Fase 2 (sezione 9, Passo 3).

Uso: python verifiche.py <ID> [--sim N]
Per ogni verifica: registrazione nel log (tipo_test 'verifica', verifica_di = ID)
con la previsione, poi esecuzione in COSTRUZIONE, poi risultato. Le verifiche:
  1. robustezza: parametri vicini (dichiarati in VICINI[ID]);
  2. timeframe adiacenti (dichiarati in ADIACENTI[ID]);
  4. stabilita' per anno: gia' nelle metriche, qui si riassume;
  5. dipendenza dai dati: R medio senza i 5 trade migliori; regola intra-barra opposta;
  6. ritardo di una barra;
  7. liquidazione: conteggio delle violazioni (nelle metriche);
  8. costi doppi.
Niente qui cambia la variante: i numeri servono a scartarla o a tenerla.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import dati_btc as d  # noqa: E402
import strumenti as s  # noqa: E402
import varianti as V  # noqa: E402

# --- verifiche dichiarate per variante ------------------------------------------------
# ogni voce: (nome, tf, costruttore_entra(serie), costruttore_uscita(serie), parametri_motore | None)

def _v12_entra(serie):
    return V._entra_funding_negativo(serie)

def _v08_entra(q):
    return lambda se: V._entra_funding(se, "long", q=q)


VICINI = {
    "BTCUSDT-V08-long": [
        ("stop 1,5 ATR", "8h", _v08_entra(90.0), lambda se: {"stop_atr": 1.5, "atr_n": 14, "max_barre": 3}, None),
        ("stop 3 ATR", "8h", _v08_entra(90.0), lambda se: {"stop_atr": 3.0, "atr_n": 14, "max_barre": 3}, None),
        ("uscita a 2 barre (16 ore)", "8h", _v08_entra(90.0), lambda se: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 2}, None),
        ("uscita a 4 barre (32 ore)", "8h", _v08_entra(90.0), lambda se: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 4}, None),
        ("uscita a 6 barre (48 ore)", "8h", _v08_entra(90.0), lambda se: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 6}, None),
        ("percentile 85 (soglia piu' larga)", "8h", _v08_entra(85.0), lambda se: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 3}, None),
        ("percentile 95 (soglia piu' stretta)", "8h", _v08_entra(95.0), lambda se: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 3}, None),
    ],
    "BTCUSDT-V12-long": [
        ("stop 1,5 ATR", "8h", _v12_entra, lambda se: {"stop_atr": 1.5, "atr_n": 14, "max_barre": 3}, None),
        ("stop 3 ATR", "8h", _v12_entra, lambda se: {"stop_atr": 3.0, "atr_n": 14, "max_barre": 3}, None),
        ("uscita a 2 barre (16 ore)", "8h", _v12_entra, lambda se: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 2}, None),
        ("uscita a 4 barre (32 ore)", "8h", _v12_entra, lambda se: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 4}, None),
        ("uscita a 6 barre (48 ore)", "8h", _v12_entra, lambda se: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 6}, None),
        ("soglia funding < -0,005% (piu' stretta)", "8h", lambda se: (lambda f: (lambda i: "long" if (np.isfinite(f[i]) and f[i] < -0.00005) else None))(se.funding_ultimo()), lambda se: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 3}, None),
    ],
}
ADIACENTI = {
    "BTCUSDT-V08-long": [
        ("timeframe 4h, stessa regola (270 settlement = 540 barre), uscita a 6 barre (24 ore)", "4h", lambda se: V._entra_funding(se, "long", q=90.0, n=540), lambda se: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 6}, None),
        ("timeframe 12h, stessa regola (270 settlement = 180 barre), uscita a 2 barre (24 ore)", "12h", lambda se: V._entra_funding(se, "long", q=90.0, n=180), lambda se: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 2}, None),
    ],
    "BTCUSDT-V12-long": [
        ("timeframe 4h, stessa regola, uscita a 6 barre (24 ore)", "4h", _v12_entra, lambda se: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 6}, None),
        ("timeframe 12h, stessa regola, uscita a 2 barre (24 ore)", "12h", _v12_entra, lambda se: {"stop_atr": 2.0, "atr_n": 14, "max_barre": 2}, None),
    ],
}


def esegui_verifica(id_, nome, tf, entra_b, uscita_b, parametri, n_sim, previsione, con_baseline=True, direzione_di=None):
    serie = s.Serie(tf)
    entra = entra_b(serie)
    uscita = uscita_b(serie)
    s.registra({"id": f"{id_}/verifica/{nome}", "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": id_,
                "verifica": nome, "timeframe": tf, "periodo": "costruzione", "previsione": previsione,
                "parametri_motore": ({k: getattr(parametri, k) for k in ("moltiplicatore_costi", "ritardo_barre", "riempimento_intrabarra")} if parametri else "standard")})
    out, ris = s.esamina(serie, entra, uscita, d.COSTRUZIONE, parametri=parametri, n_sim_caso=n_sim, con_baseline=con_baseline, direzione_di=direzione_di)
    m = out["metriche"]
    rs = sorted(t.r for t in ris.trades)
    extra = {"r_medio_senza_5_migliori": round(float(np.mean(rs[:-5])), 4) if len(rs) > 5 else None}
    b = out.get("baseline_b_casuale") or {}
    voce = {"id": f"{id_}/verifica/{nome}", "tipo": "risultato", "verifica_di": id_, "verifica": nome, "periodo": "costruzione",
            "metriche": {k: m[k] for k in ("n_trade", "profit_factor", "win_rate", "r_medio", "r_mediano", "rendimento_totale", "drawdown_max", "r_medio_per_anno", "n_trade_per_anno", "esiti", "n_violazioni_liquidazione", "n_ridotti", "stop_pct")},
            **extra, "baseline_b_casuale": ({k: b[k] for k in ("r_medio_caso_mediano", "r_medio_caso_p90", "percentile_del_candidato")} | {"netta": b["confronto_con_sim_mediana"].get("netta")} if b else None)}
    s.registra(voce)
    s.salva_risultato(f"{id_}.verifica.{nome.replace(' ', '_').replace('/', '-').replace(',', '')}", {**out, **extra})
    print(nome, "|", json.dumps({"n": m["n_trade"], "pf": m["profit_factor"], "r": m["r_medio"], "r_med": m["r_mediano"], "anni": m["r_medio_per_anno"], "senza5": extra["r_medio_senza_5_migliori"], "pct_caso": b.get("percentile_del_candidato"), "netta": (b.get("confronto_con_sim_mediana") or {}).get("netta"), "viol": m["n_violazioni_liquidazione"]}, default=str))
    return out


def main(argv):
    id_ = argv[1]
    n_sim = int(argv[argv.index("--sim") + 1]) if "--sim" in argv else 50
    v = V.VARIANTI[id_]
    tf = v["tf"]
    entra_b, uscita_b = v["entra"], v["uscita"]
    dd = v["direzione_di"]
    # 6. ritardo di una barra
    esegui_verifica(id_, "ritardo di 1 barra", tf, entra_b, uscita_b, d.parametri(ritardo_barre=1), n_sim,
                    "peggiora gradualmente (R medio piu' basso ma non crolla a zero o negativo): un crollo indicherebbe lookahead", direzione_di=dd(s.Serie(tf)))
    # 8. costi doppi
    esegui_verifica(id_, "costi doppi", tf, entra_b, uscita_b, d.parametri(moltiplicatore_costi=2.0), n_sim,
                    "R medio scende di circa 0,03-0,05 (i costi di andata e ritorno valgono ~0,04 R con stop a 2 ATR); resta positivo se il vantaggio e' vero", direzione_di=dd(s.Serie(tf)))
    # 5. regola intra-barra opposta
    esegui_verifica(id_, "regola intra-barra opposta (target prima)", tf, entra_b, uscita_b, d.parametri(intrabarra="target_prima"), n_sim,
                    "nessuna differenza (la variante non ha target)", con_baseline=False)
    # 1. robustezza
    for nome, tf2, e2, u2, p2 in VICINI.get(id_, []):
        esegui_verifica(id_, f"robustezza: {nome}", tf2, e2, u2, p2, n_sim, "R medio dello stesso segno e ordine di grandezza (area stabile, non picco)", direzione_di=dd(s.Serie(tf2)))
    # 2. timeframe adiacenti
    for nome, tf2, e2, u2, p2 in ADIACENTI.get(id_, []):
        esegui_verifica(id_, f"adiacente: {nome}", tf2, e2, u2, p2, n_sim, "R medio positivo anche sul timeframe adiacente (serve a verificare, non a scegliere)", direzione_di=dd(s.Serie(tf2)))


if __name__ == "__main__":
    main(sys.argv)
