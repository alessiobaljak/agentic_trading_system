"""Prova del codice senza numeri (lezioni/metodo.md): le quattro fabbriche di un modulo girano su prezzi INVENTATI.

Nessun dato di mercato, nessun esame: candele sintetiche (passeggiata casuale con seme fisso), motore con
l'ingresso a limite del terreno. Stampa solo «ok» per ogni variante, o l'errore. Controlla anche che la
strategia casuale con le barre di segnale dei trade della variante rifaccia gli stessi trade (il controllo
che gruppo.py fa su ogni moneta).

Uso: python3 -u research/campagne/PANIERE/codice/prova_codice.py <modulo.py> <file JSON con la lista dei p>
"""

import importlib.util
import json
import random
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE))

from research.src import motore  # noqa: E402
from research.src.motore import Candela, Parametri  # noqa: E402

GIORNO = 86_400_000


class ContestoFinto:
    timeframe = "1d"
    ms_per_barra = GIORNO

    def __init__(self, btc):
        self._btc = btc

    def btc_chiuse_entro(self, ts):
        return [c for c in self._btc if c.close_ts <= ts]

    def funding_regolato_entro(self, ts):
        return []


def candele_finte(seme, n=900, inizio=1_577_836_800_000):
    rnd = random.Random(seme)
    prezzo = 100.0
    out = []
    for i in range(n):
        apertura = prezzo
        prezzo = max(1.0, prezzo * (1 + rnd.gauss(0.001, 0.04)))
        alto = max(apertura, prezzo) * (1 + abs(rnd.gauss(0, 0.015)))
        basso = min(apertura, prezzo) * (1 - abs(rnd.gauss(0, 0.015)))
        ts = inizio + i * GIORNO
        out.append(Candela(ts, apertura, alto, basso, prezzo, 1000.0, ts + GIORNO - 1))
    return out


def main():
    percorso = Path(sys.argv[1]).resolve()
    lista_p = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    spec = importlib.util.spec_from_file_location("variante_in_prova", percorso)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    candele = candele_finte(1)
    ctx = ContestoFinto(candele_finte(2))
    par = Parametri(ingresso="limite", limite_validita_barre=1, commissione_maker_per_lato=0.0002)
    for p in lista_p:
        nome = p.get("nome", str(p))
        try:
            crea = modulo.crea_variante(ctx, dict(p))
            crea_a = modulo.crea_a(ctx, dict(p))
            crea_cas = modulo.crea_casuale(ctx, dict(p))
            crea_seg = modulo.crea_segnale(ctx, dict(p))
            ris = motore.esegui(candele, None, None, [], crea(), par)
            motore.esegui(candele, None, None, [], crea_a(), par)
            motore.barre_vietate_segnale_non_valido(candele, crea_seg, par)
            indice = {c.ts: i for i, c in enumerate(candele)}
            segnali = frozenset(indice[t.ts_segnale] for t in ris.trades)
            rifatto = motore.esegui(candele, None, None, [], crea_cas(segnali), par)
            uguali = [(t.ts_entrata, t.ts_uscita, t.esito) for t in ris.trades] == \
                     [(t.ts_entrata, t.ts_uscita, t.esito) for t in rifatto.trades]
            durata = max((sum(1 for c in candele if t.ts_entrata <= c.ts <= t.ts_uscita) for t in ris.trades), default=0)
            print(nome, "ok" if uguali and ris.trades else "ATTENZIONE", "casuale uguale" if uguali else "casuale DIVERSA",
                  "con trade" if ris.trades else "SENZA trade", "durata massima entro il tetto" if durata <= 61 else "DURATA OLTRE")
        except Exception as errore:  # la prova deve dire l'errore, non fermarsi
            print(nome, "ERRORE", type(errore).__name__, errore)
    print("fatto")


if __name__ == "__main__":
    main()
