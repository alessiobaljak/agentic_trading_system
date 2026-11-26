"""La ricostruzione, una volta sola, della memoria scritta prima del 26 novembre 2026 (controllo del 26 novembre, punti 2.2 e 2.4).

Prima la memoria del modello aveva come uscita il prezzo del momento in cui il programma si accorgeva della chiusura (errore medio 48
USDT, 5 uscite su 11 dalla parte impossibile dello stop) e non aveva un'operazione eseguita e chiusa fra due controlli (il corto a
58.450 delle 15:01 del 25 novembre). Qui si rifà tutto dal conto simulato (posizioni chiuse e movimenti, salvati con i prezzi veri)
e dal diario (stop all'invio e spostamenti, il motivo scritto all'apertura). Le operazioni che il conto non ha più restano come sono.

Funzione pura: legge i dati che le si passano e ritorna la memoria nuova con un piccolo rapporto; non scrive niente.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from trader_ai.operazioni import iso_da_ms, ms, tipo_di_stop, un_r

TOLLERANZA = 1e-6


def _posizioni_dai_movimenti(movimenti: List[dict]) -> List[dict]:
    """Le posizioni chiuse come le raccontano i movimenti, in ordine: commissione d'entrata, risultato (o liquidazione),
    commissione d'uscita. Una posizione alla volta (il conto ne tiene una sola)."""
    out, cur = [], None
    for m in movimenti:
        cosa, come = m.get("cosa"), m.get("come")
        if cosa == "commissione" and come in ("a mercato", "limite eseguito"):
            cur = {"spese_entrata": -m["importo"], "spese": -m["importo"], "da_limite": come == "limite eseguito"}
            out.append(cur)
        elif cosa == "risultato" and cur is not None and "risultato_prezzo" not in cur:
            cur.update(risultato_prezzo=m["importo"], uscita=m.get("prezzo"), come=come)
        elif cosa == "liquidazione" and cur is not None and "risultato_prezzo" not in cur:
            cur.update(risultato_prezzo=m["importo"], uscita=m.get("prezzo"), come="liquidazione", chiusa=True)
        elif cosa == "commissione" and cur is not None and "risultato_prezzo" in cur and not cur.get("chiusa"):
            cur["spese"] += -m["importo"]
            cur["chiusa"] = True
    return [p for p in out if "risultato_prezzo" in p]


def _funding(chiuse: List[dict], movimenti: List[dict], applicati: List[int]) -> List[float]:
    """Il funding di ogni posizione chiusa: i pagamenti dei movimenti, appaiati in ordine con le ore registrate (le più recenti)."""
    pagamenti = [m for m in movimenti if m.get("cosa") == "funding"]
    k = min(len(pagamenti), len(applicati))
    tot = [0.0] * len(chiuse)
    for m, t in zip(pagamenti[len(pagamenti) - k:], applicati[len(applicati) - k:]):
        t = m.get("funding_ms") or t
        for i, p in enumerate(chiuse):
            if p["aperta_ms"] <= t and (p.get("chiusa_ms") is None or t < p["chiusa_ms"]):
                tot[i] += m["importo"]
                break
    return tot


def _dal_diario(diario: List[dict]) -> Tuple[List[dict], List[dict], dict]:
    aperture = [r for r in diario if r.get("evento") == "aperta"]
    modifiche = [r for r in diario if r.get("evento") == "modificata"]
    decisioni = {r["ora"]: r for r in diario if "risposta" in r and "ora" in r}
    return aperture, modifiche, decisioni


def _stop_e_spostamenti(op: dict, apertura: Optional[dict], modifiche: List[dict], eseguita_ms: int, chiusa_ms: int) -> None:
    if apertura is None:
        return
    stop, obiettivo = apertura.get("stop"), apertura.get("obiettivo")
    inizio = ms(apertura["ora"])
    spostamenti = []
    for r in modifiche:
        t = ms(r["ora"])
        if t < inizio or t > chiusa_ms:
            continue
        prima = t < eseguita_ms
        for campo, vecchio in (("stop", stop), ("obiettivo", obiettivo)):
            nuovo = r.get(campo)
            if nuovo is not None and (vecchio is None or abs(nuovo - vecchio) > TOLLERANZA):
                spostamenti.append({"ora": r["ora"], "campo": campo, "da": vecchio, "a": nuovo, "prima_dell_esecuzione": prima})
        stop, obiettivo = r.get("stop", stop), r.get("obiettivo", obiettivo)
    # lo stop e l'obiettivo in vigore all'esecuzione: quelli all'invio con gli spostamenti di prima dell'esecuzione
    si, oi = apertura.get("stop"), apertura.get("obiettivo")
    for s in spostamenti:
        if s["prima_dell_esecuzione"]:
            if s["campo"] == "stop":
                si = s["a"]
            else:
                oi = s["a"]
    op.update(stop_iniziale=si, obiettivo_iniziale=oi, spostamenti=spostamenti)


