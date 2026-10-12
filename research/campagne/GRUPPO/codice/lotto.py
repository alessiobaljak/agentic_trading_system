"""Varianti in serie: per ognuna conta, poi registrazione (o scarto) nel log PRIMA del test, poi l'esame di costruzione.

Uso: python3 -u lotto.py LOTTO.json   (file in lavoro/: lista di spec come quelle di registra.py, ognuna con
«p_file» = file dei parametri in lavoro/; «parametri» si legge da p_file). In serie: gli id del log sono
progressivi (lezioni/metodo.md). I risultati si scrivono dopo, a parte, con registra.py risultato.
"""
import json
import sys
import time
from datetime import datetime, timezone

from comune import CARTELLA_GRUPPO, aggiungi_al_log, prossimo_id

from research.src import gruppo

LAVORO = CARTELLA_GRUPPO / "lavoro"
CODICE = CARTELLA_GRUPPO / "codice"


def adesso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    import hashlib
    lotto = json.loads((LAVORO / sys.argv[1]).read_text())
    for spec in lotto:
        p = json.loads((LAVORO / spec.pop("p_file")).read_text())
        spec["parametri"] = p
        modulo = CODICE / spec["modulo"]
        conta = gruppo.conta_trade_di_gruppo(modulo, p, spec["timeframe"], processi=4)
        nome = spec["variante_nome"]
        (LAVORO / f"{nome}_conta.json").write_text(json.dumps(conta, ensure_ascii=False, indent=1, sort_keys=True))
        tipo = "scarto" if conta["esito"] == "scarto" else "registrazione"
        voce = {"id": prossimo_id(), "tipo": tipo, "data": adesso()}
        voce.update(spec)
        if voce.get("famiglia") is None and voce.get("ritocco_di") is None:
            voce["famiglia"] = voce["id"]
        voce["modulo_sha256"] = hashlib.sha256(modulo.read_bytes()).hexdigest()
        for k in ("trade_stimati", "trade_stimati_per_moneta", "monete_con_trade", "quota_moneta_piu_presente",
                  "moneta_piu_presente", "stima_trade_validazione", "motivi"):
            voce[k] = conta[k]
        voce["esito_stima"] = conta["esito"]
        if tipo == "registrazione":
            precedenti = [json.loads(x) for x in (CARTELLA_GRUPPO / "log.jsonl").read_text().splitlines() if x.strip()]
            voce["variante_n"] = 1 + sum(1 for x in precedenti if x.get("tipo") == "registrazione"
                                         and x.get("tipo_test") == "variante")
        else:
            voce["motivo_scarto"] = "; ".join(conta["motivi"])
        aggiungi_al_log(voce)
        print(voce["id"], nome, tipo, conta["trade_stimati"], flush=True)
        if tipo == "registrazione":
            t0 = time.time()
            e = gruppo.esame_di_gruppo(modulo, p, spec["timeframe"], "costruzione", voce["id"], processi=4)
            (LAVORO / f"{voce['id']}_costruzione_esame.json").write_text(
                json.dumps(e, ensure_ascii=False, indent=1, sort_keys=True))
            print("  esame fatto in", round(time.time() - t0), "s; candidato", e.get("candidato"),
                  "t", e.get("t"), flush=True)


if __name__ == "__main__":
    main()
