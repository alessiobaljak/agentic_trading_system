"""Fase 0: verifica di ogni file in-sample contro il CHECKSUM remoto e copia delle impronte.

Scrive data/insample/BTCUSDT/fase0_verifica.json e campagne/BTCUSDT/impronte.json.
"""
import hashlib
import json
from datetime import date, datetime, timezone

from comune import CARTELLA, SIMBOLO, TIMEFRAME, dati

INIZIO, FINE = date(2020, 1, 1), date(2023, 12, 31)
DATI = CARTELLA.parents[1] / "data" / "insample" / SIMBOLO
esito = {"ok": 0, "diversi": [], "senza_checksum": [], "mancanti": []}
for tipo in ("klines", "markPriceKlines", "fundingRate"):
    for tf in (TIMEFRAME if tipo != "fundingRate" else [None]):
        for anno, mese in dati.mesi_del_periodo(INIZIO, FINE):
            p = dati.percorso_mese(SIMBOLO, tipo, tf, anno, mese)
            url = dati.url_mese(SIMBOLO, tipo, tf, anno, mese)
            if not p.is_file():
                esito["mancanti"].append(url)
                continue
            for tentativo in range(5):
                try:
                    testo = dati.fetch_http(dati.url_checksum(url))
                    break
                except OSError:
                    import time
                    time.sleep(2 ** tentativo)
            else:
                raise RuntimeError(f"rete: {url}")
            if testo is None:
                esito["senza_checksum"].append(url)
                continue
            if dati.leggi_checksum(testo, url) == dati.impronta_file(p):
                esito["ok"] += 1
            else:
                esito["diversi"].append(url)

# buchi del mark a 1h
ms = 3_600_000
mark = dati.carica_candele(SIMBOLO, "1h", INIZIO, FINE, tipo="markPriceKlines")
buchi = []
for a, b in zip(mark, mark[1:]):
    if b.ts != a.ts + ms:
        buchi.append([datetime.fromtimestamp((a.ts + ms) / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M"),
                      (b.ts - a.ts) // ms - 1])
esito["buchi_mark_1h"] = buchi
# scarto in ms dei settlement di funding rispetto all'ora piena
righe = dati.carica_funding_dettaglio(SIMBOLO, INIZIO, FINE)
scarti = [t % ms for t, _o, _r in righe]
esito["funding_scarto_ms_max"] = max(scarti)
esito["funding_con_scarto"] = sum(1 for s in scarti if s)

impronte = dati.calcola_impronte(SIMBOLO)
testo = json.dumps(impronte, indent=1, sort_keys=True) + "\n"
(CARTELLA / "impronte.json").write_text(testo)
esito["impronte_file"] = len(impronte)
esito["sha256_impronte_json"] = hashlib.sha256(testo.encode()).hexdigest()
(DATI / "fase0_verifica.json").write_text(json.dumps(esito, indent=1))
print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in esito.items()}))
