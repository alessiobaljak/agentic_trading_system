"""Il messaggio al modello (REGOLE.md, versione 7, sezione 4).

Tre parti (controllo del 26 novembre 2026):
1. le istruzioni fisse (`system`, `istruzioni.md`), nella cache da un'ora;
2. la memoria stabile: bilancio delle operazioni chiuse, le lezioni scritte dal modello, le operazioni chiuse con la loro scheda. Cambia
   solo quando un'operazione si chiude (e a mezzanotte), quindi sta anche lei nella cache da un'ora: qui dentro niente che cambi con
   l'ora o con il prezzo;
3. il resto, nuovo a ogni chiamata: ora e chiamate rimaste, decisione non eseguita, conto e operazione aperta (o ordine in attesa),
   mercato, approccio e note, candele (le chiuse e quella in corso) con gli indicatori.

Solo dati della moneta, del conto e della memoria del trader: nessun dato dell'altra sessione, nessun consiglio di strategia. Numeri con
il punto per i decimali, come nella risposta.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from typing import Dict, List, Optional, Tuple

from trader_ai import calendario
from trader_ai.indicatori import riassunto, vwap
from trader_ai.limiti import OBIETTIVO_GIORNO_QUOTA, Conto, Posizione, guadagno_netto, obiettivo_usdt
from trader_ai.operazioni import (COMMISSIONE_MERCATO, CATEGORIE, bilancio, durata_min, netto_a, pareggio, serie_perdente,
                                  spese_entrata, un_r, uscita_effettiva)

ISTRUZIONI = Path(__file__).with_name("istruzioni.md")
#: Quante candele chiuse si mostrano per intervallo (gli indicatori si calcolano su tutte quelle ricevute).
MOSTRATE = 48
MINUTI = {"1m": 1, "5m": 5, "15m": 15, "30m": 30}
#: Operazioni chiuse in memoria: le ultime 30, di cui le ultime 5 con la scheda intera.
OPERAZIONI_MOSTRATE, SCHEDE_INTERE = 30, 5
LEZIONI_MOSTRATE, NOTE_MOSTRATE = 10, 10


@dataclass
class Memoria:
    operazioni: List[dict] = field(default_factory=list)
    lezioni: List[dict] = field(default_factory=list)      # {"ora", "testo", "dopo", "giorno_netto", "fissata"}
    note: List[str] = field(default_factory=list)
    approccio: Optional[str] = None
    scarto: Optional[str] = None
    inizio: dict = field(default_factory=lambda: {"giorno": "-", "conto": 1000.0})
    giorno: str = ""                                        # oggi, UTC (AAAA-MM-GG)


# --- numeri ----------------------------------------------------------------------------------------------------------
def _cifre(x: float, significative: int) -> int:
    if not x:
        return 0
    return max(0, significative - 1 - math.floor(math.log10(abs(x))))


def _p(x: Optional[float]) -> str:
    """Un prezzo con 6 cifre significative (60123.4 su BTC)."""
    return "-" if x is None else f"{x:.{_cifre(x, 6)}f}"


def _pc(x: float) -> str:
    """Un prezzo nelle candele, con 5 cifre significative (60123 su BTC: l'errore massimo è mezzo dollaro)."""
    return f"{x:.{_cifre(x, 5)}f}"


def _v(x: Optional[float]) -> str:
    if x is None:
        return "-"
    return f"{x:.0f}" if abs(x) >= 100 else f"{x:.1f}" if abs(x) >= 10 else f"{x:.2f}"


def _s(x: Optional[float]) -> str:
    """Un numero piccolo (MACD, rapporti): poche cifre, senza notazione esponenziale."""
    if x is None:
        return "-"
    a = abs(x)
    return f"{x:.0f}" if a >= 100 else f"{x:.1f}" if a >= 10 else f"{x:.2f}" if a >= 0.1 else f"{x:.4f}"


def _volte(n: int) -> str:
    return f"{n} volta" if n == 1 else f"{n} volte"


def _pct(a: float, b: Optional[float]) -> str:
    return "-" if not b else f"{(a / b - 1) * 100:+.2f}%"


def _dt(iso: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(iso) if iso else None


def _dh(iso: Optional[str]) -> str:
    d = _dt(iso)
    return d.astimezone(timezone.utc).strftime("%d/%m %H:%M") if d else "-"


def _hm(iso: Optional[str]) -> str:
    d = _dt(iso)
    return d.astimezone(timezone.utc).strftime("%H:%M") if d else "-"


def _data(giorno: str) -> str:
    try:
        return date.fromisoformat(giorno).strftime("%d/%m")
    except ValueError:
        return giorno


def _aperta(c: dict, nome: str) -> datetime:
    return c.get("aperta") or c["chiusa"] - timedelta(minutes=MINUTI.get(nome, 0))


# --- la memoria stabile (in cache) ------------------------------------------------------------------------------------
def _uscite(b: dict) -> str:
    parti = [f"{k} {b['uscite'][k]}" for k in CATEGORIE if b["uscite"][k]]
    return ", ".join(parti) if parti else "-"


def riga_bilancio(nome: str, ops: List[dict]) -> str:
    if not ops:
        return f"{nome}: nessuna operazione chiusa"
    b = bilancio(ops)
    riga = f"{nome}: {b['n']} operazioni, netto {b['netto']:+.2f} USDT"
    if b["con_dettaglio"]:
        riga += f" (prezzo {b['prezzo']:+.2f}, spese {-b['spese']:+.2f}, funding {b['funding']:+.2f})"
    riga += f"; vinte {b['vinte']}, perse {b['perse']}"
    lati = []
    for lato, nome_lato in (("lungo", "lunghi"), ("corto", "corti")):
        x = [o for o in ops if o["lato"] == lato]
        if x:
            lati.append(f"{nome_lato} {len(x)} ({sum(o['risultato'] > 0 for o in x)} vinte, {sum(o['risultato'] < 0 for o in x)} "
                        f"perse, {bilancio(x)['netto']:+.2f})")          # con la stessa regola del netto (revisione, N2)
    return riga + "; " + ", ".join(lati) + f"; uscite: {_uscite(b)}"


def riga_lezione(lez: dict) -> str:
    dopo = f", dopo l'operazione #{lez['dopo']}" if lez.get("dopo") else ""
    giorno = f", giorno a {lez['giorno_netto']:+.2f}" if lez.get("giorno_netto") is not None else ""
    return f"- {_dh(lez.get('ora'))}{dopo}{giorno}: {lez['testo']}"


def _spostamenti(o: dict, campo: str) -> Tuple[list, list]:
    tutti = [s for s in o.get("spostamenti") or [] if s.get("campo") == campo]
    return [s for s in tutti if s.get("prima_dell_esecuzione")], [s for s in tutti if not s.get("prima_dell_esecuzione")]


def _verso_stop(lato: str, entrata: float, iniziale: float, ultimo: Optional[float]) -> str:
    """Da che parte sta lo stop spostato: in perdita più vicino o più lontano, oppure oltre l'entrata dalla parte del guadagno."""
    if ultimo is None:
        return "-"
    guadagno = ultimo > entrata if lato == "lungo" else ultimo < entrata
    if guadagno:
        return "oltre l'entrata, dalla parte del guadagno"
    return "più vicino all'entrata" if abs(ultimo - entrata) < abs(iniziale - entrata) else "più lontano dall'entrata"


def scheda(o: dict) -> str:
    """La scheda intera di un'operazione chiusa (controllo del 26 novembre 2026, punto 3.1): fatti, non giudizi."""
    tipo = o.get("tipo") or "-"
    d = durata_min(o)
    tempi = f"{_dh(o.get('aperta'))}"
    if tipo == "limite" and o.get("eseguita"):
        tempi += f", eseguito {_hm(o['eseguita'])}"
    tempi += f" -> chiusa {_hm(o.get('chiusa'))}" + (f" ({d:.0f} min)" if d is not None else "")
    q = o.get("quantita")
    valore = f" valore {q * o['entrata']:.0f}" if q else ""
    parti = [f"#{o.get('n', '?')} {tempi} {o['lato']} x{o['leva']:g}{valore}",
             f"entrata {_p(o['entrata'])} ({tipo}" + (f": {o['nota']}" if o.get("nota") else "") + ")"]
    si = o.get("stop_iniziale")
    if si:
        dist = abs(si - o["entrata"])
        stop = f"stop iniziale {_p(si)} ({dist / o['entrata'] * 100:.2f}%"
        stop += f", {dist / o['atr15']:.2f} ATR15)" if o.get("atr15") else ")"
        prima, dopo = _spostamenti(o, "stop")
        if prima:
            stop += f"; prima dell'esecuzione l'avevi spostato {_volte(len(prima))}, da {_p(prima[0].get('da'))}"
        if dopo:
            ultimo = dopo[-1].get("a")
            stop += f"; poi spostato {_volte(len(dopo))} fino a {_p(ultimo)} ({_verso_stop(o['lato'], o['entrata'], si, ultimo)})"
        parti.append(stop)
    oi = o.get("obiettivo_iniziale")
    _, ob_dopo = _spostamenti(o, "obiettivo")
    if oi or ob_dopo:
        parti.append(f"obiettivo {_p(oi)}" + (f" -> {_p(ob_dopo[-1].get('a'))}" if ob_dopo else ""))
    else:
        parti.append("nessun obiettivo")
    parti.append(f"uscita {_p(o.get('uscita'))}" + (" (stimata)" if o.get("uscita_stimata") else "") + f": {o.get('come', '-')}")
    netto = f"{o['risultato']:+.2f} netti"
    if o.get("r") is not None:
        netto += f" ({o['r']:+.2f} R)"
    if o.get("risultato_prezzo") is not None:
        netto += f"; prezzo {o['risultato_prezzo']:+.2f}, spese {-(o.get('spese') or 0):+.2f}, funding {o.get('funding') or 0:+.2f}"
    parti.append(netto)
    if o.get("favore_r") is not None and o.get("contro_r") is not None:
        parti.append(f"dall'esecuzione il prezzo è andato al massimo {o['favore_r']:+.2f} R a favore e {-o['contro_r']:.2f} R contro")
    if o.get("motivo"):
        parti.append(f"motivo all'apertura: {o['motivo']}")
    if o.get("approccio"):
        parti.append(f"approccio: {o['approccio']}")
    return " | ".join(parti)


def scheda_corta(o: dict) -> str:
    d = durata_min(o)
    r = f" ({o['r']:+.2f} R)" if o.get("r") is not None else ""
    eseguito = f" (limite, eseguito {_hm(o['eseguita'])})" if o.get("tipo") == "limite" and o.get("eseguita") else ""
    return (f"#{o.get('n', '?')} {_dh(o.get('aperta'))}{eseguito} {o['lato']} x{o['leva']:g} {_p(o['entrata'])} -> "
            f"{_p(o.get('uscita'))} {o.get('come', '-')} {o['risultato']:+.2f}{r}" + (f", {d:.0f} min" if d is not None else ""))


def _ripartenza_di_oggi(m: "Memoria") -> Optional[str]:
    """L'ora della ripartenza da 1.000 USDT se è avvenuta oggi (avvio.Trader.azzera; diciannovesima revisione, problema 269)."""
    ini = m.inizio or {}
    return ini.get("ora") if ini.get("prima") and ini.get("giorno") == m.giorno else None


def blocco_stabile(m: Memoria) -> str:
    """La memoria che cambia solo quando un'operazione si chiude (o a mezzanotte): va nella cache da un'ora."""
    ops = m.operazioni
    prima = m.inizio.get("prima") or None
    ripartita = ""
    if prima:
        # il proprietario, 28 novembre 2026: «riparti da 1000 USD» (avvio.Trader.azzera); la memoria di prima resta
        ripartita = (f"; il conto è ripartito da {m.inizio.get('conto', 0):.0f} USDT quel giorno: prima, dal "
                     f"{_data(prima.get('giorno') or '-')}, era arrivato a {prima.get('fine') or 0:.2f}; le operazioni di prima restano "
                     f"qui sotto")
    righe = ["# La tua memoria (cambia solo quando un'operazione si chiude)",
             f"prova iniziata il {_data(m.inizio.get('giorno', '-'))} con {m.inizio.get('conto', 0):.0f} USDT, su un conto "
             f"simulato con i prezzi veri di Binance{ripartita}", "",
             "## Bilancio delle operazioni chiuse (netto = prezzo + spese + funding)"]
    ieri = (date.fromisoformat(m.giorno) - timedelta(days=1)).isoformat() if m.giorno else ""
    ripartenza = _ripartenza_di_oggi(m)
    oggi = [o for o in ops if str(o.get("chiusa", ""))[:10] == m.giorno and (not ripartenza or str(o.get("chiusa", "")) > ripartenza)]
    righe.append(riga_bilancio(f"oggi ({_data(m.giorno)}{', dalla ripartenza' if ripartenza else ''})", oggi))
    righe.append(riga_bilancio(f"ieri ({_data(ieri)})", [o for o in ops if str(o.get("chiusa", ""))[:10] == ieri]))
    tutte = "dall'inizio" if not ops or ops[0].get("n") in (1, None) else f"ultime {len(ops)} in memoria"
    if prima and tutte == "dall'inizio":
        tutte = "dall'inizio, anche prima della ripartenza"
    righe.append(riga_bilancio(tutte, ops))
    righe += ["", "## Le tue lezioni (scritte da te; restano anche nei giorni dopo)"]
    fisse = [x for x in m.lezioni if x.get("fissata")][-LEZIONI_MOSTRATE:]
    righe += [riga_lezione(x) for x in fisse] or ["nessuna ancora"]
    righe += ["", "## Le tue operazioni chiuse (1 R = la perdita netta prevista allo stop in vigore all'esecuzione, spese "
                  "comprese; a favore e contro: quanto è andato il prezzo degli scambi fra esecuzione e chiusura)"]
    ultime = ops[-OPERAZIONI_MOSTRATE:]
    if not ultime:
        righe.append("nessuna operazione chiusa finora")
    else:
        b = bilancio(ultime)
        durata = f"; durata mediana {b['durata_mediana']:.0f} min" if b["durata_mediana"] is not None else ""
        righe.append(f"ultime {len(ultime)}: uscite {_uscite(b)}{durata}; spese {b['spese']:.2f} USDT")
        righe += [scheda_corta(o) for o in ultime[:-SCHEDE_INTERE]]
        righe += [scheda(o) for o in ultime[-SCHEDE_INTERE:]]
    return "\n".join(righe)


# --- il resto (nuovo a ogni chiamata) ---------------------------------------------------------------------------------
def _atr_testo(dist: float, atr: Dict[str, Optional[float]]) -> str:
    parti = [f"{dist / atr[k]:.2f} ATR{k[:-1]}" for k in ("15m", "5m", "30m") if atr.get(k)]
    return " = " + parti[0] + (f" ({', '.join(parti[1:])})" if len(parti) > 1 else "") if parti else ""


def _dist(livello: float, da: float, atr: Dict[str, Optional[float]], nome: str) -> str:
    return f"dal {nome} {(livello / da - 1) * 100:+.2f}%{_atr_testo(abs(livello - da), atr)}"


def righe_posizione(p: Posizione, a: dict, prezzo: float, moneta: str, atr: Dict[str, Optional[float]],
                    ora: datetime) -> List[str]:
    q, e = p.quantita, p.entrata
    valore = q * e
    limite = a.get("tipo") == "limite"
    spese = a.get("spese_entrata") if a.get("spese_entrata") is not None else spese_entrata(valore, limite)
    funding = a.get("funding") or 0.0
    es = _dt(a.get("eseguita"))
    quando = f", eseguita alle {es.strftime('%H:%M')}, {(ora - es).total_seconds() / 60:.0f} min fa" if es else ""
    base = moneta.replace("USDT", "")
    tipo = "limite" if limite else ("mercato: " + a["nota"] if a.get("nota") else "mercato")
    righe = [f"posizione aperta: {p.lato} {q:g} {base}, entrata {_p(e)} ({tipo}{quando}), "
             f"leva {p.leva:g}, valore {valore:.0f}, margine {valore / p.leva:.0f}"]
    si = a.get("stop_iniziale")
    stop = f"stop {_p(p.stop)}"
    if si and abs(si - p.stop) > 1e-9:
        _, dopo = _spostamenti(a, "stop")
        stop += f" (iniziale {_p(si)}, spostato {_volte(len(dopo))})"
    righe.append(f"{stop}: {_dist(p.stop, prezzo, atr, 'prezzo')}")
    if p.obiettivo:
        righe.append(f"obiettivo {_p(p.obiettivo)}: {_dist(p.obiettivo, prezzo, atr, 'prezzo')}")
    else:
        righe.append("nessun obiettivo sul conto")
    if p.liquidazione:
        righe.append(f"liquidazione {_p(p.liquidazione)}: dal prezzo {(p.liquidazione / prezzo - 1) * 100:+.2f}%")
    lordo = (prezzo - e) * q if p.lato == "lungo" else (e - prezzo) * q
    netto = netto_a(p.lato, e, q, prezzo, spese, funding, moneta)
    costo_uscita = uscita_effettiva(p.lato, prezzo, moneta) * q * COMMISSIONE_MERCATO + abs(
        uscita_effettiva(p.lato, prezzo, moneta) - prezzo) * q
    righe.append(f"risultato adesso: lordo {lordo:+.2f}; se chiudi adesso netto {netto:+.2f} (spese d'entrata pagate "
                 f"{spese:.2f}, uscita a mercato circa {costo_uscita:.2f}, funding {funding:+.2f})")
    r = a.get("R") or un_r(p.lato, e, q, si or p.stop, spese, moneta)
    allo_stop = netto_a(p.lato, e, q, p.stop, spese, funding, moneta)
    riga = f"allo stop: netto {allo_stop:+.2f}" + (f" ({allo_stop / r:+.2f} R)" if r else "")
    if p.obiettivo:
        all_ob = netto_a(p.lato, e, q, p.obiettivo, spese, funding, moneta)
        riga += f"; all'obiettivo: netto {all_ob:+.2f}" + (f" ({all_ob / r:+.2f} R)" if r else "")
    riga += f"; pareggio netto (uscita a mercato) {_p(pareggio(p.lato, e, q, spese, funding, moneta))}"
    righe.append(riga)
    if r:
        righe.append(f"1 R = {r:.2f} USDT (perdita netta allo stop in vigore all'esecuzione)")
        if a.get("escursione"):
            fav, contro = a["escursione"]
            righe.append(f"dall'esecuzione il prezzo è andato al massimo {fav * q / r:+.2f} R a favore e {-contro * q / r:.2f} R "
                         f"contro")
    return righe


def righe_attesa(p: Posizione, a: dict, prezzo: float, moneta: str, atr: Dict[str, Optional[float]],
                 ora: datetime) -> List[str]:
    """Un ordine limite non eseguito non è un'operazione (controllo del 26 novembre 2026, punto 2.1)."""
    q, lim = p.quantita, p.entrata
    valore = q * lim
    messo = _dt(a.get("inviato") or a.get("aperta"))
    quando = f", messo alle {messo.strftime('%H:%M')} ({(ora - messo).total_seconds() / 60:.0f} min fa)" if messo else ""
    verso = "sotto" if p.lato == "lungo" else "sopra"
    righe = ["ordine limite IN ATTESA, non eseguito: nessuna posizione e nessun risultato",
             f"{p.lato} {q:g} {moneta.replace('USDT', '')} a {_p(lim)} (valore {valore:.0f}, margine {valore / p.leva:.0f} bloccato, "
             f"leva {p.leva:g}){quando}; "
             f"il prezzo adesso è {_p(prezzo)} ({_pct(prezzo, lim)} dal limite)",
             f"si esegue solo quando il prezzo degli scambi va oltre {_p(lim)} ({verso}); stop {_p(p.stop)} e "
             + (f"obiettivo {_p(p.obiettivo)} lavorano" if p.obiettivo else "nessun obiettivo; lo stop lavora")
             + " solo dall'esecuzione; «chiudi» lo annulla"]
    spese = spese_entrata(valore, True)
    r = un_r(p.lato, lim, q, p.stop, spese, moneta)
    riga = f"se si esegue: stop {_dist(p.stop, lim, atr, 'limite')}"
    if r:
        riga += f"; 1 R = {r:.2f} USDT"
    if p.obiettivo:
        ob = netto_a(p.lato, lim, q, p.obiettivo, spese, 0.0, moneta)
        riga += f"; all'obiettivo netto {ob:+.2f}" + (f" ({ob / r:+.2f} R)" if r else "")
    righe.append(riga)
    return righe


def blocco_conto(c: Conto, prezzo: float, aperta: Optional[dict], m: Memoria, moneta: str,
                 atr: Dict[str, Optional[float]], ora: datetime) -> str:
    guadagno = c.conto - c.conto_mezzanotte
    netto = guadagno_netto(c)
    ob = obiettivo_usdt(c)
    chiusura = f", {netto:+.2f} se chiudi adesso (spese di chiusura tolte)" if c.spese_chiusura else ""
    ripartenza = _ripartenza_di_oggi(m)
    da = f"dalla ripartenza delle {_hm(ripartenza)} UTC" if ripartenza else "da mezzanotte UTC"
    base = "del conto alla ripartenza" if ripartenza else "del conto a mezzanotte"
    righe = [f"conto {c.conto:.2f} USDT (disponibile {c.disponibile:.2f}); {da} {guadagno:+.2f}{chiusura}; obiettivo "
             f"del giorno ({OBIETTIVO_GIORNO_QUOTA:.0%} {base}, {c.conto_mezzanotte:.2f}, contato dopo le spese di "
             f"chiusura) {ob:.2f}: mancano {max(0.0, round(ob, 2) - round(netto, 2)):.2f}"]
    ini = m.inizio.get("conto")
    if ini:
        righe.append(f"dall'inizio della prova ({_data(m.inizio.get('giorno', '-'))}, {ini:.0f} USDT): {c.conto - ini:+.2f} "
                     f"({(c.conto / ini - 1) * 100:+.1f}%)")
    serie = serie_perdente(m.operazioni)
    if serie:
        lati = ", ".join(f"{n} {uno if n == 1 else tanti}" for lato, uno, tanti in (("lungo", "lungo", "lunghi"),
                                                                                    ("corto", "corto", "corti"))
                         for n in [sum(o["lato"] == lato for o in serie)] if n)
        righe.append(f"operazioni perse di fila adesso: {len(serie)} ({lati}), netto {sum(o['risultato'] for o in serie):+.2f}; "
                     f"il prezzo dall'entrata della prima: {_pct(prezzo, serie[0]['entrata'])}")
    p = c.posizione
    if p is None:
        righe.append("nessuna operazione aperta e nessun ordine in attesa")
    elif p.in_attesa:
        righe += righe_attesa(p, aperta or {}, prezzo, moneta, atr, ora)
    else:
        righe += righe_posizione(p, aperta or {}, prezzo, moneta, atr, ora)
    return "\n".join(righe)


def _var_oi(storia: List[Tuple[int, float]], ora_ms: int, ore: float) -> str:
    if not storia:
        return "-"
    ultimo = storia[-1][1]
    prima = [v for t, v in storia if t <= ora_ms - ore * 3600_000]
    return _pct(ultimo, prima[-1]) if prima and prima[-1] else "-"


def blocco_mercato(ora: datetime, moneta: str, candele: Dict[str, List[dict]], mercato: dict,
                   posizione: Optional[Posizione]) -> str:
    prezzo = mercato["prezzo"]
    ora_ms = int(ora.timestamp() * 1000)
    righe = [f"prezzo mark {_p(prezzo)} (stop, obiettivo e liquidazione scattano su questo; le candele sono dei prezzi degli scambi)"
             + (f"; indice {_p(mercato['indice'])} (premio del perpetuo sull'indice "
                f"{(prezzo / mercato['indice'] - 1) * 1e4:+.1f} punti base)" if mercato.get("indice") else "")]
    f = mercato.get("funding")
    if f is not None:
        riga = (f"funding {f * 100:+.4f}% ogni 8 ore (positivo: i lunghi pagano i corti; livello base +0.0100%), prossimo pagamento "
                f"fra {mercato.get('minuti_al_prossimo_funding', '-')} min")
        if posizione is not None and not posizione.in_attesa:
            importo = posizione.quantita * prezzo * f * (-1 if posizione.lato == "lungo" else 1)
            riga += f"; sulla tua posizione circa {importo:+.2f} USDT"
        righe.append(riga)
    oi, storia = mercato.get("interesse_aperto"), mercato.get("interesse_aperto_storia") or []
    if oi:
        righe.append(f"interesse aperto {oi:.0f} {moneta.replace('USDT', '')}: in 1 ora {_var_oi(storia, ora_ms, 1)}, in 4 ore "
                     f"{_var_oi(storia, ora_ms, 4)}")
    mezzanotte = ora.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    c5 = [c for c in candele.get("5m", []) if _aperta(c, "5m") >= mezzanotte]
    if c5:
        vol = sum(c["volume"] for c in c5)
        acq = [c.get("acquisti") for c in c5]
        quota = f"; acquisti a mercato {sum(acq) / vol * 100:.1f}% del volume" if vol and None not in acq else ""
        righe.append(f"da mezzanotte UTC: da {_p(c5[0]['apertura'])} a {_p(prezzo)} ({_pct(prezzo, c5[0]['apertura'])}); vwap del "
                     f"giorno {_p(vwap(c5))}{quota}")
    c30 = candele.get("30m", [])
    if c30:
        ieri = mezzanotte - timedelta(days=1)
        oggi30 = [c for c in c30 if _aperta(c, "30m") >= mezzanotte]
        ieri30 = [c for c in c30 if ieri <= _aperta(c, "30m") < mezzanotte]
        ore = (ora - _aperta(c30[0], "30m")).total_seconds() / 3600

        def intervallo(cs):
            lo, hi = min(c["minimo"] for c in cs), max(c["massimo"] for c in cs)
            return lo, hi, f"{_p(lo)}-{_p(hi)} ({(hi / lo - 1) * 100:.2f}%)"
        parti = []
        if oggi30:
            lo, hi, testo = intervallo(oggi30)
            parti.append(f"oggi {testo}, il prezzo è a {_pct(prezzo, hi)} dal massimo e {_pct(prezzo, lo)} dal minimo")
        if ieri30:
            parti.append(f"ieri {intervallo(ieri30)[2]}")
        parti.append(f"ultime {ore:.0f} ore {intervallo(c30)[2]}")
        righe.append("livelli (candele da 30 minuti): " + "; ".join(parti))
        chiuse30 = [c for c in c30 if not c.get("in_corso")]
        fasce = []
        for da, a, nome in calendario.FASCE:
            amp = [(c["massimo"] - c["minimo"]) / c["apertura"] * 100 for c in chiuse30 if da <= _aperta(c, "30m").hour < a]
            if amp:
                fasce.append(f"{nome} {median(amp):.2f}%")
        if fasce:
            righe.append(f"ampiezza mediana di una candela da 30 minuti nelle ultime {ore:.0f} ore, per fascia oraria: "
                         + ", ".join(fasce))
    righe.append(calendario.riga_orari(ora))
    return "\n".join(righe)


def blocco_intervallo(nome: str, candele: List[dict], ora: datetime) -> str:
    candele = [c for c in candele if _aperta(c, nome) <= ora]          # mai una candela aperta dopo l'ora della chiamata
    chiuse = [c for c in candele if not c.get("in_corso") and c["chiusa"] <= ora]
    in_corso = next((c for c in candele if c.get("in_corso") or c["chiusa"] > ora), None)
    if not chiuse:
        return f"## candele {nome}: nessuna"
    righe = [f"## candele {nome} (ora d'apertura UTC: apertura massimo minimo chiusura volume acquisti%)"]
    giorno = None

    def riga(c):
        acq = f" {c['acquisti'] / c['volume'] * 100:.0f}" if c.get("acquisti") is not None and c["volume"] else ""
        return f"{_pc(c['apertura'])} {_pc(c['massimo'])} {_pc(c['minimo'])} {_pc(c['chiusura'])} {_v(c['volume'])}{acq}"
    for c in chiuse[-MOSTRATE:]:
        t = _aperta(c, nome)
        if t.date() != giorno:
            giorno = t.date()
            righe.append(f"-- {giorno:%d/%m} --")
        righe.append(f"{t:%H:%M} {riga(c)}")
    if in_corso is not None:
        t = _aperta(in_corso, nome)
        righe.append(f"in corso, aperta alle {t:%H:%M} (da {(ora - t).total_seconds() / 60:.0f} min): {riga(in_corso)}")
    ind = riassunto(chiuse)
    atr = ind.get("atr14")
    ultima = chiuse[-1]["chiusura"]
    righe.append(f"indicatori sull'ultima candela chiusa: ema9 {_pc(ind['ema9'])}, ema21 {_pc(ind['ema21'])}, ema50 "
                 f"{_pc(ind['ema50'])}; bollinger {_pc(ind['bollinger_bassa'])} / {_pc(ind['bollinger_media'])} / "
                 f"{_pc(ind['bollinger_alta'])}; macd {_s(ind['macd'])}, segnale {_s(ind['macd_segnale'])}; atr14 {_s(atr)}"
                 + (f" ({atr / ultima * 100:.2f}%)" if atr else "")
                 + f"; ampiezza mediana delle ultime 20 candele {_s(ind['ampiezza_mediana20'])} "
                   f"({ind['ampiezza_mediana20'] / ultima * 100:.2f}%)")
    righe.append("ultime 4 candele chiuse (dalla più vecchia): rsi14 " + " ".join(_s(x) if x is None else f"{x:.0f}"
                                                                                 for x in ind["ultimi_rsi14"])
                 + "; istogramma macd " + " ".join(_s(x) for x in ind["ultimi_macd_istogramma"])
                 + "; volume/media20 " + " ".join(_s(x) for x in ind["ultimi_volume_su_media20"]))
    return "\n".join(righe)


def atr_per_intervallo(candele: Dict[str, List[dict]], ora: datetime) -> Dict[str, Optional[float]]:
    return {k: riassunto([c for c in v if not c.get("in_corso") and c["chiusa"] <= ora]).get("atr14")
            for k, v in candele.items()}


def blocco_variabile(ora: datetime, motivo: str, moneta: str, candele: Dict[str, List[dict]], mercato: dict, conto: Conto,
                     aperta: Optional[dict], m: Memoria, chiamate: str) -> str:
    prezzo = mercato["prezzo"]
    atr = atr_per_intervallo(candele, ora)
    righe = [f"ora {ora.astimezone(timezone.utc):%Y-%m-%d %H:%M} UTC; motivo della chiamata: {motivo}", f"chiamate: {chiamate}"]
    if m.scarto:
        righe += ["", "# La tua decisione precedente NON è stata eseguita", m.scarto]
    righe += ["", "# Conto", blocco_conto(conto, prezzo, aperta, m, moneta, atr, ora)]
    righe += ["", f"# {moneta}", blocco_mercato(ora, moneta, candele, mercato, conto.posizione)]
    righe += ["", "# Il tuo approccio e le tue note", f"approccio attuale: {m.approccio or 'nessuno ancora'}"]
    nuove = [x for x in m.lezioni if not x.get("fissata")][-LEZIONI_MOSTRATE:]
    if nuove:
        righe.append("lezioni scritte dopo l'ultima operazione chiusa:")
        righe += [riga_lezione(x) for x in nuove]
    if m.note:
        righe.append(f"le tue note (ultime {min(len(m.note), NOTE_MOSTRATE)} chiamate):")
        righe += [f"- {x}" for x in m.note[-NOTE_MOSTRATE:]]
    for nome, c in candele.items():
        righe += ["", blocco_intervallo(nome, c, ora)]
    return "\n".join(righe)


def costruisci(ora: datetime, motivo: str, moneta: str, candele: Dict[str, List[dict]], mercato: dict, conto: Conto,
               aperta: Optional[dict], memoria: Memoria, chiamate: str) -> Tuple[str, str, str]:
    """Ritorna (system, memoria stabile, resto). `candele`: intervallo («5m», «15m», «30m») -> candele (chiuse e quella in
    corso); `mercato`: prezzo, indice, funding, minuti al prossimo funding, interesse aperto e la sua storia."""
    return (ISTRUZIONI.read_text(), blocco_stabile(memoria),
            blocco_variabile(ora, motivo, moneta, candele, mercato, conto, aperta, memoria, chiamate))
