"""La prova sul conto demo SUO prima del primo avvio (condizione della quinta revisione del percorso degli ordini, 23 novembre 2026,
`revisioni/2026-11-23-quinta.md`): con la quantità minima di BTC verifica dal vivo come il demo tratta gli ordini condizionati.
Nessuna chiamata al modello. Alla fine il conto resta pulito (posizione chiusa, ordini annullati); a ogni errore si chiude tutto.

    python -m trader_ai.avvio controlla      # prima: deve dire «conto pulito per il primo avvio: sì»
    python -m trader_ai.prova                # la prova (dalla macchina: bash trader_ai/vps/installa.sh prova)

I punti (in parole semplici):
 1. il conto è pulito e nella modalità a una posizione;
 2. un'apertura minima a mercato riceve stop e obiettivo, e il demo li restituisce con i nostri nomi (tais / tait);
 3. un secondo stop «chiudi tutto» accanto al primo: il demo lo accetta o lo rifiuta? (serve a sapere come si sposta lo stop);
 4. uno stop già oltre il prezzo viene rifiutato (il trader in quel caso chiude subito);
 5. la chiusura con «solo riduzione» toglie la posizione; l'annullamento toglie stop e obiettivo;
 6. un ordine limite lontano dal prezzo con stop e obiettivo senza posizione: accettati o no? Poi annullamento: tutto sparisce;
 7. alla fine il conto è pulito: zero posizioni e zero ordini (la pulizia aspetta le pause chieste da Binance e riprova).
"""
from __future__ import annotations

import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from trader_ai.avvio import CARTELLA, CONFIG, Trader
from trader_ai.conto_demo import ContoDemo, arrotonda, controlla_chiavi, nostro


def _quantita_minima(c: ContoDemo, prezzo: float) -> float:
    f = c.filtri()
    passo = f["passo_quantita"]
    q = max(f["quantita_min"], math.ceil((max(f["valore_min"], 100.0) * 1.05 / prezzo) / passo) * passo)
    return arrotonda(q + passo / 2, passo)


