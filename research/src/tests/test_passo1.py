"""Il Passo 1 da capo a fondo, senza rete: un mondo finto (exchangeInfo, indice del
bucket con pagine, file mensili giornalieri del 2023) e la selezione che ne esce.

Cosa si protegge: il listing viene da exchangeInfo per i contratti di oggi e dal
primo file per i delistati; il volume si scarica SOLO per chi passa i filtri su
listing, primo mese e fine dati al mese (nessuno scarico inutile, nessun file del
vault); la fine dei dati al giorno (file 2023-12 presente, ultima candela il 17
dicembre); un errore di scarico che resta il motivo, senza «nessun volume»; la
copertura incompleta segnalata e non esclusa; le sospette ridenominazioni
elencate; i file scritti (candidate, campagna, conteggi, schede) e che la scheda
non porti il delisting, ne' da dove viene la data di listing.
"""
import io
import json
import zipfile
from datetime import date, timedelta
from pathlib import Path

from research.src import dati
from research.src import passo1
from research.src import selezione as sel

MS_G = 86_400_000
T2023 = 1_672_531_200_000
PREF = "data/futures/um/monthly/klines/"


def _zip_1d(simbolo, anno, mese, volume_quote, ultimo_giorno=None):
    """Un file mensile giornaliero finto: un giorno per riga, quote volume costante;
    con ``ultimo_giorno`` le righe si fermano li' (contratto morto a meta' mese)."""
    primo = date(anno, mese, 1)
    giorno = primo
    righe = ["open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore"]
    while giorno.month == mese and (ultimo_giorno is None or giorno <= ultimo_giorno):
        ts = dati.ms_da_data(giorno)
        righe.append(f"{ts},1,2,0.5,1.5,10,{ts + MS_G - 1},{volume_quote},3,1,1,0")
        giorno += timedelta(days=1)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(f"{simbolo}-1d-{anno}-{mese:02d}.csv", "\n".join(righe) + "\n")
    return buf.getvalue()


def _pagina_prefissi(simboli, troncata=False):
    corpo = "".join(f"<CommonPrefixes><Prefix>{PREF}{s}/</Prefix></CommonPrefixes>" for s in simboli)
    return (f'<?xml version="1.0"?><ListBucketResult><Prefix>{PREF}</Prefix>'
            f"<IsTruncated>{'true' if troncata else 'false'}</IsTruncated>{corpo}</ListBucketResult>").encode()


def _pagina_chiavi(simbolo, mesi):
    corpo = "".join(f"<Contents><Key>{PREF}{simbolo}/1d/{simbolo}-1d-{a}-{m:02d}.zip</Key></Contents>" for a, m in mesi)
    return f'<?xml version="1.0"?><ListBucketResult><IsTruncated>false</IsTruncated>{corpo}</ListBucketResult>'.encode()


def _mesi(da, a, senza=()):
    out = []
    y, m = da
    while (y, m) <= a:
        if (y, m) not in senza:
            out.append((y, m))
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


#: un file mensile che non e' uno zip: lo scarico riesce, la lettura no
ROTTO = object()

MONDO = {
    # simbolo: (negoziata oggi, onboardDate, mesi in archivio, volume quote giornaliero 2023, ultimo giorno 2023)
    "BTCUSDT": (True, date(2019, 9, 8), _mesi((2020, 1), (2026, 9)), 20e9, None),
    "ALTUSDT": (True, date(2021, 6, 1), _mesi((2021, 6), (2026, 9)), 60e6, None),
    "NEWUSDT": (True, date(2022, 3, 1), _mesi((2022, 3), (2026, 9)), 5e9, None),         # troppo giovane: sospetta nuovo nome
    "THINUSDT": (True, date(2020, 5, 1), _mesi((2020, 5), (2026, 9)), 3e6, None),        # illiquida
    "DEADUSDT": (False, None, _mesi((2020, 2), (2024, 8)), 300e6, None),                 # morta nel vault: idonea
    "GONEUSDT": (False, None, _mesi((2020, 2), (2023, 5)), 1e9, None),                   # sparita a meta' 2023: sospetta
    "DECUSDT": (False, None, _mesi((2020, 3), (2023, 12)), 400e6, date(2023, 12, 17)),   # file 2023-12 ma morta il 17
    "HOLEUSDT": (True, date(2020, 6, 1), _mesi((2020, 6), (2026, 9), senza=((2023, 7),)), 80e6, None),  # un mese di buco
    "BADUSDT": (True, date(2020, 4, 1), _mesi((2020, 4), (2026, 9)), ROTTO, None),       # file del 2023 illeggibili
}


def _fetch_finto(chiamate):
    def fetch(url):
        chiamate.append(url)
        if "exchangeInfo" in url:
            syms = [{"symbol": s, "status": "TRADING", "contractType": "PERPETUAL", "quoteAsset": "USDT",
                     "onboardDate": dati.ms_da_data(v[1]), "deliveryDate": 4133404800000}
                    for s, v in MONDO.items() if v[0]]
            syms.append({"symbol": "BTCUSDT_240329", "status": "TRADING", "contractType": "CURRENT_QUARTER",
                         "quoteAsset": "USDT", "onboardDate": 1, "deliveryDate": 2})
            return json.dumps({"symbols": syms}).encode()
        if url.startswith(dati.URL_INDICE_ARCHIVIO):
            if "delimiter=" in url:
                return _pagina_prefissi(list(MONDO) + ["BTCUSDT_210326", "ETHUSDC"])
            simbolo = url.split("klines/")[1].split("/")[0]
            return _pagina_chiavi(simbolo, MONDO[simbolo][2])
        if url.endswith(".CHECKSUM"):
            return None
        # un file mensile giornaliero
        nome = url.rsplit("/", 1)[-1]
        simbolo = nome.split("-")[0]
        anno, mese = int(nome[-11:-7]), int(nome[-6:-4])
        assert anno == 2023, f"scarico fuori dal 2023: {url}"      # mai dati del vault
        _, _, mesi, volume, ultimo_giorno = MONDO[simbolo]
        if (anno, mese) not in mesi:
            return None                                             # 404: mese assente dall'archivio
        if volume is ROTTO:
            return b"questo non e' uno zip"
        return _zip_1d(simbolo, anno, mese, volume, ultimo_giorno)
    return fetch


