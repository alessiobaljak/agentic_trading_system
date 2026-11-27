"""Programma 6, seconda prova: le candele giornaliere e il funding di tutti i perpetui USDT-M dell'archivio pubblico di
Binance, anche quelli tolti dal listino (SECONDA.md, sezione 2), con il CHECKSUM.

Scrive in ``research/data/p6g/<SIMBOLO>/{giorni,funding}/`` (fuori da git) e in ``scarico_giorni.json`` un'impronta per
simbolo e tipo: numero di file, primo e ultimo, e lo SHA-256 dell'elenco ordinato «nome impronta» (si ricalcola dai file).
Riprende da dove si e' fermato.

Dal 27 novembre 2026 (audit del 26 novembre, raccolta-3: il 20 e il 26 novembre un solo errore di rete aveva fermato tutto lo
scarico, e nessuno se n'era accorto) l'errore di una moneta non ferma le altre: la moneta resta con l'impronta di prima e
l'errore va nel registro; dopo ``ERRORI_DI_FILA`` errori di fila la rete e' giu' e le monete rimaste si saltano. Alla fine il
file ha, sotto la chiave ``_esito``, quante monete attive non hanno l'ultimo giorno che hanno le altre (``esito``), e lo
schermo lo dice in una riga. Codice di uscita: 0 completo, 2 finito ma incompleto (monete senza l'ultimo giorno, errori,
monete saltate); un altro codice vuol dire che lo scarico e' caduto prima della fine.

Uso: python3 -m research.programma6.scarico_giorni [SIMBOLO ...]
     python3 -m research.programma6.scarico_giorni --riga <scarico_giorni.json> <codice di uscita dello scarico> [<PAPER.md>]
         la riga «Scarico incompleto: ...» (vuota se lo scarico e' completo), aggiunta in fondo a PAPER.md se indicato
         (``paper/aggiorna.sh``)
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from research.programma5.strumenti.scarico import BASE, _prendi, elenca
from research.programma5.strumenti.universo import STABILI, simboli
from research.src.dati import leggi_checksum

RADICE = Path(__file__).resolve().parents[2]
DATI = RADICE / "research" / "data" / "p6g"
QUI = Path(__file__).parent
MESE_IN_CORSO = datetime.now(timezone.utc).strftime("%Y-%m")
CHIAVE_ESITO = "_esito"     # l'esito dell'ultimo scarico, nel file delle impronte (non e' un simbolo: [A-Z0-9]+USDT)
SETTIMANA = 7               # giorni: una moneta con una candela giornaliera in quelli prima dell'ultimo giorno e' attiva
ERRORI_DI_FILA = 10         # dopo tanti errori di fila la rete e' giu': le monete rimaste si saltano (si riprendono dopo)


def ammesso(s: str) -> bool:
    return bool(re.fullmatch(r"[A-Z0-9]+USDT", s)) and not any(s.startswith(x) for x in STABILI)


def _mese_piu(m: str, k: int) -> str:
    a, mm = int(m[:4]), int(m[5:7]) - 1 + k
    return f"{a + mm // 12:04d}-{mm % 12 + 1:02d}"


def _mesi(chiavi_: list) -> list:
    return sorted({x.group(1) for x in (re.search(r"-(\d{4}-\d{2})\.zip$", k) for k in chiavi_) if x})


def _giornalieri(prefisso: str, ultimo: str) -> list:
    """I file giornalieri dei mesi dopo l'ultimo mensile pubblicato, fino al mese in corso (solo se l'ultimo mensile e'
    degli ultimi due mesi: una moneta tolta dal listino da tempo non ha giornalieri)."""
    out = []
    if not ultimo or ultimo < _mese_piu(MESE_IN_CORSO, -2):
        return out
    m = _mese_piu(ultimo, 1)
    while m <= MESE_IN_CORSO:
        out += elenca(f"{prefisso}-{m}-")
        m = _mese_piu(m, 1)
    return out


def chiavi(s: str, premio: bool = False) -> dict:
    mensili = elenca(f"data/futures/um/monthly/klines/{s}/1d/")
    mm = _mesi(mensili)
    giorni = list(mensili) + _giornalieri(f"data/futures/um/daily/klines/{s}/1d/{s}-1d", mm[-1] if mm else "")
    funding = elenca(f"data/futures/um/monthly/fundingRate/{s}/")
    out = {"giorni": sorted(giorni), "funding": sorted(funding)}
    if premio:
        # l'indice del premio orario dei mesi senza il file del funding (per stimarlo: programma6/paper/REGOLE.md)
        fm = _mesi(funding)
        out["premio"] = sorted(_giornalieri(f"data/futures/um/daily/premiumIndexKlines/{s}/1h/{s}-1h", fm[-1] if fm else ""))
    return out


def _scarica(chiave: str, dest: Path):
    nome = chiave.rsplit("/", 1)[1]
    f = dest / nome
    ok = f.with_suffix(".zip.ok")
    if f.exists() and ok.exists():
        return nome, ok.read_text().strip()
    contenuto = _prendi(BASE + chiave)
    if contenuto is None:
        return nome, None
    somma = _prendi(BASE + chiave + ".CHECKSUM")
    impronta = hashlib.sha256(contenuto).hexdigest()
    if somma is not None and leggi_checksum(somma, chiave) != impronta:
        raise RuntimeError(f"CHECKSUM diverso per {chiave}")
    dest.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(".tmp")
    tmp.write_bytes(contenuto)
    tmp.replace(f)
    ok.write_text(impronta if somma is not None else impronta + " senza-checksum")
    return nome, ok.read_text().strip()


def impronta(esiti: list) -> dict:
    righe = sorted(f"{n} {h}" for n, h in esiti if h)
    return {"file": len(righe), "primo": righe[0].split()[0] if righe else "", "ultimo": righe[-1].split()[0] if righe else "",
            "sha256": hashlib.sha256("\n".join(righe).encode()).hexdigest()}


def uno(s: str, premio: bool = False) -> dict:
    out = {}
    for tipo, ch in chiavi(s, premio).items():
        with ThreadPoolExecutor(max_workers=8) as ex:
            esiti = list(ex.map(lambda k: _scarica(k, DATI / s / tipo), ch))
        out[tipo] = impronta(esiti)
    return out


def ultimo_giorno(imp_giorni):
    """Il giorno dell'ultima candela di una moneta dall'impronta dei suoi giorni: la data dell'ultimo file giornaliero, o
    l'ultimo giorno del mese dell'ultimo file mensile; None senza file."""
    m = re.search(r"-(\d{4})-(\d{2})(?:-(\d{2}))?\.zip$", (imp_giorni or {}).get("ultimo", ""))
    if not m:
        return None
    a, mm = int(m.group(1)), int(m.group(2))
    if m.group(3):
        return date(a, mm, int(m.group(3)))
    return date(a + mm // 12, mm % 12 + 1, 1) - timedelta(days=1)


def esito(imp: dict, errori: dict, fatte=(), quando: str = "", saltate=()) -> dict:
    """Quante monete attive non hanno l'ultimo giorno D che hanno le altre (il piu' recente fra tutte le impronte).

    Attiva: una moneta con una candela giornaliera nei ``SETTIMANA`` giorni prima di D. Una moneta scaricata senza errori in
    questo giro (``fatte``) ha tutto quello che l'archivio pubblica ora: conta solo se ha almeno il giorno prima di D (se
    all'archivio mancano i suoi ultimi due giorni e' una moneta tolta dal listino, non uno scarico a meta'), e se non ha D e'
    fra le «assenti nell'archivio». Una moneta con un errore che non ha nessuna impronta conta come attiva senza D."""
    fatte = set(fatte)
    giorni = {s: ultimo_giorno(v.get("giorni")) for s, v in imp.items() if s != CHIAVE_ESITO and isinstance(v, dict)}
    noti = [g for g in giorni.values() if g]
    d = max(noti) if noti else None
    attive, senza = [], []
    for s, g in sorted(giorni.items()):
        if g is not None and g >= d - timedelta(days=1 if s in fatte else SETTIMANA):
            attive.append(s)
            if g < d:
                senza.append(s)
    for s in sorted(errori):
        if giorni.get(s) is None:
            attive.append(s)
            senza.append(s)
    per_errore = [s for s in senza if s in errori]
    assenti = [s for s in senza if s in fatte]
    return {"quando": quando, "giorno": d.isoformat() if d else None, "attive": len(attive),
            "senza_ultimo_giorno": len(senza), "per_errore": len(per_errore), "assenti_nell_archivio": len(assenti),
            "non_scaricate": len(senza) - len(per_errore) - len(assenti), "monete_senza": senza,
            "errori": dict(sorted(errori.items())), "saltate": len(list(saltate))}