def ricostruisci(ops: List[dict], storia: Optional[dict], diario: List[dict], simbolo: str) -> Tuple[List[dict], dict]:
    """Ritorna (operazioni ricostruite e numerate, rapporto)."""
    rapporto = {"corrette": 0, "aggiunte": 0, "lasciate": 0}
    ops = [dict(o) for o in ops]
    if storia:
        chiuse = [p for p in storia.get("chiuse") or [] if p.get("chiusa_ms") is not None]
        dai_mov = _posizioni_dai_movimenti(storia.get("movimenti") or [])
        k = min(len(chiuse), len(dai_mov))
        chiuse, dai_mov = chiuse[len(chiuse) - k:], dai_mov[len(dai_mov) - k:]
        for p, m in zip(chiuse, dai_mov):               # i due racconti devono dire la stessa cosa, altrimenti non si tocca niente
            atteso = -p["margine"] if m["come"] == "liquidazione" else \
                (1 if p["lato"] == "lungo" else -1) * (m["uscita"] - p["entrata"]) * p["quantita"]
            if abs(atteso - m["risultato_prezzo"]) > 1e-4:
                raise ValueError(f"posizione del {iso_da_ms(p['aperta_ms'])}: movimenti e posizione non tornano")
        funding = _funding(chiuse, storia.get("movimenti") or [], storia.get("funding_applicati") or [])
        aperture, modifiche, decisioni = _dal_diario(diario)
        usate = set()
        for i, (p, m) in enumerate(zip(chiuse, dai_mov)):
            op = next((o for j, o in enumerate(ops) if j not in usate and o["lato"] == p["lato"]
                       and abs(o["entrata"] - p["entrata"]) < TOLLERANZA and (ms(o["aperta"]) or 0) <= p["aperta_ms"] + 1000), None)
            apertura = next((r for r in reversed(aperture) if r.get("lato") == p["lato"]
                             and abs((r.get("entrata") or 0) - p["entrata"]) < TOLLERANZA and ms(r["ora"]) <= p["aperta_ms"] + 1000),
                            None)
            if op is None:
                if apertura is None:
                    continue
                op = {"aperta": apertura["ora"], "lato": p["lato"], "leva": apertura.get("leva") or p["leva"],
                      "entrata": p["entrata"], "approccio": apertura.get("approccio", ""), "margine": apertura.get("margine"),
                      "come": "-"}
                ops.append(op)
                usate.add(len(ops) - 1)
                rapporto["aggiunte"] += 1
            else:
                usate.add(ops.index(op))
                rapporto["corrette"] += 1
            if apertura is not None and apertura["ora"] != op["aperta"]:
                apertura = next((r for r in aperture if r["ora"] == op["aperta"]), apertura)
            vecchio_come = op.get("come", "")
            come = m["come"]
            op.update(tipo="limite" if m["da_limite"] else "mercato", quantita=p["quantita"], entrata=p["entrata"],
                      eseguita=iso_da_ms(p["aperta_ms"]), chiusa=iso_da_ms(p["chiusa_ms"]), uscita=m["uscita"],
                      uscita_stimata=False, spese_entrata=round(m["spese_entrata"], 6), spese=round(m["spese"], 6),
                      funding=round(funding[i], 6), risultato_prezzo=round(m["risultato_prezzo"], 6),
                      risultato=round(m["risultato_prezzo"] - m["spese"] + funding[i], 2))
            _stop_e_spostamenti(op, apertura, modifiche, p["aperta_ms"], p["chiusa_ms"])
            if come == "stop":
                op["come"] = tipo_di_stop(op.get("spostamenti") or [])
            elif come in ("obiettivo", "liquidazione"):
                op["come"] = come
            elif vecchio_come in ("chiusa dal modello", "chiusa da te"):
                op["come"] = "chiusa da te"
            elif vecchio_come and vecchio_come not in ("stop", "obiettivo", "-") and not vecchio_come.startswith("chiusa sul conto"):
                op["come"] = vecchio_come
            else:
                op["come"] = "chiusa a mercato"
            decisione = decisioni.get(op["aperta"])
            if decisione and (decisione.get("risposta") or {}).get("diario"):
                op["motivo"] = decisione["risposta"]["diario"][:300]
            r = un_r(op["lato"], op["entrata"], op["quantita"], op.get("stop_iniziale"), op["spese_entrata"], simbolo)
            if r:
                op["R"], op["r"] = round(r, 4), round(op["risultato"] / r, 2)
        rapporto["lasciate"] = len(ops) - len(usate)
    ops.sort(key=lambda o: ms(o.get("eseguita") or o.get("aperta")) or 0)
    for n, o in enumerate(ops, start=1):
        o["n"] = n
        if o.get("come") == "chiusa dal modello":
            o["come"] = "chiusa da te"
    return ops, rapporto


def lezioni_dal_diario(diario: List[dict], ops: List[dict]) -> List[dict]:
    """I perché dei cambi di approccio scritti dal modello prima del 26 novembre 2026 (campo `perche`): diventano lezioni, con la
    loro data e l'ultima operazione chiusa prima (revisione del 26 novembre 2026, punto B7). Il testo è quello del modello."""
    out = []
    for r in diario:
        risposta = r.get("risposta") or {}
        if not (risposta.get("cambio_approccio") and (risposta.get("perche") or "").strip()) or "ora" not in r:
            continue
        t = ms(r["ora"])
        prima = [o for o in ops if (ms(o.get("chiusa")) or 0) <= t]
        out.append({"ora": r["ora"], "testo": "cambio di approccio: " + risposta["perche"].strip()[:380],
                    "dopo": prima[-1].get("n") if prima else None, "giorno_netto": r.get("guadagno_giorno"), "fissata": True})
    return out
