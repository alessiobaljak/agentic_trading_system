"""IL REPORT GIORNALIERO (1 ott 2026, richiesta del proprietario: «una struttura
del report mattutino che dovra' poi essere sempre uguale … metti questo report
nella dashboard cosi' al mattino devo solo consultare una sezione»).

La STRUTTURA E' FISSA: nove sezioni, sempre le stesse, nello stesso ordine,
anche quando un dato manca (allora la sezione lo dice). Cambia il contenuto,
non la forma, cosi' il proprietario sa dove guardare ogni mattina:

  1. in_breve   — In breve: le 4-6 righe che contano
  2. paper      — Il paper ieri (e la settimana, e dal 27 set)
  3. gate       — Come va il gate
  4. imparato   — Cosa ci dicono i dati: ingressi, uscite e trailing, stop,
                  rischio, direzione e mercato, strategie e idee
  5. funzioni   — Le funzioni servono? (bot/learning/contributi.py)
  6. capito     — Cosa abbiamo capito (la stella polare: docs/capito.md)
  7. cambiato   — Cosa e' cambiato nel sistema (i commit)
  8. attesa     — Aspetta il tuo si', in lavorazione, prossime letture
  9. salute     — Salute e costi (anomalie, spesa AI, letture Firebase)

Ogni sezione: {id, titolo, righe: [str], tabella: {colonne, righe}|None,
fonte: str, errore: str|None}. Tutto e' PURO: le letture le fa
`scripts/report_giornaliero.py`. Ogni sezione e' calcolata da sola (fail-open):
una che fallisce scrive il suo errore e le altre escono lo stesso.

Giornate in ORA ITALIANA (`bot/core/tempo.py`), per data di USCITA dei trade.
R = pnl / (|entry - stop originale| x size), come nei conti in R (K8).
"""
from __future__ import annotations

import re
import statistics
import time
from datetime import datetime, timedelta, timezone

from bot.core.tempo import fuso, giorno_locale

VERSIONE_SCHEMA = 1
#: la fine del difetto della sessione (J13): da qui il paper e' «pulito»
DAL_PULITO = datetime(2026, 9, 27, 19, 40, tzinfo=timezone.utc).timestamp()
#: i titoli fissi, nell'ordine di stampa
SEZIONI = (
    ("in_breve", "In breve"),
    ("paper", "Il paper ieri"),
    ("gate", "Come va il gate"),
    ("imparato", "Cosa ci dicono i dati"),
    ("funzioni", "Le funzioni servono?"),
    ("capito", "Cosa abbiamo capito"),
    ("cambiato", "Cosa è cambiato nel sistema"),
    ("attesa", "Aspetta il tuo sì e prossime letture"),
    ("salute", "Salute e costi"),
)
#: gli esiti che non sono decisioni della strategia (chiusure a mano, kill...)
_ESTERNI = {"manual", "kill_switch", "circuit_breaker"}


# --------------------------------------------------------------------------- #
# utilita'                                                                     #
# --------------------------------------------------------------------------- #
def _num(v) -> float | None:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if (f != f or f in (float("inf"), float("-inf"))) else f


def _ts(v) -> float | None:
    f = _num(v)
    if f is not None:
        return f
    if v:
        try:
            return datetime.fromisoformat(str(v).replace("Z", "+00:00")).timestamp()
        except (TypeError, ValueError):
            return None
    return None


def uscita_ts(t: dict) -> float | None:
    return _ts(t.get("exit_ts")) or _ts(t.get("exit_time"))


def ingresso_ts(t: dict) -> float | None:
    return _ts(t.get("entry_ts")) or _ts(t.get("entry_time"))


def _rischio(t: dict) -> float | None:
    from bot.learning.drift import stop_originale
    try:
        stop = stop_originale(t)
        if stop is None:
            return None
        r = abs(float(t.get("entry_price") or 0) - stop) * float(t.get("size") or 0)
        return r if r > 0 else None
    except Exception:  # noqa: BLE001
        return None


