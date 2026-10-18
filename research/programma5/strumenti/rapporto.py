"""Programma 5: il rapporto di un periodo di un'idea (C.md, V.md, R.md, A.md) dal suo file .json, con l'esito
dell'esame (REGOLE.md, sezione 5).

Uso: python3 -m research.programma5.strumenti.rapporto I-005 C
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

IDEE = Path(__file__).resolve().parents[1] / "idee"
#: l'esame delle idee fino a I-016 (REGOLE.md, sezione 5); le idee dopo hanno ``esame.json`` (sezione 6ter)
ESAME_VECCHIO = {"soglia_v": 0.005, "soglia_r": None, "senza_giorno_migliore": False, "solo_r": False}


def esame_idea(cartella: Path) -> dict:
    f = cartella / "esame.json"
    return {**ESAME_VECCHIO, **(json.loads(f.read_text(encoding="utf-8")) if f.exists() else {})}


def senza_giorno_migliore(trade_csv: Path) -> float:
    """Il netto medio a trade togliendo il giorno di calendario con la somma dei netti piu' alta."""
    import pandas as pd
    t = pd.read_csv(trade_csv)
    giorno = t["minuto"] // 1440
    somme = t.groupby(giorno)["netto"].sum()
    resto = t[giorno != somme.idxmax()]
    return float(resto["netto"].mean()) if len(resto) else float("nan")


def esito(periodo: str, e: dict, n_varianti: int, cfg: dict = ESAME_VECCHIO, senza_migliore: float = None) -> tuple:
    """(supera, motivo) del passo dell'esame per una variante."""
    if not e.get("trade"):
        return False, "nessun trade"
    nt, nd = e["netto"], e["netto_doppio"]
    if periodo == "V" and cfg.get("solo_r"):
        return True, "V e' costruzione per questa idea (REGOLE.md, 6ter, punto 3)"
    if periodo in ("C", "C2"):
        if not (nt["basso"] > 0):
            return False, "netto dopo i costi con l'intervallo non sopra zero"
        if not (nt["media"] > e.get("caso_netto", float("-inf"))):
            return False, "non meglio del caso"
        return True, f"passa {periodo}"
    if periodo == "V":
        soglia = cfg["soglia_v"] / n_varianti
        if not (nt["media"] > 0 and nt["p"] <= soglia):
            return False, f"p {nt['p']:.4f} oltre la soglia {soglia:.4f} o netto non positivo"
        if not nd["media"] > 0:
            return False, "non positivo a costi doppi"
        return True, "passa V"
    if periodo == "R":
        if not nt["basso"] > 0:
            return False, "netto con l'intervallo non sopra zero"
        if cfg.get("soglia_r") and not nt["p"] <= cfg["soglia_r"] / n_varianti:
            return False, f"p {nt['p']:.4f} oltre la soglia {cfg['soglia_r'] / n_varianti:.4f}"
        if cfg.get("senza_giorno_migliore") and not (senza_migliore is not None and senza_migliore > 0):
            return False, "non positivo togliendo il giorno migliore"
        anni = [a for a in e["per_anno"].values() if a["trade"] > 0]
        if sum(1 for a in anni if a["netto"] > 0) < 2:
            return False, "positivo in meno di 2 anni su 3"
        if not nd["media"] > 0:
            return False, "non positivo a costi doppi"
        monete = [m for m in e["per_moneta"].values() if m["trade"] >= 20]
        pos = sum(1 for m in monete if m["netto"] > 0)
        if len(monete) < 3 or pos < 3 or pos < 0.6 * len(monete):
            return False, f"positivo su {pos} monete su {len(monete)} con almeno 20 trade"
        if e["trade"] < 100:
            return False, "meno di 100 trade"
        return True, "passa R: strategia valida"
    if periodo == "V2":
        # REGOLE.md, sezione 7
        if not nt["basso"] > 0:
            return False, "netto con l'intervallo non sopra zero"
        soglia = 0.005 / n_varianti
        if not nt["p"] <= soglia:
            return False, f"p {nt['p']:.4f} oltre la soglia {soglia:.4f}"
        if not nd["media"] > 0:
            return False, "non positivo a costi doppi"
        if not (senza_migliore is not None and senza_migliore > 0):
            return False, "non positivo togliendo il giorno migliore"
        meta = e.get("per_meta", {})
        if len(meta) < 2 or any(v["netto"] <= 0 for v in meta.values()):
            return False, "non positivo in tutte e due le metà"
        monete = [m for m in e["per_moneta"].values() if m["trade"] >= 20]
        pos = sum(1 for m in monete if m["netto"] > 0)
        if len(monete) < 5 or pos < 0.6 * len(monete):
            return False, f"positivo su {pos} monete su {len(monete)} con almeno 20 trade"
        if e["trade"] < 200:
            return False, "meno di 200 trade"
        return True, "passa V2: strategia valida"
    return True, "informativo"


