"""IL BACKLOG IN DASHBOARD (1 ott 2026, backlog J2, richiesta del proprietario:
«cosa aspetta il sì» in dashboard, ma senza informazioni da aggiornare a mano).

La fonte resta UNA: `docs/backlog.md`, che si aggiorna comunque a ogni scoperta
(regola di CLAUDE.md). Qui lo si legge e lo si trasforma in un documento per la
dashboard; `scripts/report_giornaliero.py` lo pubblica in Firebase dopo ogni giro
del gate (la macchina ha il repo aggiornato dall'agente ops). Nessuna seconda
copia: se il file cambia, la dashboard cambia al giro dopo.

Formato atteso (scritto anche in testa al file):
  * un gruppo e' `## N. Nome` (N da 0: il gruppo 0 e' «Aspettano il tuo sì»);
  * una voce e' `### SIGLA. Titolo`, seguita dal suo testo;
  * la tabella dell'indice dice, per gruppo, «cosa le sblocca».
Tutto e' puro e fail-open: un file malformato da' gruppi vuoti, mai un'eccezione.
"""
from __future__ import annotations

import re

#: quanto testo per voce va in dashboard (il dettaglio resta nel file)
TESTO_MAX = 600
#: il gruppo delle proposte che aspettano il si' del proprietario
GRUPPO_SI = 0

_GRUPPO = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$")
_VOCE = re.compile(r"^###\s+([A-Z][A-Za-z0-9-]*)\.\s+(.+?)\s*$")
_RIGA_INDICE = re.compile(r"^\|\s*\*\*(\d+)\.\s+([^*|]+?)\*\*\s*\|([^|]*)\|([^|]*)\|\s*$")
_AGGIORNATO = re.compile(r"\*\*Aggiornato il ([^*]+?)\.\*\*")


def _pulisci(testo: str) -> str:
    """Il markdown che sul telefono e' rumore: grassetti, codice, spazi doppi."""
    t = testo.replace("**", "").replace("`", "")
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= TESTO_MAX else t[:TESTO_MAX - 1].rstrip() + "…"


def leggi_backlog(testo: str | None) -> dict:
    """Il documento della dashboard dal testo di `docs/backlog.md`. Pura.

    {"aggiornato": str|None, "gruppi": [{numero, nome, cosa_serve, voci: [{sigla,
    titolo, testo}]}], "aspetta_si": [voci del gruppo 0], "n_voci": int}"""
    righe = (testo or "").splitlines()
    m = _AGGIORNATO.search(testo or "")
    indice: dict[int, dict] = {}
    for r in righe:
        mi = _RIGA_INDICE.match(r.strip())
        if mi:
            indice[int(mi.group(1))] = {"nome": mi.group(2).strip(),
                                        "cosa_serve": _pulisci(mi.group(4))}
    gruppi: list[dict] = []
    gruppo: dict | None = None
    voce: dict | None = None
    corpo: list[str] = []

    def _chiudi_voce():
        nonlocal voce, corpo
        if voce is not None and gruppo is not None:
            voce["testo"] = _pulisci(" ".join(corpo))
            gruppo["voci"].append(voce)
        voce, corpo = None, []

    for r in righe:
        mg = _GRUPPO.match(r)
        if mg:
            _chiudi_voce()
            n = int(mg.group(1))
            gruppo = {"numero": n, "nome": mg.group(2).strip(),
                      "cosa_serve": (indice.get(n) or {}).get("cosa_serve"), "voci": []}
            gruppi.append(gruppo)
            continue
        if r.startswith("## "):          # un'altra sezione di secondo livello
            _chiudi_voce()
            gruppo = None
            continue
        mv = _VOCE.match(r)
        if mv and gruppo is not None:
            _chiudi_voce()
            voce = {"sigla": mv.group(1), "titolo": _pulisci(mv.group(2))}
            continue
        if voce is not None and r.strip() != "---":
            corpo.append(r)
    _chiudi_voce()
    gruppi.sort(key=lambda g: g["numero"])
    si = next((g for g in gruppi if g["numero"] == GRUPPO_SI), None)
    return {"aggiornato": m.group(1).strip() if m else None,
            "gruppi": gruppi,
            "aspetta_si": list(si["voci"]) if si else [],
            "n_voci": sum(len(g["voci"]) for g in gruppi)}
