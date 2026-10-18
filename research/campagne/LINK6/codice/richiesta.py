"""Richiesta al coordinamento di una verifica sulle monete di controllo (guida pratica, sezione 3bis).

Uso: python3 research/campagne/LINK6/codice/richiesta.py <lotto.json> <id_variante> <id_richiesta> <tipo>

tipo: fase3 (la variante del lotto ha "confronto_con"), verifica_12 o validazione.
Registra la verifica nel log (tipo_test verifica, verifica_di, monete_di_controllo true, con la specifica) e scrive
campagne/LINK6/richieste/<id_richiesta>.json. Dopo: commit, push e attesa della risposta.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
from research.src.catalogo3 import normalizza  # noqa: E402

CRITERI = {
    "fase3": "Fase 3, punto 4: la media fra le monete di controllo dell'R medio e' piu' alta con la variante nuova "
             "di almeno 0,05 R rispetto alla variante di confronto, sul periodo di costruzione",
    "verifica_12": "Fase 4, verifica 12: R medio sopra la media delle proprie entrate casuali su almeno 7 monete su 9 "
                   "(meno di 30 trade conta come non superata) e media fra le monete dell'R medio positiva",
    "validazione": "sezione 10.3, validazione sulle monete di controllo",
}


def main():
    lotto = comune.leggi_lotto(sys.argv[1])
    vid, rid, tipo = sys.argv[2], sys.argv[3], sys.argv[4]
    if tipo not in CRITERI:
        raise SystemExit(f"tipo sconosciuto: {tipo}")
    voce = lotto[vid]
    richiesta = {"id": rid, "variante": vid, "tipo": tipo}
    registrazione = {"id": rid, "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": vid,
                     "monete_di_controllo": True, "tipo_verifica": tipo,
                     "specifica": normalizza(voce["specifica"]), "periodo": "costruzione" if tipo != "validazione"
                     else "validazione", "previsione": voce["previsione"], "criterio_successo": CRITERI[tipo]}
    if tipo == "fase3":
        conf = voce["confronto_con"]
        regs = [v for v in comune.voci() if v.get("id") == conf and v.get("tipo") == "registrazione"]
        if not regs:
            raise SystemExit(f"la variante di confronto {conf} non e' registrata")
        richiesta["confronto_con"] = conf
        registrazione["confronto_con"] = conf
        registrazione["specifica_confronto"] = regs[0]["specifica"]
    percorso = comune.CAMPAGNA / "richieste" / f"{rid}.json"
    if percorso.exists():
        raise SystemExit(f"la richiesta {rid} esiste gia'")
    comune.aggiungi(registrazione)
    percorso.write_text(json.dumps(richiesta, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"richiesta {rid} registrata e scritta in {percorso}")


if __name__ == "__main__":
    main()
