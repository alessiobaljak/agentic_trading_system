"""Stampa i campi delle baseline (a) e (b) di un esame salvato (solo lettura, nessun calcolo nuovo).

Uso: python3 -u guarda_baseline.py FILE.json [CHIAVE_ESAME]   (CHIAVE_ESAME per il controllo positivo: senza_ritardo)
"""
import json
import sys

from comune import CARTELLA_GRUPPO

if __name__ == "__main__":
    e = json.loads((CARTELLA_GRUPPO / "lavoro" / sys.argv[1]).read_text())
    if len(sys.argv) > 2:
        e = e["esami"][sys.argv[2]]
    for nome in ("baseline_a", "baseline_b"):
        b = e[nome]
        print(nome, json.dumps({k: v for k, v in b.items() if not isinstance(v, (dict, list))}, ensure_ascii=False))
    print("pavimento_sfasate", json.dumps({k: v for k, v in e["pavimento_sfasate"].items()
                                          if not isinstance(v, (dict, list))}, ensure_ascii=False))
    errori = sorted((v["a"]["errore_standard"], s, v["a"]["n_trade"], v["a"]["n_blocchi"], v["trade"])
                    for s, v in e["per_moneta"].items() if v.get("a"))
    print("errore della (a) per moneta: min", errori[0], "mediana", errori[len(errori) // 2], "max", errori[-1])