def _r(t: dict) -> float | None:
    from bot.learning.drift import r_multiplo
    try:
        return r_multiplo(t)
    except Exception:  # noqa: BLE001
        return None


def _usd(v) -> str:
    return "—" if v is None else f"{v:+.2f}"


def _rr(v) -> str:
    return "—" if v is None else f"{v:+.3f}R"


def _pct(v, dec: int = 0) -> str:
    return "—" if v is None else f"{v * 100:.{dec}f}%"


def _med(xs) -> float | None:
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def blocco(trades: list[dict]) -> dict:
    """I numeri di un gruppo di trade: n, vinti, PnL, R netto/lordo/costi medi."""
    n = len(trades)
    pnl = sum(_num(t.get("pnl")) or 0.0 for t in trades)
    vinti = sum(1 for t in trades if (_num(t.get("pnl")) or 0) > 0)
    rn, rl, rc = [], [], []
    for t in trades:
        r = _r(t)
        if r is None:
            continue
        rn.append(r)
        rischio = _rischio(t)
        lordo, costi = _num(t.get("gross_pnl_usdt")), _num(t.get("total_cost_usdt"))
        if rischio and lordo is not None:
            rl.append(lordo / rischio)
        if rischio and costi is not None:
            rc.append(costi / rischio)
    m = lambda xs: round(sum(xs) / len(xs), 3) if xs else None  # noqa: E731
    return {"n": n, "vinti": vinti, "win_rate": (vinti / n) if n else None,
            "pnl": round(pnl, 2), "n_r": len(rn), "r_netto": m(rn), "r_lordo": m(rl),
            "costi_r": m(rc)}


def periodi(trades: list[dict], giorno: str) -> dict:
    """I trade per periodo: ieri (giorno), 7 giorni fino a ieri, dal 27 set, tutto."""
    d = datetime.fromisoformat(giorno).date()
    sette = {(d - timedelta(days=i)).isoformat() for i in range(7)}
    out = {"ieri": [], "7g": [], "pulito": [], "tutto": []}
    for t in trades or []:
        ex = uscita_ts(t)
        if ex is None:
            continue
        g = giorno_locale(ex)
        if g > giorno:
            continue                 # oggi: non e' ancora una giornata chiusa
        out["tutto"].append(t)
        if g == giorno:
            out["ieri"].append(t)
        if g in sette:
            out["7g"].append(t)
        en = ingresso_ts(t)
        if en is not None and en >= DAL_PULITO:
            out["pulito"].append(t)
    return out


def _sezione(sid: str, righe=None, tabella=None, fonte: str = "", errore=None) -> dict:
    titolo = dict(SEZIONI)[sid]
    return {"id": sid, "titolo": titolo, "righe": list(righe or []), "tabella": tabella,
            "fonte": fonte, "errore": errore}


