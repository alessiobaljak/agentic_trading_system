"""Comandi della campagna: causalita', conteggio dei trade, test della Fase 2 e verifiche.

Uso:
  python esegui.py causale <nome>
  python esegui.py conta <nome>                      (una volta sola per variante)
  python esegui.py testa <nome> [opzioni] [--tag T]
opzioni del test: --costi 2  --ritardo 1  --intrabarra target_prima  --periodo validazione
Ogni esito si scrive in data/insample/1000SHIBUSDT/risultati/ (fuori da git) e si stampa.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadro as q  # noqa: E402
import varianti  # noqa: E402

CONTEGGI = q.CARTELLA_DATI / "risultati" / "conteggi.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("comando")
    ap.add_argument("nome")
    ap.add_argument("--costi", type=float, default=1.0)
    ap.add_argument("--ritardo", type=int, default=0)
    ap.add_argument("--intrabarra", default="stop_prima")
    ap.add_argument("--periodo", default="costruzione")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    v = varianti.VARIANTI[a.nome]

    if a.comando == "causale":
        serie = q.carica(v.tf, con_btc=v.con_btc)
        n = q.candele_costruzione(serie)
        serie.candele = serie.candele[:n]
        problemi = q.verifica_causalita(v, serie)
        print(json.dumps({"nome": v.id, "causale": not problemi, "problemi": problemi[:10]}, ensure_ascii=False))
        return

    if a.comando == "conta":
        CONTEGGI.parent.mkdir(parents=True, exist_ok=True)
        fatti = json.loads(CONTEGGI.read_text()) if CONTEGGI.is_file() else {}
        if v.id in fatti:
            print("GIA' CONTATA (si conta una volta sola):", json.dumps(fatti[v.id]))
            return
        c = q.conta(v)
        fatti[v.id] = c
        CONTEGGI.write_text(json.dumps(fatti, indent=1))
        print(json.dumps({"nome": v.id, **c}))
        return

    if a.comando == "testa":
        par = q.parametri(moltiplicatore_costi=a.costi, ritardo_barre=a.ritardo, riempimento=a.intrabarra)
        ris = q.esame(v, par, periodo=a.periodo)
        trades = ris.pop("_trades", [])
        nome = v.id + (("_" + a.tag) if a.tag else "")
        q.salva(nome, ris)
        q.salva(nome + "_trade", trades)
        print(json.dumps(ris, ensure_ascii=False, default=str))
        return
    raise SystemExit("comando sconosciuto")


if __name__ == "__main__":
    main()
