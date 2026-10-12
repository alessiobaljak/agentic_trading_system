"""Scarico dei dati della Fase 0 del gruppo (regole.md, sezione 2, punti 2-5), solo con research/src/dati.py.

Uso:
  python3 -u scarico.py base          file del punto 2: 1d di last e mark e funding delle 80 monete,
                                      last di BTCUSDT su tutti i timeframe ammessi
  python3 -u scarico.py tf <TF>       last e mark del timeframe TF per le 80 monete (punto 3)

Ogni file si scarica al massimo 3 volte (punto 9): un 404 e' un buco; un errore che resiste a 3 tentativi
si scrive in errori e lo script finisce con codice 2 (STOP). Le impronte (punto 5) si scrivono in
campagne/GRUPPO/impronte/ una volta sola, al primo scarico senza errori; se il file delle impronte c'e'
gia', si confrontano con verifica-impronte e una differenza e' STOP (codice 3).
Gli indirizzi si costruiscono mese per mese dal primo mese della scheda al 2023-12: niente elenchi.
"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

from comune import CARTELLA_GRUPPO, RADICE_RICERCA, dati, monete, schede

TIMEFRAME_AMMESSI = ("15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d")
INIZIO_BTC = date(2020, 1, 1)
FINE = date(2023, 12, 31)
TENTATIVI = 3
CARTELLA_IMPRONTE = CARTELLA_GRUPPO / "impronte"
CARTELLA_LAVORO = CARTELLA_GRUPPO / "lavoro"


def compiti_base():
    """(simbolo, tipo, intervallo, inizio) dei file del punto 2."""
    compiti = []
    for s, scheda in schede().items():
        inizio = scheda["primo_mese"]
        compiti.append((s, "klines", "1d", inizio))
        compiti.append((s, "markPriceKlines", "1d", inizio))
        compiti.append((s, "fundingRate", None, inizio))
    for tf in TIMEFRAME_AMMESSI:
        compiti.append(("BTCUSDT", "klines", tf, INIZIO_BTC))
    return compiti


def compiti_timeframe(tf):
    if tf not in TIMEFRAME_AMMESSI:
        raise ValueError(f"timeframe non ammesso: {tf}")
    compiti = []
    for s, scheda in schede().items():
        compiti.append((s, "klines", tf, scheda["primo_mese"]))
        compiti.append((s, "markPriceKlines", tf, scheda["primo_mese"]))
    return compiti


def scarica_un_mese(simbolo, tipo, intervallo, anno, mese):
    """Fino a 3 tentativi; ritorna ('presente'|'buco'|'errore', percorso o messaggio)."""
    ultimo = None
    for tentativo in range(TENTATIVI):
        try:
            percorso = dati.scarica_mese(simbolo, tipo, intervallo, anno, mese, RADICE_RICERCA)
            return ("presente", percorso) if percorso is not None else ("buco", None)
        except Exception as errore:  # noqa: BLE001  (rete, CHECKSUM: si riprova, poi STOP)
            ultimo = f"{type(errore).__name__}: {errore}"
            time.sleep(2 * (tentativo + 1))
    return "errore", ultimo


def nome_impronte(simbolo_btc, tipo, intervallo):
    base = f"{tipo}_{intervallo}" if intervallo else tipo
    return f"BTCUSDT_{base}.json" if simbolo_btc else f"{base}.json"


def main():
    modo = sys.argv[1]
    compiti = compiti_base() if modo == "base" else compiti_timeframe(sys.argv[2])
    dati.azzera_checksum_mancanti()
    lavori = []
    for simbolo, tipo, intervallo, inizio in compiti:
        for anno, mese in dati.mesi_del_periodo(inizio, FINE):
            lavori.append((simbolo, tipo, intervallo, anno, mese))
    print("file da controllare o scaricare:", len(lavori), flush=True)
    t0 = time.time()
    esiti = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futuri = {pool.submit(scarica_un_mese, *l): l for l in lavori}
        for i, (futuro, l) in enumerate(futuri.items(), 1):
            esiti[l] = futuro.result()
            if i % 500 == 0:
                print(f"{i}/{len(lavori)} in {time.time() - t0:.0f} s", flush=True)
    print(f"finito in {time.time() - t0:.0f} s", flush=True)

    riassunto = {}
    errori = []
    gruppi = {}
    for (simbolo, tipo, intervallo, anno, mese), (esito, valore) in esiti.items():
        chiave = f"{simbolo}|{tipo}|{intervallo or '-'}"
        voce = riassunto.setdefault(chiave, {"attesi": 0, "presenti": 0, "buchi": []})
        voce["attesi"] += 1
        if esito == "presente":
            voce["presenti"] += 1
            gruppi.setdefault((simbolo == "BTCUSDT", tipo, intervallo), {}).setdefault(simbolo, []).append(valore)
        elif esito == "buco":
            voce["buchi"].append(f"{anno:04d}-{mese:02d}")
        else:
            errori.append({"file": f"{simbolo} {tipo} {intervallo} {anno:04d}-{mese:02d}", "errore": valore})
    for voce in riassunto.values():
        voce["buchi"].sort()
    uscita = {"modo": sys.argv[1:], "file": len(lavori), "errori": errori,
              "checksum_mancanti": list(dati.CHECKSUM_MANCANTI), "per_serie": riassunto}
    nome = "scarico_base" if modo == "base" else f"scarico_{sys.argv[2]}"
    (CARTELLA_LAVORO / f"{nome}.json").write_text(json.dumps(uscita, ensure_ascii=False, indent=1, sort_keys=True))
    print("errori:", len(errori), "checksum mancanti:", len(dati.CHECKSUM_MANCANTI), flush=True)
    if errori:
        print("STOP: errori di scarico dopo 3 tentativi", flush=True)
        sys.exit(2)

    CARTELLA_IMPRONTE.mkdir(parents=True, exist_ok=True)
    differenze_totali = []
    for (btc, tipo, intervallo), per_simbolo in sorted(gruppi.items(), key=lambda x: str(x[0])):
        trovate = {}
        for simbolo in sorted(per_simbolo):
            cartella = RADICE_RICERCA / "data" / "insample" / simbolo
            trovate[simbolo] = {p.relative_to(cartella).as_posix(): dati.impronta_file(p)
                                for p in sorted(per_simbolo[simbolo])}
        file_impronte = CARTELLA_IMPRONTE / nome_impronte(btc, tipo, intervallo)
        if not file_impronte.exists():
            file_impronte.write_text(json.dumps(trovate, indent=1, sort_keys=True) + "\n")
            print("impronte scritte:", file_impronte.name, sum(len(v) for v in trovate.values()), "file", flush=True)
        else:
            attese = json.loads(file_impronte.read_text())
            for simbolo, file_attesi in sorted(attese.items()):
                diff = dati.verifica_impronte(simbolo, RADICE_RICERCA, file_attesi)
                differenze_totali += [f"{simbolo}: {d}" for d in diff]
            print("impronte confrontate:", file_impronte.name, flush=True)
    if differenze_totali:
        print("STOP: impronte diverse o file mancanti:", differenze_totali[:50], flush=True)
        sys.exit(3)


if __name__ == "__main__":
    main()