# --------------------------------------------------------------------------- #
# 2. il paper                                                                  #
# --------------------------------------------------------------------------- #
def sez_paper(trades: list[dict], controllo: dict | None, giorno: str) -> dict:
    validate = [t for t in trades or [] if not t.get("esplorativa")
                and str(t.get("exit_reason") or "") not in _ESTERNI]
    p = periodi(validate, giorno)
    tutti = periodi(trades or [], giorno)
    righe_tab = []
    for nome, chiave in (("ieri", "ieri"), ("7 giorni", "7g"), ("dal 27 set", "pulito"),
                         ("tutto", "tutto")):
        b = blocco(p[chiave])
        righe_tab.append([nome, b["n"], _pct(b["win_rate"]), _usd(b["pnl"]), _rr(b["r_netto"]),
                          _rr(b["r_lordo"]), _rr(b["costi_r"])])
    ieri = blocco(p["ieri"])
    conto_ieri = blocco(tutti["ieri"])
    paper = (controllo or {}).get("paper") or {}
    salute = (controllo or {}).get("salute") or {}
    righe = [
        f"Ieri ({giorno}): {ieri['n']} trade delle validate, {ieri['vinti']} vinti, "
        f"{_usd(ieri['pnl'])} USDT, {_rr(ieri['r_netto'])} netti a trade. Sul conto (esplorativi "
        f"e chiusure esterne compresi): {conto_ieri['n']} trade, {_usd(conto_ieri['pnl'])} USDT.",
    ]
    eq = _num(paper.get("equity"))
    if eq is not None:
        righe.append(f"Equity {eq:.2f} USDT ({_usd(_num(paper.get('rendimento_pct')))}% dall'inizio "
                     f"del paper, il {paper.get('paper_dal') and giorno_locale(float(paper['paper_dal']))}).")
    pos = salute.get("posizioni_aperte")
    if pos is not None:
        righe.append(f"Adesso {pos} posizioni aperte, rischio aperto "
                     f"{_num(salute.get('rischio_aperto_pct')) or 0:.2f}% del capitale, "
                     f"uPnL {_usd(_num(salute.get('upnl_totale')))} USDT.")
    giornate = [g for g in ((paper.get("giornate") or {}).get("ultime_7") or [])
                if isinstance(g, dict)]
    if giornate:
        pos_g = sum(1 for g in giornate if (_num(g.get("pnl_tutti")) or 0) > 0)
        neg_g = sum(1 for g in giornate if (_num(g.get("pnl_tutti")) or 0) < 0)
        righe.append(f"Ultimi 7 giorni sul conto: {pos_g} in utile, {neg_g} in perdita.")
    bm = paper.get("benchmark") or {}
    if _num(bm.get("btc_dal_paper_pct")) is not None:
        righe.append(f"Confronto: BTC comprato il primo giorno {_num(bm['btc_dal_paper_pct']):+.1f}%, "
                     f"noi {_num(bm.get('noi_pct')) or 0:+.1f}%.")
    return _sezione("paper", righe,
                    {"colonne": ["periodo", "trade", "vinti", "PnL USDT", "R netto", "R lordo",
                                 "costi R"], "righe": righe_tab},
                    "trades (Firestore) per data di uscita, ora italiana; equity e posizioni dal "
                    "controllo orario del bot")


