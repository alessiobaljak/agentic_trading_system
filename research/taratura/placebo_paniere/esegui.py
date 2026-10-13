#!/usr/bin/env python3
"""La prova a placebo dell'esame di gruppo a BARRE GIORNALIERE (seconda edizione; regole in ``regole.md`` qui).

E' il lanciatore della prova a 1 ora (``research/taratura/placebo_gruppo/esegui.py``) con sei cose diverse, tutte
dichiarate qui e niente altro: il timeframe (solo «1d»), le serie di file controllate (1d), i mesi dichiarati, l'elenco
e le schede del paniere (``research/campagne/PANIERE/``), i file della prova (questa cartella) e il ramo remoto su cui
devono stare (il principale). Tutto il resto (sfasamento comune, ingressi placebo, esame, identita', ripresa) e' lo
stesso codice, importato: cambiarlo qui sarebbe una seconda implementazione da tenere uguale a mano.

Uso: ``python research/taratura/placebo_paniere/esegui.py --radice-dati research --lavoro <fuori da git>``.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence

QUI = Path(__file__).resolve().parent
RADICE_REPO = QUI.parents[2]
sys.path.insert(0, str(RADICE_REPO))
sys.path.insert(0, str(QUI.parent / "placebo_gruppo"))

import esegui as E  # noqa: E402  (il lanciatore della prova a 1 ora)
import placebo_paniere as PP  # noqa: E402  (le sei regole con i parametri per il giorno)
from research.src import dati, gruppo  # noqa: E402

#: i sei cambiamenti dichiarati
E.ESITI_DEFINITIVI = QUI
E.REGOLE_DELLA_PROVA = QUI / "regole.md"
E.SERIE_DEI_FILE = (("klines", "1d"), ("markPriceKlines", "1d"), ("fundingRate", None))
#: mesi di file attesi sulle 80 schede (contati al Passo 0, 13 ott 2026: 3.061 klines/1d, 3.061 mark 1d, 3.044 funding)
E.MESI_DICHIARATI = {"klines/1d": 3061, "markPriceKlines/1d": 3061, "fundingRate": 3044}
E.SCHEDE_DEL_PRINCIPALE = E.PRINCIPALE / "research" / "campagne" / "PANIERE" / "schede"
E.MONETE_DEL_PRINCIPALE = E.PRINCIPALE / "research" / "campagne" / "PANIERE" / "monete.csv"
E.RAMO_REMOTO = "origin/claude/brave-albattani-1b12fv"
TIMEFRAME = ("1d",)
#: il modulo delle regole di QUESTA prova (parametri per il giorno, correzione 1 di regole.md): lo usa il
#: lanciatore per gli istanti di segnale e lo esegue gruppo.py dal file, per ogni moneta
E.PG = PP
E.MODULO = QUI / "placebo_paniere.py"
E.REGOLA_DELL_USCITA = {u: next(r for r in PP.REGOLE if PP.USCITA_DELLA_REGOLA[r] == u) for u in PP.USCITE}
FILE_DELLA_PROVA = ("placebo_paniere.py", "esegui.py", "regole.md")


def identita_corrente(radice: Path, posizioni, funzionamento: bool):
    """L'identita' della prova a 1 ora piu' i file di QUESTA cartella (il lanciatore e le regole del paniere)."""
    identita = E.identita_corrente(radice, posizioni, funzionamento, regole=E.REGOLE_DELLA_PROVA)
    identita["codice"] = {"placebo_paniere.py": E.sha256_file(QUI / "placebo_paniere.py"),
                          "esegui_gruppo.py": E.sha256_file(E.QUI / "esegui.py"),
                          "esegui.py": E.sha256_file(QUI / "esegui.py")}
    identita["formato"] = 3
    return identita


def controlla_esame_contro_identita(riga, identita):
    """L'esame della riga ha usato il modulo di QUESTA prova e gli strumenti dell'identita'."""
    esame = riga.get("esame")
    if not esame:
        return []
    diverse = []
    if esame.get("impronta_variante") != identita["codice"]["placebo_paniere.py"]:
        diverse.append("placebo_paniere.py (impronta della variante dell'esame)")
    if esame.get("impronte_strumenti") != identita["strumenti"]:
        diverse.append("strumenti (impronte dell'esame)")
    return diverse


