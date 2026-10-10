"""Stampa i numeri principali di un dizionario salvato da esegui_esame.py (solo lettura, nessun calcolo nuovo).

Uso: python3 -u riassunto.py FILE.json [FILE.json ...]   (file in campagne/GRUPPO/lavoro/)
"""
import json
import sys

from comune import CARTELLA_GRUPPO


def r(x, n=3):
    return None if x is None else (round(x, n) if isinstance(x, float) else x)


def riassunto(e):
    m = e["metriche"]
    a, b = e.get("baseline_a") or {}, e.get("baseline_b") or {}
    out = {
        "trade": m["trade"], "r_medio": r(m["r_medio"], 4), "profit_factor": r(m.get("profit_factor")),
        "r_medio_per_anno": {k: r(v, 3) for k, v in (m.get("r_medio_per_anno") or {}).items()},
        "r_senza_30_migliori": r(m.get("r_medio_senza_30_migliori"), 4), "drawdown_max": r(m.get("drawdown_max"), 3),
        "a": {"media": r(a.get("media"), 4), "t": r(a.get("t"), 2), "soglia": r(a.get("soglia"), 2),
              "netta": a.get("netta"), "valutabile": a.get("valutabile")},
        "b": {"media": r(b.get("media"), 4), "t": r(b.get("t"), 2), "soglia": r(b.get("soglia"), 2),
              "netta": b.get("netta"), "valutabile": b.get("valutabile"), "p_value": r(b.get("p_value"), 4)},
        "pavimento_sfasate": r((e.get("pavimento_sfasate") or {}).get("pavimento"), 4),
        "percentile_caso": r(e.get("percentile_caso"), 1), "t": r(e.get("t"), 2), "valutabile": e.get("valutabile"),
        "motivi_non_valutabile": e.get("motivi_non_valutabile"),
        "candidato": e.get("candidato"), "validazione": e.get("validazione"),
        "blocco": e.get("blocco"), "n_blocchi": e.get("n_blocchi"), "effetto_grappolo": r(e.get("effetto_grappolo"), 1),
        "monete_con_trade": e.get("monete_con_trade"), "quota_piu_presente": r(e.get("quota_moneta_piu_presente"), 3),
        "uscite_massime_in_un_giorno": e.get("uscite_massime_in_un_giorno"),
        "estremi": e.get("estremi"), "stabilita": e.get("stabilita"),
        "quota_monete_sopra_b_j": e.get("quota_monete_sopra_b_j"),
    }
    return out


if __name__ == "__main__":
    for nome in sys.argv[1:]:
        e = json.loads((CARTELLA_GRUPPO / "lavoro" / nome).read_text())
        if "esami" in e:  # controllo positivo
            print(nome, {k: e[k] for k in ("passa", "condizioni", "t_senza_ritardo", "t_con_ritardo")})
            for k, v in e["esami"].items():
                print(" ", k, json.dumps(riassunto(v), ensure_ascii=False))
        else:
            print(nome, json.dumps(riassunto(e), ensure_ascii=False))