# --------------------------------------------------------------------------- #
# 3. il gate                                                                   #
# --------------------------------------------------------------------------- #
def sez_gate(gate: dict | None, portafoglio: dict | None, r1: dict | None) -> dict:
    g = gate or {}
    meta, giro, reg = g.get("meta") or {}, g.get("giro") or {}, g.get("registro") or {}
    cerv = g.get("cervello") or {}
    righe = []
    if not g:
        return _sezione("gate", ["Il documento del gate non e' disponibile."],
                        fonte="dashboard/gate", errore="documento assente")
    at = _num(meta.get("generato_at"))
    durata = _num(meta.get("durata_s"))
    ora = lambda x: datetime.fromtimestamp(x, fuso()).strftime("%d/%m %H:%M")  # noqa: E731
    fatto = (f"{giro.get('valutazioni', 'n/d')} valutazioni, {giro.get('passate', 'n/d')} passate"
             + (f", durato {int(durata // 3600)}h{int(durata % 3600 // 60):02d}" if durata else ""))
    if meta.get("stato") == "in_corso":
        # all'inizio di un giro il documento porta solo `meta` nuovo: i numeri
        # (giro, registro) sono ancora quelli del giro precedente
        inizio = _num(meta.get("iniziato_at"))
        righe.append(f"Un giro e' in corso" + (f" dalle {ora(inizio)}" if inizio else "")
                     + (f"; il precedente era finito alle {ora(at)}" if at else "")
                     + f": {fatto}.")
    else:
        righe.append(f"Ultimo giro: {meta.get('stato') or 'n/d'} ({meta.get('modalita') or 'n/d'})"
                     + (f", finito alle {ora(at)}" if at else "") + f": {fatto}.")
    delta = reg.get("validate_delta_giro")
    righe.append(
        f"Validate {reg.get('validate', 'n/d')}"
        + (f" ({int(delta):+d} nel giro)" if isinstance(delta, (int, float)) and delta else "")
        + f" su {reg.get('coin_coperte', 'n/d')} coin, copertura "
        f"{_pct(_num(reg.get('copertura')), 1)}; declassate {reg.get('declassate', 'n/d')}.")
    vit = (g.get("strategie") or {}).get("vite") or {}
    if vit:
        righe.append(f"Ultimi 7 giorni: {vit.get('promosse_7g', 'n/d')} promosse, "
                     f"{vit.get('rimosse_7g', 'n/d')} rimosse.")
    var = cerv.get("varianti") or {}
    intorno = cerv.get("intorno") or {}
    if var or intorno:
        righe.append(f"Il cervello: varianti dai referti {var.get('create', 0)} create, "
                     f"{len(var.get('promosse') or [])} promosse; intorno "
                     f"{intorno.get('madri', 0)} madri, {len(intorno.get('promosse') or [])} promosse.")
    occ, lim = reg.get("occupazione"), reg.get("limite")
    if occ is not None and lim:
        righe.append(f"Registro: {occ} coppie su un tetto di {lim}.")
    esp = giro.get("esplorative") or {}
    if esp:
        righe.append(f"Esplorative: {esp.get('attive', 'n/d')} attive, poi validate "
                     f"{esp.get('validate_poi', 'n/d')}, scartate {esp.get('scartate', 'n/d')}.")
    pf = portafoglio or {}
    fc = pf.get("fuori_campione") if isinstance(pf.get("fuori_campione"), dict) else {}
    if fc.get("lettura"):
        righe.append(f"Fuori campione (le validate guadagnano anche DOPO la scelta? ultimo "
                     f"report del {str(pf.get('updated_at') or '')[:10]}): {str(fc['lettura'])[:400]}")
    if r1:
        righe.append(f"R1, il gate rigiocato nel passato: {r1.get('date_finite', 0)} date su "
                     f"{r1.get('date_totali', 26)}, {r1.get('unita', 0)} unita' fatte.")
    return _sezione("gate", righe, fonte="dashboard/gate (scritto dalla discovery a ogni giro), "
                    "portfolio/backtest, data/replay_gate")


# --------------------------------------------------------------------------- #
# 4. cosa ci dicono i dati                                                     #
# --------------------------------------------------------------------------- #
def _area(nome: str, gruppi: dict, f) -> list:
    """Una riga di tabella: l'area e il valore di `f` su ieri, 7 giorni e tutto."""
    return [nome] + [f(gruppi[k]) for k in ("ieri", "7g", "tutto")]


