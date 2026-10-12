"""Fase 0, punto 1 (regole.md, sezione 2, punto 1): le date per moneta da dati.periodi_gruppo, prima di caricare un prezzo.

Uso: python3 -u fase0_periodi.py [DATA_DA_date_-u]  (con la data scrive anche la nota nel log).
"""
import json
import sys

from comune import aggiungi_al_log, periodi, prossimo_id, schede

if __name__ == "__main__":
    sch = schede()
    p = periodi()
    print("fine_costruzione", p["fine_costruzione"], "inizio_validazione", p["inizio_validazione"],
          "giorni_validazione", p["giorni_validazione"], "giorni_moneta", p["giorni_moneta"],
          "obiettivo", p["giorni_moneta_obiettivo"], "costruzione", p["giorni_moneta_costruzione"],
          "validazione", p["giorni_moneta_validazione"])
    giorni_c = [v["giorni_costruzione"] for v in p["monete"].values()]
    print("giorni di costruzione per moneta: da", min(giorni_c), "a", max(giorni_c))
    tabella = {}
    for s in sch:
        v = p["monete"][s]
        tabella[s] = {"inizio_costruzione": str(v["inizio"]), "fine_costruzione": str(v["fine_costruzione"]),
                      "inizio_validazione": str(v["inizio_validazione"]),
                      "giorni_costruzione": v["giorni_costruzione"]}
    print(json.dumps(tabella, ensure_ascii=False))
    if len(sys.argv) > 1:
        voce = {
            "id": prossimo_id(), "tipo": "nota", "data": sys.argv[1],
            "testo": ("Fase 0, punto 1 (regole.md, sezione 2, punto 1), prima di caricare qualunque prezzo: date da "
                      "dati.periodi_gruppo sui primi mesi delle 80 schede (monete.csv, impronta 0cf217c3...d8e2 "
                      "verificata con sha256sum). Taglio comune: fine della costruzione "
                      f"{p['fine_costruzione']} 23:59:59.999 UTC per tutte, validazione dal {p['inizio_validazione']} "
                      f"al {p['fine_validazione']} ({p['giorni_validazione']} giorni). Giorni-moneta {p['giorni_moneta']}, "
                      f"obiettivo {p['giorni_moneta_obiettivo']}, costruzione {p['giorni_moneta_costruzione']}, "
                      f"validazione {p['giorni_moneta_validazione']}; costruzione da {min(giorni_c)} a {max(giorni_c)} "
                      "giorni per moneta: coincidono con regole.md, sezione 1, punto 3. Per ogni moneta, in "
                      "periodi_per_moneta: inizio della costruzione, fine della costruzione, inizio della validazione."),
            "periodi_per_moneta": tabella,
        }
        aggiungi_al_log(voce)
        print("nota scritta:", voce["id"])
