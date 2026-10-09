"""Fase 0 punto 2: scarico dei file mensili fino al 2023-12-31 (MATICUSDT e riferimento BTCUSDT).

MATICUSDT: klines e markPriceKlines su tutti i timeframe ammessi, piu' il funding,
dal 2020-10 (primo mese della scheda) al 2023-12. BTCUSDT: solo klines (last) sugli
stessi timeframe e mesi, come riferimento di mercato. Il blocco del vault e il
controllo del CHECKSUM remoto sono quelli di ``scarica_mese``. Un file gia' su disco
non si riscarica: per quelli si rilegge il CHECKSUM remoto e si confronta l'impronta
(cosi' anche i file di una corsa precedente hanno il controllo). Il rapporto va in
``data/insample/MATICUSDT/scarico_rapporto.txt`` (fuori da git).
"""
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402

TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO, FINE = date(2020, 10, 1), date(2023, 12, 31)
RAPPORTO = dati.RADICE_DEFAULT / "data" / "insample" / "MATICUSDT" / "scarico_rapporto.txt"

lavori = []
for anno, mese in dati.mesi_del_periodo(INIZIO, FINE):
    for tf in TF:
        lavori.append(("MATICUSDT", "klines", tf, anno, mese))
        lavori.append(("MATICUSDT", "markPriceKlines", tf, anno, mese))
        lavori.append(("BTCUSDT", "klines", tf, anno, mese))
    lavori.append(("MATICUSDT", "fundingRate", None, anno, mese))


def controlla_su_disco(lavoro, percorso):
    """Impronta del file su disco contro il CHECKSUM remoto: 'ok', 'senza_checksum' o 'diversa'."""
    simbolo, tipo, tf, anno, mese = lavoro
    url = dati.url_mese(simbolo, tipo, tf, anno, mese)
    testo = dati.fetch_http(dati.url_checksum(url))
    if testo is None:
        return "senza_checksum"
    attesa = dati.leggi_checksum(testo, url)
    return "ok" if attesa == dati.impronta_file(percorso) else "diversa"


def uno(lavoro):
    simbolo, tipo, tf, anno, mese = lavoro
    errore = None
    for _ in range(4):
        try:
            gia = dati.percorso_mese(simbolo, tipo, tf, anno, mese).is_file()
            p = dati.scarica_mese(simbolo, tipo, tf, anno, mese)
            if p is None:
                return lavoro, None, "assente"
            return lavoro, p, controlla_su_disco(lavoro, p) if gia else "ok_allo_scarico"
        except dati.IntegritaFallita as e:
            return lavoro, e, "integrita_fallita"
        except Exception as e:  # rete: si riprova
            errore = e
    return lavoro, errore, "errore"


with ThreadPoolExecutor(max_workers=12) as ex:
    esiti = list(ex.map(uno, lavori))

righe = []
conteggi = {}
for lavoro, _p, stato in esiti:
    conteggi[stato] = conteggi.get(stato, 0) + 1
    if stato not in ("ok", "ok_allo_scarico"):
        righe.append(f"{stato} {lavoro}")
righe.insert(0, f"file richiesti {len(lavori)}; esiti {conteggi}")
righe.append(f"CHECKSUM mancanti allo scarico: {len(dati.CHECKSUM_MANCANTI)}")
righe.extend(f"senza_checksum_allo_scarico {u}" for u in dati.CHECKSUM_MANCANTI)
RAPPORTO.write_text("\n".join(righe) + "\n", encoding="utf-8")
print(righe[0])