def sez_imparato(trades: list[dict], controllo: dict | None, giorno: str) -> dict:
    validate = [t for t in trades or [] if not t.get("esplorativa")
                and str(t.get("exit_reason") or "") not in _ESTERNI]
    p = periodi(validate, giorno)

    def persi(ts):
        return [t for t in ts if (_num(t.get("pnl")) or 0) < 0]

    def q_classe(classe):
        def f(ts):
            con = [t for t in persi(ts) if isinstance(t.get("post_mortem"), dict)]
            if not con:
                return "—"
            k = sum(1 for t in con if t["post_mortem"].get("classe") == classe)
            return f"{k}/{len(con)}"
        return f

    def med(campo, fmt="{:.2f}"):
        def f(ts):
            v = _med([_num(t.get(campo)) for t in ts])
            return "—" if v is None else fmt.format(v)
        return f

    def trailing(verdetto):
        def f(ts):
            v = [t for t in ts if t.get("trailing_verdict")]
            if not v:
                return "—"
            return f"{sum(1 for t in v if t.get('trailing_verdict') == verdetto)}/{len(v)}"
        return f

    def stop_quota(ts):
        if not ts:
            return "—"
        return f"{sum(1 for t in ts if t.get('exit_reason') == 'stop_loss')}/{len(ts)}"

    def post_stop(v):
        def f(ts):
            con = [t for t in ts if t.get("post_stop_verdict")]
            if not con:
                return "—"
            return f"{sum(1 for t in con if t.get('post_stop_verdict') == v)}/{len(con)}"
        return f

    def tp1(ts):
        con = [t for t in ts if t.get("scale_stage_reached") is not None]
        if not con:
            return "—"
        return f"{sum(1 for t in con if (_num(t.get('scale_stage_reached')) or 0) >= 1)}/{len(con)}"

    def rischio(ts):
        v = _med([_num(t.get("risk_effective_pct")) for t in ts])
        return "—" if v is None else f"{v * 100:.2f}%"

    def leva(ts):
        v = [_num(t.get("leverage")) for t in ts]
        v = [x for x in v if x is not None]
        return "—" if not v else f"{sum(v) / len(v):.2f}x"

    def r_dir(d):
        def f(ts):
            b = blocco([t for t in ts if str(t.get("direction") or "").lower() == d])
            return f"{b['n']} a {_rr(b['r_netto'])}" if b["n"] else "—"
        return f

    def ingresso_vs_segnale(ts):
        v = _med([_num(t.get("ingresso_vs_segnale_r")) for t in ts])
        return "non ancora raccolto" if v is None else f"{v:+.3f}R"

    tabella = [
        ["INGRESSI", "", "", ""],
        _area("perdite «mai andate a favore»", p, q_classe("ingresso")),
        _area("latenza segnale → ingresso (s, mediana)", p, med("latenza_s", "{:.0f}")),
        _area("ingresso rispetto al segnale (mediana)", p, ingresso_vs_segnale),
        ["USCITE E TRAILING", "", "", ""],
        _area("perdite morte sotto il primo gradino", p, q_classe("uscita")),
        _area("trailing prematuri / verdetti", p, trailing("premature")),
        _area("trailing protetti / verdetti", p, trailing("protected")),
        _area("arrivati al primo target", p, tp1),
        _area("massimo a favore (mediana, R)", p, med("mfe_r")),
        ["STOP LOSS", "", "", ""],
        _area("chiusi a stop", p, stop_quota),
        _area("stop seguiti da un rimbalzo (rumore)", p, post_stop("rumore")),
        _area("massimo contro (mediana, R)", p, med("mae_r")),
        ["RISCHIO", "", "", ""],
        _area("rischio effettivo per trade (mediana)", p, rischio),
        _area("leva media", p, leva),
        ["DIREZIONE", "", "", ""],
        _area("long: trade e R netto", p, r_dir("long")),
        _area("short: trade e R netto", p, r_dir("short")),
    ]
    righe = []
    ref = ((controllo or {}).get("learning") or {}).get("misurato") or {}
    ipotesi = (ref.get("referti") or {}).get("ipotesi") or []
    if ipotesi:
        righe.append("Ipotesi nate dai referti (le prova il gate sulla storia): "
                     + "; ".join(str(x) for x in ipotesi[:5]))
    trail = (controllo or {}).get("paper", {}).get("trailing") or {}
    if trail.get("proposta_paper") is not None or trail.get("verdetti_totali"):
        righe.append(f"Trailing in tutto: {trail.get('prematuri', 0)} prematuri e "
                     f"{trail.get('protetti', 0)} protetti su {trail.get('verdetti_totali', 0)} "
                     f"verdetti; proposta del paper: {trail.get('proposta_paper') or 'nessuna'}.")
    return _sezione("imparato", righe,
                    {"colonne": ["", "ieri", "7 giorni", "tutto"], "righe": tabella},
                    "trades (referti, verdetti trailing e post-stop, mfe/mae, rischio) e "
                    "controllo orario (ipotesi, trailing)")


