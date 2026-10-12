"""Fase 0, punto 1: scrive nel log le date di costruzione e validazione PRIMA dei prezzi."""
from comune import PERIODI, aggiungi_log, SIMBOLO

p = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in PERIODI.items()}
aggiungi_log({
    "id": f"{SIMBOLO}-N001",
    "tipo": "nota",
    "argomento": "rifiuto del guardiano",
    "testo": ("All'avvio un comando che leggeva requirements.txt (per sapere come installare pytest) "
              "e' stato rifiutato dal guardiano: percorso fuori da quelli ammessi. Errore mio, non aggirato: "
              "pytest, numpy, scipy e pyyaml installati con pip senza leggere il file. Test del guardiano: "
              "691 passati."),
})
aggiungi_log({
    "id": f"{SIMBOLO}-N002",
    "tipo": "nota",
    "argomento": "fase 0: periodi della campagna (scritti prima di caricare i prezzi)",
    "fonte": "scheda_moneta.md (primo mese 2020-01-01) e research/src/dati.py periodi_campagna",
    "periodi": p,
})
print(p)
