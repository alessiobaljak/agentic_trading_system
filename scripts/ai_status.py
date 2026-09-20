"""IL LIVELLO AI E' ACCESO, E COSA STA PRODUCENDO? — una domanda, un comando.

Il 19 settembre il proprietario ha scoperto che l'AI non girava da sei giorni (chiave
rifiutata) e che, quando girava, proponeva strategie senza vedere un solo dato del
paper. Rimessa la chiave, per sapere se era davvero accesa servivano TRE comandi
diversi (`connettivita`, `log-gate`, `shadow`) e la lettura incrociata dei loro log —
cioe' una diagnosi che nessuno avrebbe rifatto spontaneamente fra un mese.

Questo script risponde in una schermata a quattro domande, nell'ordine in cui
servono:

  1. la chiave funziona? (una chiamata vera, minima)
  2. l'AI sta PROPONENDO strategie? (dal registro delle spec scoperte)
  3. l'AI sta DECIDENDO in ombra? (dal documento `ai_shadow`)
  4. quali PROVE del paper le stiamo passando? (lo stesso digest che riceve)

SOLA LETTURA. Non scrive niente e non decide niente: una diagnosi che modifica lo
stato non e' una diagnosi. L'unico costo e' la chiamata del punto 1, che vale una
frazione di centesimo (max_tokens=5).

Uso:
    .venv/bin/python -m scripts.ai_status
"""
from __future__ import annotations

import time
from datetime import datetime, timezone

from bot.config import settings
from bot.core.firebase_client import decode_pairs, get_firebase

OK, FAIL, SKIP = "✅", "❌", "➖"


def _quando(ts) -> str:
    """Un tempo assoluto E quanto fa: «ieri» e «6 giorni fa» si distinguono a colpo
    d'occhio, due date no."""
    try:
        ts = float(ts)
    except (TypeError, ValueError):
        return "mai"
    if ts <= 0:
        return "mai"
    ore = (time.time() - ts) / 3600
    quando = datetime.fromtimestamp(ts, timezone.utc).strftime("%d %b %H:%M")
    if ore < 48:
        return f"{quando} UTC ({ore:.0f}h fa)"
    return f"{quando} UTC ({ore/24:.0f} giorni fa)"


def prova_chiave() -> bool:
    """Una chiamata vera. Un ping che non chiama l'API direbbe «configurata», che
    non e' la stessa cosa: la chiave del 19 settembre era configurata E rifiutata."""
    if not settings.ANTHROPIC_API_KEY:
        print(f"{SKIP} chiave: NON configurata (ANTHROPIC_API_KEY vuota)")
        return False
    try:
        import anthropic

        from bot.ai.client import _headers
        anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY,
                            default_headers=_headers()).messages.create(
            model=settings.ANTHROPIC_MODEL, max_tokens=5,
            messages=[{"role": "user", "content": "ping"}])
        ws = " · workspace impostato" if settings.ANTHROPIC_WORKSPACE_ID else ""
        print(f"{OK} chiave: funziona · modello {settings.ANTHROPIC_MODEL}{ws}")
        return True
    except Exception as exc:  # noqa: BLE001
        # il messaggio INTERO: oggi «401 invalid x-api-key» e «400 not scoped to a
        # workspace» hanno lo stesso sintomo visibile ma cause opposte, e troncare
        # il testo e' bastato a far sembrare buona una chiave rotta e viceversa
        print(f"{FAIL} chiave: {type(exc).__name__}: {exc}")
        return False