# --------------------------------------------------------------------------- #
# 5. le funzioni servono?                                                      #
# --------------------------------------------------------------------------- #
def sez_funzioni(trades: list[dict], specs: dict | None) -> dict:
    from bot.learning.contributi import contributi, per_origine
    righe_tab = []
    for v in contributi(trades or []):
        c = v["confronto"]
        righe_tab.append([v["nome"], f"{c['toccati']['n']} a {_rr(c['toccati']['r_medio'])}",
                          f"{c['altri']['n']} a {_rr(c['altri']['r_medio'])}",
                          ("—" if c.get("differenza") is None
                           else f"{c['differenza']:+.3f} ±{c['margine']:.3f}"),
                          c["verdetto"],
                          _usd(v.get("usdt_risparmiati")) if "usdt_risparmiati" in v else ""])
    righe = ["Regola (scritta prima dei numeri): sotto 10 trade per gruppo «campione piccolo»; "
             "oltre 2 errori standard nel verso atteso «contribuisce», nel verso opposto «va "
             "contro»; altrimenti «non si vede ancora». USDT: quanto ha risparmiato (o tolto) la "
             "riduzione di size rispetto alla size piena."]
    if specs is not None:
        po = per_origine(trades or [], specs)
        righe.append("Origine delle strategie nel paper: "
                     + (" · ".join(f"{o} {s['n']} trade a {_rr(s['r_medio'])}"
                                   for o, s in po.items()) or "nessun trade"))
    return _sezione("funzioni", righe,
                    {"colonne": ["funzione", "toccati", "altri", "differenza", "verdetto", "USDT"],
                     "righe": righe_tab},
                    "trades; bot/learning/contributi.py")


# --------------------------------------------------------------------------- #
# 6. cosa abbiamo capito                                                       #
# --------------------------------------------------------------------------- #
_DATA = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$")


def note_capito(testo: str | None) -> list[tuple[str, list[str]]]:
    """[(data, [righe])] da `docs/capito.md`, la piu' recente per prima."""
    out: list[tuple[str, list[str]]] = []
    for r in (testo or "").splitlines():
        m = _DATA.match(r)
        if m:
            out.append((m.group(1), []))
        elif out and r.strip().startswith(("* ", "- ")):
            out[-1][1].append(r.strip()[2:].replace("**", "").replace("`", ""))
        elif out and out[-1][1] and r.startswith("  ") and r.strip():
            out[-1][1][-1] += " " + r.strip().replace("**", "").replace("`", "")
    out.sort(key=lambda x: x[0], reverse=True)
    return out


def sez_capito(testo: str | None, giorno: str, oggi: str) -> dict:
    note = note_capito(testo)
    if not note:
        return _sezione("capito", ["Nessuna nota ancora in docs/capito.md."], fonte="docs/capito.md")
    data, righe = note[0]
    testa = []
    if data not in (giorno, oggi):
        testa.append(f"ATTENZIONE: l'ultima nota e' del {data}: da allora non e' stato scritto "
                     f"niente di nuovo capito.")
    else:
        testa.append(f"Note del {data}:")
    return _sezione("capito", testa + righe, fonte="docs/capito.md (scritto ogni giorno dal "
                    "controllo del mattino, pubblicato dalla macchina)")


# --------------------------------------------------------------------------- #
# 7. cosa e' cambiato                                                          #
# --------------------------------------------------------------------------- #
_RUMORE = re.compile(r"^(ops:|state snapshot|Merge |merge )", re.I)


def sez_cambiato(commit: list[dict] | None) -> dict:
    """`commit`: [{hash, at, titolo}] dal git log della macchina (ultime 36 ore)."""
    utili = [c for c in commit or [] if c.get("titolo") and not _RUMORE.match(str(c["titolo"]))]
    if commit is None:
        return _sezione("cambiato", ["Storia dei commit non leggibile sulla macchina."],
                        fonte="git log", errore="git non disponibile")
    if not utili:
        return _sezione("cambiato", ["Nessuna modifica al sistema nelle ultime 36 ore."],
                        fonte="git log (ultime 36 ore, senza i commit automatici)")
    righe = [f"{datetime.fromtimestamp(c['at'], fuso()).strftime('%d/%m %H:%M')} — "
             f"{str(c['titolo'])[:220]}" for c in utili[:15]]
    if len(utili) > 15:
        righe.append(f"… e altre {len(utili) - 15} modifiche.")
    return _sezione("cambiato", righe, fonte="git log del repo sulla macchina (ultime 36 ore, "
                    "senza i commit automatici ops e snapshot)")


