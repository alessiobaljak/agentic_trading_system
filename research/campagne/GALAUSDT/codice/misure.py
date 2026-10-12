"""Misure di processo della consegna, dal log (date dall'orologio della macchina)."""

import json
from datetime import datetime

from research.campagne.GALAUSDT.codice import registro


def ts(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


def main():
    voci = [json.loads(r) for r in registro.LOG.read_text(encoding="utf-8").splitlines() if r.strip()]
    prima, ultima = ts(voci[0]["data"]), ts(voci[-1]["data"])
    pause = sum((ts(v["pausa_a"]) - ts(v["pausa_da"])).total_seconds() for v in voci if "pausa_da" in v)
    per_idea = {}
    reg = {v["id"]: v for v in voci if v.get("tipo") in ("registrazione", "scarto") and v.get("tipo_test") == "variante"}
    for v in voci:
        if v["id"] in reg and v.get("tipo") in ("registrazione", "risultato", "scarto"):
            idea = reg[v["id"]]["idea"]
            per_idea.setdefault(idea, []).append(ts(v["data"]))
    out = {
        "prima_voce": voci[0]["data"], "ultima_voce": voci[-1]["data"],
        "minuti_totali": (ultima - prima).total_seconds() / 60, "minuti_pause": pause / 60,
        "minuti_senza_pause": ((ultima - prima).total_seconds() - pause) / 60,
        "minuti_per_idea": {k: round((max(d) - min(d)).total_seconds() / 60, 1) for k, d in sorted(per_idea.items())},
    }
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
