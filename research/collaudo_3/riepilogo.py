"""Riepilogo del collaudo del protocollo 3: legge gli esiti grezzi delle prove A e B
(``research/collaudo_3/esiti/*.jsonl``) e applica le soglie della sezione 13bis e di ``regole.md``.

Uso: ``python3 research/collaudo_3/riepilogo.py`` (stampa un JSON con i numeri e «passa»/«non passa»).
Non ricalcola niente: solo conteggi sugli esiti gia' scritti.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

ESITI = Path(__file__).resolve().parent / "esiti"


def _righe(nome: str):
    p = ESITI / nome
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def prova_a() -> dict:
    righe = [r for r in _righe("prova_a.jsonl") if "impossibile" not in r]
    impossibili = [r for r in _righe("prova_a.jsonl") if "impossibile" in r]
    estratte = _righe("prova_a_estrazioni.jsonl")
    n = len(righe)
    superano = [r for r in righe if r["supera_fase2"]]
    p = sorted(r["p_value"] for r in righe if r["p_value"] is not None)
    sotto_010 = sum(1 for x in p if x < 0.10)
    decimi = [sum(1 for x in p if k / 10 <= x < (k + 1) / 10 or (k == 9 and x == 1.0)) for k in range(10)]
    r_medi = [r["r_medio"] for r in righe]
    casuali = [r["media_casuali"] for r in righe if r.get("media_casuali") is not None]
    per_tf = {}
    for r in righe:
        per_tf[r["variante"]["timeframe"]] = per_tf.get(r["variante"]["timeframe"], 0) + 1
    passa = n == 100 and len(superano) <= 5 and sotto_010 <= 15
    return {
        "varianti_con_fase2": n, "estratte_in_tutto": len(estratte),
        "scartate_sotto_150_trade": sum(1 for e in estratte if not e["tenuta"]),
        "entrate_casuali_impossibili": len(impossibili),
        "superano_fase2": len(superano), "soglia_superano": 5,
        "p_sotto_0_10": sotto_010, "soglia_p_sotto_0_10": 15,
        "p_value_per_decimi": decimi,
        "p_minimo": p[0] if p else None,
        "r_medio_delle_varianti": sum(r_medi) / n if n else None,
        "r_medio_delle_entrate_casuali": sum(casuali) / len(casuali) if casuali else None,
        "varianti_per_timeframe": dict(sorted(per_tf.items())),
        "che_superano": [{"numero": r["numero"], "variante": r["variante"], "trade": r["trade"],
                          "r_medio": r["r_medio"], "p_value": r["p_value"], "fase4": r.get("fase4")}
                         for r in superano],
        "passa": passa,
    }


def prova_b() -> dict:
    righe = _righe("prova_b.jsonl")
    out = {"regole": {}}
    tutte_passano = True
    for nome in ("B1", "B2", "B3"):
        rr = [r for r in righe if r["regola"] == nome]
        zero = [r for r in rr if r["ampiezza"] == 0.0]
        con = [r for r in rr if r["ampiezza"] > 0]
        alla_soglia = [r for r in con if r["r_medio"] >= 0.35]
        superano_soglia = sum(1 for r in alla_soglia if r["supera_fase2"])
        quota = superano_soglia / len(alla_soglia) if alla_soglia else None
        a06 = sum(1 for r in rr if r["ampiezza"] == 0.6 and r["r_medio"] >= 0.35)
        riserva = any(r["ampiezza"] == 0.9 for r in rr)
        zona = [r for r in con if 0.2 <= r["r_medio"] < 0.35]
        attese_zona = sum(1 for r in zona if r["r_medio"] * math.sqrt(max(r["trade"], 1)) / 1.2 >= 2)
        casuali = {}
        for a in sorted({r["ampiezza"] for r in rr}):
            v = [r["media_casuali"] for r in rr if r["ampiezza"] == a and r["media_casuali"] is not None]
            casuali[str(a)] = sum(v) / len(v) if v else None
        salita = None
        if casuali.get("0.0") is not None:
            salite = [casuali[k] - casuali["0.0"] for k in casuali if k != "0.0" and casuali[k] is not None]
            salita = sum(salite) / len(salite) if salite else None
        r_medi = {}
        for a in sorted({r["ampiezza"] for r in rr}):
            v = [r["r_medio"] for r in rr if r["ampiezza"] == a]
            r_medi[str(a)] = sum(v) / len(v) if v else None
        segnali_ok = all(r["segnali_uguali"] for r in rr)
        passa = (len(zero) == 30 and sum(1 for r in zero if r["supera_fase2"]) <= 3
                 and quota is not None and quota >= 0.80 and segnali_ok)
        tutte_passano = tutte_passano and passa
        out["regole"][nome] = {
            "prove": len(rr), "superano_senza_vantaggio": sum(1 for r in zero if r["supera_fase2"]),
            "soglia_senza_vantaggio": 3,
            "prove_con_vantaggio_ad_almeno_0_35_r": len(alla_soglia), "di_queste_superano": superano_soglia,
            "quota": quota, "soglia_quota": 0.80,
            "serie_a_0_35_r_con_p_0_6": a06, "riserva_p_0_9_fatta": riserva,
            "r_medio_per_ampiezza": r_medi,
            "zona_0_2_0_35": {"prove": len(zona), "superano": sum(1 for r in zona if r["supera_fase2"]),
                              "attese_con_la_5_2": attese_zona},
            "esecuzione_media_limit": (sum(r["esecuzione"] for r in rr if r.get("esecuzione") is not None)
                                       / max(1, sum(1 for r in rr if r.get("esecuzione") is not None)))
            if nome == "B3" else None,
            "r_medio_entrate_casuali_per_ampiezza": casuali,
            "salita_media_entrate_casuali": salita,
            "stop_salita_oltre_0_05": salita is not None and salita > 0.05,
            "segnali_uguali_in_tutte": segnali_ok,
            "passa": passa,
        }
    out["passa"] = tutte_passano
    return out


def main() -> None:
    print(json.dumps({"prova_a": prova_a(), "prova_b": prova_b()}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