# --------------------------------------------------------------------------- #
# 8. attesa e letture                                                          #
# --------------------------------------------------------------------------- #
_LETTURA = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|([^|]*)\|([^|]*)\|\s*$")


def letture(testo: str | None) -> list[dict]:
    """Il calendario delle letture da `docs/letture.md`: righe di tabella
    `| AAAA-MM-GG | cosa | regola/fonte |`."""
    out = []
    for r in (testo or "").splitlines():
        m = _LETTURA.match(r.strip())
        if m:
            out.append({"data": m.group(1), "cosa": m.group(2).strip(),
                        "regola": m.group(3).strip()})
    return sorted(out, key=lambda x: x["data"])


def sez_attesa(backlog: dict | None, testo_letture: str | None, oggi: str) -> dict:
    righe = []
    b = backlog or {}
    si = b.get("aspetta_si") or []
    righe.append("Aspettano il tuo sì: " + ("; ".join(f"{v.get('sigla')}. {v.get('titolo')}"
                                                     for v in si) if si else "niente."))
    lav = next((g for g in b.get("gruppi") or [] if g.get("numero") == 1), None)
    if lav and lav.get("voci"):
        righe.append("In lavorazione: " + "; ".join(f"{v.get('sigla')}. {v.get('titolo')}"
                                                    for v in lav["voci"]))
    prossime = [x for x in letture(testo_letture) if x["data"] >= oggi][:6]
    tab = {"colonne": ["data", "cosa si legge", "regola"],
           "righe": [[x["data"], x["cosa"], x["regola"]] for x in prossime]} if prossime else None
    if not prossime:
        righe.append("Nessuna lettura in calendario.")
    return _sezione("attesa", righe, tab, "docs/backlog.md e docs/letture.md")


# --------------------------------------------------------------------------- #
# 9. salute e costi                                                            #
# --------------------------------------------------------------------------- #
def sez_salute(controllo: dict | None, spesa_ieri: dict | None, giorno: str) -> dict:
    c = controllo or {}
    meta, salute = c.get("meta") or {}, c.get("salute") or {}
    righe = [f"Semafori: sistema {meta.get('semaforo_sistema', 'n/d')}, paper "
             f"{meta.get('semaforo_paper', 'n/d')}."]
    anomalie = salute.get("anomalie") or c.get("anomalie") or []
    for a in anomalie[:8]:
        if isinstance(a, dict):
            righe.append(f"Anomalia {a.get('codice')}: {a.get('testo')}")
    if salute.get("riavvii_24h") is not None:
        righe.append(f"Riavvii del bot nelle 24 ore: {salute['riavvii_24h']}.")
    if salute.get("letture_firestore_24h") is not None:
        righe.append(f"Letture Firestore nelle 24 ore: {salute['letture_firestore_24h']} "
                     f"(quota gratuita 50.000).")
    from bot.ai.spesa import riepilogo
    voci = riepilogo(spesa_ieri) if spesa_ieri else []
    if voci:
        tot = sum(v["usd"] for v in voci)
        righe.append(f"Spesa AI di ieri ({giorno}): {tot:.2f} $ in {sum(v['n'] for v in voci)} "
                     f"chiamate — " + ", ".join(f"{v['etichetta']} {v['usd']:.2f} $" for v in voci[:5]))
    else:
        righe.append(f"Spesa AI di ieri ({giorno}): nessun dato.")
    return _sezione("salute", righe, fonte="controllo orario del bot; ai_spesa")