def stato_proposte(fb) -> None:
    """Quante spec portano la firma dell'AI, e quando e' stata l'ultima."""
    try:
        doc = fb.get_doc("discovered_strategies", "specs") or {}
    except Exception as exc:  # noqa: BLE001
        print(f"{FAIL} proposte: registro spec non leggibile ({str(exc)[:70]})")
        return
    specs = decode_pairs(doc.get("specs"))
    if not specs:
        print(f"{SKIP} proposte: nessuna spec nel registro")
        return
    # Le spec dell'AI portano `mechanism` — il meccanismo dichiarato — e quelle
    # casuali no. E' l'UNICO modo di distinguerle: l'id e' calcolato allo stesso
    # modo di proposito («niente corsie preferenziali», dice il codice che le
    # costruisce), quindi al gate arrivano indistinguibili. Giusto per la
    # validazione, scomodo per sapere se l'AI sta lavorando: questo campo e'
    # l'unica traccia.
    motivate = [s for s in specs.values()
                if isinstance(s, dict) and s.get("mechanism")]
    print(f"{OK if motivate else FAIL} proposte: {len(motivate)} spec con un "
          f"meccanismo dichiarato su {len(specs)} totali")
    if not motivate:
        print("   nessuna spec motivata: o l'AI non ha ancora girato col codice "
              "nuovo,\n   oppure sta proponendo e le proposte non vengono salvate")

    # PERCHE' ne sopravvivono cosi' poche. Il 19 settembre il log diceva «19/20
    # scartate» e il motivo, aggiunto la sera stessa, era gia' illeggibile il
    # mattino dopo: il canale ops mostra le ultime righe del journal e in mezzo
    # l'ottimizzo ne scrive migliaia. Ora l'esito vive su Firebase e si legge qui.
    try:
        esito = fb.get_doc("ai_hypotheses", "last") or {}
    except Exception:  # noqa: BLE001
        esito = {}
    if esito.get("proposte"):
        acc, tot = esito.get("accettate", 0), esito["proposte"]
        print(f"   ultimo giro: {acc}/{tot} proposte accettate · {_quando(esito.get('at'))}")
        for motivo, quante in list((esito.get("motivi") or {}).items())[:6]:
            print(f"     scartate ×{quante}: {motivo}")


def stato_ombra(fb) -> None:
    """Se l'ombra registra, fra qualche settimana «l'AI avrebbe fatto meglio?»
    diventa un conto. Se non registra, quella domanda resta senza risposta per
    sempre — ed e' l'unico percorso che porta l'AI a un ruolo operativo."""
    try:
        righe = fb.query_collection("ai_shadow") or []
    except Exception as exc:  # noqa: BLE001
        print(f"{FAIL} ombra: non leggibile ({str(exc)[:70]})")
        return
    if not righe:
        print(f"{FAIL} ombra: nessuna decisione registrata")
        print("   normale se il bot e' ripartito da poco: l'ombra scatta solo "
              "quando\n   c'e' un segnale da valutare (~10 al giorno), non a ogni ciclo")
        return
    ultima = max((float(r.get("at", 0) or 0) for r in righe), default=0)
    print(f"{OK} ombra: {len(righe)} decisioni registrate · ultima {_quando(ultima)}")
    accordi = sum(1 for r in righe if r.get("verdict") == "accordo")
    print(f"   d'accordo col bot {accordi}/{len(righe)} volte "
          f"(serve piu' campione per dire se conviene ascoltarla)")


def stato_prove(fb) -> None:
    """LE STESSE prove che riceve l'AI, non una loro descrizione: se qui si
    stampasse un riassunto diverso, si verificherebbe un testo che nessuno manda."""
    from scripts.discover_strategies import prove_dal_paper, scala_dal_paper

    prove = prove_dal_paper(fb)
    if not prove:
        print(f"{FAIL} prove: nessuna. L'AI sta proponendo alla cieca.")
    else:
        print(f"{OK} prove passate all'AI:")
        for riga in prove.splitlines():
            print(f"   {riga}")

    scala = scala_dal_paper(fb)
    if scala:
        print(f"{OK} scala candidata dal vissuto: {list(scala)} "
              f"(si aggiunge alle fisse, sceglie il gate)")
    else:
        print(f"{SKIP} scala dal vissuto: non ancora (servono 10 trade con mfe)")


def main() -> int:
    print("=" * 62)
    print("STATO DEL LIVELLO AI")
    print("=" * 62)
    viva = prova_chiave()
    fb = get_firebase()
    print()
    stato_proposte(fb)
    print()
    stato_ombra(fb)
    print()
    stato_prove(fb)
    print("=" * 62)
    if not viva:
        print("La chiave non risponde: tutto il resto qui sotto e' fermo di "
              "conseguenza.")
        return 1
    print("Promemoria: l'AI NON decide i trade. Propone strategie (che il gate "
          "valida)\ne decide in ombra (che non tocca niente). E' voluto: una sua "
          "decisione non e'\nriproducibile, quindi non potrebbe mai passare il GATE 1.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
