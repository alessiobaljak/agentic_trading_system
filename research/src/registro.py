"""Il registro delle prove (`research/REGISTRO.md`, oltre 200 KB) interrogato senza leggerlo tutto: quante prove, il conto delle prove,
le ultime prove, le idee della coda divise per stato. Serve alla sessione principale e agli agenti (`.claude/agents/`), che non devono
leggere il registro per intero (regole dei token in `CLAUDE.md`).

Uso:
  python3 -m research.src.registro --riepilogo        al massimo 20 righe
  python3 -m research.src.registro --prova 148        la riga di una prova, intera
  python3 -m research.src.registro --cerca G1N        le righe che contengono il testo (accorciate)

Le idee (27 novembre 2026, audit del 26 novembre, punti_ciechi-7). Si leggono solo nella sezione 5 («## 5. Idee in coda», fino al
titolo «## » dopo): prima si contava ogni riga numerata del file, anche le regole 1 e 2 in testa al registro, e una voce era chiusa
solo se barrata, quindi il riepilogo diceva «48 aperte» con la coda quasi vuota. Una voce è la riga «N. » e le righe rientrate sotto
di lei. Il suo stato, nell'ordine:
  1. «barrata»    il titolo è barrato («N. ~~...~~»): chiusa, come sempre nel registro;
  2. «[stato: X]» lo stato scritto a mano, in qualunque punto della voce (di solito in fondo), con X fra «aperta», «in avanti»,
                  «in attesa», «non si fa» e «provata»: vale più delle parole, ed è il modo di correggere una voce letta male;
  3. le parole della voce, in quest'ordine (vince il primo stato trovato):
     «non si fa»  «non si fa», «non si fanno», «non si prova», «non si avvia», «si fa solo se», «si riprende se», «si riprende
                  solo», «si riprende con l'idea»; «sul passato non si fa» non conta (vuol dire «solo in avanti»);
     «in avanti»  la misura in avanti è partita: «si misura in avanti», «misura in avanti dal», «regole della misura in avanti»,
                  «raccolta partita», «la raccolta parte», «si raccoglie da»;
     «in attesa»  aspetta il proprietario, i dati o una data: «**In attesa», «in attesa del proprietario», «**sospesa»,
                  «**Ferma**», «**Non ancora**», «per ora no», «si riguarda quando», «aspetta i dati», «decide il proprietario»,
                  «appena il proprietario»;
     «provata»    «→ prova N»: già nella sezione 1 ma non barrata (va barrata);
  4. «aperta»     nessuna delle precedenti: la coda vera, da provare o da chiudere con il perché.
Le parole sono strette apposta (in grassetto dove il registro le scrive così: «gli ordini in attesa» o «la moneta non ancora quotata»
non sono stati). Una voce che le parole non riconoscono resta «aperta», cioè in vista: l'errore che si accetta è una voce chiusa che
sembra aperta, mai il contrario; si corregge con «[stato: X]».
"""
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

REGISTRO = Path(__file__).resolve().parents[1] / "REGISTRO.md"
_RIGA = re.compile(r"^\|\s*(\d+)\s*\|(.*)$")
_CONTO = re.compile(r"Totale nel conto:.*?=\s*\*\*(\d+)\*\*")

_SEZIONE_IDEE = re.compile(r"^##\s+5\.")                      # «## 5. Idee in coda: ...»
_SEZIONE = re.compile(r"^##\s")                               # il titolo di una sezione qualunque («### » no)
_VOCE = re.compile(r"^(\d+)\.\s+(.*)$")                       # una voce comincia in colonna 0
_MARCA = re.compile(r"(?:\*\*)?\[stato:\s*(aperta|in avanti|in attesa|non si fa|provata)\s*\](?:\*\*)?", re.IGNORECASE)
_TITOLO = re.compile(r"^(~~|\*\*)(.+?)\1")

