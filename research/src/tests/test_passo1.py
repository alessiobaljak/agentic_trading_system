"""Il Passo 1 da capo a fondo, senza rete: un mondo finto (exchangeInfo, indice del
bucket con pagine, file mensili giornalieri del 2023) e la selezione che ne esce.

Cosa si protegge: il listing viene da exchangeInfo per i contratti di oggi e dal
primo file per i delistati; il volume si scarica SOLO per chi passa i filtri su
listing e fine dati (nessuno scarico inutile, nessun file del vault); i file
scritti (candidate, campagna, schede) e che la scheda non porti il delisting.
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


def _zip_1d(simbolo, anno, mese, volume_quote):
    """Un file mensile giornaliero finto: un giorno per riga, quote volume costante."""
    primo = date(anno, mese, 1)
    giorno = primo
    righe = ["open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore"]
    while giorno.month == mese:
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


def _mesi(da, a):
    out = []
    y, m = da
    while (y, m) <= a:
        out.append((y, m))
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


MONDO = {
    # simbolo: (negoziata oggi, onboardDate, mesi in archivio, volume quote giornaliero 2023)
    "BTCUSDT": (True, date(2019, 9, 8), _mesi((2020, 1), (2026, 9)), 20e9),
    "ALTUSDT": (True, date(2021, 6, 1), _mesi((2021, 6), (2026, 9)), 60e6),
    "NEWUSDT": (True, date(2022, 3, 1), _mesi((2022, 3), (2026, 9)), 5e9),       # troppo giovane
    "THINUSDT": (True, date(2020, 5, 1), _mesi((2020, 5), (2026, 9)), 3e6),      # illiquida
    "DEADUSDT": (False, None, _mesi((2020, 2), (2024, 8)), 300e6),               # morta nel vault: idonea
    "GONEUSDT": (False, None, _mesi((2020, 2), (2023, 5)), 1e9),                 # morta prima del 2024
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
        return _zip_1d(simbolo, anno, mese, MONDO[simbolo][3])
    return fetch


def test_passo1_da_capo_a_fondo(tmp_path):
    chiamate = []
    r = passo1.esegui(radice=tmp_path, fetch=_fetch_finto(chiamate), n=2, scrivi=True)
    assert [c.simbolo for c in r["campagna"]] == ["BTCUSDT", "DEADUSDT"]
    assert [c.simbolo for c in r["altre_idonee"]] == ["ALTUSDT"]
    assert {c.simbolo for c in r["escluse"]} == {"NEWUSDT", "THINUSDT", "GONEUSDT"}
    k = r["conteggi"]
    assert k["candidate"] == 6 and k["idonee"] == 3 and k["campagna_delistate_oggi"] == 1
    # il listing: exchangeInfo per i vivi, primo file per i morti
    btc = next(c for c in r["campagna"] if c.simbolo == "BTCUSDT")
    dead = next(c for c in r["campagna"] if c.simbolo == "DEADUSDT")
    assert btc.listing == date(2019, 9, 8) and btc.listing_da == "exchangeInfo"
    assert dead.listing == date(2020, 2, 1) and dead.listing_da == "archivio" and dead.delisting == date(2024, 8, 31)
    # il volume si scarica solo per chi passa listing e fine dati: 12 file x 4 contratti
    zip_scaricati = [u for u in chiamate if u.endswith(".zip")]
    assert len(zip_scaricati) == 12 * 4 and all("-2023-" in u for u in zip_scaricati)
    assert not any("NEWUSDT" in u or "GONEUSDT" in u for u in zip_scaricati)
    # i file scritti
    assert (tmp_path / "universo" / "monete_campagna.csv").exists()
    righe = (tmp_path / "universo" / "candidate.csv").read_text(encoding="utf-8").splitlines()
    assert len(righe) == 7 and righe[0].startswith("simbolo,")
    scheda = (tmp_path / "campagne" / "DEADUSDT" / "scheda_moneta.md").read_text(encoding="utf-8")
    assert "2020-02-01" in scheda and "2024" not in scheda
    assert not (tmp_path / "campagne" / "ALTUSDT").exists()
    conteggi = json.loads((tmp_path / "universo" / "conteggi.json").read_text(encoding="utf-8"))
    assert conteggi["conteggi"]["idonee_delistate_oggi"] == 1
