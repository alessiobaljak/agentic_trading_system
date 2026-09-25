"""
IL CONTROLLO AUTOMATICO da riga di comando — voce ops `controllo` (25 set 2026).

Stampa i due semafori, le anomalie e le tre letture del documento
`dashboard/controllo` (contratto: docs/controllo_schema.md), calcolate ADESSO
dagli stessi dati che il bot pubblica ogni ora. Serve quando la dashboard non
basta o il bot tace: dal canale ops la risposta torna in `ops/results/`.

Sola lettura per default. `--publish` scrive il documento con
`generato_da="ops"` (voce ops separata e commentata: e' un ripiego, il bot e'
la fonte). Senza Firebase (in locale, nei test) gira sullo store in memoria:
tutto vuoto, ma esce con 0.

Uso:
    .venv/bin/python -m scripts.controllo
    .venv/bin/python -m scripts.controllo --publish
    .venv/bin/python -m scripts.controllo --json
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone


def _quando(ts) -> str:
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except (TypeError, ValueError):
        return "—"


def stampa(doc: dict) -> None:
    """Il documento in righe leggibili: semafori, anomalie, letture, cambiamenti."""
    m = doc.get("meta") or {}
    print(f"CONTROLLO AUTOMATICO — generato da {m.get('generato_da')} alle "
          f"{_quando(m.get('generato_at'))} (durata {m.get('durata_ms')} ms, "
          f"impostazioni: {m.get('fonte_impostazioni')})")
    print(f"  semaforo SISTEMA: {str(m.get('semaforo_sistema')).upper():7}  "
          f"semaforo PAPER: {str(m.get('semaforo_paper')).upper()}")
    prec = m.get("precedente_at")
    print(f"  controllo precedente: {_quando(prec) if prec else 'nessuno'}")
    errori = m.get("errori") or []
    print(f"  sezioni fallite: {', '.join(errori) if errori else 'nessuna'}")

    anomalie = (doc.get("salute") or {}).get("anomalie") or []
    print(f"\nANOMALIE ({len(anomalie)}):")
    if not anomalie:
        print("  nessuna")
    for a in anomalie:
        extra = []
        if a.get("valore") is not None:
            extra.append(f"valore {a['valore']}")
        if a.get("soglia") is not None:
            extra.append(f"soglia {a['soglia']}")
        coda = f" ({', '.join(extra)})" if extra else ""
        print(f"  [{a.get('gravita')}] {a.get('codice')} ({a.get('famiglia')}): {a.get('testo')}{coda}")

    print("\nLETTURE:")
    for nome in ("salute", "paper", "learning"):
        sez = doc.get(nome) or {}
        print(f"  {nome + ':':10} {sez.get('lettura', '—')}")
        if sez.get("errore"):
            print(f"  {'':10} errore: {sez['errore']}")

    att = ((doc.get("learning") or {}).get("attivo") or {})
    cambi = att.get("cambiamenti_24h")
    print("\nCAMBIAMENTI DEL LEARNING dal controllo precedente:")
    if cambi:
        for c in cambi:
            print(f"  - {c}")
    elif isinstance(cambi, list):
        print("  nessuno: nessun pezzo del learning ha cambiato decisione")
    else:
        print("  non calcolati")

    manca = doc.get("manca") or []
    if manca:
        print("\nCOSA QUESTO CONTROLLO NON PUO' DARE:")
        for r in manca:
            print(f"  - {r.get('evidenza')}: {r.get('perche')} -> {r.get('come_avere')}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--publish", action="store_true",
                    help="scrive dashboard/controllo e /controllo con generato_da=ops "
                         "(ripiego: il bot e' la fonte)")
    ap.add_argument("--json", action="store_true", help="stampa il documento intero in JSON")
    args = ap.parse_args(argv)

    from bot.core.firebase_client import get_firebase
    from bot.learning.controllo import esegui

    fb = get_firebase()
    doc = esegui(fb, "ops", settings_da_bot=False, pubblica=bool(args.publish))
    if args.json:
        print(json.dumps(doc, ensure_ascii=False, indent=1, default=str))
    else:
        stampa(doc)
    if args.publish:
        print("\n[controllo] pubblicato: fs dashboard/controllo + rtdb /controllo (generato_da=ops)")
    if not getattr(fb, "is_live", False):
        print("\n[firebase] non connesso: letto lo store in memoria, i numeri sopra sono vuoti")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
