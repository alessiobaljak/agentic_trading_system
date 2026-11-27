"""L'archivio delle notizie di Alpaca (fonte Benzinga), un file per mese nella cartella dei dati (mai nel repository: licenza).

    scarica(2016, 2024, minuti=240)   # riprende da dove era arrivato; si ferma da solo dopo `minuti`
    carica(2016, 2024)                # una riga per notizia: creata (UTC), simboli (lista), testo (titolo e riassunto)
"""
from __future__ import annotations

import time
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from stock.dati import alpaca
from stock.dati.archivio import cartella_dati


def _file(anno: int, mese: int):
    return cartella_dati() / "notizie" / f"{anno}-{mese:02d}.csv.gz"


def mesi(dal_anno: int, al_anno: int) -> list[tuple[int, int]]:
    return [(a, m) for a in range(dal_anno, al_anno + 1) for m in range(1, 13)]


def mesi_fra(dal: tuple[int, int], al: tuple[int, int]) -> list[tuple[int, int]]:
    """I mesi (anno, mese) da `dal` ad `al` compresi."""
    return [(a, m) for a in range(dal[0], al[0] + 1) for m in range(1, 13) if dal <= (a, m) <= al]


def mancanti(dal_anno: int, al_anno: int, elenco: list[tuple[int, int]] | None = None) -> list[tuple[int, int]]:
    return [(a, m) for a, m in (elenco or mesi(dal_anno, al_anno)) if not _file(a, m).exists()]


# chiusure anticipate della borsa (alle 13:00 di New York), dal calendario della NYSE: la prova 45 entra alle 12:30
CHIUSURE_ANTICIPATE = {date(2026, 11, 27), date(2026, 12, 24)}


def ordini_in_corso(adesso: datetime) -> bool:
    """Vero nei minuti in cui le strategie del demo mandano gli ordini (giorni feriali, ora di New York): lì non si scarica, per non
    consumare il limite di richieste di Alpaca, che ricerca e demo condividono. Le finestre (audit del 27 novembre 2026): la riserva
    della sera della miscela del mattino (8:20-8:50), l'apertura della prima candela (9:05-10:10), la prova 45 e la chiusura della prima
    candela (15:25-16:20), la sera della miscela (19:00-19:20); nei giorni della banca centrale e nelle loro vigilie le 13:50-14:10 della
    miscela; nelle chiusure anticipate le 12:25-13:20 della prova 45."""
    from stock.dati.fomc import COMUNICATI_AVANTI
    ny = adesso.astimezone(ZoneInfo("America/New_York"))
    if ny.weekday() >= 5:
        return False
    minuti = ny.hour * 60 + ny.minute
    finestre = [(8 * 60 + 20, 8 * 60 + 50), (9 * 60 + 5, 10 * 60 + 10), (15 * 60 + 25, 16 * 60 + 20), (19 * 60, 19 * 60 + 20)]
    giorno = ny.date()
    if giorno in COMUNICATI_AVANTI or giorno + timedelta(days=1) in COMUNICATI_AVANTI:
        finestre.append((13 * 60 + 50, 14 * 60 + 10))
    if giorno in CHIUSURE_ANTICIPATE:
        finestre.append((12 * 60 + 25, 13 * 60 + 20))
    return any(da <= minuti <= a for da, a in finestre)


def scarica(dal_anno: int, al_anno: int, minuti: float = 240, pausa: float = 0.5,
            elenco: list[tuple[int, int]] | None = None) -> list[tuple[int, int]]:
    """Scarica i mesi che mancano, uno alla volta (il file si scrive solo a mese completo); restituisce quelli rimasti.
    Si ferma dopo `minuti`, e non scarica nei minuti degli ordini (`ordini_in_corso`)."""
    partenza = time.monotonic()
    for a, m in mancanti(dal_anno, al_anno, elenco):
        if time.monotonic() - partenza > minuti * 60:
            break
        if ordini_in_corso(datetime.now(UTC)):
            print("minuti degli ordini: mi fermo, rilanciare dopo", flush=True)
            break
        inizio = datetime(a, m, 1, tzinfo=UTC)
        fine = datetime(a + (m == 12), m % 12 + 1, 1, tzinfo=UTC)
        n, completo = alpaca.notizie(None, inizio, fine, pagine_massime=100_000, pausa=pausa)
        if not completo:
            raise RuntimeError(f"{a}-{m:02d}: elenco non completo")
        df = pd.DataFrame({"id": [x.get("id") for x in n], "creata": [x.get("created_at") for x in n],
                           "simboli": [" ".join(x.get("symbols") or []) for x in n],
                           "titolo": [(x.get("headline") or "").replace("\n", " ") for x in n],
                           "riassunto": [(x.get("summary") or "").replace("\n", " ") for x in n]})
        df = df[df["creata"] < fine.isoformat().replace("+00:00", "Z")].drop_duplicates("id")
        p = _file(a, m)
        p.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(p, index=False, compression="gzip")
        print(f"notizie {a}-{m:02d}: {len(df)} ({(time.monotonic() - partenza) / 60:.0f} min)", flush=True)
    return mancanti(dal_anno, al_anno, elenco)


def carica(dal_anno: int, al_anno: int, elenco: list[tuple[int, int]] | None = None) -> pd.DataFrame:
    pezzi = []
    for a, m in (elenco or mesi(dal_anno, al_anno)):
        df = pd.read_csv(_file(a, m), dtype=str, keep_default_na=False)
        pezzi.append(pd.DataFrame({"creata": pd.to_datetime(df["creata"], utc=True, format="ISO8601"),
                                   "simboli": df["simboli"].str.split(),
                                   "testo": df["titolo"] + " " + df["riassunto"]}))
    return pd.concat(pezzi, ignore_index=True).sort_values("creata", kind="stable").reset_index(drop=True)
