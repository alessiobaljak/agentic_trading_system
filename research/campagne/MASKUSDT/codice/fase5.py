"""Fase 5: prove dello scettico sul candidato MASKUSDT-029, solo costruzione, registrate prima.

1. Il filtro del funding regge anche sulle regole d'uscita originali della famiglia (006: target 1
   volta lo stop, uscita a 6 barre)? Se il filtro fosse solo rumore adattato a 028, su 006 non
   dovrebbe migliorare il t.
2. Il filtro e' solo un modo di entrare meno spesso? Si confronta con la (b) calcolata sugli stessi
   ingressi della variante senza filtro (gia' nel log: 028, t 2,08) — il t di 029 deve venire da
   R medio piu' alto, non da un errore piu' piccolo.
Non sono varianti: non cambiano il candidato e non ne producono altri.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import quadro  # noqa: E402
import registro  # noqa: E402
from campagna import _scrivi_esito, stampa  # noqa: E402
from registro_ritocchi import R2  # noqa: E402
from verifiche import breve  # noqa: E402


class FiltroSu006(R2):
    rr = 1.0
    barre_max = 6


def main():
    vid = "MASKUSDT-029-S-filtro-su-006"
    var = FiltroSu006()
    cont = quadro.conta(var)
    registro.aggiungi({"id": vid, "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": "MASKUSDT-029",
                       "verifica": "Fase 5, prova dello scettico: filtro del funding sulle regole di 006 (target 1, uscita 6 barre)",
                       "periodo": "costruzione", "trade_stimati": cont["trade"],
                       "previsione": "se il filtro ha un meccanismo, il t contro la (b) sale rispetto a 006 (1,54); se e' rumore adattato a 028, resta simile o scende",
                       "criterio_successo": "t contro la (b) sopra quello di 006"})
    e = quadro.valuta(var)
    _scrivi_esito(vid, e)
    b = breve(e)
    registro.aggiungi({"id": vid, "tipo": "risultato", "metriche_breve": b, "baseline_b": e.get("baseline_b")})
    stampa(vid, json.dumps(registro._pulisci(b)))
    print(json.dumps(registro._pulisci(b)))


if __name__ == "__main__":
    main()
