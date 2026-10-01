"""Quello che la DASHBOARD legge senza che nessuno lo aggiorni a mano.

1 ott 2026, richieste del proprietario: «cosa aspetta il sì» in dashboard senza
aggiornarlo a mano (backlog J2) e, dopo, il REPORT GIORNALIERO in una sezione
sola della dashboard.

Questo script gira SULLA MACCHINA, dove il repo e' aggiornato dall'agente ops:
  * dopo ogni giro del gate (lo lancia `scripts/discover_strategies.py` alla
    fine, in un processo a parte con un tempo massimo: un suo errore non tocca
    il gate);
  * a richiesta, dal canale ops (`report-giornaliero`).

Cosa pubblica:
  * `dashboard/backlog` (Firestore) e `/backlog` (RTDB): `docs/backlog.md` letto
    da `bot.learning.backlog_doc` — una fonte sola, nessuna copia;
  * IL REPORT GIORNALIERO (`bot/learning/report.py`, nove sezioni fisse):
    `dashboard/report_giornaliero` e `/report_giornaliero` (l'ultimo) e
    `report_giornaliero/{giorno}` (la storia, uno per giorno, riscritto a ogni
    giro di quel giorno).

Letture per giro (stima): i trade (~200 documenti, crescono col paper), 4
documenti Firestore (spec, portafoglio, spesa AI di ieri, nessun altro); il
controllo e il gate si leggono dallo specchio RTDB, che non conta nella quota.
Con 8 giri al giorno ~1.700 letture: la quota gratuita e' 50.000.

Uso:
  python -m scripts.report_giornaliero --pubblica   # legge e scrive Firebase
  python -m scripts.report_giornaliero              # stampa e basta
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time

from bot.learning.backlog_doc import leggi_backlog

#: la radice del repo (questo file sta in scripts/)
RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSIONE_SCHEMA = 1


def _commit(radice: str = RADICE) -> str | None:
    """L'hash corto del commit del repo sulla macchina: dice da quale versione
    dei file viene il documento. None se git non risponde."""
    try:
        out = subprocess.run(["git", "-C", radice, "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or None
    except Exception:  # noqa: BLE001
        return None


def doc_backlog(radice: str = RADICE, now: float | None = None) -> dict:
    """Il documento del backlog per la dashboard. Senza file: gruppi vuoti e
    `errore`, mai un'eccezione."""
    now = time.time() if now is None else now
    meta = {"versione_schema": VERSIONE_SCHEMA, "generato_at": now,
            "fonte": "docs/backlog.md", "commit": _commit(radice)}
    try:
        with open(os.path.join(radice, "docs", "backlog.md"), encoding="utf-8") as f:
            testo = f.read()
    except OSError as exc:
        return {"meta": {**meta, "errore": f"backlog non leggibile ({exc})"[:200]},
                "gruppi": [], "aspetta_si": [], "n_voci": 0, "aggiornato": None}
    return {"meta": meta, **leggi_backlog(testo)}


def commit_recenti(radice: str = RADICE, ore: int = 36) -> list[dict] | None:
    """[{hash, at, titolo}] dei commit delle ultime `ore` sul repo della macchina;
    None se git non risponde."""
    try:
        out = subprocess.run(["git", "-C", radice, "log", f"--since={ore} hours ago",
                              "--no-merges", "--format=%h%x09%ct%x09%s"],
                             capture_output=True, text=True, timeout=20)
        if out.returncode != 0:
            return None
    except Exception:  # noqa: BLE001
        return None
    righe = []
    for r in out.stdout.splitlines():
        parti = r.split("\t", 2)
        if len(parti) == 3:
            try:
                righe.append({"hash": parti[0], "at": float(parti[1]), "titolo": parti[2]})
            except ValueError:
                continue
    return righe


def avanzamento_r1(radice: str = RADICE) -> dict | None:
    """Quanto ha fatto R1 (il gate rigiocato nel passato), dai suoi file locali:
    date del piano, date con almeno un'unita', unita' finite. None se non e'
    ancora partito."""
    base = os.path.join(radice, "data", "replay_gate")
    try:
        with open(os.path.join(base, "piano.json"), encoding="utf-8") as f:
            piano = json.load(f)
    except (OSError, ValueError):
        return None
    date = list(piano.get("date") or [])
    universo = list(piano.get("universo") or [])
    unita, finite = 0, 0
    for d in date:
        cartella = os.path.join(base, "unita", str(d))
        try:
            n = sum(1 for x in os.listdir(cartella) if x.endswith(".json"))
        except OSError:
            n = 0
        unita += n
        if universo and n >= len(universo):
            finite += 1
    return {"date_totali": len(date), "date_finite": finite, "unita": unita}


