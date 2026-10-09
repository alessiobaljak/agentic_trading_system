"""Fase 4: le verifiche del candidato MATICUSDT-025 sui dati di costruzione.

Uso: python research/campagne/MATICUSDT/codice/verifiche_025.py <gruppo>
gruppi: identita, robustezza, timeframe, ritardo, costi_doppi, intrabarra
Ogni gruppo scrive esiti/verifica_025_<gruppo>.json. Nessuna verifica cambia le regole.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candidato_025 as cand  # noqa: E402
import quadro  # noqa: E402

ESITI = Path(__file__).resolve().parents[1] / "esiti"


def sintesi(r):
    m = r["metriche"]
    b = r.get("baseline_b", {})
    a = r.get("baseline_a", {})
    return {"trade": m["trade"], "r_medio": m["r_medio"], "r_medio_senza_3_migliori": m["r_medio_senza_3_migliori"],
            "r_medio_per_anno": m["r_medio_per_anno"], "violazioni_liquidazione": m["violazioni_liquidazione"],
            "trade_ridotti_tetto_leva": m["trade_ridotti_tetto_leva"], "profit_factor": m["profit_factor"],
            "drawdown_max": m["drawdown_max"],
            "b_media": b.get("media"), "t_b": b.get("t"), "soglia_b": b.get("soglia"), "netta_b": b.get("netta"),
            "valutabile_b": b.get("valutabile"), "t_a": a.get("t"), "netta_a": a.get("netta"),
            "percentile_caso": r.get("percentile_caso")}


gruppo = sys.argv[1]
out = {}
if gruppo == "identita":
    out["predefiniti"] = sintesi(quadro.valuta(cand.fabbrica(), "1h"))
elif gruppo == "robustezza":
    casi = {"finestra": (5, 7), "k_sd": (1.6, 2.4), "media": (576, 864), "btc": (19, 29), "tenuta": (10, 14),
            "atr_n": (11, 17), "atr_mult": (1.6, 2.4), "tetto": (0.048, 0.072)}
    for nome, valori in casi.items():
        for v in valori:
            f = cand.fabbrica(**{nome: v})
            c = quadro.conta(f, "1h")
            caso = {"trade_stimati": c["trade"]}
            if c["trade"] >= quadro.TRADE_MINIMI_COSTRUZIONE:
                caso.update(sintesi(quadro.valuta(f, "1h", con_baseline_a=False)))
            out[f"{nome}={v}"] = caso
elif gruppo == "timeframe":
    for tf, conv in (("30m", {"finestra": 12, "media": 1440, "btc": 48, "tenuta": 24, "atr_n": 28}),
                     ("2h", {"finestra": 3, "media": 360, "btc": 12, "tenuta": 6, "atr_n": 7})):
        f = cand.fabbrica(**conv)
        c = quadro.conta(f, tf)
        caso = {"parametri": conv, "trade_stimati": c["trade"]}
        if c["trade"] >= quadro.TRADE_MINIMI_COSTRUZIONE:
            caso.update(sintesi(quadro.valuta(f, tf, con_baseline_a=False)))
        out[tf] = caso
elif gruppo == "ritardo":
    out["ritardo_1"] = sintesi(quadro.valuta(cand.fabbrica(), "1h", ritardo=1, con_baseline_a=False))
elif gruppo == "costi_doppi":
    out["costi_doppi"] = sintesi(quadro.valuta(cand.fabbrica(), "1h", moltiplicatore_costi=2.0, con_baseline_a=False))
elif gruppo == "intrabarra":
    out["target_prima"] = sintesi(quadro.valuta(cand.fabbrica(), "1h", intrabarra="target_prima", con_baseline_a=False))
else:
    raise SystemExit("gruppo sconosciuto")
(ESITI / f"verifica_025_{gruppo}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps(out, ensure_ascii=False))