def controlla_prova():
    """I file di questa cartella committati e sul ramo principale remoto (come ``E.controlla_prova`` per i suoi)."""
    # `ramo` esplicito: il predefinito di E.controlla_prova e' legato alla definizione (origin/research/coordinamento)
    codice = E.controlla_prova(cartella=QUI, file=FILE_DELLA_PROVA, ramo=E.RAMO_REMOTO)
    codice.update(E.controlla_prova(cartella=E.QUI, file=("esegui.py",), ramo=E.RAMO_REMOTO))
    return codice


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Prova a placebo dell'esame di gruppo a barre giornaliere (regole.md qui)")
    parser.add_argument("--radice-dati", type=Path, default=os.environ.get("PLACEBO_RADICE_DATI"))
    parser.add_argument("--lavoro", type=Path, default=Path(os.environ.get("PLACEBO_LAVORO") or
                                                           (RADICE_REPO.parent / "placebo_paniere_lavoro")))
    parser.add_argument("--k", type=int, nargs="+", default=list(E.K_DELLA_PROVA))
    parser.add_argument("--periodo", nargs="+", default=list(E.PERIODI), choices=list(E.PERIODI))
    parser.add_argument("--massimo-minuti", type=float, default=None)
    parser.add_argument("--processi", type=int, default=4)
    parser.add_argument("--solo-copertura", action="store_true")
    parser.add_argument("--funzionamento", action="store_true",
                        help="prova di funzionamento: righe segnate, in <lavoro>/esiti_funzionamento/, mai un esito")
    args = parser.parse_args(argv)
    if args.radice_dati is None or not (Path(args.radice_dati) / "data" / "insample").is_dir():
        parser.error("--radice-dati deve essere la cartella che contiene data/insample/")
    inizio = time.monotonic()
    funzionamento = bool(args.funzionamento)
    lavoro = E.controlla_lavoro(args.lavoro, [RADICE_REPO, E.PRINCIPALE])
    attese, fonte, bozza = E.impronte_attese(None, regole=E.REGOLE_DELLA_PROVA, funzionamento=funzionamento)
    if funzionamento:
        codice = {"commit_prova": E._git(QUI, "rev-parse", "HEAD").strip(), "commit_file_della_prova": None}
        codice.update(E.controlla_principale(attese, pulito=False))
    else:
        codice = controlla_prova()
        codice.update(E.controlla_principale(attese))
    if dati.marcatore_di_campagna() is not None:
        raise SystemExit("c'e' un marcatore di campagna nel branch principale: la prova gira senza")
    radice = E.radice_di_lettura(lavoro, args.radice_dati, schede=E.SCHEDE_DEL_PRINCIPALE)
    caricatore = gruppo.CaricatoreDisco(str(radice))
    posizioni, _ = gruppo._monete_con_posizione(None)
    E.controlla_copertura(caricatore, None, args.processi, severa=not funzionamento)
    identita = identita_corrente(radice, posizioni, funzionamento)
    if args.solo_copertura:
        print(f"solo copertura: identita' {E._sha256_canonico(identita)[:16]}, nessun esame", flush=True)
        return 0
    esiti = (lavoro / "esiti_funzionamento") if funzionamento else QUI
    cartella_gruppo = lavoro / "gruppo" / E._sha256_canonico(identita)[:16]
    ks = sorted(set(args.k))
    fatte = {k: E.righe_fatte(esiti / f"esiti_k{k}.jsonl", identita) for k in ks}
    compiti = E.compiti_da_fare(ks, TIMEFRAME, args.periodo, fatte)
    print(f"principale {codice['commit_principale'][:8]} ({codice['ramo_principale']}), impronte attese da {fonte}"
          f"{' (FUNZIONAMENTO)' if funzionamento else ''}; esiti in {esiti}; k {ks}: da fare {len(compiti)}, "
          f"gia' fatte {sum(len(v) for v in fatte.values())}", flush=True)
    preparato = None
    errori_di_fila = 0
    for n, (tf, periodo, regola, direzione, k) in enumerate(compiti, 1):
        minuti = (time.monotonic() - inizio) / 60
        if args.massimo_minuti is not None and minuti >= args.massimo_minuti:
            print(f"fermato dopo {minuti:.1f} minuti: {len(compiti) - n + 1} da fare", flush=True)
            return 3
        if preparato is None or (preparato["timeframe"], preparato["periodo"]) != (tf, periodo):
            preparato = None
            t0 = time.monotonic()
            preparato = E.prepara(tf, periodo, caricatore, None, args.processi)
            print(f"dati {tf} {periodo} pronti: {len(preparato['monete'])} monete, L {preparato['L']}, "
                  f"{time.monotonic() - t0:.0f} s", flush=True)
        t0 = time.monotonic()
        try:
            riga = E.esegui_placebo(preparato, regola, direzione, k, caricatore=caricatore,
                                    cartella_gruppo=cartella_gruppo, radice=radice, processi=args.processi)
            errori_di_fila = 0
        except Exception as errore:  # noqa: BLE001
            riga = {"formato": 3, "etichetta": E.etichetta(tf, regola, direzione, periodo, k), "timeframe": tf,
                    "regola": regola, "direzione": direzione, "periodo": periodo, "k": k,
                    "errore": f"{type(errore).__name__}: {errore}\n{traceback.format_exc()}"[:4000]}
            errori_di_fila += 1
        cambiati = E.differenze_di_identita(identita, identita_corrente(radice, posizioni, funzionamento))
        cambiati += controlla_esame_contro_identita(riga, identita)
        if cambiati:
            print(f"FERMO: durante {riga['etichetta']} e' cambiato {', '.join(cambiati)}; la riga non e' scritta.", flush=True)
            return 4
        riga.update({"identita": identita, "impronte_attese_da": fonte, "regole_bozza": bozza,
                     "funzionamento": funzionamento, "radice_dati": str(Path(args.radice_dati).resolve()),
                     "lavoro": str(lavoro), "secondi": round(time.monotonic() - t0, 1),
                     "scritta": datetime.now(timezone.utc).isoformat(timespec="seconds"), **codice})
        E.scrivi_riga(esiti / f"esiti_k{k}.jsonl", riga)
        stato = "ERRORE" if riga.get("errore") else ("scarto" if riga.get("conta") and not riga.get("esame") else "esame fatto")
        print(f"[{n}/{len(compiti)}] {riga['etichetta']}: {stato}, {riga['secondi']:.0f} s", flush=True)
        if errori_di_fila >= 3:
            print("tre errori di fila: fermo", flush=True)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