def test_passo1_da_capo_a_fondo(tmp_path):
    chiamate = []
    r = passo1.esegui(radice=tmp_path, fetch=_fetch_finto(chiamate), n=2, scrivi=True)
    assert [c.simbolo for c in r["campagna"]] == ["BTCUSDT", "DEADUSDT"]
    assert [c.simbolo for c in r["altre_idonee"]] == ["HOLEUSDT", "ALTUSDT"]
    assert {c.simbolo for c in r["escluse"]} == {"NEWUSDT", "THINUSDT", "GONEUSDT", "DECUSDT", "BADUSDT"}
    k = r["conteggi"]
    assert k["candidate"] == 9 and k["idonee"] == 4 and k["escluse"] == 5 and k["campagna_delistate_oggi"] == 1
    assert k["escluse_per_listing"] == 1 and k["escluse_per_volume"] == 1 and k["escluse_per_errore_scarico"] == 1
    assert k["escluse_per_fine_dati"] == 2 and k["escluse_per_fine_dati_giorno"] == 1
    # il listing: exchangeInfo per i vivi, primo file per i morti (solo nel CSV, non nella scheda)
    btc = next(c for c in r["campagna"] if c.simbolo == "BTCUSDT")
    dead = next(c for c in r["campagna"] if c.simbolo == "DEADUSDT")
    assert btc.listing == date(2019, 9, 8) and btc.listing_da == "exchangeInfo"
    assert dead.listing == date(2020, 2, 1) and dead.listing_da == "archivio" and dead.delisting == date(2024, 8, 31)
    assert btc.ultimo_giorno_2023 == date(2023, 12, 31) and btc.giorni_2023 == 365
    # fine dei dati al giorno: il file 2023-12 c'e', ma l'ultima candela e' del 17 dicembre
    dec = next(c for c in r["escluse"] if c.simbolo == "DECUSDT")
    assert dec.ultimo_giorno_2023 == date(2023, 12, 17) and dec.giorni_2023 == 351
    assert dec.motivi_esclusione == ["dati che finiscono il 2023-12-17 (prima del 2023-12-31)"]
    # un errore di scarico resta IL motivo: niente «nessun volume nel 2023»
    bad = next(c for c in r["escluse"] if c.simbolo == "BADUSDT")
    assert len(bad.motivi_esclusione) == 1 and bad.motivi_esclusione[0].startswith("errore nello scarico del 2023: ")
    # la copertura incompleta si segnala, non esclude: HOLEUSDT e' idonea con 334 giorni
    hole = next(c for c in r["altre_idonee"] if c.simbolo == "HOLEUSDT")
    assert hole.giorni_2023 == 334 and r["copertura_incompleta"] == ["HOLEUSDT"]
    assert k["idonee_con_copertura_incompleta"] == 1
    # le sospette ridenominazioni: sparite nel 2022-2023 e nate nel 2022-2023, nessuna cucitura
    assert r["sospette_ridenominazioni"] == {"sparite_2022_2023": ["DECUSDT", "GONEUSDT"],
                                             "listate_2022_2023": ["NEWUSDT"]}
    assert all(c.serie_collegata == c.simbolo for c in r["campagna"] + r["altre_idonee"] + r["escluse"])
    # il volume si scarica solo per chi passa listing, primo mese e fine dati al mese: 12 file x 7 contratti
    zip_scaricati = [u for u in chiamate if u.endswith(".zip")]
    assert len(zip_scaricati) == 12 * 7 and all("-2023-" in u for u in zip_scaricati)
    assert not any("NEWUSDT" in u or "GONEUSDT" in u for u in zip_scaricati)
    # i file scritti
    assert (tmp_path / "universo" / "monete_campagna.csv").exists()
    righe = (tmp_path / "universo" / "candidate.csv").read_text(encoding="utf-8").splitlines()
    assert len(righe) == 10 and righe[0].startswith("simbolo,serie_collegata,")
    scheda = (tmp_path / "campagne" / "DEADUSDT" / "scheda_moneta.md").read_text(encoding="utf-8")
    assert "2020-02-01" in scheda and "2024" not in scheda
    # la scheda non dice da dove viene la data: «archivio» vorrebbe dire «delistata»
    assert "archivio" not in scheda and "exchangeInfo" not in scheda
    scheda_btc = (tmp_path / "campagne" / "BTCUSDT" / "scheda_moneta.md").read_text(encoding="utf-8")
    assert "2019-09-08" in scheda_btc and "exchangeInfo" not in scheda_btc
    assert "La data di listing può essere approssimata al primo giorno del mese." in scheda and \
        "La data di listing può essere approssimata al primo giorno del mese." in scheda_btc
    assert not (tmp_path / "campagne" / "ALTUSDT").exists()
    conteggi = json.loads((tmp_path / "universo" / "conteggi.json").read_text(encoding="utf-8"))
    assert conteggi["conteggi"]["idonee_delistate_oggi"] == 1
    assert conteggi["copertura_incompleta"] == ["HOLEUSDT"]
    assert conteggi["sospette_ridenominazioni"]["listate_2022_2023"] == ["NEWUSDT"]
