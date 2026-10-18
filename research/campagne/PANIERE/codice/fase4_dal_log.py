"""Fase 4: stabilità, estremi, liquidazione e quota della moneta più presente dei candidati, letti dal loro risultato nel log.

Sono già calcolati da gruppo.esame_di_gruppo (chiavi «stabilita», «estremi», «liquidazione»): qui si leggono soltanto.
Uso: fase4_dal_log.py <id> [...]
"""

import json
import sys
from pathlib import Path

CODICE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODICE))

import registro  # noqa: E402


def main():
    esito = {}
    for id_c in sys.argv[1:]:
        r = [v for v in registro.voci() if v["id"] == id_c and v["tipo"] == "risultato"][-1]
        esito[id_c] = {k: r.get(k) for k in ("stabilita", "estremi", "liquidazione", "quota_moneta_piu_presente",
                                             "moneta_piu_presente", "quota_monete_sopra_b_j", "posizioni_aperte_insieme",
                                             "uscite_massime_in_un_giorno", "effetto_grappolo")}
    (CODICE.parent / "lavoro" / "fase4_dal_log.json").write_text(json.dumps(esito, indent=1, ensure_ascii=False) + "\n",
                                                                 encoding="utf-8")
    print(json.dumps(esito, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
