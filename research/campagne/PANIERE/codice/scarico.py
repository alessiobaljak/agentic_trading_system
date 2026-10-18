"""Fase 0, punto 2: scarico delle serie di regole.md del paniere, sezione 2, e confronto con impronte_1d.json.

Per le 80 monete di monete.csv (dal primo mese della scheda) e per BTCUSDT (dal 2020-01), fino al 2023-12:
candele giornaliere del last (klines/1d), del mark (markPriceKlines/1d) e funding (fundingRate). Nessun
altro timeframe, nessuna data oltre il 2023-12-31. Solo con research/src/dati.py (scarica_mese, con il
CHECKSUM remoto acceso). Ogni file si prova al massimo 3 volte (regole del gruppo, sezione 2, punto 9):
un 404 è un buco; un errore che resiste a 3 tentativi si scrive e lo scarico finisce con un errore (STOP).

Avanzamento ed esito si scrivono man mano in lavoro/scarico_esito.json, così si leggono anche se lo
script si interrompe. Alla fine verifica_impronte confronta ogni simbolo con impronte_1d.json, sui soli
file delle serie scaricate; i file registrati di altre serie si elencano a parte (non si scaricano).
"""

import csv
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE))

from research.src import dati  # noqa: E402

CARTELLA = RADICE / "research" / "campagne" / "PANIERE"
ESITO = CARTELLA / "lavoro" / "scarico_esito.json"
SERIE = (("klines", "1d"), ("markPriceKlines", "1d"), ("fundingRate", None))
PREFISSI = ("klines/1d/", "markPriceKlines/1d/", "fundingRate/")
TENTATIVI = 3
FINE = date(2023, 12, 31)


def monete():
    with open(CARTELLA / "monete.csv", encoding="utf-8") as f:
        return [riga["simbolo"] for riga in csv.DictReader(f)]


def scarica_con_tentativi(simbolo, tipo, intervallo, anno, mese):
    ultimo = None
    for tentativo in range(1, TENTATIVI + 1):
        try:
            percorso = dati.scarica_mese(simbolo, tipo, intervallo, anno, mese)
            return {"esito": "buco" if percorso is None else "ok", "tentativi": tentativo}
        except dati.IntegritaFallita as errore:
            ultimo = f"checksum: {errore}"
        except dati.VietatoInCampagna:
            raise
        except Exception as errore:  # rete: si riprova
            ultimo = f"{type(errore).__name__}: {errore}"
        time.sleep(2 * tentativo)
    return {"esito": "errore", "tentativi": TENTATIVI, "errore": ultimo}


def scrivi(stato):
    ESITO.write_text(json.dumps(stato, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    simboli = monete()
    inizi = {s: dati.leggi_scheda_gruppo(s)["primo_mese"] for s in simboli}
    inizi["BTCUSDT"] = date(2020, 1, 1)
    compiti = []
    for s in list(simboli) + ["BTCUSDT"]:
        for tipo, intervallo in SERIE:
            for anno, mese in dati.mesi_del_periodo(inizi[s], FINE):
                compiti.append((s, tipo, intervallo, anno, mese))
    dati.azzera_checksum_mancanti()
    stato = {"compiti": len(compiti), "fatti": 0, "ok": 0, "buchi": [], "errori": [], "finito": False}
    scrivi(stato)
    print("compiti", len(compiti))
    with ThreadPoolExecutor(max_workers=8) as esecutore:
        futuri = {esecutore.submit(scarica_con_tentativi, *c): c for c in compiti}
        for futuro in as_completed(futuri):
            s, tipo, intervallo, anno, mese = futuri[futuro]
            nome = f"{s} {tipo} {intervallo or ''} {anno}-{mese:02d}"
            r = futuro.result()
            stato["fatti"] += 1
            if r["esito"] == "ok":
                stato["ok"] += 1
            elif r["esito"] == "buco":
                stato["buchi"].append(nome)
            else:
                stato["errori"].append({"file": nome, "errore": r["errore"]})
            if stato["fatti"] % 500 == 0:
                stato["checksum_mancanti"] = list(dati.CHECKSUM_MANCANTI)
                scrivi(stato)
                print("fatti", stato["fatti"], "errori", len(stato["errori"]))
    stato["buchi"].sort()
    stato["checksum_mancanti"] = list(dati.CHECKSUM_MANCANTI)

    impronte = json.loads((CARTELLA / "impronte_1d.json").read_text(encoding="utf-8"))
    confronto = {}
    non_scaricati = {}
    for s in list(simboli) + ["BTCUSDT"]:
        attese = impronte.get(s, {})
        da_confrontare = {n: h for n, h in attese.items() if n.startswith(PREFISSI)}
        altre = sorted(n for n in attese if not n.startswith(PREFISSI))
        differenze = dati.verifica_impronte(s, dati.RADICE_DEFAULT, da_confrontare)
        su_disco = dati.calcola_impronte(s)
        in_piu = sorted(n for n in su_disco if n not in attese)
        confronto[s] = {"attese": len(da_confrontare), "differenze": differenze, "file_in_piu_su_disco": in_piu}
        if altre:
            non_scaricati[s] = {"n": len(altre), "primo": altre[0], "ultimo": altre[-1]}
    stato["confronto_impronte"] = confronto
    stato["registrati_non_scaricati"] = non_scaricati
    stato["simboli_con_differenze"] = sorted(s for s, c in confronto.items() if c["differenze"])
    stato["simboli_con_file_in_piu"] = sorted(s for s, c in confronto.items() if c["file_in_piu_su_disco"])
    stato["finito"] = True
    scrivi(stato)
    print("ok", stato["ok"], "buchi", len(stato["buchi"]), "errori", len(stato["errori"]),
          "checksum mancanti", len(stato["checksum_mancanti"]))
    print("simboli con differenze", stato["simboli_con_differenze"])
    print("simboli con file in piu", stato["simboli_con_file_in_piu"])
    print("registrati e non scaricati", non_scaricati)
    print("fatto")
    if stato["errori"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
