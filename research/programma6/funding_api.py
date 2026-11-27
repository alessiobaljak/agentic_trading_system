"""Il funding vero dopo l'ultimo file mensile dell'archivio, dall'interfaccia pubblica di Binance (audit del 26 novembre 2026,
problema motore-1).

L'archivio pubblico (data.binance.vision) pubblica il funding solo a mese finito. Fino ad allora il pannello metteva la media dei
90 giorni prima (``seconda.riempi_funding``) e il paper la stima dall'indice del premio (``paper/aggiorna.applica_stima``): a
novembre 2026 la ricerca di G1 sceglieva cosi' monete diverse dal paper (in media 12 al giorno dal lato diverso). In piu' l'ultimo
giorno del mese restava senza il regolamento delle 00:00 del giorno dopo, che sta nel file del mese dopo.

Per ogni moneta con candele recenti si fa una richiesta a ``/fapi/v1/fundingRate`` (da www.binance.com: fapi.binance.com da qui
risponde 451), con ``limit`` 1000, dal primo istante dopo l'ultimo regolamento gia' scaricato (archivio mensile o file di qui), e
una pausa fra le richieste (il limite e' 500 richieste ogni 5 minuti). Le righe vanno in
``research/data/p6g/<SIMBOLO>/funding_api/`` (fuori da git), un file per moneta,
``<SIMBOLO>-fundingRate-api-fino-<AAAA-MM-GG>T<HHMM>.csv``, con le colonne dell'interfaccia (fundingTime, fundingRate,
markPrice): il nome dice fino a quando (UTC) il file ha tutti i regolamenti. ``seconda.funding_giorni`` le legge dopo l'archivio;
dove ci sono tutti e due (stesso minuto) vince l'archivio.

Uso: python3 -m research.programma6.funding_api [--simboli BTCUSDT,ETHUSDT]
"""
from __future__ import annotations

import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

URL = "https://www.binance.com/fapi/v1/fundingRate"
TESTATA = {"User-Agent": "Mozilla/5.0"}
LIMITE = 1000
PAUSA = 0.7                  # secondi fra due richieste: 500 ogni 5 minuti sono una ogni 0,6
PAGINE_MAX = 5               # piu' di una pagina solo se l'archivio e' indietro di mesi (monete col funding ogni ora)
MARGINE_MS = 10 * 60_000     # un regolamento conta come scaricato solo se la richiesta e' di 10 minuti dopo
GIORNI_RECENTI = 60          # si chiede il funding delle monete con una candela giornaliera negli ultimi 60 giorni
ERRORI_DI_FILA = 5           # dopo 5 richieste di fila andate male lo scarico si ferma (rete giu': non si aspettano ore)
GIORNO_MS = 86_400_000
CARTELLA = "funding_api"
COLONNE = ["fundingTime", "fundingRate", "markPrice"]
FORMATO = "%Y-%m-%dT%H%M"
PREFISSO = "-fundingRate-api-fino-"


class Bloccato(RuntimeError):
    """Si smette subito: Binance ha bloccato l'indirizzo (418), risponde ancora 429 dopo un minuto, o non risponde piu'."""


# ---------------------------------------------------------------------------
# lettura (la usa seconda.funding_giorni)
# ---------------------------------------------------------------------------