def riga_esito(es: dict) -> str:
    """La riga a schermo alla fine dello scarico."""
    return (f"[giorni] esito: {es['attive']} monete attive, {es['senza_ultimo_giorno']} senza il giorno {es['giorno']} "
            f"({es['per_errore']} per un errore dello scarico, {es['assenti_nell_archivio']} assenti nell'archivio, "
            f"{es['non_scaricate']} non scaricate in questo giro); monete con un errore: {len(es['errori'])}; saltate dopo "
            f"{ERRORI_DI_FILA} errori di fila: {es['saltate']}")


def _monete(n: int) -> str:
    return f"{n} {'moneta' if n == 1 else 'monete'}"


def riga_paper(imp: dict, codice: int = 0) -> str:
    """La riga per il fondo di ``paper/PAPER.md`` (``paper/aggiorna.sh``), vuota se lo scarico e' completo. ``codice`` e' il
    codice di uscita dello scarico: con 0 o 2 l'esito scritto alla fine vale; con un altro lo scarico e' caduto prima della
    fine, e le monete senza l'ultimo giorno si contano dalle impronte scritte fino a li'. Con la rete giu' per tutte le monete
    l'ultimo giorno non avanza e nessuna «manca»: la riga c'e' lo stesso, con gli errori e le monete saltate."""
    es = imp.get(CHIAVE_ESITO) if codice in (0, 2) else None
    caduto = not isinstance(es, dict)
    if caduto:
        es = esito(imp, {})
    n, e, sa = es.get("senza_ultimo_giorno", 0), len(es.get("errori") or {}), es.get("saltate", 0)
    if not (caduto or n or e or sa):
        return ""
    quale = f"il giorno {es['giorno']}" if es.get("giorno") else "nessun giorno scaricato"
    testa = f"Scarico incompleto: {_monete(n)} senza {quale}" if n else "Scarico incompleto"
    if caduto:
        come = "non ha scritto il suo esito" if codice in (0, 2) else "si è fermato prima della fine"
        return (testa + f" (lo scarico delle candele giornaliere {come}, codice {codice}: registro in `scarico_giorni.log` "
                "nella cartella delle impronte).")
    parti = [f"{es[k]} {t}" for k, t in (("per_errore", "per un errore dello scarico"),
                                         ("assenti_nell_archivio", "assenti nell'archivio"),
                                         ("non_scaricate", "non scaricate in questo giro")) if n and es.get(k)]
    if e and not n:
        parti.append(f"{_monete(e)} con un errore dello scarico, ultimo giorno scaricato {es.get('giorno')}")
    if sa:
        parti.append(f"{sa} saltate dopo {ERRORI_DI_FILA} errori di fila")
    return testa + f" ({', '.join(parti)}; elenco in `research/programma6/scarico_giorni.json`, voce `{CHIAVE_ESITO}`)."


