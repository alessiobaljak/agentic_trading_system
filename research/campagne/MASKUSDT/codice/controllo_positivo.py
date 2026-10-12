"""Controllo positivo degli strumenti (lezioni/metodo.md): nota prima, test, nota dopo. Nessun budget."""
import json
import sys
from pathlib import Path

CODICE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODICE))

import quadro  # noqa: E402
import registro  # noqa: E402
from campagna import _scrivi_esito  # noqa: E402
from varianti_base import ControlloPositivo  # noqa: E402


def main():
    registro.aggiungi({
        "id": "MASKUSDT-CP-1", "tipo": "nota", "controllo_positivo": "prima",
        "testo": ("Controllo positivo degli strumenti, prima del test. Strategia con lookahead DICHIARATO: a 1 ora "
                  "entra long all'apertura della barra i+1 se la barra i+1 chiude sopra la sua apertura (legge di "
                  "proposito la barra successiva), stop 2 ATR, target 2 volte lo stop, uscita dopo 1 barra. Stesse "
                  "baseline delle varianti vere. Atteso: batte nettamente la (a) e la (b) senza ritardo; con il "
                  "ritardo di una barra il t contro la (b) ricalcolata crolla sotto la meta' (vicino a zero). "
                  "Se non succede, nessun risultato della campagna vale.")})
    var = ControlloPositivo()
    senza = quadro.valuta(var)
    con = quadro.valuta(var, ritardo_barre=1)
    _scrivi_esito("controllo_positivo_senza_ritardo", senza)
    _scrivi_esito("controllo_positivo_ritardo_1", con)

    def breve(e):
        return {"trade": e["metriche"]["trade"], "r_medio": e["metriche"]["r_medio"],
                "t_a": e.get("baseline_a", {}).get("t"), "netta_a": e.get("baseline_a", {}).get("netta"),
                "t_b": e["baseline_b"].get("t"), "netta_b": e["baseline_b"].get("netta"),
                "media_b": e["baseline_b"].get("media")}
    s, c = breve(senza), breve(con)
    passato = bool(s["netta_a"] and s["netta_b"] and (c["t_b"] is not None) and
                   float(c["t_b"]) < 0.5 * float(s["t_b"]))
    registro.aggiungi({"id": "MASKUSDT-CP-2", "tipo": "nota", "controllo_positivo": "dopo",
                       "senza_ritardo": s, "ritardo_1": c, "superato": passato,
                       "testo": "Esito del controllo positivo degli strumenti."})
    print(json.dumps({"senza": s, "con": c, "superato": passato}, default=str))


if __name__ == "__main__":
    main()
