"""Esegue in SERIE una lista di varianti: registrazione nel log (prima), test, risultato (dopo).

  python lotto.py <primo_variante_n> <ID> [<ID> ...]

Per ogni id: scrive la registrazione (schede.principale), esegue comune.valuta sul periodo di
costruzione, scrive la voce `risultato` con i campi della sezione 6. ``previsione_corretta`` si
legge confrontando l'R medio con l'intervallo «R medio fra a e b» della previsione registrata.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
import registro  # noqa: E402
import schede  # noqa: E402
from varianti import VARIANTI  # noqa: E402


def intervallo_previsto(testo):
    m = re.search(r"R medio fra ([-+]?\d+(?:,\d+)?) e ([-+]?\d+(?:,\d+)?)", testo)
    if not m:
        return None
    return float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", "."))


def risultato(vid, ris):
    met = ris.get("metriche", {})
    prev = schede.S[vid][4] if vid in schede.S else schede.EXTRA_PREV[vid]
    iv = intervallo_previsto(prev)
    r = met.get("r_medio")
    corretta = None if (iv is None or r is None) else bool(iv[0] <= r <= iv[1])
    a, b = ris.get("baseline_a", {}), ris.get("baseline_b", {})
    commento = (f"R medio {r} ({'dentro' if corretta else 'fuori da'} l'intervallo previsto {iv}); "
                f"t contro la (a) {a.get('t')} (netta {a.get('netta')}), contro la (b) {b.get('t')} "
                f"(netta {b.get('netta')}); candidato: {ris.get('candidato')}.")
    voce = {"id": vid, "tipo": "risultato", "metriche": met, "blocco": ris.get("blocco"),
            "baseline_a": a, "baseline_b": b, "percentile_caso": ris.get("percentile_caso"),
            "buy_and_hold_per_anno": ris.get("buy_and_hold_per_anno"), "candidato": ris.get("candidato"),
            "previsione_corretta": corretta, "commento": commento}
    return voce


if __name__ == "__main__":
    n = int(sys.argv[1])
    for vid in sys.argv[2:]:
        schede.principale("registra", vid, n)
        tf, costr = VARIANTI[vid][0], VARIANTI[vid][1]
        ris = comune.valuta(tf, costr, "costruzione")
        voce = risultato(vid, ris)
        registro.aggiungi(voce)
        (schede.BOZZE / f"ris_{vid}.json").write_text(json.dumps(comune.pulito(ris), ensure_ascii=False, default=str))
        print(vid, "n", n, "trade", voce["metriche"].get("trade"), "R", voce["metriche"].get("r_medio"),
              "t_a", voce["baseline_a"].get("t"), "t_b", voce["baseline_b"].get("t"), "cand", voce["candidato"], flush=True)
        n += 1
