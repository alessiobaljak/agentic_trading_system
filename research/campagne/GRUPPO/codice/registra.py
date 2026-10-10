"""Aggiunge al log le voci di una variante, con i numeri presi dai file salvati da esegui_esame.py (mai a mano).

Uso:
  python3 -u registra.py registrazione SPEC.json DATA   (SPEC in lavoro/: campi scritti prima del test; DATA da date -u)
  python3 -u registra.py scarto SPEC.json DATA
  python3 -u registra.py risultato SPEC.json DATA       (SPEC: id, esame (file in lavoro/), previsione_corretta, commento)
  python3 -u registra.py nota SPEC.json DATA            (SPEC: i campi della nota, senza id)
Per registrazione e scarto SPEC ha «conta»: il file di conta_trade_di_gruppo in lavoro/, da cui si copiano
trade_stimati, trade_stimati_per_moneta, monete_con_trade, quota_moneta_piu_presente, moneta_piu_presente e la stima
di validazione; e «modulo»: il file in codice/, di cui si scrive lo SHA-256.
"""
import hashlib
import json
import sys

from comune import CARTELLA_GRUPPO, aggiungi_al_log, prossimo_id

LAVORO = CARTELLA_GRUPPO / "lavoro"
CODICE = CARTELLA_GRUPPO / "codice"


def main():
    tipo, spec_file, data = sys.argv[1], LAVORO / sys.argv[2], sys.argv[3]
    spec = json.loads(spec_file.read_text())
    if tipo in ("registrazione", "scarto"):
        conta = json.loads((LAVORO / spec.pop("conta")).read_text())
        modulo = spec["modulo"]
        voce = {"id": spec.pop("id", None) or prossimo_id(), "tipo": tipo, "data": data}
        voce.update(spec)
        voce["modulo_sha256"] = hashlib.sha256((CODICE / modulo).read_bytes()).hexdigest()
        voce["parametri_conta"] = conta["parametri"]
        if voce["parametri_conta"] != spec["parametri"]:
            raise ValueError("i parametri della conta non sono quelli registrati")
        for chiave in ("trade_stimati", "trade_stimati_per_moneta", "monete_con_trade", "quota_moneta_piu_presente",
                       "moneta_piu_presente", "stima_trade_validazione", "esito", "motivi"):
            voce[chiave] = conta[chiave]
        voce["esito_stima"] = voce.pop("esito")
        del voce["parametri_conta"]
        if tipo == "registrazione" and voce["esito_stima"] != "registrabile":
            raise ValueError("la stima dice scarto: si registra come scarto")
        if tipo == "scarto" and voce["esito_stima"] != "scarto":
            raise ValueError("la stima dice registrabile")
    elif tipo == "risultato":
        esame = json.loads((LAVORO / spec.pop("esame")).read_text())
        voce = {"id": spec.pop("id"), "tipo": "risultato", "data": data}
        voce.update(esame)
        voce.update(spec)
    elif tipo == "nota":
        voce = {"id": prossimo_id(), "tipo": "nota", "data": data}
        voce.update(spec)
    else:
        raise ValueError(tipo)
    aggiungi_al_log(voce)
    print("scritta", voce["id"], voce["tipo"])


if __name__ == "__main__":
    main()
