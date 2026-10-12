"""Fase 2: testa sul periodo di costruzione UNA variante gia' registrata e scrive il risultato.

Uso: python research/campagne/ETHUSDT/codice/testa.py <nome in ipotesi.md>

Rifiuta una variante senza registrazione o gia' testata. Il risultato porta i campi
della sezione 6 (metriche, blocco, baseline_a, baseline_b, percentile_caso,
buy_and_hold_per_anno), il confronto con la previsione e un commento. L'esito completo
va anche in data/insample/ETHUSDT/lavoro/<nome>_costruzione.json.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
import idee  # noqa: E402
import registro  # noqa: E402


def commento(esito, reg):
    m = esito["metriche"]
    a, b = esito.get("baseline_a", {}), esito.get("baseline_b", {})
    parti = []
    if esito.get("candidato"):
        parti.append("CANDIDATO: batte nettamente la (a) e la (b) con R medio positivo")
    else:
        if not esito.get("valutabile"):
            parti.append("non valutabile")
        parti.append(f"contro la (a): t {a.get('t')}, {'netta' if a.get('netta') else 'non netta'}")
        parti.append(f"contro la (b): t {b.get('t')}, {'netta' if b.get('netta') else 'non netta'}")
        if m["r_medio"] <= 0:
            parti.append("R medio dopo i costi non positivo")
    if m["trade"] != reg["trade_stimati"]:
        parti.append(f"ATTENZIONE: trade del test {m['trade']} diversi da quelli stimati {reg['trade_stimati']}")
    return "; ".join(parti)


def main() -> None:
    nome = sys.argv[1]
    voci = registro.voci()
    reg = [v for v in voci if v.get("variante_ipotesi") == nome and v["tipo"] == "registrazione"]
    if len(reg) != 1:
        raise SystemExit(f"{nome}: serve esattamente una registrazione, trovate {len(reg)}")
    reg = reg[0]
    if any(v["id"] == reg["id"] and v["tipo"] == "risultato" for v in voci):
        raise SystemExit(f"{nome} ({reg['id']}) ha gia' un risultato")
    V, kw, tf = idee.VARIANTI[nome]
    esito = comune.valuta(V, kw, tf)
    uscita = comune.LAVORO / f"{nome}_costruzione.json"
    uscita.parent.mkdir(parents=True, exist_ok=True)
    uscita.write_text(json.dumps(registro.pulisci({"id": reg["id"], "nome": nome, "esito": esito}), indent=1,
                                 ensure_ascii=False) + "\n", encoding="utf-8")
    prev = reg["previsione_numeri"]
    r = esito["metriche"]["r_medio"]
    netta_b = bool(esito.get("baseline_b", {}).get("netta", False))
    corretta = bool(prev["r_medio_min"] <= r <= prev["r_medio_max"] and netta_b == prev["batte_nettamente_b"])
    voce = {
        "id": reg["id"],
        "tipo": "risultato",
        "variante_ipotesi": nome,
        "metriche": esito["metriche"],
        "blocco": esito.get("blocco"),
        "baseline_a": esito.get("baseline_a"),
        "baseline_b": esito.get("baseline_b"),
        "percentile_caso": esito.get("percentile_caso"),
        "buy_and_hold_per_anno": esito.get("buy_and_hold_per_anno"),
        "valutabile": esito.get("valutabile"),
        "candidato": esito.get("candidato"),
        "barre": esito.get("barre"),
        "previsione_corretta": corretta,
        "commento": commento(esito, reg),
    }
    registro.aggiungi(voce)
    b = esito.get("baseline_b", {})
    print(reg["id"], nome, "R medio", round(r, 4), "trade", esito["metriche"]["trade"],
          "t(a)", esito.get("baseline_a", {}).get("t"), "t(b)", b.get("t"), "candidato", esito.get("candidato"))


if __name__ == "__main__":
    main()