STATI = ("barrata", "provata", "non si fa", "in avanti", "in attesa", "aperta")   # l'ordine di stampa
CHIUSI = ("barrata", "provata", "non si fa")
_PLURALE = {"barrata": "barrate", "provata": "provate", "aperta": "aperte"}
_PAROLE = (                                                   # l'ordine in cui si cercano: vince il primo
    ("non si fa", re.compile(r"(?<!sul passato )\bnon si (?:fa|fanno|prova|provano|avvia|avviano)\b(?! sul passato)"
                             r"|\bsi fa solo se\b|\bsi riprende (?:se|solo|con l'idea)\b", re.IGNORECASE)),
    ("in avanti", re.compile(r"\bsi misura in avanti\b|\bmisura in avanti dal\b|\bregole della misura in avanti\b"
                             r"|\braccolta (?:è )?partita\b|\bla raccolta parte\b|\bsi raccoglie da\b", re.IGNORECASE)),
    ("in attesa", re.compile(r"\*\*in attesa\b|\bin attesa del(?:la)? (?:proprietario|risposta)\b|\*\*sospes[ao]\b"
                             r"|\*\*ferm[ao]\*\*|\*\*non ancora\*\*|\bper ora no\b|\bsi riguarda quando\b"
                             r"|\baspetta (?:i dati|il proprietario|la risposta)\b|\bdecide il proprietario\b"
                             r"|\bappena il proprietario\b", re.IGNORECASE)),
    ("provata", re.compile(r"→\s*prov[ae]\s+\d+")),
)


def stato_della_voce(testo: str) -> str:
    """Lo stato di una voce della sezione 5 (testo intero, righe rientrate comprese): l'ordine è nel commento in testa al file."""
    marche = _MARCA.findall(testo)
    pulito = _MARCA.sub("", testo).strip()
    if re.match(r"^\**~~", pulito):
        return "barrata"
    if marche:
        return marche[-1].lower()                             # se sono più d'una vale l'ultima, la più recente
    for stato, parole in _PAROLE:
        if parole.search(pulito):
            return stato
    return "aperta"


def _titolo(testo: str) -> str:
    pulito = _MARCA.sub("", testo).strip()
    t = _TITOLO.match(pulito)
    return (t.group(2) if t else pulito).strip("*~ ")


def leggi_idee(righe: list) -> tuple:
    """Le voci della sezione 5, ognuna con numero, riga del file, titolo, stato e testo; e la riga del titolo della sezione."""
    inizio = next((i for i, r in enumerate(righe) if _SEZIONE_IDEE.match(r)), None)
    if inizio is None:
        return [], None
    voci, corrente = [], None
    for i in range(inizio + 1, len(righe)):
        r = righe[i]
        if _SEZIONE.match(r):
            break                                             # la sezione dopo
        m = _VOCE.match(r)
        if m:
            corrente = {"n": int(m.group(1)), "riga": i + 1, "parti": [m.group(2)]}
            voci.append(corrente)
        elif r[:1].isspace() and r.strip() and corrente is not None:
            corrente["parti"].append(r.strip())               # la voce continua sulla riga rientrata
        elif r.strip():
            corrente = None                                   # un paragrafo fra le voci («**Dalla ricerca ...**»): non è una voce
    for v in voci:
        v["testo"] = " ".join(v.pop("parti"))
        v["titolo"], v["stato"] = _titolo(v["testo"]), stato_della_voce(v["testo"])
    return voci, inizio + 1


def leggi(percorso: Path = REGISTRO) -> dict:
    righe = percorso.read_text(encoding="utf-8").splitlines()
    prove, conto = {}, None
    for riga in righe:
        m = _RIGA.match(riga)
        if m:
            celle = [c.strip() for c in m.group(2).split("|")]
            prove[int(m.group(1))] = celle
            continue
        c = _CONTO.search(riga)
        if c:
            conto = int(c.group(1))
    idee, sezione = leggi_idee(righe)
    return {"prove": prove, "conto": conto, "idee": idee, "sezione_idee": sezione,
            "stati": Counter(v["stato"] for v in idee),
            "idee_aperte": [(v["n"], v["titolo"]) for v in idee if v["stato"] == "aperta"],
            "idee_chiuse": sum(v["stato"] in CHIUSI for v in idee)}


