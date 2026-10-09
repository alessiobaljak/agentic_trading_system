"""Test di Fase 2 di una variante GIA' REGISTRATA nel log: scrive risultati/<chiave>.json.

Controlla che nel log ci sia la registrazione con lo stesso id e che il numero di trade del
test coincida con ``trade_stimati``. Uso: python prova.py V-01 [V-02 ...]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
from log_campagna import ids_esistenti  # noqa: E402
from varianti import VARIANTI  # noqa: E402

CARTELLA_RIS = comune.CARTELLA / "risultati"
CARTELLA_RIS.mkdir(exist_ok=True)


def registrazione(id_):
    for v in ids_esistenti():
        if v.get("id") == id_ and v.get("tipo") == "registrazione":
            return v
    return None


def main():
    for chiave in sys.argv[1:]:
        var = VARIANTI[chiave]
        reg = registrazione(var.id)
        if reg is None:
            raise SystemExit(f"{var.id}: manca la registrazione nel log, il test non parte")
        ris = comune.valuta(var, "costruzione")
        if ris["metriche"]["trade"] != reg["trade_stimati"]:
            ris["avviso"] = f"trade del test {ris['metriche']['trade']} diversi da trade_stimati {reg['trade_stimati']}"
        voce = {"id": var.id, "tipo": "risultato"}
        voce.update(comune.per_log(ris))
        (CARTELLA_RIS / f"{chiave}.json").write_text(json.dumps(voce, ensure_ascii=False, indent=1), encoding="utf-8")
        m = ris["metriche"]
        a, b = ris.get("baseline_a", {}), ris.get("baseline_b", {})
        print(chiave, "trade", m["trade"], "r_medio", m["r_medio"], "pf", m["profit_factor"],
              "| a: media", a.get("media"), "t", a.get("t"), "netta", a.get("netta"),
              "| b: media", b.get("media"), "t", b.get("t"), "netta", b.get("netta"),
              "| percentile", ris.get("percentile_caso"), "| candidato", ris.get("candidato"), flush=True)


if __name__ == "__main__":
    main()
