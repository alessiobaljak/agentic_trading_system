"""
IL CONTROLLO AUTOMATICO da riga di comando — voce ops `controllo` (25 set 2026).

Stampa i due semafori, le anomalie e le tre letture del documento
`dashboard/controllo` (contratto: docs/controllo_schema.md), calcolate ADESSO
dagli stessi dati che il bot pubblica ogni ora. Serve quando la dashboard non
basta o il bot tace: dal canale ops la risposta torna in `ops/results/`.

Dal 29 set 2026, IN CODA all'output di prima (che resta identico), due sezioni
chieste dal proprietario per il report del mattino: «COME IMPARA IL TRAILING»
e «COSA IMPARANO LE STRATEGIE» (`bot/learning/apprendimento.py`), con i
confronti «ieri» e «stanotte» dalle foto giornaliere che il bot scrive su RTDB
(`/learning_giorni`). Riusano i dati gia' letti per il controllo; in piu' due
documenti Firestore (`learning/ipotesi_storia`, `gate_history/lifecycle`), le
due foto e, se manca quella di ieri, l'indice `/learning_indice` (RTDB, al
massimo 3 letture; nessuna se il RTDB non risponde). Una lettura che fallisce
lo dice nella sezione, il resto esce.
`--json` resta com'era: solo il documento.

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
import time
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

    # le letture Firestore del bot (28 set 2026): solo il documento scritto dal
    # bot le porta; da ops sarebbero quelle di questo processo, appena nato
    sal = doc.get("salute") or {}
    lett = sal.get("letture_firestore_24h")
    print("\nLETTURE FIRESTORE DEL BOT (ultime 24 h, quota gratuita 50.000/giorno):")
    if lett is None:
        print("  non misurate in questo documento (le conta solo il bot: vedi il controllo orario)")
    else:
        per = " · ".join(f"{r.get('chi')} {r.get('n')}" for r in (sal.get("letture_per_chiamante") or []))
        print(f"  {lett}" + (f" ({per})" if per else ""))
    ct = sal.get("cache_trade")
    if isinstance(ct, dict):
        print(f"  cache trade: {ct.get('cache')} in memoria contro {ct.get('firestore')} su Firestore "
              f"({'allineata' if ct.get('allineata') else 'DISALLINEATA, ricaricata'}, "
              f"verificata {_quando(ct.get('verificata_at'))})")

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


def _foto(fb, giorno: str):
    """La foto del learning di un giorno (RTDB), o None se manca o non si legge."""
    from bot.learning.apprendimento import FOTO_BASE
    try:
        v = fb.get_rtdb(f"{FOTO_BASE}/{giorno}")
    except Exception:  # noqa: BLE001
        return None
    return v if isinstance(v, dict) and v else None


def _ultima_foto(fb, now: float):
    """(giorno, at) della foto piu' recente prima di ieri, dall'indice che il bot
    scrive insieme alla foto (`FOTO_INDICE`, pochi byte): UNA lettura RTDB. Fino
    al 29 set sera si guardavano le foglie `at` di 34 giorni una per una: 34
    richieste in fila, ognuna ritentata fino a 4 volte se il RTDB risponde 503."""
    from bot.learning.apprendimento import FOTO_INDICE, finestre, ultima_dall_indice
    try:
        indice = fb.get_rtdb(FOTO_INDICE)
    except Exception:  # noqa: BLE001
        return None
    return ultima_dall_indice(indice, finestre(now)["ieri"][2])


def _rtdb_muto(fb, dati: dict) -> bool:
    """Il RTDB non risponde? Da `carica_dati` (`rtdb_degradato_s`) o, se e'
    cominciato dopo, dal client. Con il RTDB muto `get_rtdb` non solleva: ridà
    lo specchio in memoria, vuoto in un processo appena nato, e una foto che c'e'
    sembrerebbe mancare."""
    try:
        if float(dati.get("rtdb_degradato_s") or 0) > 0:
            return True
    except (TypeError, ValueError):
        pass
    try:
        return bool(getattr(fb, "is_live", False)) and float(fb.degraded_for()) > 0
    except Exception:  # noqa: BLE001
        return False


def _leggi(fb, coll: str, doc_id: str, errori: list):
    """Un documento Firestore in piu' (chiamata POSIZIONALE: i client finti dei
    test hanno solo `get_doc(coll, id)`); None e una riga in `errori` se fallisce."""
    try:
        v = fb.get_doc(coll, doc_id)
    except Exception as exc:  # noqa: BLE001
        errori.append(f"{coll}/{doc_id}: {str(exc)[:80]}")
        return None
    return v if isinstance(v, dict) else None


def stampa_apprendimento(fb, dati: dict, doc: dict) -> None:
    """Le sezioni «COME IMPARA IL TRAILING» e «COSA IMPARANO LE STRATEGIE» (29
    set 2026), in coda all'output di sempre. Qui solo le letture; le righe le
    scrivono le funzioni pure di `bot/learning/apprendimento.py`. Fail-open:
    una sezione che fallisce stampa perche', l'altra esce lo stesso."""
    from bot.learning import apprendimento as ap
    try:
        now = float((doc.get("meta") or {}).get("generato_at"))
    except (TypeError, ValueError):
        now = time.time()
    errori: list[str] = []
    fin = ap.finestre(now)
    # RTDB muto (29 set 2026): le foto non si leggono affatto. Uno specchio vuoto
    # direbbe «mancano», che e' falso, e ogni richiesta sarebbe ritentata
    muto = _rtdb_muto(fb, dati)
    foto_oggi = foto_ieri = ultima = None
    if not muto:
        foto_oggi = _foto(fb, fin["stanotte"][2])
        foto_ieri = _foto(fb, fin["ieri"][2])
        muto = _rtdb_muto(fb, {})
    if not muto and foto_ieri is None:
        ultima = _ultima_foto(fb, now)
    senza_foto = "RTDB non raggiungibile: foto non lette" if muto else None
    storia = _leggi(fb, "learning", "ipotesi_storia", errori)
    vite = _leggi(fb, "gate_history", "lifecycle", errori)
    # lo stato di ADESSO con dei buchi (letture del controllo fallite) farebbe
    # un confronto «stanotte» falso: panchine «uscite», ipotesi «sparite»
    mancano = ap.letture_mancanti(dati)
    manca_adesso = (f"stato di adesso incompleto: letture fallite ({', '.join(mancano)})"
                    if mancano else None)
    adesso = None
    if not manca_adesso:
        try:
            adesso = ap.impronta_giorno(dati, now)
        except Exception as exc:  # noqa: BLE001
            manca_adesso = f"stato di adesso non calcolato ({str(exc)[:80]})"
            errori.append(f"stato di adesso: {str(exc)[:80]}")
    print()
    print("\n".join(ap.righe_foto(now, foto_oggi, foto_ieri, ultima, rtdb_muto=muto)))
    for titolo, fn in (("COME IMPARA IL TRAILING",
                        lambda: ap.sezione_trailing(dati, now, foto_oggi, foto_ieri, adesso,
                                                    perche_senza_foto=senza_foto,
                                                    manca_adesso=manca_adesso)),
                       ("COSA IMPARANO LE STRATEGIE",
                        lambda: ap.sezione_strategie(dati, now, storia, vite, foto_oggi,
                                                     foto_ieri, adesso, perche_senza_foto=senza_foto,
                                                     manca_adesso=manca_adesso))):
        try:
            righe = fn()
        except Exception as exc:  # noqa: BLE001
            righe = [titolo, f"  sezione non calcolata: {type(exc).__name__}: {str(exc)[:160]}"]
        print()
        print("\n".join(righe))
    for e in errori:
        print(f"  [lettura fallita] {e}")


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
    dati: dict = {}
    doc = esegui(fb, "ops", settings_da_bot=False, pubblica=bool(args.publish), dati_out=dati)
    if args.json:
        print(json.dumps(doc, ensure_ascii=False, indent=1, default=str))
    else:
        stampa(doc)
    if args.publish:
        print("\n[controllo] pubblicato: fs dashboard/controllo + rtdb /controllo (generato_da=ops)")
    if not getattr(fb, "is_live", False):
        print("\n[firebase] non connesso: letto lo store in memoria, i numeri sopra sono vuoti")
    if not args.json:
        # IN CODA, dopo tutto l'output di prima (29 set 2026): chi lo legge a
        # occhio o con uno script trova le righe vecchie al loro posto
        stampa_apprendimento(fb, dati, doc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
