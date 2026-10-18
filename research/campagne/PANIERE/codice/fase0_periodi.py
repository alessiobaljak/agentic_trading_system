"""Fase 0, punto 1 (regole del gruppo, sezione 2, punto 1): periodi delle 80 monete del paniere, prima di caricare un prezzo.

Legge monete.csv e le schede del paniere con dati.leggi_scheda_gruppo, calcola il taglio comune con
dati.periodi_gruppo e scrive tutto in lavoro/fase0_periodi.json. Riassume anche impronte_1d.json
(quanti file per moneta e per tipo, primo e ultimo nome), senza aprire nessun file di dati.
"""

import csv
import json
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE))

from research.src import dati  # noqa: E402

CARTELLA = RADICE / "research" / "campagne" / "PANIERE"


def monete():
    with open(CARTELLA / "monete.csv", encoding="utf-8") as f:
        return [riga["simbolo"] for riga in csv.DictReader(f)]


def main():
    simboli = monete()
    schede = {s: dati.leggi_scheda_gruppo(s) for s in simboli}
    p = dati.periodi_gruppo({s: schede[s]["primo_mese"] for s in simboli})
    uscita = {
        "n_monete": len(simboli),
        "fine_costruzione": p["fine_costruzione"].isoformat(),
        "inizio_validazione": p["inizio_validazione"].isoformat(),
        "fine_validazione": p["fine_validazione"].isoformat(),
        "giorni_validazione": p["giorni_validazione"],
        "giorni_moneta": p["giorni_moneta"],
        "giorni_moneta_obiettivo": p["giorni_moneta_obiettivo"],
        "giorni_moneta_costruzione": p["giorni_moneta_costruzione"],
        "giorni_moneta_validazione": p["giorni_moneta_validazione"],
        "monete": {
            s: {
                "primo_mese": schede[s]["primo_mese"].isoformat(),
                "slippage_per_lato": schede[s]["slippage_per_lato"],
                "inizio_costruzione": p["monete"][s]["inizio"].isoformat(),
                "fine_costruzione": p["monete"][s]["fine_costruzione"].isoformat(),
                "inizio_validazione": p["monete"][s]["inizio_validazione"].isoformat(),
                "giorni_costruzione": p["monete"][s]["giorni_costruzione"],
            }
            for s in simboli
        },
    }
    impronte = json.loads((CARTELLA / "impronte_1d.json").read_text(encoding="utf-8"))
    riassunto = {}
    for s in sorted(impronte):
        per_tipo = {}
        for nome in sorted(impronte[s]):
            tipo = nome.split("/")[0]
            per_tipo.setdefault(tipo, []).append(nome)
        riassunto[s] = {t: {"n": len(v), "primo": v[0], "ultimo": v[-1]} for t, v in per_tipo.items()}
    uscita["impronte"] = {
        "n_simboli": len(impronte),
        "n_file": sum(len(v) for v in impronte.values()),
        "simboli_fuori_elenco": sorted(set(impronte) - set(simboli)),
        "monete_senza_impronte": sorted(set(simboli) - set(impronte)),
        "per_simbolo": riassunto,
    }
    destinazione = CARTELLA / "lavoro" / "fase0_periodi.json"
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    destinazione.write_text(json.dumps(uscita, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("fine costruzione", uscita["fine_costruzione"], "giorni validazione", uscita["giorni_validazione"])
    print("giorni-moneta", uscita["giorni_moneta"], "obiettivo", uscita["giorni_moneta_obiettivo"],
          "costruzione", uscita["giorni_moneta_costruzione"])
    gc = [v["giorni_costruzione"] for v in uscita["monete"].values()]
    print("giorni di costruzione per moneta: da", min(gc), "a", max(gc))
    print("impronte: simboli", uscita["impronte"]["n_simboli"], "file", uscita["impronte"]["n_file"],
          "fuori elenco", uscita["impronte"]["simboli_fuori_elenco"],
          "monete senza impronte", uscita["impronte"]["monete_senza_impronte"])
    print("BTCUSDT", riassunto.get("BTCUSDT"))
    print("fatto")


if __name__ == "__main__":
    main()
