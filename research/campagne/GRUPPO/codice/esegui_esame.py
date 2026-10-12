"""Script di lavoro: chiama le funzioni di research/src/gruppo.py e salva il loro dizionario cosi' com'e'.

Nessun calcolo d'esame qui: ogni numero lo calcola gruppo.py.

Uso:
  python3 -u esegui_esame.py conta     MODULO P_JSON TF NOME
  python3 -u esegui_esame.py esame     MODULO P_JSON TF PERIODO ID [opzioni JSON]
  python3 -u esegui_esame.py positivo  MODULO P_JSON TF DIREZIONE
MODULO e' il nome del file in campagne/GRUPPO/codice/; P_JSON e' un file JSON in campagne/GRUPPO/lavoro/ con i
parametri; l'uscita va in campagne/GRUPPO/lavoro/<NOME o ID>_<azione>.json, e un riassunto sullo schermo.
"""
import json
import sys
import time

from comune import CARTELLA_GRUPPO

from research.src import gruppo

CODICE = CARTELLA_GRUPPO / "codice"
LAVORO = CARTELLA_GRUPPO / "lavoro"


def salva(nome, dizionario):
    percorso = LAVORO / f"{nome}.json"
    percorso.write_text(json.dumps(dizionario, ensure_ascii=False, indent=1, sort_keys=True))
    return percorso


def main():
    azione, modulo, p_file = sys.argv[1], CODICE / sys.argv[2], LAVORO / sys.argv[3]
    p = json.loads(p_file.read_text())
    tf = sys.argv[4]
    t0 = time.time()
    if azione == "conta":
        r = gruppo.conta_trade_di_gruppo(modulo, p, tf, processi=4)
        nome = f"{sys.argv[5]}_conta"
        salva(nome, r)
        print(json.dumps({k: r[k] for k in ("trade_stimati", "monete_con_trade", "quota_moneta_piu_presente",
                                              "moneta_piu_presente", "esito", "motivi", "stima_trade_validazione")},
                         ensure_ascii=False))
    elif azione == "esame":
        periodo, ident = sys.argv[5], sys.argv[6]
        opzioni = json.loads(sys.argv[7]) if len(sys.argv) > 7 else {}
        r = gruppo.esame_di_gruppo(modulo, p, tf, periodo, ident, processi=4, **opzioni)
        salva(f"{ident}_{periodo}_esame", r)
        print("salvato", ident, periodo)
    elif azione == "positivo":
        ident = sys.argv[6] if len(sys.argv) > 6 else "GRUPPO-controllo-positivo"
        r = gruppo.controllo_positivo(modulo, p, tf, sys.argv[5], id=ident, processi=4)
        salva("controllo_positivo" if len(sys.argv) <= 6 else ident, r)
        print(json.dumps({k: r[k] for k in ("passa", "condizioni", "t_senza_ritardo", "t_con_ritardo")},
                         ensure_ascii=False))
    print(f"secondi: {time.time() - t0:.0f}")


if __name__ == "__main__":
    main()