def aggiungi_riga(file_json: str, codice: int, paper=None) -> str:
    """``riga_paper`` dal file delle impronte; se non e' vuota e c'e' ``paper``, la aggiunge in fondo a quel file."""
    try:
        imp = json.loads(Path(file_json).read_text())
    except (OSError, ValueError):
        imp = {}
    riga = riga_paper(imp if isinstance(imp, dict) else {}, codice)
    if riga and paper:
        with open(paper, "a", encoding="utf-8") as f:
            f.write("\n" + riga + "\n")
    return riga


def _uno_o_errore(s: str, premio: bool, stato: dict):
    """``uno`` senza far cadere lo scarico: (impronta, None, False), (None, (errore in una riga, traceback), False), o
    (None, None, True) per una moneta saltata dopo ``ERRORI_DI_FILA`` errori di fila."""
    with stato["lock"]:
        if stato["di_fila"] >= ERRORI_DI_FILA:
            return None, None, True
    try:
        r = uno(s, premio)
    except Exception as e:  # qualunque errore di una moneta si registra e si va avanti con le altre
        with stato["lock"]:
            stato["di_fila"] += 1
        return None, (f"{type(e).__name__}: {e}"[:300], traceback.format_exc()), False
    with stato["lock"]:
        stato["di_fila"] = 0
    return r, None, False


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--riga"]:
        riga = aggiungi_riga(argv[1], int(argv[2]), argv[3] if len(argv) > 3 else None)
        if riga:
            print(riga, flush=True)
        return 0
    tutti = argv or [s for s in simboli() if ammesso(s)]
    dest = QUI / "scarico_giorni.json"
    imp = json.loads(dest.read_text()) if dest.exists() else {}
    import os
    premio = os.environ.get("P6_PREMIO") == "1"
    if os.environ.get("P6_IMPRONTE"):
        dest = Path(os.environ["P6_IMPRONTE"]) / "scarico_giorni.json"
        if not dest.exists() and (QUI / "scarico_giorni.json").exists():
            imp = json.loads((QUI / "scarico_giorni.json").read_text())
        elif dest.exists():
            imp = json.loads(dest.read_text())
    imp.pop(CHIAVE_ESITO, None)          # l'esito del giro di prima non vale piu': si riscrive alla fine
    errori, fatte, saltate = {}, [], []
    stato = {"lock": threading.Lock(), "di_fila": 0}
    with ThreadPoolExecutor(max_workers=int(os.environ.get("P6_FILI", "4"))) as ex:
        for s, (r, err, saltata) in zip(tutti, ex.map(lambda x: _uno_o_errore(x, premio, stato), tutti)):
            if saltata:
                saltate.append(s)
                continue
            if err:
                errori[s] = err[0]
                print(f"[giorni] {s}: ERRORE {err[0]} (resta l'impronta di prima)", flush=True)
                print(err[1], file=sys.stderr, flush=True)
                continue
            fatte.append(s)
            imp[s] = r
            print(f"[giorni] {s}: {r['giorni']['file']} giorni/mesi, {r['funding']['file']} funding", flush=True)
            dest.write_text(json.dumps(imp, indent=0, sort_keys=True))
    es = esito(imp, errori, fatte, datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), saltate)
    imp[CHIAVE_ESITO] = es
    dest.write_text(json.dumps(imp, indent=0, sort_keys=True))
    print(riga_esito(es), flush=True)
    return 2 if es["senza_ultimo_giorno"] or errori or saltate else 0


if __name__ == "__main__":
    raise SystemExit(main())
