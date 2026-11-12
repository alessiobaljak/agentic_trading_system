"""L'archivio delle notizie di Alpaca (fonte Benzinga), un file per mese nella cartella dei dati (mai nel repository: licenza).

    scarica(2016, 2024, minuti=240)   # riprende da dove era arrivato; si ferma da solo dopo `minuti`
    carica(2016, 2024)                # una riga per notizia: creata (UTC), simboli (lista), testo (titolo e riassunto)
"""
from __future__ import annotations

import time
from datetime import UTC, datetime

import pandas as pd

from stock.dati import alpaca
from stock.dati.archivio import cartella_dati


def _file(anno: int, mese: int):
    return cartella_dati() / "notizie" / f"{anno}-{mese:02d}.csv.gz"


def mesi(dal_anno: int, al_anno: int) -> list[tuple[int, int]]:
    return [(a, m) for a in range(dal_anno, al_anno + 1) for m in range(1, 13)]


def mancanti(dal_anno: int, al_anno: int) -> list[tuple[int, int]]:
    return [(a, m) for a, m in mesi(dal_anno, al_anno) if not _file(a, m).exists()]


def scarica(dal_anno: int, al_anno: int, minuti: float = 240) -> list[tuple[int, int]]:
    """Scarica i mesi che mancano, uno alla volta (il file si scrive solo a mese completo); restituisce quelli rimasti."""
    partenza = time.monotonic()
    for a, m in mancanti(dal_anno, al_anno):
        if time.monotonic() - partenza > minuti * 60:
            break
        inizio = datetime(a, m, 1, tzinfo=UTC)
        fine = datetime(a + (m == 12), m % 12 + 1, 1, tzinfo=UTC)
        n, completo = alpaca.notizie(None, inizio, fine, pagine_massime=100_000)
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
    return mancanti(dal_anno, al_anno)


def carica(dal_anno: int, al_anno: int) -> pd.DataFrame:
    pezzi = []
    for a, m in mesi(dal_anno, al_anno):
        df = pd.read_csv(_file(a, m), dtype=str, keep_default_na=False)
        pezzi.append(pd.DataFrame({"creata": pd.to_datetime(df["creata"], utc=True),
                                   "simboli": df["simboli"].str.split(),
                                   "testo": df["titolo"] + " " + df["riassunto"]}))
    return pd.concat(pezzi, ignore_index=True).sort_values("creata", kind="stable").reset_index(drop=True)
