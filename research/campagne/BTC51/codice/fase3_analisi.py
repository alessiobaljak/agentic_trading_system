"""Fase 3: studio dei trade di varianti GIA' registrate e testate (nessuna variante nuova, nessun
calcolo su specifiche non registrate). Rilancia il motore sulla stessa specifica del log e divide i trade
per anno, motivo d'uscita, larghezza dello stop, peso del funding, ora d'ingresso e giorno della settimana.

Uso: python3 research/campagne/BTC51/codice/fase3_analisi.py V-011 V-012 ...
Esito in risultati/fase3_<id>.json e un riassunto a schermo.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lotto  # noqa: E402
import registro  # noqa: E402
from research.src import catalogo3 as cat  # noqa: E402
from research.src import motore3 as mot  # noqa: E402
from research.src import statistica3 as st  # noqa: E402


def gruppi(trade, chiave):
    g = defaultdict(list)
    for t in trade:
        g[chiave(t)].append(t.r)
    return {str(k): {"n": len(v), "r_medio": round(sum(v) / len(v), 3), "somma": round(sum(v), 2)}
            for k, v in sorted(g.items(), key=lambda x: str(x[0]))}


def main(ids):
    for vid in ids:
        reg = [x for x in registro.voci() if x.get("id") == vid and x.get("tipo") == "registrazione"]
        if not reg:
            raise SystemExit(f"{vid} non registrata")
        spec = reg[0]["specifica"]
        s, a, b = lotto.serie_costruzione(spec["timeframe"])
        c = cat.compila(spec, s)
        tr = mot.esegui(c, mot.Regole(), mot.COSTI_NORMALI, a, b).trade
        larg = sorted(st.larghezza_stop(t) for t in tr)
        quinti = [larg[int(len(larg) * q / 5)] for q in range(1, 5)]

        def fascia(t):
            w = st.larghezza_stop(t)
            return sum(w >= q for q in quinti)

        dt = lambda t: datetime.fromtimestamp(t.ts_ingresso / 1000, tz=timezone.utc)
        out = {
            "id": vid, "trade": len(tr),
            "funding_in_r_medio": round(sum(t.funding / t.rischio_usdt for t in tr) / len(tr), 4),
            "commissioni_in_r_medio": round(sum(t.commissioni / t.rischio_usdt for t in tr) / len(tr), 4),
            "per_anno": gruppi(tr, lambda t: dt(t).year),
            "per_semestre": gruppi(tr, lambda t: f"{dt(t).year}-{1 + (dt(t).month - 1) // 6}"),
            "per_motivo": gruppi(tr, lambda t: t.motivo),
            "per_quinto_larghezza_stop": gruppi(tr, fascia),
            "quinti_larghezza": [round(q, 5) for q in quinti],
            "per_ora_utc": gruppi(tr, lambda t: dt(t).hour // 4 * 4),
            "per_giorno": gruppi(tr, lambda t: "fine_settimana" if dt(t).weekday() >= 5 else "feriale"),
        }
        Path(lotto.RISULTATI / f"fase3_{vid}.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(out))


if __name__ == "__main__":
    main(sys.argv[1:])