def _leggi_testo(radice: str, *percorso: str) -> str | None:
    try:
        with open(os.path.join(radice, *percorso), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def doc_report(fb, backlog: dict, radice: str = RADICE, now: float | None = None) -> dict:
    """Legge tutto quello che il report usa (fail-open per fonte) e lo costruisce."""
    from datetime import datetime, timedelta

    from bot.core.firebase_client import decode_pairs
    from bot.core.tempo import giorno_locale
    from bot.learning.report import costruisci_report
    now = time.time() if now is None else now
    ieri = (datetime.fromisoformat(giorno_locale(now)).date() - timedelta(days=1)).isoformat()

    def _prova(f, nome):
        try:
            return f()
        except Exception as exc:  # noqa: BLE001
            print(f"[report] {nome} non letto ({str(exc)[:120]})")
            return None

    trades = _prova(lambda: fb.query_collection("trades", order_by="exit_ts"), "trades") or []
    controllo = _prova(lambda: fb.get_rtdb("/controllo"), "controllo")
    gate = _prova(lambda: fb.get_rtdb("/gate"), "gate")
    portafoglio = _prova(lambda: fb.get_doc("portfolio", "backtest"), "portafoglio")
    specs = _prova(lambda: decode_pairs((fb.get_doc("discovered_strategies", "specs") or {})
                                        .get("specs")), "spec")
    spesa = _prova(lambda: fb.get_doc("ai_spesa", ieri), "spesa AI")
    return costruisci_report(
        trades=trades, controllo=controllo if isinstance(controllo, dict) else None,
        gate=gate if isinstance(gate, dict) else None,
        portafoglio=portafoglio if isinstance(portafoglio, dict) else None,
        backlog=backlog, specs=specs if isinstance(specs, dict) else None,
        capito=_leggi_testo(radice, "docs", "capito.md"),
        testo_letture=_leggi_testo(radice, "docs", "letture.md"),
        commit=commit_recenti(radice), spesa_ieri=spesa if isinstance(spesa, dict) else None,
        r1=avanzamento_r1(radice), now=now, versione=_commit(radice))


def testo_report(rep: dict, max_righe: int = 12) -> str:
    """Il report in testo semplice, sezione per sezione: lo stampa la richiesta
    ops `report-giornaliero`, cosi' chi non vede la dashboard (il controllo del
    mattino, una sessione di lavoro) legge LO STESSO report pubblicato."""
    out = [f"REPORT GIORNALIERO del {rep['meta'].get('giorno')} (versione "
           f"{rep['meta'].get('commit')})"]
    for s in rep.get("sezioni") or []:
        out.append(f"\n== {s.get('titolo')}" + (f"  [ERRORE: {s['errore']}]" if s.get("errore") else ""))
        for r in (s.get("righe") or [])[:max_righe]:
            out.append(f"  - {r}")
        tab = s.get("tabella") or {}
        if tab.get("righe"):
            if tab.get("colonne"):
                out.append("    " + " | ".join(str(c) for c in tab["colonne"]))
            for r in tab["righe"][:30]:
                out.append("    " + " | ".join("" if x is None else str(x) for x in r))
    return "\n".join(out)


def _scrivi(fb, collezione: str, doc_id: str, percorso_rtdb: str, doc: dict) -> bool:
    """Firestore e specchio RTDB, come il documento del gate. Non solleva mai."""
    from bot.core.registry import pulisci_per_firestore
    doc = pulisci_per_firestore(doc)
    ok = False
    try:
        fb.set_doc(collezione, doc_id, doc)
        ok = True
    except Exception as exc:  # noqa: BLE001
        print(f"[report] Firestore {collezione}/{doc_id} non scritto ({str(exc)[:160]})")
    try:
        fb.set_rtdb(percorso_rtdb, doc)
    except Exception as exc:  # noqa: BLE001
        print(f"[report] RTDB {percorso_rtdb} non scritto ({str(exc)[:160]})")
    return ok


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pubblica", action="store_true",
                    help="scrive in Firebase (senza: stampa e basta)")
    args = ap.parse_args(argv)
    backlog = doc_backlog()
    print(f"[report] backlog: {backlog.get('n_voci', 0)} voci in "
          f"{len(backlog.get('gruppi') or [])} gruppi, aspettano il si' "
          f"{len(backlog.get('aspetta_si') or [])} (commit {backlog['meta'].get('commit')})")
    if not args.pubblica:
        print(json.dumps(backlog, ensure_ascii=False, indent=1)[:4000])
        return 0
    from bot.core.firebase_client import get_firebase
    fb = get_firebase()
    ok = _scrivi(fb, "dashboard", "backlog", "/backlog", backlog)
    print(f"[report] backlog pubblicato: {'si' if ok else 'NO'}")
    rep = doc_report(fb, backlog)
    errori = [s["id"] for s in rep["sezioni"] if s.get("errore")]
    ok2 = _scrivi(fb, "dashboard", "report_giornaliero", "/report_giornaliero", rep)
    try:
        from bot.core.registry import pulisci_per_firestore
        fb.set_doc("report_giornaliero", rep["meta"]["giorno"], pulisci_per_firestore(rep))
    except Exception as exc:  # noqa: BLE001
        print(f"[report] storia report_giornaliero/{rep['meta']['giorno']} non scritta "
              f"({str(exc)[:120]})")
    print(f"[report] report del {rep['meta']['giorno']} pubblicato: {'si' if ok2 else 'NO'}"
          + (f" (sezioni con errore: {', '.join(errori)})" if errori else ""))
    print(testo_report(rep))
    return 0 if (ok and ok2) else 1


if __name__ == "__main__":
    raise SystemExit(main())