def _corto(t: str, n: int) -> str:
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[: n - 1] + "…"


def riepilogo(dati: dict, ultime: int = 5, massimo: int = 20) -> list:
    prove, stati = dati["prove"], dati.get("stati", Counter())
    idee = sorted(dati.get("idee", []), key=lambda v: v["n"])
    righe = [f"prove nel registro: {len(prove)} (ultima: {max(prove) if prove else '-'}); conto delle prove: {dati['conto']}"]
    if dati.get("sezione_idee") is None:
        righe.append("idee: sezione «## 5.» non trovata nel registro, nessuna idea letta")
    else:
        conti = ", ".join(f"{stati[s]} {_PLURALE.get(s, s) if stati[s] != 1 else s}" for s in STATI if stati[s])
        righe.append(f"idee della sezione 5 (riga {dati['sezione_idee']}): {len(idee)} voci, {conti or 'nessuna'}")
        for s, nome in (("provata", "provate ma non barrate"), ("non si fa", "non si fa"), ("in avanti", "in avanti"),
                        ("in attesa", "in attesa")):
            numeri = [str(v["n"]) for v in idee if v["stato"] == s]
            if numeri:
                righe.append(f"  {nome}: {', '.join(numeri)}")
    righe.append("ultime prove (numero, descrizione, verdetto):")
    for n in sorted(prove)[-ultime:]:
        c = prove[n]
        righe.append(f"  {n}: {_corto(c[0] if c else '', 70)} → {_corto(c[3] if len(c) > 3 else '', 45)}")
    aperte = [v for v in idee if v["stato"] == "aperta"]
    righe.append(f"idee aperte ({len(aperte)}):" if aperte else "idee aperte: nessuna")
    posto = massimo - len(righe)
    mostrate = aperte if len(aperte) <= posto else aperte[: max(posto - 1, 0)]
    for v in mostrate:
        righe.append(f"  {v['n']}. {_corto(v['titolo'], 80)} (riga {v['riga']})")
    if len(mostrate) < len(aperte):
        righe.append("  … e le altre: " + ", ".join(str(v["n"]) for v in aperte[len(mostrate):]))
    return righe[:massimo]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--riepilogo", action="store_true")
    p.add_argument("--prova", type=int)
    p.add_argument("--cerca")
    a = p.parse_args(argv)
    dati = leggi(REGISTRO)     # il percorso letto qui (non il default della funzione): i test lo cambiano
    if a.prova is not None:
        c = dati["prove"].get(a.prova)
        print(f"| {a.prova} | " + " | ".join(c) + " |" if c else f"prova {a.prova} non trovata")
        return
    if a.cerca:
        trovate = [(n, c) for n, c in sorted(dati["prove"].items()) if a.cerca.lower() in " ".join(c).lower()]
        for n, c in trovate[:20]:
            print(f"{n}: {_corto(c[0], 100)}")
        print(f"(trovate {len(trovate)})")
        # anche le idee della coda (sezione 5): dal 27 novembre 2026, dopo che tre scout su tre non avevano visto idee già in coda
        # (135 e 150), perché --cerca leggeva solo le righe delle prove
        idee = [v for v in dati["idee"] if a.cerca.lower() in v["testo"].lower()]
        for v in idee[:20]:
            print(f"idea {v['n']} ({v['stato']}, riga {v['riga']}): {_corto(v['titolo'], 90)}")
        print(f"(idee trovate {len(idee)})")
        return
    print("\n".join(riepilogo(dati)))


if __name__ == "__main__":
    main()