def prova(c: ContoDemo) -> list:
    esiti = []

    def punto(n, cosa, ok, dettaglio=""):
        esiti.append({"punto": n, "cosa": cosa, "ok": ok, "dettaglio": str(dettaglio)[:300]})
        print(f"[prova] {n}. {'OK ' if ok else 'NO '} {cosa} {dettaglio}", flush=True)

    pos_tutte, ordini_tutti = c.posizioni_tutte(), c.ordini_tutti()
    motivo = Trader(c, lambda *_: None).estraneo(None, pos_tutte, ordini_tutti)
    if motivo is None and (pos_tutte or ordini_tutti):                # pulito vuol dire vuoto, anche di ordini nostri
        motivo = f"{len(pos_tutte)} posizioni e {len(ordini_tutti)} ordini aperti"
    punto(1, "conto pulito (zero posizioni, zero ordini) e a una posizione", motivo is None, motivo or "")
    if motivo:
        return esiti
    tick = c.filtri()["passo_prezzo"]
    ts = lambda s: f"tai{s}{int(time.time() * 1000)}"
    try:
        prezzo = c.mercato()["prezzo"]
        q = _quantita_minima(c, prezzo)
        c.prepara(5)
        esito = c.apri("lungo", q, ts("o"))
        pos = next((p for p in c.posizioni_simbolo()), None)
        c.condizionato("lungo", "STOP_MARKET", arrotonda(prezzo * 0.97, tick), ts("s"))
        c.condizionato("lungo", "TAKE_PROFIT_MARKET", arrotonda(prezzo * 1.03, tick), ts("t"))
        algo = [o for o in c.ordini_simbolo() if o["_algo"]]
        nomi = sorted(str(o.get("clientAlgoId", "")) [:4] for o in algo)
        punto(2, "apertura minima con stop e obiettivo sul conto", pos is not None and nomi == ["tais", "tait"],
              f"quantità {q}, eseguita a {esito.get('avgPrice')}; campi di un ordine condizionato: "
              f"{sorted(algo[0].keys()) if algo else 'nessuno'}")
        try:
            c.condizionato("lungo", "STOP_MARKET", arrotonda(prezzo * 0.975, tick), ts("s"))
            punto(3, "secondo stop «chiudi tutto» accanto al primo", True, "ACCETTATO")
        except Exception as e:  # noqa: BLE001
            punto(3, "secondo stop «chiudi tutto» accanto al primo", True, f"RIFIUTATO: {e}")
        try:
            c.condizionato("lungo", "STOP_MARKET", arrotonda(prezzo * 1.01, tick), ts("s"))
            punto(4, "stop già oltre il prezzo rifiutato", False, "ACCETTATO: il trader non se ne accorgerebbe")
        except Exception as e:  # noqa: BLE001
            punto(4, "stop già oltre il prezzo rifiutato", True, e)
        c.chiudi({"lato": "lungo", "quantita": pos["quantita"] if pos else q}, ts("x"))
        time.sleep(2)
        resti = [p for p in c.posizioni_simbolo()], [o for o in c.ordini_simbolo() if nostro(o)]
        punto(5, "chiusura e annullamento: niente posizione, niente ordini", resti == ([], []), resti)
        prezzo = c.mercato()["prezzo"]
        limite = arrotonda(prezzo * 0.90, tick)
        c.apri("lungo", _quantita_minima(c, limite), ts("o"), "LIMIT", limite)
        accettati = []
        for tipo, livello, sigla in (("STOP_MARKET", 0.88, "s"), ("TAKE_PROFIT_MARKET", 1.05, "t")):
            try:
                c.condizionato("lungo", tipo, arrotonda(prezzo * livello, tick), ts(sigla))
                accettati.append(f"{tipo} accettato senza posizione")
            except Exception as e:  # noqa: BLE001
                accettati.append(f"{tipo} RIFIUTATO senza posizione: {str(e)[:120]}")
        c.annulla_tutto()
        time.sleep(2)
        resti = [o for o in c.ordini_simbolo() if nostro(o)]
        punto(6, "ordine limite con stop e obiettivo, poi annullamento", not resti, "; ".join(accettati) + f"; resti {resti}")
    except Exception as e:  # noqa: BLE001
        punto(0, "errore durante la prova", False, e)
    finally:
        pulito, dettaglio = pulisci(c)
        punto(7, "conto pulito alla fine", pulito, dettaglio)
    return esiti


def pulisci(c: ContoDemo, tentativi: int = 8) -> tuple:
    """Chiude la posizione e annulla gli ordini; se Binance chiede una pausa la aspetta e riprova. (pulito, dettaglio)."""
    dettaglio = ""
    for _ in range(tentativi):
        attesa = c.pausa_fino - time.time()
        if attesa > 0:
            print(f"[prova] Binance chiede una pausa: aspetto {attesa:.0f} secondi", flush=True)
            time.sleep(attesa + 1)
        try:
            pos = next((p for p in c.posizioni_simbolo()), None)
            c.chiudi(pos, f"taix{int(time.time() * 1000)}")
            time.sleep(2)
            restano = c.posizioni_tutte(), c.ordini_tutti()
            if restano == ([], []):
                return True, "zero posizioni, zero ordini"
            dettaglio = f"restano {len(restano[0])} posizioni e {len(restano[1])} ordini"
        except Exception as e:  # noqa: BLE001
            dettaglio = str(e)[:200]
            time.sleep(5)
    return False, dettaglio + " — CHIUDI A MANO DAL SITO DEL DEMO"


def main() -> int:
    cfg = json.loads(CONFIG.read_text())
    chiave, segreto = controlla_chiavi()
    try:
        esiti = prova(ContoDemo(chiave, segreto, cfg["moneta"]))
    except Exception as e:  # noqa: BLE001 - anche un errore imprevisto lascia un esito scritto
        esiti = [{"punto": 0, "cosa": "errore imprevisto", "ok": False, "dettaglio": str(e)[:300]}]
    f = Path(os.environ.get("TRADER_AI_DATI") or CARTELLA) / f"prova_{datetime.now(timezone.utc):%Y-%m-%d_%H%M}.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(esiti, ensure_ascii=False, indent=1))
    ok = bool(esiti) and all(e["ok"] for e in esiti)
    print(f"[prova] {'TUTTO BENE' if ok else 'QUALCOSA NON VA'}: dettagli in {f}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
