"""Fase 1, punto 7: registra nel log gli scarti per pochi trade e le varianti ammesse (prima dei test)."""
import sys
sys.path.insert(0, "research/campagne/SOLUSDT/codice")
import log

SCARTI = [
    ("I-02", "1h", "short", {"finestra": 90, "percentile": 95, "soglia": 0.0003}, {"grezzi": 57, "non_sovrapposti": 33}, "con il 90° percentile e soglia 0,02%: 96 grezzi, 45 non sovrapposti"),
    ("I-02", "1h", "long", {"finestra": 90, "percentile": 95, "soglia": 0.0003}, {"grezzi": 54, "non_sovrapposti": 25}, "con il 90° percentile e soglia 0,02%: 91 grezzi, 43 non sovrapposti"),
    ("I-04", "4h", "long", {"modo": "ritraccio", "soglia_atr": 1.0}, {"grezzi": 20, "non_sovrapposti": 20}, "con soglia 0,5 ATR: 29"),
    ("I-04", "4h", "short", {"modo": "ritraccio", "soglia_atr": 1.0}, {"grezzi": 33, "non_sovrapposti": 33}, "con soglia 0,5 ATR: 41"),
    ("I-06", "1h", "long", {"soglia_sigma": 3.0}, {"grezzi": 70, "non_sovrapposti": 59}, "con 2,5 sigma: 131 grezzi, 95 non sovrapposti (ancora sotto 100)"),
    ("I-06", "1h", "short", {"soglia_sigma": 3.0}, {"grezzi": 95, "non_sovrapposti": 80}, "con 2,5 sigma: 158 grezzi, 122 non sovrapposti: quella variante e' ammessa e registrata a parte"),
    ("I-07", "4h", "long", {"n_ingresso": 20, "n_uscita": 10}, {"grezzi": 237, "non_sovrapposti": 85}, "durata media con entrate casuali e stessa uscita: 18 barre; a 1h la stessa regola da' 325 non sovrapposti: registrata a parte"),
    ("I-07", "4h", "short", {"n_ingresso": 20, "n_uscita": 10}, {"grezzi": 195, "non_sovrapposti": 71}, "durata media con entrate casuali: 19 barre; a 1h 310: registrata a parte"),
    ("I-11", "4h", "long", {"n_media": 50, "mult": 3.0}, {"grezzi": 126, "non_sovrapposti": 45}, "con volume oltre 2 volte la media: 337 grezzi, 91 non sovrapposti (ancora sotto 100)"),
    ("I-12", "1h", "long", {"n_minimo": 100}, {"grezzi": 33, "non_sovrapposti": 28}, "con minimo su 50 barre: 68 grezzi, 54 non sovrapposti"),
    ("I-12", "1h", "short", {"n_minimo": 100}, {"grezzi": 45, "non_sovrapposti": 36}, "con minimo su 50 barre: 71 grezzi, 57 non sovrapposti"),
]

for idea, tf, d, par, stima, nota in SCARTI:
    log.scrivi({"id": f"SOLUSDT-{log.prossimo_numero():03d}", "tipo": "scarto", "fase": "1", "idea": idea,
                "timeframe": tf, "direzione": d, "parametri": par, "trade_stimati": stima,
                "motivo": "stima dei trade sotto il minimo di costruzione (100): nessun budget consumato",
                "nota": "Stima = segnali sui dati di costruzione 2021-01-01 -> 2023-01-04, senza eseguire il backtest; 'non sovrapposti' assume la durata attesa della posizione. Una sola soglia piu' larga provata, scelta solo sui conteggi: " + nota})
print(open("research/campagne/SOLUSDT/log.jsonl").read().count("\n"), "voci")
