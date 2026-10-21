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
    "M1": "modello che unisce tutti gli indicatori (alberi)",
    "F2": "funding fra monete, pesi uguali",
    "C1": "28 indicatori combinati (CTREND)",
    "A1": "tendenza pubblicata (9 canali di Donchian)",
    "F3 + M1 a rischio uguale": "le due più forti insieme",
    "F5": "funding fra monete con la banda: la più solida sul passato",
    "K2": "K1 con la banda (costruzione)",
    "M6": "il modello con la media di cinque semi",
    "M7": "M6 con la banda",
    "F5 + M7 a rischio uguale (informazione)": "funding con la banda e modello con la banda insieme",
    "F5 + M7 + K2 a rischio uguale (informazione)": "le tre con la banda insieme",
    "M7 + M8 a rischio uguale (informazione)": "i due modelli insieme",
}

#: le strategie in parole semplici, per la scheda «Strategie nuove» (stato al 21 ottobre 2026, fonte research/REGISTRO.md)
STRATEGIE = [
    {"nome": "Monete appena quotate, short con uscita (N3)", "stato": "validata sul passato",
     "monete": "ogni moneta nuova dei futures di Binance (circa 100-240 l'anno)",
     "regola": "short a 7 giorni dalla quotazione contro il Bitcoin; esce se la moneta sale del 30%, se no dopo 30 giorni",
     "passato": "Binance dal 2021: +4,3% a operazione su 613 (p 0,0017); Gate.io dal 2023: +7,6% su 449 (p 0,0001)"},
    {"nome": "Funding con la banda (F5)", "stato": "la più solida a portafoglio; non passa il voto corretto (0,81 su 0,95)",
     "monete": "le 100 più scambiate dei futures di Binance (circa 25 long e 25 short alla volta)",
     "regola": "long dove il funding è basso, short dove è alto; si entra nel 20% e si esce sotto il 40%; ogni lunedì",
     "passato": "dal 2021 Sharpe 1,93, +57% l'anno, ogni anno positiva; a costi tripli Sharpe 1,60"},
    {"nome": "Funding al tetto (E4)", "stato": "promettente, non confermata",
     "monete": "le monete dove Binance accorcia l'intervallo del funding con funding positivo (circa 20 l'anno)",
     "regola": "short la moneta contro il Bitcoin per 7 giorni",
     "passato": "Binance dal 2023: +11,7% a operazione su 62 (p 0,0047); su Gate.io non confermata"},
]


def documento(paper: dict, adesso: float | None = None) -> dict:
    """Il documento per la dashboard: le candidate (periodi, rendimento, Sharpe, l'ultima settimana o l'ultimo giorno)
    le posizioni di adesso (F5, F3, K1, M1), le strategie in parole semplici e gli eventi di N3 e E4."""
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
    for nome in ("F5", "F3", "K1", "M1"):
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
        "strategie": STRATEGIE,
        "eventi_n3": [{k: x.get(k) for k in ("mercato", "simbolo", "ingresso", "stato", "r", "fermata")}
                      for x in (paper.get("eventi_N3") or [])],
        "eventi_e4": [{"simbolo": x.get("simbolo"), "data": x.get("data"), "r7": x.get("r7")}
                      for x in (paper.get("eventi_E4") or [])],
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
