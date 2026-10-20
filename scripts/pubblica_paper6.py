"""Pubblica il paper del programma 6 sulla dashboard (20 ott 2026).

Il paper delle candidate del programma 6 (`research/programma6/paper/`) si calcola fuori dalla macchina, ogni mattina,
dai dati pubblici di Binance, e finisce nel repository (`paper.json`). La dashboard legge solo Firebase: questo script
prende `paper.json` e lo scrive in RTDB `/paper6` e in Firestore `dashboard/paper6`, gia' ridotto a quello che il
pannello mostra. Lo lancia GitHub Actions (`.github/workflows/snapshot.yml`), che ha gia' le credenziali di Firebase:
sulla macchina non serve installare niente. Non tocca il bot, le posizioni, i trade o il saldo del paper del bot.

Uso: python -m scripts.pubblica_paper6 [percorso di paper.json]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
FONTE = RADICE / "research" / "programma6" / "paper" / "paper.json"

DESCRIZIONI = {
    "F3": "funding fra monete, pesi secondo la volatilità",
    "K1": "denaro che entra, leva che costa poco",
    "F2": "funding fra monete, pesi uguali",
    "C1": "28 indicatori combinati (CTREND)",
    "A1": "tendenza pubblicata (9 canali di Donchian)",
}


def documento(paper: dict, adesso: float | None = None) -> dict:
    """Il documento per la dashboard: le candidate (periodi, rendimento, Sharpe, l'ultima settimana o l'ultimo giorno)
    e le posizioni di adesso di F3 e K1."""
    candidate = []
    for nome, c in (paper.get("candidate") or {}).items():
        serie = c.get("settimane") or c.get("giorni") or {}
        ultima = sorted(serie.items())[-1] if serie else None
        candidate.append({
            "nome": nome,
            "descrizione": DESCRIZIONI.get(nome, ""),
            "periodi": int(c.get("periodi") or 0),
            "unita": "giorni" if "giorni" in c else "settimane",
            "totale": c.get("totale"),
            "sharpe": c.get("sharpe"),
            "ultimo": {"data": ultima[0], "netto": ultima[1]} if ultima else None,
        })
    posizioni = {}
    for nome in ("F3", "K1"):
        a = (paper.get("adesso") or {}).get(nome) or {}
        posizioni[nome] = {"lunedi": a.get("lunedi"),
                           "long": [{"moneta": k, "peso": v} for k, v in sorted((a.get("long") or {}).items(), key=lambda x: -x[1])],
                           "short": [{"moneta": k, "peso": v} for k, v in sorted((a.get("short") or {}).items(), key=lambda x: x[1])]}
    return {
        "meta": {"versione_schema": 1, "generato_at": float(adesso if adesso is not None else time.time()),
                 "fonte": "research/programma6/paper/paper.json"},
        "dati_fino_al": paper.get("dati_fino_al"),
        "funding_stimato_dal": paper.get("funding_stimato_dal"),
        "inizio_misura": {"giorni": "2026-10-20", "settimane": "2026-10-26"},
        "verdetto": "a 52 settimane (25 ottobre 2027) e a 104 settimane, mai prima",
        "candidate": candidate,
        "posizioni": posizioni,
        "nuove_nell_universo": paper.get("nuove_nell_universo") or [],
    }


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    fonte = Path(argv[0]) if argv else FONTE
    if not fonte.exists():
        print(f"[paper6] {fonte} non c'e': niente da pubblicare")
        return 0
    doc = documento(json.loads(fonte.read_text(encoding="utf-8")))
    from bot.core.firebase_client import get_firebase
    fb = get_firebase()
    fb.set_rtdb("/paper6", doc)
    fb.set_doc("dashboard", "paper6", doc)
    print(f"[paper6] pubblicato: dati fino al {doc['dati_fino_al']}, {len(doc['candidate'])} candidate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
