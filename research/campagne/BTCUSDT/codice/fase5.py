"""Fase 5: i test dello scettico, sui dati di costruzione, registrati prima di eseguirli.

* V10, V11: stop fisso al 2% dal close per il candidato e per le sue baseline (stesso
  calcolo del segnale). Se il vantaggio contro la (b) era un effetto della normalizzazione
  in R (stop all'apertura del giorno, vicinissimo per gli ingressi a caso), qui sparisce.
* famiglia V19 (V32, V33, V35): placebo d'orario. La stessa regola con il segnale in altre
  mezz'ore del giorno (03:00, 07:00, 11:00, 15:00, 19:00 UTC, uscita mezz'ora dopo). Se
  l'effetto e' di fine giornata, le ore placebo non battono la (b).
Uso: python fase5.py stop V10 V11 | python fase5.py placebo V35 [V33 V32]
"""
import sys

import fase4
import quadro
from comune import SIMBOLO, aggiungi_log
from quadro import Variante
from research.src.motore import Segnale


def con_stop_fisso(v, pct=0.02):
    base_segnale = v.segnale

    def segnale(stato, storia):
        s = base_segnale(stato, storia)
        if s is None:
            return None
        c = storia[-1].close
        return Segnale(s.direzione, stop=c * (1 - pct) if s.direzione == "long" else c * (1 + pct))

    return Variante(v.id, v.tf, v.direzione, v.prepara, v.condizione, segnale, v.uscita)


def registra_ed_esegui(lid, vid, nome, criterio, crea):
    aggiungi_log({"id": lid, "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": f"{SIMBOLO}-{vid}",
                  "verifica": nome, "fase": 5, "periodo": "costruzione", "criterio_successo": criterio})
    v = crea()
    n = quadro.conta(v)["trade"]
    e = quadro.valuta_costruzione(v)
    voce = {"id": lid, "tipo": "risultato", "trade_contati": n, **fase4._ridotto(e)}
    aggiungi_log(voce)
    print(lid, voce["trade"], voce["r_medio"], voce["baseline_b"], flush=True)
    return voce


if sys.argv[1] == "stop":
    for vid in sys.argv[2:]:
        crit = ("con lo stop fisso al 2% (candidato, (a) e (b)) il candidato batte ancora nettamente la (b) e ha R medio > 0; "
                "altrimenti il vantaggio di Fase 2 si attribuisce alla normalizzazione in R e il candidato non va in validazione")
        registra_ed_esegui(f"{SIMBOLO}-{vid}-S01", vid, "scettico: stop fisso al 2%", crit,
                           lambda vid=vid: con_stop_fisso(fase4.costruisci(vid)[0]))
elif sys.argv[1] == "placebo":
    for vid in sys.argv[2:]:
        for k, ora in enumerate((3, 7, 11, 15, 19), start=1):
            crit = ("placebo: se almeno 2 delle 5 ore battono nettamente la (b), l'effetto non e' di fine giornata e "
                    "il candidato non va in validazione")
            registra_ed_esegui(f"{SIMBOLO}-{vid}-P{k:02d}", vid, f"scettico: placebo d'orario, segnale alle {ora:02d}:00 UTC",
                               crit, lambda vid=vid, ora=ora: fase4.costruisci(vid, ora_segnale_min=ora * 60)[0])