def scrivi(idea: str, periodo: str) -> str:
    cartella = IDEE / idea
    dati = json.loads((cartella / f"{periodo}.json").read_text(encoding="utf-8"))
    cfg = esame_idea(cartella)
    if periodo == "V2":
        import pandas as pd
        for n in dati:
            f = cartella / f"trade_V2_{n}.csv.gz"
            if dati[n].get("trade") and f.exists():
                tt = pd.read_csv(f)
                prima = tt["minuto"] < 29_453_760          # 2026-01-01 00:00 UTC in minuti dall'epoca
                dati[n]["per_meta"] = {"2025-07 → 2025-12": {"trade": int(prima.sum()),
                                                            "netto": float(tt["netto"][prima].mean())},
                                       "2026-01 → 2026-09": {"trade": int((~prima).sum()),
                                                            "netto": float(tt["netto"][~prima].mean())}}
    senza = {n: senza_giorno_migliore(cartella / f"trade_{periodo}_{n}.csv.gz")
             for n in dati if dati[n].get("trade") and (cartella / f"trade_{periodo}_{n}.csv.gz").exists()}
    righe = [f"# {idea} — periodo {periodo}", "",
             f"Numeri da `{periodo}.json` (calcolo `calcolo.py {periodo}`); esame di `research/programma5/REGOLE.md`, "
             "sezione 5. Rendimenti in % del valore della posizione, a trade.", "",
             "| Variante | Trade | Netto | Intervallo al 95% | p | A costi doppi | Lordo | Caso (netto) | Esito |",
             "|---|---|---|---|---|---|---|---|---|"]
    for n, e in dati.items():
        ok, motivo = esito(periodo, e, len(dati), cfg, senza.get(n))
        if not e.get("trade"):
            righe.append(f"| {n} | 0 | | | | | | | {motivo} |")
            continue
        nt, nd = e["netto"], e["netto_doppio"]
        righe.append(f"| {n} | {e['trade']} | {100 * nt['media']:+.3f}% | {100 * nt['basso']:+.3f}; "
                     f"{100 * nt['alto']:+.3f} | {nt['p']:.4f} | {100 * nd['media']:+.3f}% | {100 * e['lordo']:+.3f}% | "
                     f"{100 * e.get('caso_netto', float('nan')):+.3f}% | {'**' + motivo + '**' if ok else motivo} |")
    righe += ["", "Senza il giorno migliore (netto medio a trade): " + ", ".join(
        f"{n} {100 * v:+.3f}%" for n, v in senza.items()), ""]
    if periodo == "V2":
        righe += ["Per metà di V2: " + "; ".join(f"{n}: " + ", ".join(f"{k} {100 * v['netto']:+.3f}% ({v['trade']})"
                                                               for k, v in e.get("per_meta", {}).items())
                                                for n, e in dati.items() if e.get("trade")), ""]
    righe += ["", "Per anno e per moneta (netto medio a trade):", ""]
    for n, e in dati.items():
        if not e.get("trade"):
            continue
        anni = ", ".join(f"{a}: {100 * v['netto']:+.3f}% ({v['trade']})" for a, v in e["per_anno"].items())
        monete = ", ".join(f"{s[:-4]} {100 * v['netto']:+.3f}% ({v['trade']})" for s, v in e["per_moneta"].items())
        righe += [f"* **{n}** — anni: {anni}", f"  — monete: {monete}"]
    testo = "\n".join(righe) + "\n"
    (cartella / f"{periodo}.md").write_text(testo, encoding="utf-8")
    return testo


if __name__ == "__main__":
    print(scrivi(sys.argv[1], sys.argv[2]))