# --------------------------------------------------------------------------- #
# 1. in breve, e il documento intero                                           #
# --------------------------------------------------------------------------- #
def sez_in_breve(sez: dict, controllo: dict | None, backlog: dict | None,
                 trades: list[dict], giorno: str) -> dict:
    righe = []
    meta = (controllo or {}).get("meta") or {}
    if meta.get("semaforo_sistema") == "rosso":
        righe.append("PRIMA DI TUTTO: il sistema ha un'anomalia rossa (vedi Salute e costi).")
    validate = [t for t in trades or [] if not t.get("esplorativa")
                and str(t.get("exit_reason") or "") not in _ESTERNI]
    p = periodi(validate, giorno)
    i, s, pu = blocco(p["ieri"]), blocco(p["7g"]), blocco(p["pulito"])
    righe.append(f"Paper ieri: {i['n']} trade, {_usd(i['pnl'])} USDT ({_rr(i['r_netto'])} a trade). "
                 f"Ultimi 7 giorni {_usd(s['pnl'])} USDT ({_rr(s['r_netto'])}); dal 27 set "
                 f"{_rr(pu['r_netto'])} netti a trade su {pu['n_r']}.")
    g = (sez.get("gate") or {}).get("righe") or []
    if g:
        righe.append("Gate: " + g[0])
    si = (backlog or {}).get("aspetta_si") or []
    righe.append(f"Aspettano il tuo sì: {len(si)}." if si else "Niente aspetta il tuo sì.")
    cap = (sez.get("capito") or {}).get("righe") or []
    if len(cap) > 1:
        righe.append("Capito: " + cap[1])
    return _sezione("in_breve", righe, fonte="le sezioni qui sotto")


def costruisci_report(*, trades: list[dict], controllo: dict | None, gate: dict | None,
                      portafoglio: dict | None, backlog: dict | None, specs: dict | None,
                      capito: str | None, testo_letture: str | None, commit: list[dict] | None,
                      spesa_ieri: dict | None, r1: dict | None, now: float | None = None,
                      versione: str | None = None) -> dict:
    """Il report del giorno PRIMA di `now` (ora italiana). Nove sezioni, sempre."""
    now = time.time() if now is None else now
    oggi = giorno_locale(now)
    giorno = (datetime.fromisoformat(oggi).date() - timedelta(days=1)).isoformat()
    calcoli = {
        "paper": lambda: sez_paper(trades, controllo, giorno),
        "gate": lambda: sez_gate(gate, portafoglio, r1),
        "imparato": lambda: sez_imparato(trades, controllo, giorno),
        "funzioni": lambda: sez_funzioni(trades, specs),
        "capito": lambda: sez_capito(capito, giorno, oggi),
        "cambiato": lambda: sez_cambiato(commit),
        "attesa": lambda: sez_attesa(backlog, testo_letture, oggi),
        "salute": lambda: sez_salute(controllo, spesa_ieri, giorno),
    }
    sez: dict[str, dict] = {}
    for sid, f in calcoli.items():
        try:
            sez[sid] = f()
        except Exception as exc:  # noqa: BLE001 — una sezione rotta non ferma le altre
            sez[sid] = _sezione(sid, ["Sezione non calcolata."],
                                errore=f"{type(exc).__name__}: {str(exc)[:160]}")
    try:
        sez["in_breve"] = sez_in_breve(sez, controllo, backlog, trades, giorno)
    except Exception as exc:  # noqa: BLE001
        sez["in_breve"] = _sezione("in_breve", ["Sintesi non calcolata."],
                                   errore=f"{type(exc).__name__}: {str(exc)[:160]}")
    return {"meta": {"versione_schema": VERSIONE_SCHEMA, "generato_at": now, "giorno": giorno,
                     "oggi": oggi, "commit": versione, "stato": "finito"},
            "sezioni": [sez[sid] for sid, _ in SEZIONI]}