def nome_file(simbolo: str, fino_ms: int) -> str:
    return simbolo + PREFISSO + datetime.fromtimestamp(int(fino_ms) // 60_000 * 60, tz=timezone.utc).strftime(FORMATO) + ".csv"


def fino_dal_nome(nome: str) -> int | None:
    """Fino a quando (ms, al minuto, per difetto) il file ha tutti i regolamenti."""
    if PREFISSO not in nome or not nome.endswith(".csv"):
        return None
    try:
        d = datetime.strptime(nome.split(PREFISSO)[1][:-4], FORMATO).replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return int(d.timestamp()) * 1000


def leggi(cartella: Path) -> tuple[pd.DataFrame, int | None]:
    """I regolamenti scaricati (colonne ts in ms e tasso) e fino a quando sono completi (ms), o None se non ci sono file."""
    file = [p for p in (sorted(cartella.glob("*.csv")) if cartella.is_dir() else []) if fino_dal_nome(p.name) is not None]
    vuoto = pd.DataFrame({"ts": np.array([], np.int64), "tasso": np.array([], float)})
    if not file:
        return vuoto, None
    fino = max(fino_dal_nome(p.name) for p in file)
    parti = [x for x in (pd.read_csv(p, usecols=["fundingTime", "fundingRate"]) for p in file) if len(x)]
    if not parti:
        return vuoto, fino
    df = pd.concat(parti, ignore_index=True)
    out = pd.DataFrame({"ts": df["fundingTime"].astype(np.int64).to_numpy(), "tasso": df["fundingRate"].astype(float).to_numpy()})
    return out.drop_duplicates("ts").sort_values("ts", ignore_index=True), fino


def ultimo_giorno_completo(fino_ms: int) -> int:
    """L'ultimo giorno di tenuta con tutti i regolamenti, se i file sono completi fino a ``fino_ms``: il giorno D finisce con il
    regolamento delle 00:00 del giorno dopo (come in ``seconda.funding_giorni``)."""
    return int(fino_ms) // GIORNO_MS - 1


# ---------------------------------------------------------------------------
# scarico
# ---------------------------------------------------------------------------

_SESSIONE = []


def _chiedi(params: dict):
    """Una richiesta (sulla stessa connessione delle precedenti): la lista dei regolamenti, o il codice HTTP se non e' andata (0 se
    la risposta non e' una lista, -1 se la connessione non va)."""
    import requests
    if not _SESSIONE:
        _SESSIONE.append(requests.Session())
    try:
        r = _SESSIONE[0].get(URL, params=params, headers=TESTATA, timeout=30)
    except requests.RequestException:
        return -1
    if r.status_code != 200:
        return r.status_code
    try:
        d = r.json()
    except ValueError:
        return 0
    return d if isinstance(d, list) else 0


def scarica_moneta(simbolo: str, dal_ms: int, adesso_ms: int, chiedi=_chiedi, pausa=time.sleep) -> tuple[list, int | None]:
    """Le righe dal ``dal_ms`` in poi e fin dove sono complete (ms), o ``([], None)`` se una richiesta non va. Una pagina da 1000
    basta per 333 giorni di funding ogni 8 ore; se e' piena si chiede la successiva, fino a ``PAGINE_MAX``."""
    righe, inizio = [], int(dal_ms)
    for k in range(PAGINE_MAX):
        if k:
            pausa(PAUSA)
        d = chiedi({"symbol": simbolo, "startTime": inizio, "limit": LIMITE})
        if d == 429:                                   # troppe richieste: si aspetta un minuto e si riprova una volta
            pausa(60)
            d = chiedi({"symbol": simbolo, "startTime": inizio, "limit": LIMITE})
        if d in (418, 429):                            # bloccati, o ancora troppe richieste: si smette (il paper non aspetta ore)
            raise Bloccato(f"{simbolo} ({d})")
        if not isinstance(d, list):
            return [], None
        d = sorted((x for x in d if int(x["fundingTime"]) >= inizio), key=lambda x: int(x["fundingTime"]))
        righe += d
        if len(d) < LIMITE:
            return righe, int(adesso_ms) - MARGINE_MS
        inizio = int(d[-1]["fundingTime"]) + 1
    return righe, int(righe[-1]["fundingTime"])       # pagine finite: completo fino all'ultimo regolamento


def salva(cartella: Path, simbolo: str, righe: list, fino_ms: int) -> Path:
    """Unisce le righe nuove a quelle gia' scaricate in un file solo (il nome dice fino a quando e' completo); i file vecchi si
    tolgono dopo aver scritto il nuovo."""
    cartella.mkdir(parents=True, exist_ok=True)
    vecchi = [p for p in cartella.glob("*.csv") if fino_dal_nome(p.name) is not None]
    nuove = pd.DataFrame([{k: str(x.get(k, "")) for k in COLONNE} for x in righe], columns=COLONNE)
    tutto = pd.concat([pd.read_csv(p, dtype=str, keep_default_na=False) for p in vecchi] + [nuove], ignore_index=True)[COLONNE]
    tutto = tutto.assign(_t=tutto["fundingTime"].astype(np.int64)).drop_duplicates("_t").sort_values("_t")[COLONNE]
    fino = max([int(fino_ms)] + [fino_dal_nome(p.name) for p in vecchi])
    nuovo = cartella / nome_file(simbolo, fino)
    tmp = nuovo.with_suffix(".tmp")
    tutto.to_csv(tmp, index=False)
    tmp.replace(nuovo)
    for p in vecchi:
        if p != nuovo:
            p.unlink(missing_ok=True)
    return nuovo


def ultimo_archivio_ms(cartella_archivio: Path) -> int | None:
    """L'ultimo regolamento dell'archivio mensile (basta l'ultimo file con righe)."""
    from research.src.dati import funding_da_zip
    for p in reversed(sorted(cartella_archivio.glob("*.zip"))):
        righe = funding_da_zip(p)
        if righe:
            return max(r[0] for r in righe)
    return None


def _date_candele(cartella_giorni: Path) -> list:
    """Le date dei file di candele giornaliere (``AAAA-MM-GG``; il primo del mese per i file mensili)."""
    out = []
    for p in cartella_giorni.glob("*-1d-*.zip"):
        x = p.name.rsplit("-1d-", 1)[1][:-4]
        out.append(x if len(x) == 10 else x + "-01")
    return out


def da_scaricare(dati: Path, esclusi=(), tipi=None, oggi: datetime | None = None) -> dict:
    """Le monete da chiedere e da quando (ms): quelle con una candela giornaliera negli ultimi ``GIORNI_RECENTI`` giorni, dal
    primo istante dopo l'ultimo regolamento dell'archivio o dei file di qui (per una moneta senza funding: dalla prima candela).
    Fuori gli esclusi per nome e i contratti che oggi non sono monete (``tipi_contratto``)."""
    from research.programma6 import tipi_contratto as tc
    tipi = tc.leggi() if tipi is None else tipi
    recente = ((oggi or datetime.now(timezone.utc)) - timedelta(days=GIORNI_RECENTI)).strftime("%Y-%m-%d")
    out = {}
    for d in sorted(p for p in dati.iterdir() if p.is_dir() and p.name not in esclusi):
        t = tipi.get(d.name)
        if t is not None and not tc.e_moneta_ricerca(t):
            continue
        date = _date_candele(d / "giorni")
        if not date or max(date) < recente:
            continue
        a, _ = leggi(d / CARTELLA)
        ultimi = [x for x in (ultimo_archivio_ms(d / "funding"), int(a["ts"].max()) if len(a) else None) if x is not None]
        if ultimi:
            out[d.name] = max(ultimi) + 1
        else:
            out[d.name] = int(datetime.strptime(min(date), "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()) * 1000
    return out


def main(argv=None) -> dict:
    from research.programma6 import seconda as sc
    argv = sys.argv[1:] if argv is None else argv
    scelte = set(argv[argv.index("--simboli") + 1].split(",")) if "--simboli" in argv else None
    piano = da_scaricare(sc.DATI, sc.ESCLUSI)
    if scelte is not None:
        piano = {s: v for s, v in piano.items() if s in scelte}
    esito = {"monete": len(piano), "scritte": 0, "senza_righe": [], "errori": [], "righe": 0, "bloccato": None}
    di_fila = 0
    try:
        for k, (s, dal) in enumerate(sorted(piano.items())):
            if k:
                time.sleep(PAUSA)
            cartella = sc.DATI / s / CARTELLA
            righe, fino = scarica_moneta(s, dal, int(time.time() * 1000))
            if fino is None:
                esito["errori"].append(s)
                di_fila += 1
                if di_fila >= ERRORI_DI_FILA:              # l'interfaccia non risponde: si smette, restano i file gia' scaricati
                    raise Bloccato(f"{ERRORI_DI_FILA} errori di fila, l'ultimo a {s}")
                continue
            di_fila = 0
            if not righe:
                esito["senza_righe"].append(s)
                if not any(fino_dal_nome(p.name) for p in (cartella.glob("*.csv") if cartella.is_dir() else [])):
                    continue                           # niente da scrivere: nessun file e nessun regolamento nuovo
            salva(cartella, s, righe, fino)            # anche senza righe nuove: il file si dice completo fino ad adesso
            esito["scritte"] += 1
            esito["righe"] += len(righe)
    except Bloccato as ex:
        esito["bloccato"] = str(ex)
    print(f"[funding_api] monete {esito['monete']}, file scritti {esito['scritte']}, righe nuove {esito['righe']}, "
          f"senza righe nuove {len(esito['senza_righe'])}, errori {len(esito['errori'])}"
          + (f" ({', '.join(esito['errori'][:10])})" if esito["errori"] else "")
          + (f"; FERMATO prima della fine: {esito['bloccato']}" if esito["bloccato"] else ""), flush=True)
    return esito


if __name__ == "__main__":
    main()
