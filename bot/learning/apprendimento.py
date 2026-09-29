"""
COME IMPARA IL SISTEMA, GIORNO PER GIORNO — la foto giornaliera del learning e
le due sezioni nuove del controllo del mattino (29 set 2026).

PERCHE'. Richiesta del proprietario: «nel report mattutino voglio avere
visibilita' di come impara e adatta il trailing, e anche delle strategie cosa
sta imparando». Il circuito c'era gia' tutto (il paper da' i verdetti e
propone, il gate sceglie, il bot usa), ma quasi ogni pezzo tiene SOLO lo stato
di adesso: il registro, i pesi, i referti e il documento del gate vengono
sovrascritti. Cosi' «cosa e' cambiato ieri» non si poteva dire, e il
«CAMBIAMENTI DEL LEARNING» del controllo confronta con un'ora prima.

Due pezzi:
  * LA FOTO DEL GIORNO. Il bot, alla prima pubblicazione del controllo di ogni
    giorno italiano, scrive su RTDB `/learning_giorni/{YYYY-MM-DD}` l'impronta
    di `impronta_giorno`, costruita coi dati GIA' letti per il controllo
    (nessuna lettura Firestore in piu'). La foto del giorno D e' lo stato a
    inizio giornata D: «ieri» = foto di oggi meno foto di ieri; «stanotte» =
    stato di adesso meno foto di oggi. Accanto, l'indice `/learning_indice`
    {giorno: ora della foto}. Le foto piu' vecchie di 35 giorni si
    cancellano. Con letture del controllo fallite o col RTDB muto la foto si
    rimanda all'ora dopo: una foto coi buchi inventerebbe dei cambi.
  * GLI EVENTI DATATI. Molte cose hanno gia' una data e non servono foto:
    ipotesi e varianti (`learning/ipotesi_storia`), promosse e rimosse
    (`gate_history/lifecycle`), `declassata_at`, `sostituita_at`,
    `nata_intorno_at`, le esplorative (`since`/`fine`), e dal 29 set i verdetti
    (`trailing_verdict_at`, `post_stop_verdict_at`).

Questo modulo e' PURO: niente rete, niente print. Le letture le fa
`scripts/controllo.py` (voce ops `controllo`, gia' in lista bianca e lanciata
ogni mattina), la scrittura della foto `bot/main.py` (`foto_learning_giorno`).
Le regole che si citano (quando il paper propone un keep) sono quelle di
`bot/learning/metrics.py`: qui si riusano, non si riscrivono.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from fractions import Fraction
from statistics import mean

from bot.config import settings
from bot.core.tempo import fuso, giorno_locale, inizio_giorno_locale
# peso sotto il quale strategia×regime e' «in panchina»: la STESSA costante del
# controllo, importata e non ricopiata (29 set 2026: una copia a mano poteva
# divergere senza che nessun test lo dicesse)
from bot.learning.controllo import SOGLIA_PANCHINA
from bot.learning.metrics import (KEEP_PAPER_LARGO, KEEP_PAPER_MIN_VERDETTI, KEEP_PAPER_QUOTA,
                                  KEEP_PAPER_STRETTO, KEEP_STRATEGIA_MIN_VERDETTI,
                                  KEEP_STRATEGIA_QUOTA_RUMORE, TRAILING_MIN_SAMPLE,
                                  compute_trailing_keep, conta_verdetti_strategia,
                                  proposta_keep, proposta_keep_strategia)
from bot.learning.referti import ESITI_ESTERNI

#: dove vivono le foto (RTDB: fuori dalla quota Firestore di 50.000 letture)
FOTO_BASE = "/learning_giorni"
#: l'indice delle foto scritte, {giorno: at}: pochi byte, letti con UNA chiamata
#: per sapere di quando e' l'ultima foto (29 set 2026: prima si guardavano fino a
#: 34 foglie una per una). Fuori da FOTO_BASE: leggerlo non scarica le foto
FOTO_INDICE = "/learning_indice"
#: quante giornate di foto si tengono: oltre si cancellano (una volta al giorno)
FOTO_CONSERVA_GIORNI = 35
#: al riavvio non si sa quando e' stata fatta l'ultima pulizia: si spazzano
#: questi giorni oltre la soglia (le foto piu' vecchie, se restano, nessuno le legge)
FOTO_SPAZZATA_GIORNI = 7
FOTO_VERSIONE = 1
#: le letture del controllo da cui e' fatta la foto (come le scrive
#: `controllo.carica_dati` in `errori_lettura`): se una fallisce, la foto avrebbe
#: dei buchi e il confronto del giorno dopo inventerebbe cambi (panchine
#: «uscite», ipotesi «sparite»). Si rimanda, non si scrive (29 set 2026)
FONTI_FOTO = ("fs:strategy_registry/validated", "fs:strategy_weights/current",
              "fs:drift/current", "fs:learning/referti", "fs:strategy_registry/esplorative",
              "rtdb:/adapt_state", "fs:trades")
#: da quando il trade chiuso porta il keep in uso (`profit_lock_keep`, 25 set 2026)
KEEP_SUL_TRADE_DAL = "2026-09-25"
#: quanti trade con mfe servono a una strategia per una scala propria: COPIA di
#: `scripts/discover_strategies.SCALA_STRATEGIA_MIN_TRADES` (il bot non importa
#: la discovery; se le due copie divergessero, tests/test_apprendimento.py lo dice)
SCALA_STRATEGIA_MIN_TRADES = 5
#: righe massime per un elenco coppia per coppia, poi «e altre N»
MAX_RIGHE = 8
#: elementi massimi per un elenco dentro una riga, poi «e altre N»
MAX_VOCI = 3
#: caratteri che il RTDB rifiuta nelle chiavi
_VIETATI = str.maketrans({c: "_" for c in ".#$[]/"})
_MESI = ("gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic")
_VERDETTI = (("premature", "prematuro", "prematuri"), ("protected", "protetto", "protetti"),
             ("neutral", "neutro", "neutri"))


# --------------------------------------------------------------------------- #
# attrezzi                                                                     #
# --------------------------------------------------------------------------- #
def _f(v):
    """float o None: mai zero al posto di un dato che manca."""
    if v is None or isinstance(v, bool):
        return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return None if (math.isnan(x) or math.isinf(x)) else x


def _ts(v):
    """Epoch da un numero o da una stringa ISO (naive = UTC); None se manca."""
    x = _f(v)
    if x is not None:
        return x
    if not v or isinstance(v, bool):
        return None
    try:
        d = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.timestamp()


def _exit_ts(t: dict):
    return _ts(t.get("exit_ts")) or _ts(t.get("exit_time"))


def _chiave(k) -> str:
    """Una chiave accettabile al RTDB (senza `. # $ [ ] /`)."""
    return str(k).translate(_VIETATI)


def _mappa(x) -> dict:
    return x if isinstance(x, dict) else {}


def _lista(x) -> list:
    """Il RTDB restituisce una lista, o un dict se la lista ha buchi, o niente."""
    if isinstance(x, list):
        return [v for v in x if v is not None]
    if isinstance(x, dict):
        return [v for v in x.values() if v is not None]
    return []


def _num(v, dec: int = 2) -> str:
    """Numero all'italiana («0,65»)."""
    return f"{v:.{dec}f}".replace(".", ",")


def _k(v) -> str:
    """Un keep o un peso nel testo: «0,65», «0,5»; «default» se non c'e'."""
    x = _f(v)
    return "default" if x is None else f"{x:g}".replace(".", ",")


def _r(v) -> str:
    """Un R col segno: «+0,12»; «n/d» se non misurabile."""
    return "n/d" if v is None else f"{v:+.2f}".replace(".", ",")


def _pct(a: int, b: int) -> str:
    return _num(100.0 * a / b, 1) + "%" if b else "n/d"


def giorno_testo(giorno) -> str:
    """«2026-09-29» -> «29 set»."""
    try:
        a, m, g = str(giorno).split("-")
        return f"{int(g)} {_MESI[int(m) - 1]}"
    except (ValueError, IndexError):
        return str(giorno)


def ora_testo(ts) -> str:
    """L'ora italiana «HH:MM» di un epoch."""
    x = _f(ts)
    if x is None:
        return "?"
    return datetime.fromtimestamp(x, tz=fuso()).strftime("%H:%M")


def quando_testo(ts) -> str:
    """«29 set 06:05» (ora italiana)."""
    x = _f(ts)
    return "?" if x is None else f"{giorno_testo(giorno_locale(x))} {ora_testo(x)}"


def elenco(voci, n: int = MAX_VOCI) -> str:
    """«a, b, c e altre 4»: un elenco che non cresce con il registro."""
    voci = [str(v) for v in (voci or [])]
    testa = ", ".join(voci[:n])
    return testa + (f" e altre {len(voci) - n}" if len(voci) > n else "")


def _plurale(n: int, uno: str, tanti: str) -> str:
    return f"{n} {uno if n == 1 else tanti}"


def finestre(now: float) -> dict:
    """Le due finestre del racconto, in ora italiana: «ieri» e' la giornata
    intera prima di oggi, «stanotte» va dalla mezzanotte di oggi a adesso.
    {nome: (inizio, fine, giorno)}."""
    oggi0 = inizio_giorno_locale(now)
    ieri0 = inizio_giorno_locale(oggi0 - 1)
    return {"ieri": (ieri0, oggi0, giorno_locale(ieri0)),
            "stanotte": (oggi0, float(now), giorno_locale(now))}


def giorni_da_cancellare(giorno: str, ultimo_scritto: str | None,
                         conserva: int = FOTO_CONSERVA_GIORNI,
                         spazzata: int = FOTO_SPAZZATA_GIORNI) -> list[str]:
    """Le foto da cancellare oggi: quelle diventate piu' vecchie di `conserva`
    giorni dall'ultima scrittura. Senza ultima scrittura nota (riavvio) si
    spazzano `spazzata` giorni oltre la soglia. Mai piu' di `spazzata`."""
    try:
        d = date.fromisoformat(str(giorno))
    except ValueError:
        return []
    salto = spazzata
    if ultimo_scritto:
        try:
            salto = (d - date.fromisoformat(str(ultimo_scritto))).days
        except ValueError:
            salto = spazzata
    salto = max(1, min(int(salto), int(spazzata)))
    return [(d - timedelta(days=conserva + 1 + i)).isoformat() for i in range(salto)]


def letture_mancanti(dati) -> list[str]:
    """Le fonti della foto (`FONTI_FOTO`) la cui lettura e' fallita, dai
    `errori_lettura` di `controllo.carica_dati` («fs:coll/doc: messaggio»)."""
    errori = _mappa(dati).get("errori_lettura") or []
    fonti = {str(e).split(": ", 1)[0] for e in errori if isinstance(e, str)}
    return [f for f in FONTI_FOTO if f in fonti]


def ultima_dall_indice(indice, prima_di: str):
    """(giorno, at) della foto piu' recente PRIMA del giorno `prima_di`,
    dall'indice {giorno: at} (`FOTO_INDICE`); None se non ce n'e'."""
    giorni = sorted(g for g, at in _mappa(indice).items()
                    if isinstance(g, str) and g < str(prima_di) and at is not None)
    return (giorni[-1], _mappa(indice)[giorni[-1]]) if giorni else None


def _tf_testo(tf) -> str:
    """«15m» -> «15 minuti», «1h» -> «1 ora»: il timeframe detto a parole."""
    s = str(tf or "")
    unita = {"m": ("minuto", "minuti"), "h": ("ora", "ore"), "d": ("giorno", "giorni")}
    if len(s) >= 2 and s[:-1].isdigit() and s[-1] in unita:
        n = int(s[:-1])
        return f"{n} {unita[s[-1]][0 if n == 1 else 1]}"
    return s


def _registro(reg) -> tuple[dict, list]:
    """(pairs decodificate, chiavi validate) dal documento del registro."""
    from bot.core.firebase_client import decode_pairs
    reg = reg if isinstance(reg, dict) else {}
    pairs = decode_pairs(reg.get("pairs")) or {}
    pairs = pairs if isinstance(pairs, dict) else {}
    validate = [k for k in (reg.get("validated") or []) if isinstance(k, str)]
    return pairs, validate


def _operate(validate) -> list[str]:
    """Le validate che il bot opera davvero: validate E robuste (la regola di
    `adaptation._robust_only`, copiata in `bot/core/registry.coppie_robuste`)."""
    try:
        from bot.core.registry import coppie_robuste
        return sorted(coppie_robuste(validate))
    except Exception:  # noqa: BLE001
        return sorted(validate or [])


def _scala_str(mults) -> str | None:
    from bot.core.registry import scala_str
    return scala_str(mults)


def _trades(dati) -> list[dict]:
    return [t for t in (_mappa(dati).get("trades") or []) if isinstance(t, dict)]


def _r_multiplo(t: dict):
    from bot.learning.drift import r_multiplo
    try:
        return r_multiplo(t)
    except Exception:  # noqa: BLE001
        return None


# --------------------------------------------------------------------------- #
# i verdetti del trailing                                                      #
# --------------------------------------------------------------------------- #
def riassunto_verdetti(trades, tf: str | None = None) -> dict:
    """I verdetti del paper in numeri. `verdetti/prematuri/rumore/protetti`
    sono ESATTAMENTE quelli con cui il gate decide la proposta del keep
    (`metrics.conta_verdetti_strategia` su tutti i trade, esplorativi compresi:
    uscite `trailing_stop` sul timeframe del bot, i neutri non contano);
    `neutri` sono i neutri delle stesse uscite; `altri_tf` le uscite trailing
    su altri timeframe (non contano); `scale_out*` i verdetti scritti sulle
    uscite scale_out, che NESSUNA proposta usa (se contarli non e' deciso); `post_*`
    i verdetti dopo gli stop (nessuna regola li usa ancora)."""
    tf = settings.ORCHESTRATOR_TIMEFRAME if tf is None else tf
    rows = [t for t in (trades or []) if isinstance(t, dict)]
    c = conta_verdetti_strategia(rows, tf)
    neutri = altri = 0
    so: Counter = Counter()
    post: Counter = Counter()
    for t in rows:
        v, uscita = t.get("trailing_verdict"), t.get("exit_reason")
        if v is not None and uscita == "trailing_stop":
            if t.get("timeframe") != tf:
                altri += 1
            elif v == "neutral":
                neutri += 1
        elif v is not None and uscita == "scale_out":
            so[str(v)] += 1
        pv = t.get("post_stop_verdict")
        if pv is not None and uscita == "stop_loss":
            post[str(pv)] += 1
    out = {"verdetti": c["n"], "prematuri": c["prematuri"], "rumore": c["prematuri_rumore"],
           "protetti": c["protetti"], "neutri": neutri, "altri_tf": altri,
           "scale_out": sum(so.values()), "scale_out_prematuri": so.get("premature", 0),
           "scale_out_protetti": so.get("protected", 0), "scale_out_neutri": so.get("neutral", 0),
           "post_rumore": post.get("rumore", 0), "post_inversione": post.get("inversione", 0)}
    prop = proposta_keep(c["n"], c["prematuri"], c["protetti"])
    if prop is not None:
        out["proposta"] = prop
    return out


def verdetti_nuovi(trades, t0: float, t1: float, tf: str | None = None) -> dict:
    """I verdetti assegnati fra `t0` (compreso) e `t1` (escluso), per tipo.
    La data e' `trailing_verdict_at` / `post_stop_verdict_at` (scritte dal bot
    dal 29 set 2026); per i trade giudicati prima si usa l'uscita del trade e
    lo si conta in `stimati` (il verdetto arriva entro 24 ore dall'uscita: la
    data vera puo' cadere il giorno dopo). `trailing_stop` sono SOLO le uscite
    sul timeframe del bot, come in `riassunto_verdetti` (le sole che contano per
    le proposte); quelle degli altri timeframe vanno in `altri_tf`."""
    tf = settings.ORCHESTRATOR_TIMEFRAME if tf is None else tf
    out = {"trailing_stop": Counter(), "altri_tf": Counter(), "scale_out": Counter(),
           "stop_loss": Counter(), "stimati": 0}

    def _conta(gruppo, verdetto, at, t):
        ts = _f(at)
        stimato = ts is None
        if stimato:
            ts = _exit_ts(t)
        if ts is not None and t0 <= ts < t1:
            out[gruppo][str(verdetto)] += 1
            out["stimati"] += int(stimato)

    for t in trades or []:
        if not isinstance(t, dict):
            continue
        uscita = t.get("exit_reason")
        if uscita in ("trailing_stop", "scale_out") and t.get("trailing_verdict") is not None:
            gruppo = ("altri_tf" if uscita == "trailing_stop" and t.get("timeframe") != tf
                      else uscita)
            _conta(gruppo, t["trailing_verdict"], t.get("trailing_verdict_at"), t)
        if uscita == "stop_loss" and t.get("post_stop_verdict") is not None:
            _conta("stop_loss", t["post_stop_verdict"], t.get("post_stop_verdict_at"), t)
    return out


def _mancano(n: int, favorevoli: int, quota: float, minimo: int = 0) -> int:
    """Il minimo x >= 0 di verdetti favorevoli in piu' perche' (favorevoli + x)
    / (n + x) >= quota e n + x >= minimo. Aritmetica esatta (0,6 = 3/5): lo
    stesso confine della regola in `metrics`, senza sorprese di virgola mobile."""
    q = Fraction(str(quota))
    x = max(0, int(minimo) - int(n))
    if q < 1:
        serve = (q * n - favorevoli) / (1 - q)
        x = max(x, math.ceil(serve))
    return max(0, x)


def quanto_manca_globale(n: int, prematuri: int, protetti: int) -> dict:
    """Dove sta la proposta GLOBALE del keep (regola `metrics.proposta_keep`:
    >= 8 verdetti; prematuri >= 60% -> 0,25; protetti >= 60% -> 0,75) e quanto
    manca per cambiarla. `spegne_con`: con quanti verdetti contrari una
    proposta accesa si spegne (la regola non ha isteresi)."""
    n, prem, prot = int(n or 0), int(prematuri or 0), int(protetti or 0)
    q = KEEP_PAPER_QUOTA
    out = {"n": n, "prematuri": prem, "protetti": prot, "proposta": proposta_keep(n, prem, prot),
           "mancano_verdetti": max(0, KEEP_PAPER_MIN_VERDETTI - n),
           "mancano_protetti": _mancano(n, prot, q, KEEP_PAPER_MIN_VERDETTI),
           "mancano_prematuri": _mancano(n, prem, q, KEEP_PAPER_MIN_VERDETTI),
           "spegne_con": None}
    if out["proposta"] is not None:
        fav = prot if out["proposta"] == KEEP_PAPER_STRETTO else prem
        # il minimo y con fav / (n + y) < quota
        y = math.floor(Fraction(fav) / Fraction(str(q)) - n) + 1
        out["spegne_con"] = max(1, y)
    return out


def vicine_per_strategia(trades, n_max: int = 3) -> dict:
    """Il keep PER STRATEGIA (regola `metrics.proposta_keep_strategia`: >= 5
    verdetti della strategia; protetti >= 60% -> 0,75; prematuri >= 60% e
    almeno meta' da rumore -> 0,25): chi propone gia' e le `n_max` strategie
    piu' vicine a proporre, con quanti verdetti mancano."""
    per: dict[str, list] = defaultdict(list)
    for t in trades or []:
        if isinstance(t, dict) and isinstance(t.get("strategy"), str) and t.get("strategy"):
            per[t["strategy"]].append(t)
    propongono, vicine = [], []
    for gid, ts in per.items():
        c = conta_verdetti_strategia(ts)
        if c["n"] == 0:
            continue
        prop = proposta_keep_strategia(ts)
        if prop is not None:
            propongono.append({"strategia": gid, "keep": prop, **c})
            continue
        m_prot = _mancano(c["n"], c["protetti"], KEEP_PAPER_QUOTA, KEEP_STRATEGIA_MIN_VERDETTI)
        # 0,25: x prematuri DA RUMORE in piu' (contano come prematuri e come rumore)
        m_prem = max(_mancano(c["n"], c["prematuri"], KEEP_PAPER_QUOTA, KEEP_STRATEGIA_MIN_VERDETTI),
                     _mancano(c["prematuri"], c["prematuri_rumore"], KEEP_STRATEGIA_QUOTA_RUMORE, 1))
        # a pari distanza si dice il verso in cui la strategia gia' pende
        if m_prot < m_prem or (m_prot == m_prem and c["protetti"] >= c["prematuri"]):
            vicine.append({"strategia": gid, "verso": KEEP_PAPER_STRETTO, "mancano": m_prot, **c})
        else:
            vicine.append({"strategia": gid, "verso": KEEP_PAPER_LARGO, "mancano": m_prem, **c})
    propongono.sort(key=lambda r: (-r["n"], r["strategia"]))
    vicine.sort(key=lambda r: (r["mancano"], -r["n"], r["strategia"]))
    return {"propongono": propongono, "vicine": vicine[:n_max], "con_verdetti": len(propongono) + len(vicine)}


def scale_proprie(trades, min_trades: int = SCALA_STRATEGIA_MIN_TRADES) -> dict[str, str]:
    """{strategia: scala} per le strategie con una scala dei TP propria dal
    vissuto: la stessa regola di `discover_strategies.scale_per_strategia`
    (`exit_logic.ladder_from_mfe` sui suoi trade con `mfe_r`, esplorativi
    compresi), senza importare la discovery."""
    from bot.execution.exit_logic import ladder_from_mfe
    per: dict[str, list] = defaultdict(list)
    for t in trades or []:
        if isinstance(t, dict) and t.get("mfe_r") is not None and isinstance(t.get("strategy"), str):
            per[t["strategy"]].append(t.get("mfe_r"))
    out: dict[str, str] = {}
    for gid in sorted(per):
        if len(per[gid]) < min_trades:
            continue
        try:
            s = ladder_from_mfe(per[gid], min_trades=min_trades)
        except (TypeError, ValueError):
            continue
        if s:
            out[gid] = _scala_str(s)
    return out


def keep_in_uso(trades, dal: float | None = None) -> list[dict]:
    """«Funziona?»: i trade chiusi del paper dal 25 set (da quando il trade
    porta `profit_lock_keep`, il keep usato davvero) raggruppati per keep:
    trade, lock armato (dal referto: `post_mortem.lock_mai_armato` falso), i
    verdetti trailing, R medio (`drift.r_multiplo`) e il tragitto verso il
    target lasciato sul tavolo (`trailing_miss_to_tp`). Esiti esterni fuori.
    I gruppi NON sono confrontabili fra loro (coppie diverse): misura."""
    if dal is None:
        dal = datetime.fromisoformat(KEEP_SUL_TRADE_DAL).replace(tzinfo=fuso()).timestamp()
    per: dict[float, list] = defaultdict(list)
    for t in trades or []:
        if not isinstance(t, dict) or str(t.get("exit_reason", "")) in ESITI_ESTERNI:
            continue
        k, ex = _f(t.get("profit_lock_keep")), _exit_ts(t)
        if k is None or ex is None or ex < dal:
            continue
        per[round(k, 2)].append(t)
    out = []
    for k in sorted(per):
        rows = per[k]
        pm = [t.get("post_mortem") for t in rows if isinstance(t.get("post_mortem"), dict)]
        rs = [r for r in (_r_multiplo(t) for t in rows) if r is not None]
        miss = [m for t in rows if (m := _f(t.get("trailing_miss_to_tp"))) is not None]
        out.append({"keep": k, "trade": len(rows),
                    "con_referto": len(pm),
                    "armato": sum(1 for p in pm if not p.get("lock_mai_armato")),
                    "prematuri": sum(1 for t in rows if t.get("trailing_verdict") == "premature"),
                    "protetti": sum(1 for t in rows if t.get("trailing_verdict") == "protected"),
                    "r_medio": round(mean(rs), 3) if rs else None, "r_n": len(rs),
                    "tavolo": round(mean(miss), 2) if miss else None})
    return out


# --------------------------------------------------------------------------- #
# LA FOTO DEL GIORNO                                                           #
# --------------------------------------------------------------------------- #
def impronta_giorno(dati: dict, now: float) -> dict:
    """La foto di cio' che il learning ha DECISO adesso, dai dati di
    `controllo.carica_dati` (gia' in memoria: nessuna lettura in piu').

    Chiavi senza `. $ # [ ] /` (RTDB). I valori None non si scrivono (il RTDB
    li scarterebbe comunque): chi legge tratta la chiave assente come None.
      * `validate`: per ogni validata «SYM|strategia» il keep, la scala dei TP
        e il break-even scelti dal gate (assenti = default) e se e' declassata;
      * `pesi`: TUTTI i pesi strategia×regime, a 4 decimali come nel controllo
        (niente taglio a 10) e MAI arrotondati oltre la soglia della panchina:
        0,4962 resta sotto 0,5, come per il bot che la decide sul peso vero;
      * `cooldown`, `freno`, `ipotesi` («strategia|tipo» dai referti),
        `esplorative` attive, `trailing` (`riassunto_verdetti`)."""
    d = _mappa(dati)
    pairs, validate = _registro(d.get("registro"))
    val: dict = {}
    for k in validate:
        rec = _mappa(pairs.get(k))
        lp = _mappa(rec.get("last_params"))
        voce = {"declassata": bool(rec.get("declassata"))}
        keep = _f(lp.get("profit_lock_keep"))
        if keep is not None:
            voce["keep"] = keep
        scala = _scala_str(lp.get("scale_r_mults"))
        if scala:
            voce["scala"] = scala
        if lp.get("sl_to_breakeven") is not None:
            voce["be"] = bool(lp.get("sl_to_breakeven"))
        val[_chiave(k)] = voce
    pesi: dict = {}
    for w in _mappa(d.get("weights")).get("weights") or []:
        if not isinstance(w, dict):
            continue
        p = _f(w.get("weight"))
        if p is not None:
            p4 = round(p, 4)
            if (p < SOGLIA_PANCHINA) != (p4 < SOGLIA_PANCHINA):
                p4 = p          # l'arrotondamento la farebbe uscire (o entrare) in panchina
            pesi[_chiave(f"{w.get('strategy')}|{w.get('regime')}")] = p4
    from bot.learning.controllo import cooldown_attivi
    cd = cooldown_attivi(d.get("adapt_state"), now)
    glob = _mappa(_mappa(d.get("drift")).get("global"))
    pfv = _f(glob.get("live_pf"))
    freno = {"attivo": bool(settings.DRIFT_ENABLED and glob.get("verdict") == "drift")}
    if pfv is not None and pfv < 99:
        freno["pf_vissuto"] = round(pfv, 3)
    if _f(glob.get("expected_pf")) is not None:
        freno["pf_atteso"] = round(_f(glob.get("expected_pf")), 3)
    ipotesi = sorted({_chiave(f"{h.get('strategia')}|{h.get('tipo')}")
                      for h in (_mappa(d.get("referti")).get("ipotesi") or []) if isinstance(h, dict)})
    esp = []
    if isinstance(d.get("esplorative"), dict):
        from bot.core.firebase_client import decode_pairs
        esp = sorted(_chiave(k) for k in _mappa(decode_pairs(d["esplorative"].get("pairs"))))
    return {"versione": FOTO_VERSIONE, "at": float(now), "giorno": giorno_locale(now),
            "validate": val, "pesi": pesi,
            "cooldown": {"coin": [c["nome"] for c in cd["coin"]],
                         "strategie": [c["nome"] for c in cd["strategie"]]},
            "freno": freno, "ipotesi": ipotesi, "esplorative": esp,
            "trailing": riassunto_verdetti(_trades(d))}


def _uguali(a, b) -> bool:
    fa, fb = _f(a), _f(b)
    if fa is not None or fb is not None:
        return fa is not None and fb is not None and abs(fa - fb) < 1e-6
    return a == b


def differenze(prima: dict | None, dopo: dict | None) -> dict | None:
    """Cosa e' cambiato fra due impronte (`impronta_giorno`, anche rilette dal
    RTDB). None se ne manca una: il confronto non si inventa."""
    if not isinstance(prima, dict) or not isinstance(dopo, dict) or not prima or not dopo:
        return None
    vp, vd = _mappa(prima.get("validate")), _mappa(dopo.get("validate"))
    comuni = sorted(set(vp) & set(vd))
    coppie = []
    for k in comuni:
        a, b = _mappa(vp[k]), _mappa(vd[k])
        cambi = {c: (a.get(c), b.get(c)) for c in ("keep", "scala", "be")
                 if not _uguali(a.get(c), b.get(c))}
        if cambi:
            coppie.append({"coppia": k, **cambi})
    decl_nuove = [k for k in comuni if not _mappa(vp[k]).get("declassata") and _mappa(vd[k]).get("declassata")]
    tornate = [k for k in comuni if _mappa(vp[k]).get("declassata") and not _mappa(vd[k]).get("declassata")]
    pp, pd = _mappa(prima.get("pesi")), _mappa(dopo.get("pesi"))

    def _sotto(m, k):
        x = _f(m.get(k))
        return x is not None and x < SOGLIA_PANCHINA

    entrate = [(k, _f(pd.get(k))) for k in sorted(pd) if _sotto(pd, k) and not _sotto(pp, k)]
    uscite = [(k, _f(pd.get(k))) for k in sorted(pp) if _sotto(pp, k) and not _sotto(pd, k)]

    def _cd(foto):
        c = _mappa(foto.get("cooldown"))
        return ({f"coin {x}" for x in _lista(c.get("coin"))}
                | {f"strategia {x}" for x in _lista(c.get("strategie"))})

    cp, cdopo = _cd(prima), _cd(dopo)
    fp = bool(_mappa(prima.get("freno")).get("attivo"))
    fd = bool(_mappa(dopo.get("freno")).get("attivo"))
    ip, idd = set(_lista(prima.get("ipotesi"))), set(_lista(dopo.get("ipotesi")))
    ep, ed = set(_lista(prima.get("esplorative"))), set(_lista(dopo.get("esplorative")))
    prop_p = _f(_mappa(prima.get("trailing")).get("proposta"))
    prop_d = _f(_mappa(dopo.get("trailing")).get("proposta"))
    return {"da_at": _f(prima.get("at")), "a_at": _f(dopo.get("at")),
            "comuni": len(comuni), "coppie": coppie,
            "validate_entrate": sorted(set(vd) - set(vp)), "validate_uscite": sorted(set(vp) - set(vd)),
            "declassate_nuove": decl_nuove, "tornate_piene": tornate,
            "panchina_entrate": entrate, "panchina_uscite": uscite,
            "cooldown_iniziati": sorted(cdopo - cp), "cooldown_finiti": sorted(cp - cdopo),
            "freno": None if fp == fd else ("acceso" if fd else "spento"),
            "ipotesi_nuove": sorted(idd - ip), "ipotesi_sparite": sorted(ip - idd),
            "esplorative_entrate": sorted(ed - ep), "esplorative_uscite": sorted(ep - ed),
            "proposta": None if _uguali(prop_p, prop_d) else (prop_p, prop_d)}


# --------------------------------------------------------------------------- #
# gli eventi datati                                                            #
# --------------------------------------------------------------------------- #
def eventi_fra(t0: float, t1: float, *, storia=None, vite=None, registro=None,
               esplorative=None, drift=None, referti=None) -> dict:
    """Cio' che ha una data fra `t0` (compreso) e `t1` (escluso):
      * `learning/ipotesi_storia`: ipotesi nate (`nata_at`) e i traguardi delle
        varianti (`variante_at`, `passata_at`, `validata_at`, `bocciata_at`,
        `scartata_at`), con la frase del referto se l'ipotesi c'e' ancora;
      * `gate_history/lifecycle`: validate promosse e rimosse;
      * il registro: sostituzioni madre -> figlia (`sostituita_at`), figlie
        dell'intorno (`nata_intorno_at`), declassate nuove (`declassata_at`);
      * `strategy_registry/esplorative`: entrate (`since`), promosse e
        scartate (`fine`);
      * `drift/current`: l'accensione del freno globale (`global.dal`)."""
    def dentro(v) -> bool:
        x = _f(v)
        return x is not None and t0 <= x < t1

    motivi = {f"{h.get('strategia')}|{h.get('tipo')}": h.get("motivo")
              for h in (_mappa(referti).get("ipotesi") or []) if isinstance(h, dict)}
    voci = _mappa(_mappa(storia).get("voci"))
    nate, varianti = [], {"create": [], "passate": [], "validate": [], "bocciate": [], "scartate": []}
    campi = (("create", "variante_at"), ("passate", "passata_at"), ("validate", "validata_at"),
             ("bocciate", "bocciata_at"), ("scartate", "scartata_at"))
    for k in sorted(voci):
        v = _mappa(voci[k])
        if dentro(v.get("nata_at")):
            nate.append({"chiave": k, "strategia": v.get("strategia"), "tipo": v.get("tipo"),
                         "motivo": motivi.get(k)})
        for nome, campo in campi:
            if dentro(v.get(campo)):
                varianti[nome].append({"chiave": k, "variante": v.get("variante_id")})
    promosse, rimosse = [], []
    for e in _lista(_mappa(vite).get("events")):
        if not isinstance(e, dict) or not dentro(e.get("at")):
            continue
        if e.get("tipo") == "promossa":
            promosse.append(e)
        elif e.get("tipo") == "rimossa":
            rimosse.append(e)
    sostituzioni, intorno, declassate = [], [], []
    if isinstance(registro, dict):
        pairs, _val = _registro(registro)
        for k in sorted(pairs):
            rec = _mappa(pairs[k])
            if rec.get("sostituita_da") and dentro(rec.get("sostituita_at")):
                sym = k.split("|", 1)[0]
                sostituzioni.append({"madre": k, "figlia": f"{sym}|{rec['sostituita_da']}"})
            if dentro(rec.get("nata_intorno_at")):
                intorno.append({"figlia": k, "genitore": rec.get("genitore")})
            if dentro(rec.get("declassata_at")):
                declassate.append(k)
    esp = {"entrate": [], "promosse": [], "scartate": []}
    if isinstance(esplorative, dict):
        from bot.core.firebase_client import decode_pairs
        attive = _mappa(decode_pairs(esplorative.get("pairs")))
        finite = _mappa(decode_pairs(esplorative.get("storia")))
        for k in sorted(set(attive) | set(finite)):
            rec = _mappa(attive.get(k)) or _mappa(finite.get(k))
            if dentro(rec.get("since")):
                esp["entrate"].append(k)
        for k in sorted(finite):
            rec = _mappa(finite[k])
            if dentro(rec.get("fine")):
                esp["promosse" if rec.get("esito") == "validata" else "scartate"].append(k)
    glob = _mappa(_mappa(drift).get("global"))
    freno_at = _f(glob.get("dal")) if glob.get("verdict") == "drift" and dentro(glob.get("dal")) else None
    return {"ipotesi_nate": nate, "varianti": varianti, "promosse": promosse, "rimosse": rimosse,
            "sostituzioni": sostituzioni, "intorno": intorno, "declassate": declassate,
            "esplorative": esp, "freno_acceso_at": freno_at}


# --------------------------------------------------------------------------- #
# le righe del report                                                          #
# --------------------------------------------------------------------------- #
def righe_foto(now: float, foto_oggi=None, foto_ieri=None, ultima=None,
               rtdb_muto: bool = False) -> list[str]:
    """Da dove vengono i confronti fra stati, e cosa manca. `ultima` = (giorno,
    at) della foto piu' recente prima di ieri (dall'indice), quando manca quella
    di ieri. `rtdb_muto`: il RTDB non rispondeva, le foto che mancano non sono
    state lette (non vuol dire che non ci siano)."""
    fin = finestre(now)
    g_oggi, g_ieri = fin["stanotte"][2], fin["ieri"][2]
    testa = ("STORIA DEL LEARNING (foto dello stato scattata dal bot alla prima ora di ogni giorno "
             "italiano, RTDB /learning_giorni; da qui in giu' gli orari sono in ora italiana, "
             "quelli sopra in UTC):")
    ok_o, ok_i = isinstance(foto_oggi, dict) and foto_oggi, isinstance(foto_ieri, dict) and foto_ieri
    if ok_o and ok_i:
        return [testa, f"  foto di ieri {quando_testo(foto_ieri.get('at'))}, foto di oggi "
                       f"{quando_testo(foto_oggi.get('at'))}: i confronti «ieri» e «stanotte» qui sotto vengono da queste"]
    out = [testa]
    if rtdb_muto:
        out.append("  RTDB non raggiungibile: foto non lette, confronti fra stati non disponibili "
                   "(non vuol dire che le foto manchino)")
    elif ok_o:
        dove = (f"l'ultima foto prima di oggi e' del {giorno_testo(ultima[0])}" if ultima
                else f"la storia parte dal {giorno_testo(g_oggi)} (foto delle {ora_testo(foto_oggi.get('at'))})")
        out.append(f"  manca la foto del {giorno_testo(g_ieri)} (bot fermo tutto il giorno o foto non "
                   f"riuscita): confronto «ieri» fra stati non disponibile; {dove}")
    elif ok_i:
        out.append(f"  manca la foto di oggi ({giorno_testo(g_oggi)}): confronto «stanotte» fra stati non "
                   f"disponibile (bot fermo dalla mezzanotte o foto non riuscita); c'e' quella di ieri")
    else:
        dove = (f"l'ultima e' del {giorno_testo(ultima[0])}" if ultima
                else "nessuna foto negli ultimi 35 giorni: la storia non e' ancora partita "
                     "(la scrive il bot riavviato col codice del 29 set)")
        out.append(f"  mancano le foto del {giorno_testo(g_ieri)} e del {giorno_testo(g_oggi)}: "
                   f"confronti fra stati non disponibili; {dove}")
    out.append("  gli eventi con una data (ipotesi, varianti, promozioni, declassate nuove, esplorative, "
               "verdetti) si leggono comunque")
    return out


def _riga_nuovi(nome: str, giorno: str, nuovi: dict, gia_spiegato: bool = False) -> str:
    """La riga dei verdetti nuovi di una finestra. `gia_spiegato`: la nota sui
    verdetti senza data e' gia' stata scritta per intero nella riga sopra."""
    pezzi = []
    c = nuovi["trailing_stop"]
    if sum(c.values()):
        pezzi.append("trailing " + ", ".join(_plurale(c.get(v, 0), uno, tanti) for v, uno, tanti in _VERDETTI))
    altri = sum(nuovi.get("altri_tf", Counter()).values())
    if altri:
        pezzi.append(f"+{altri} trailing su altri timeframe (non contano per le proposte)")
    c = nuovi["scale_out"]
    if sum(c.values()):
        pezzi.append("dopo un incasso parziale " + ", ".join(_plurale(c.get(v, 0), uno, tanti)
                                                             for v, uno, tanti in _VERDETTI))
    c = nuovi["stop_loss"]
    if sum(c.values()):
        pezzi.append(f"stop {c.get('rumore', 0)} rumore, {c.get('inversione', 0)} inversione")
    testo = " · ".join(pezzi) if pezzi else "nessuno"
    if nuovi["stimati"]:
        testo += (f" ({nuovi['stimati']} senza data, come sopra)" if gia_spiegato else
                  f" ({nuovi['stimati']} senza data: contati nel giorno di uscita del trade, il "
                  f"verdetto puo' essere del giorno dopo)")
    return f"     nuovi {nome} ({giorno_testo(giorno)}): {testo}"


def _riga_coppia(c: dict) -> str:
    pezzi = []
    if "keep" in c:
        pezzi.append(f"keep {_k(c['keep'][0])} -> {_k(c['keep'][1])}")
    if "scala" in c:
        pezzi.append(f"scala {c['scala'][0] or 'default'} -> {c['scala'][1] or 'default'}")
    if "be" in c:
        be = {True: "si", False: "no", None: "default"}
        pezzi.append(f"break-even {be.get(c['be'][0], '?')} -> {be.get(c['be'][1], '?')}")
    return f"       {c['coppia']}: " + "; ".join(pezzi)


def _righe_cambi(nome: str, diff: dict | None, manca: str) -> list[str]:
    if diff is None:
        return [f"     cambiato {nome}: non disponibile ({manca})"]
    testa = (f"     cambiato {nome} (foto {quando_testo(diff['da_at'])} -> "
             f"{'adesso' if nome == 'stanotte' else 'foto ' + quando_testo(diff['a_at'])}): ")
    extra = []
    if diff["validate_entrate"] or diff["validate_uscite"]:
        extra.append(f"validate +{len(diff['validate_entrate'])} / -{len(diff['validate_uscite'])}")
    if diff["proposta"] is not None:
        extra.append(f"proposta del paper {_k(diff['proposta'][0])} -> {_k(diff['proposta'][1])}")
    coda = f" ({'; '.join(extra)})" if extra else ""
    if not diff["coppie"]:
        return [testa + f"nessuna delle {diff['comuni']} coppie presenti in entrambe le foto ha "
                        f"cambiato keep, scala o break-even" + coda]
    out = [testa + f"{len(diff['coppie'])} coppie su {diff['comuni']} hanno cambiato keep, scala o "
                   f"break-even" + coda]
    out += [_riga_coppia(c) for c in diff["coppie"][:MAX_RIGHE]]
    if len(diff["coppie"]) > MAX_RIGHE:
        out.append(f"       e altre {len(diff['coppie']) - MAX_RIGHE}")
    return out


def _distribuzione(conta: Counter, n_max: int = 5, fuori_conto=("non scelto", "non scelta")) -> str:
    """«a ×3 · b ×2 · altre 2 (×3)». Le voci di `fuori_conto` (il resto non
    ancora scelto) si scrivono sempre e non occupano un posto; se ne avanza UNA
    sola, si scrive quella invece di «altre 1»: e' spesso proprio la piu'
    interessante (la scala dal vissuto)."""
    voci = sorted(conta.items(), key=lambda kv: (-kv[1], str(kv[0])))
    scelte = [kv for kv in voci if kv[0] not in fuori_conto]
    if len(scelte) == n_max + 1:
        n_max += 1
    mostra = {kv[0] for kv in scelte[:n_max]} | {kv[0] for kv in voci if kv[0] in fuori_conto}
    testo = " · ".join(f"{v} ×{n}" for v, n in voci if v in mostra)
    resto = scelte[n_max:]
    if resto:
        testo += f" · altre {len(resto)} (×{sum(n for _, n in resto)})"
    return testo or "nessuna"


def _motivi_confronti(fin: dict, foto_oggi, foto_ieri, perche_senza_foto: str | None,
                      manca_adesso: str | None) -> dict:
    """Perche' manca il confronto «ieri» (foto di ieri -> foto di oggi) e
    «stanotte» (foto di oggi -> adesso), detto per la sezione."""
    def _foto(g):
        return perche_senza_foto or f"manca la foto del {giorno_testo(g)}"
    return {"ieri": _foto(fin["ieri"][2] if not foto_ieri else fin["stanotte"][2]),
            "stanotte": manca_adesso if (foto_oggi and manca_adesso) else _foto(fin["stanotte"][2])}


def sezione_trailing(dati: dict, now: float, foto_oggi=None, foto_ieri=None,
                     adesso: dict | None = None, perche_senza_foto: str | None = None,
                     manca_adesso: str | None = None) -> list[str]:
    """«COME IMPARA IL TRAILING»: cosa ha visto il paper, cosa propone al gate e
    quanto manca, cosa ha scelto il gate (e cosa e' cambiato ieri e stanotte,
    coppia per coppia, dalle foto), e se funziona. Righe pronte da stampare.
    `perche_senza_foto`: il motivo da dire quando una foto manca perche' non si
    e' potuta leggere (RTDB muto); `manca_adesso`: lo stato di adesso non e'
    affidabile (letture fallite) e il confronto «stanotte» non si fa."""
    d = _mappa(dati)
    tf = settings.ORCHESTRATOR_TIMEFRAME
    trades = _trades(d)
    out = ["COME IMPARA IL TRAILING (il keep e' la parte del guadagno che il trailing blocca quando si "
           "arma: con 0,5 tiene meta' del miglior guadagno visto; piu' alto = stop piu' vicino)"]
    if d.get("trades") is None:
        out.append("  trade non leggibili: verdetti e proposte non calcolati")
    fin = finestre(now)

    # a) cosa ha visto il paper
    r = riassunto_verdetti(trades, tf)
    # la legenda una volta, su righe sue (29 set 2026: in fila erano 300
    # caratteri, otto righe sul telefono)
    out.append("  a) COSA HA VISTO IL PAPER: dopo ogni uscita del trailing guarda dove va il prezzo "
               "nelle 24 ore dopo")
    out.append("     prematuro = poi e' arrivato al target: usciti troppo presto («da rumore» se lo stop "
               "e' scattato su un ritorno indietro piu' piccolo del movimento medio di una candela)")
    out.append("     protetto = poi e' tornato allo stop iniziale: l'uscita ha salvato il guadagno; "
               "neutro = ne' l'uno ne' l'altro")
    out.append(f"     uscite del trailing sulle candele da {_tf_testo(tf)} (le sole che contano per le "
               f"proposte): {r['verdetti']} verdetti = {r['prematuri']} prematuri ({r['rumore']} da "
               f"rumore) + {r['protetti']} protetti; in piu' {r['neutri']} neutri"
               + (f"; {r['altri_tf']} su altri timeframe (non contano)" if r["altri_tf"] else ""))
    if r["scale_out"]:
        out.append(f"     uscite dopo un incasso parziale (preso almeno il primo target, resto chiuso "
                   f"dallo stop): {r['scale_out']} verdetti ({r['scale_out_prematuri']} prematuri, "
                   f"{r['scale_out_protetti']} protetti, {r['scale_out_neutri']} neutri), NON usati "
                   "dalle proposte (se contarli non e' deciso)")
    if r["post_rumore"] or r["post_inversione"]:
        out.append(f"     dopo gli stop: {r['post_rumore']} rumore (il prezzo e' poi tornato al primo "
                   f"target), {r['post_inversione']} inversione (ha continuato contro, o non e' tornato "
                   "al primo target entro la finestra): nessuna regola li usa ancora")
    spiegato = False
    for nome in ("ieri", "stanotte"):
        t0, t1, g = fin[nome]
        nuovi = verdetti_nuovi(trades, t0, t1, tf)
        out.append(_riga_nuovi(nome, g, nuovi, gia_spiegato=spiegato))
        spiegato = spiegato or bool(nuovi["stimati"])

    # b) cosa propone il paper e quanto manca
    g = quanto_manca_globale(r["verdetti"], r["prematuri"], r["protetti"])
    out.append("  b) COSA PROPONE IL PAPER AL GATE (una proposta e' un candidato in piu' che il gate prova "
               "sulla storia: il paper propone, il gate sceglie)")
    testa = "     keep per tutte le coppie: "
    if g["mancano_verdetti"]:
        out.append(testa + f"{g['n']} verdetti, ne servono {KEEP_PAPER_MIN_VERDETTI}: mancano "
                           f"{g['mancano_verdetti']} verdetti per poter proporre")
    elif g["proposta"] is not None:
        fav, nome = ((g["protetti"], "protetti") if g["proposta"] == KEEP_PAPER_STRETTO
                     else (g["prematuri"], "prematuri"))
        contrari = "prematuri" if nome == "protetti" else "protetti"
        out.append(testa + f"{fav} {nome} su {g['n']} = {_pct(fav, g['n'])} (soglia 60%): PROPONE "
                           f"{_k(g['proposta'])}. Senza isteresi: si spegne con {g['spegne_con']} "
                           f"{contrari} in piu'")
    else:
        mp = g["mancano_protetti"]
        out.append(testa + f"{g['protetti']} protetti su {g['n']} verdetti = {_pct(g['protetti'], g['n'])} "
                           f"(serve il 60%): nessuna proposta. {'Manca' if mp == 1 else 'Mancano'} "
                           f"{_plurale(mp, 'protetto', 'protetti')} per proporre 0,75 (oppure "
                           f"{g['mancano_prematuri']} prematuri per 0,25)")
    v = vicine_per_strategia(trades)
    if v["propongono"]:
        prop = elenco([f"{x['strategia']} {_k(x['keep'])}" for x in v["propongono"]])
        riga = f"     keep per strategia (servono {KEEP_STRATEGIA_MIN_VERDETTI} verdetti della strategia): " \
               f"{len(v['propongono'])} strategie propongono ({prop})"
    else:
        riga = (f"     keep per strategia (servono {KEEP_STRATEGIA_MIN_VERDETTI} verdetti della strategia): "
                f"nessuna propone, su {v['con_verdetti']} con verdetti")
    vicine = []
    for x in v["vicine"]:
        if x["verso"] == KEEP_PAPER_STRETTO:
            base = f"{_plurale(x['protetti'], 'protetto', 'protetti')} su {x['n']}"
            cosa = _plurale(x["mancano"], "protetto", "protetti")
        else:
            base = (f"{_plurale(x['prematuri'], 'prematuro', 'prematuri')} "
                    f"({x['prematuri_rumore']} da rumore) su {x['n']}")
            cosa = _plurale(x["mancano"], "prematuro da rumore", "prematuri da rumore")
        vicine.append(f"       {x['strategia']} {base}: {'manca' if x['mancano'] == 1 else 'mancano'} "
                      f"{cosa} per {_k(x['verso'])}")
    # una per riga (29 set 2026): in fila su una riga sola erano 300 caratteri,
    # otto righe sul telefono
    out.append(riga + (". Le piu' vicine:" if vicine else ""))
    out += vicine
    imparato = compute_trailing_keep(trades)
    per_strat = Counter(t.get("strategy") for t in trades
                        if not t.get("esplorativa") and t.get("exit_reason") == "trailing_stop"
                        and t.get("timeframe") == tf and t.get("trailing_verdict") in ("premature", "protected"))
    massimo = max(per_strat.values(), default=0)
    out.append(f"     keep imparato dal bot da solo (vale solo per le coppie senza keep del gate; servono "
               f"{TRAILING_MIN_SAMPLE} verdetti per strategia, esplorative escluse): "
               + (f"{len(imparato)} strategie ({elenco(f'{s} {_k(k)}' for s, k in sorted(imparato.items()))})"
                  if imparato else f"nessuna strategia (la piu' avanti ha {massimo} verdetti su "
                                   f"{TRAILING_MIN_SAMPLE})"))
    giro = _mappa(_mappa(d.get("gate")).get("giro"))
    pp = _mappa(giro.get("paper_propone"))
    proprie = scale_proprie(trades)
    spiega_scala = ("scala dei target di incasso dal vissuto (multipli del rischio iniziale: «1/2/3» = "
                    "incassi a 1, 2 e 3 volte il rischio)")
    if pp:
        quando = _f(giro.get("computed_at")) or _f(_mappa(_mappa(d.get("gate")).get("meta")).get("generato_at"))
        out.append(f"     {spiega_scala}, ultimo giro del gate ({quando_testo(quando)}): "
                   f"{pp.get('scala') or 'nessuna (pochi trade)'}; keep proposto: "
                   f"{_k(pp.get('keep')) if pp.get('keep') is not None else 'nessuno'}")
    else:
        out.append(f"     {spiega_scala}: l'ultimo giro del gate non la riporta (documento "
                   f"dashboard/gate senza giro.paper_propone)")
    out.append(f"     strategie con una scala propria (almeno {SCALA_STRATEGIA_MIN_TRADES} trade col massimo "
               f"guadagno raggiunto misurato): {len(proprie)}")

    # c) cosa ha scelto il gate
    pairs, validate = _registro(d.get("registro"))
    operate = _operate(validate)
    keep_c, scala_c, be_c = Counter(), Counter(), Counter()
    dal_paper = dal_vissuto = 0
    from bot.execution.exit_logic import SCALE_LADDER_CANDIDATES
    fisse = {_scala_str(s) for s in SCALE_LADDER_CANDIDATES}
    for k in operate:
        lp = _mappa(_mappa(pairs.get(k)).get("last_params"))
        kp = _f(lp.get("profit_lock_keep"))
        keep_c[_k(kp) if kp is not None else "non scelto"] += 1
        if kp is not None and round(kp, 2) in (KEEP_PAPER_LARGO, KEEP_PAPER_STRETTO):
            dal_paper += 1
        s = _scala_str(lp.get("scale_r_mults"))
        if s and s not in fisse:
            dal_vissuto += 1
            s = f"{s} (dal vissuto)"
        scala_c[s or "non scelta"] += 1
        be = lp.get("sl_to_breakeven")
        be_c["non scelto" if be is None else ("si" if be else "no")] += 1
    be_def = "si" if settings.SCALE_OUT_SL_TO_BREAKEVEN else "no"
    out.append(f"  c) COSA HA SCELTO IL GATE per le {len(operate)} validate che il bot opera (per coppia; "
               "«non scelto» = coppia non ancora ripassata dal gate: vale il default)")
    out.append(f"     keep: {_distribuzione(keep_c, 6)} (default {_k(settings.PROFIT_LOCK_KEEP)}). "
               f"Dalle proposte del paper (0,25 e 0,75 esistono solo cosi'): {dal_paper}")
    out.append(f"     scala dei target: {_distribuzione(scala_c, 4)} (default "
               f"{_scala_str(settings.SCALE_OUT_R_MULTIPLES)}); dal vissuto in tutto: {dal_vissuto}")
    out.append(f"     stop spostato al prezzo d'ingresso dopo il primo incasso (break-even): "
               f"{_distribuzione(be_c, 3)} (default {be_def})")
    motivi = _motivi_confronti(fin, foto_oggi, foto_ieri, perche_senza_foto, manca_adesso)
    if not manca_adesso:
        adesso = adesso if isinstance(adesso, dict) else impronta_giorno(d, now)
    out += _righe_cambi("ieri", differenze(foto_ieri, foto_oggi), motivi["ieri"])
    out += _righe_cambi("stanotte", None if manca_adesso else differenze(foto_oggi, adesso),
                        motivi["stanotte"])

    # d) funziona?
    out.append(f"  d) FUNZIONA? trade chiusi dal {giorno_testo(KEEP_SUL_TRADE_DAL)} per keep in uso "
               "all'ingresso (gruppi NON confrontabili: coppie diverse; misura, non regola)")
    gruppi = keep_in_uso(trades)
    if not gruppi:
        out.append("     nessun trade chiuso col keep registrato")
    for x in gruppi:
        armato = (f"trailing armato in {x['armato']} dei {x['con_referto']} trade con referto "
                  f"({_pct(x['armato'], x['con_referto'])})" if x["con_referto"] else "trailing armato n/d")
        tavolo = "n/d" if x["tavolo"] is None else _num(x["tavolo"])
        out.append(f"     keep {_k(x['keep'])}: {x['trade']} trade · {armato} · "
                   f"{_plurale(x['prematuri'], 'prematuro', 'prematuri')}, "
                   f"{_plurale(x['protetti'], 'protetto', 'protetti')} · R medio {_r(x['r_medio'])} · "
                   f"tavolo {tavolo}")
    out.append("     R = guadagno in unita' del rischio iniziale; tavolo = parte del tragitto verso il target "
               "lasciata all'uscita trailing (0 = uscito al target, 1 = all'entrata)")
    return out


def _righe_eventi(ev: dict, diff: dict | None, manca: str) -> list[str]:
    """Le righe di una finestra («ieri» o «stanotte»): eventi datati + cambi di
    stato dalle foto. Vuota se non e' successo nulla."""
    out = []
    if ev["ipotesi_nate"]:
        voci = [f"{x['strategia']} {x['tipo']}" + (f" «{x['motivo']}»" if x.get("motivo") else "")
                for x in ev["ipotesi_nate"]]
        out.append(f"ipotesi nate dai referti {len(voci)}: {elenco(voci)}")
    # UN EVENTO, UNA RIGA (29 set 2026). La discovery scrive la stessa promozione
    # in tre posti: `promossa` nel diario, `sostituita_at` sulla madre,
    # `nata_intorno_at` sulla figlia. Contate a parte sembravano tre cose
    # successe; qui la figlia porta la sua storia dentro la riga delle promosse.
    promosse_k = {e.get("key") for e in ev["promosse"]}
    promosse_s = {str(k).split("|", 1)[-1] for k in promosse_k if k}
    storia: dict[str, dict] = defaultdict(dict)
    for x in ev["sostituzioni"]:
        storia[x["figlia"]]["madre"] = x["madre"].split("|", 1)[-1]
    for x in ev["intorno"]:
        storia[x["figlia"]]["intorno"] = x["genitore"] or "?"

    def _nota_figlia(k) -> str:
        st = storia.get(k) or {}
        if "madre" in st:
            pre = "figlia dell'intorno: " if "intorno" in st else ""
            return f"{pre}prende il posto di {st['madre']}, che smette di essere operata"
        if "intorno" in st:
            return f"figlia dell'intorno di {st['intorno']}"
        return ""

    va = ev["varianti"]
    if any(va.values()):
        pezzi = []
        for nome in ("create", "passate", "validate", "bocciate", "scartate"):
            if va[nome]:
                voci = [f"{x['chiave'].replace('|', ' ')} (variante {x['variante'] or '?'}"
                        + (", promossa: vedi sotto" if nome == "validate" and x["variante"] in promosse_s
                           else "") + ")" for x in va[nome]]
                pezzi.append(f"{nome} {len(va[nome])}: {elenco(voci)}")
        out.append("varianti dalle ipotesi: " + "; ".join(pezzi))
    if ev["promosse"] or ev["rimosse"]:
        prom = []
        for e in ev["promosse"]:
            note = [n for n in ((f"ipotesi {e['ipotesi']}" if e.get("ipotesi") else ""),
                                _nota_figlia(e.get("key"))) if n]
            prom.append(e.get("key", "?") + (f" ({'; '.join(note)})" if note else ""))
        rim = [e.get("key", "?") + (f" (vissuta {_num(float(e['vissuta_giorni']), 1)} giorni)"
                                    if _f(e.get("vissuta_giorni")) is not None else "") for e in ev["rimosse"]]
        out.append(f"validate promosse {len(prom)}" + (f": {elenco(prom)}" if prom else "")
                   + f"; rimosse {len(rim)}" + (f": {elenco(rim)}" if rim else ""))
    # le figlie che il diario non ha fra le promosse (diario illeggibile o
    # scritto in un altro giro): la loro riga resta, cosi' non si perdono
    sole = sorted(k for k in storia if k not in promosse_k)
    if sole:
        out.append(f"figlie nuove {len(sole)}: " + elenco(f"{k} ({_nota_figlia(k)})" for k in sole))
    tornate = diff["tornate_piene"] if diff else []
    if ev["declassate"] or tornate:
        pezzi = []
        if ev["declassate"]:
            pezzi.append(f"declassate nuove {len(ev['declassate'])} (size ridotta): {elenco(ev['declassate'])}")
        if tornate:
            pezzi.append(f"declassate tornate piene {len(tornate)}: {elenco(tornate)}")
        out.append("; ".join(pezzi))
    es = ev["esplorative"]
    if any(es.values()):
        out.append(f"esplorative: entrate {len(es['entrate'])}, promosse a validate {len(es['promosse'])}"
                   + (f" ({elenco(es['promosse'])})" if es["promosse"] else "")
                   + f", scartate {len(es['scartate'])}")
    if diff:
        if diff["panchina_entrate"] or diff["panchina_uscite"]:
            ent = [f"{k} ({_k(p)})" for k, p in diff["panchina_entrate"]]
            usc = [f"{k} ({_k(p) if p is not None else 'sparita'})" for k, p in diff["panchina_uscite"]]
            out.append(f"panchina (strategia×regime con peso sotto {_k(SOGLIA_PANCHINA)}: size ridotta): "
                       + (f"entrano {elenco(ent)}" if ent else "nessuna entra")
                       + (f"; escono {elenco(usc)}" if usc else ""))
        if diff["cooldown_iniziati"] or diff["cooldown_finiti"]:
            out.append("cooldown (fermo dopo 3 stop di fila) fra le due foto: "
                       + (f"iniziati {elenco(diff['cooldown_iniziati'])}" if diff["cooldown_iniziati"] else "")
                       + ("; " if diff["cooldown_iniziati"] and diff["cooldown_finiti"] else "")
                       + (f"finiti {elenco(diff['cooldown_finiti'])}" if diff["cooldown_finiti"] else ""))
        if diff["ipotesi_sparite"]:
            out.append(f"ipotesi non piu' nei referti {len(diff['ipotesi_sparite'])}: {elenco(diff['ipotesi_sparite'])}")
    if ev["freno_acceso_at"] is not None:
        out.append(f"freno globale acceso alle {ora_testo(ev['freno_acceso_at'])}")
    elif diff and diff["freno"]:
        out.append(f"freno globale {diff['freno']} fra le due foto")
    righe = [f"     - {r}" for r in out]
    if not righe:
        righe = ["     nulla di nuovo: nessuna ipotesi, variante, promozione, declassata, esplorativa"
                 + (", cambio di panchina o freno" if diff else "")]
    if diff is None:
        righe.append(f"     (panchina, cooldown, freno, declassate tornate piene, ipotesi sparite: "
                     f"non disponibili, {manca})")
    return righe


def per_strategia(dati: dict, now: float, n_max: int = 10, giorni: int = 7) -> list[dict]:
    """Le `n_max` strategie con piu' trade chiusi negli ultimi `giorni` giorni
    (esiti esterni fuori): trade, vinti, R medio, ipotesi attive dai referti,
    regimi in panchina, keep e scala proposti dal vissuto, coppie validate (di
    cui declassate)."""
    d = _mappa(dati)
    trades = _trades(d)
    dal = float(now) - giorni * 86400
    recenti: dict[str, list] = defaultdict(list)
    for t in trades:
        if str(t.get("exit_reason", "")) in ESITI_ESTERNI or not isinstance(t.get("strategy"), str):
            continue
        ex = _exit_ts(t)
        if ex is not None and dal <= ex <= now:
            recenti[t["strategy"]].append(t)
    ordine = sorted(recenti, key=lambda g: (-len(recenti[g]), g))[:n_max]
    if not ordine:
        return []
    ipotesi: dict[str, list] = defaultdict(list)
    for h in _mappa(d.get("referti")).get("ipotesi") or []:
        if isinstance(h, dict):
            ipotesi[str(h.get("strategia"))].append(str(h.get("tipo")))
    panchina: dict[str, list] = defaultdict(list)
    for w in _mappa(d.get("weights")).get("weights") or []:
        if isinstance(w, dict) and (p := _f(w.get("weight"))) is not None and p < SOGLIA_PANCHINA:
            panchina[str(w.get("strategy"))].append(str(w.get("regime")))
    pairs, validate = _registro(d.get("registro"))
    val: Counter = Counter()
    decl: Counter = Counter()
    for k in validate:
        g = k.split("|", 1)[1] if "|" in k else k
        val[g] += 1
        decl[g] += int(bool(_mappa(pairs.get(k)).get("declassata")))
    tutti: dict[str, list] = defaultdict(list)
    for t in trades:
        if isinstance(t.get("strategy"), str):
            tutti[t["strategy"]].append(t)
    proprie = scale_proprie(trades)
    out = []
    for gid in ordine:
        rows = recenti[gid]
        rs = [r for r in (_r_multiplo(t) for t in rows) if r is not None]
        out.append({"strategia": gid, "trade": len(rows),
                    "vinti": sum(1 for t in rows if (_f(t.get("pnl")) or 0.0) > 0),
                    "r_medio": round(mean(rs), 3) if rs else None,
                    "ipotesi": sorted(ipotesi.get(gid, [])), "panchina": sorted(panchina.get(gid, [])),
                    "keep": proposta_keep_strategia(tutti.get(gid, [])), "scala": proprie.get(gid),
                    "validate": val.get(gid, 0), "declassate": decl.get(gid, 0)})
    return out


def sezione_strategie(dati: dict, now: float, storia=None, vite=None, foto_oggi=None,
                      foto_ieri=None, adesso: dict | None = None, perche_senza_foto: str | None = None,
                      manca_adesso: str | None = None) -> list[str]:
    """«COSA IMPARANO LE STRATEGIE»: ieri (giornata intera, ora italiana) e
    stanotte, poi le 10 strategie piu' attive negli ultimi 7 giorni.
    `perche_senza_foto` e `manca_adesso`: come in `sezione_trailing`."""
    d = _mappa(dati)
    fin = finestre(now)
    if not manca_adesso:
        adesso = adesso if isinstance(adesso, dict) else impronta_giorno(d, now)
    motivi = _motivi_confronti(fin, foto_oggi, foto_ieri, perche_senza_foto, manca_adesso)
    out = ["COSA IMPARANO LE STRATEGIE (ipotesi dai referti del paper -> varianti giudicate dal gate "
           "sulla storia -> promozioni; e intanto declassate, esplorative, panchina, freno)"]
    if storia is None:
        out.append("  storia delle ipotesi (learning/ipotesi_storia) non disponibile: ipotesi e varianti mancano")
    if vite is None:
        out.append("  diario delle validate (gate_history/lifecycle) non disponibile: promosse e rimosse mancano")
    confronti = {"ieri": (foto_ieri, foto_oggi), "stanotte": (foto_oggi, adesso)}
    for nome in ("ieri", "stanotte"):
        t0, t1, g = fin[nome]
        ev = eventi_fra(t0, t1, storia=storia, vite=vite, registro=d.get("registro"),
                        esplorative=d.get("esplorative"), drift=d.get("drift"), referti=d.get("referti"))
        prima, dopo = confronti[nome]
        diff = None if (nome == "stanotte" and manca_adesso) else differenze(prima, dopo)
        if nome == "ieri":
            out.append(f"  IERI ({giorno_testo(g)}, giornata intera ora italiana):")
        else:
            out.append(f"  STANOTTE ({giorno_testo(g)} dalle 00:00 alle {ora_testo(now)} ora italiana):")
        out += _righe_eventi(ev, diff, motivi[nome])
    righe = per_strategia(d, now)
    out.append("  PER STRATEGIA (le 10 con piu' trade chiusi negli ultimi 7 giorni; R = guadagno in "
               "unita' del rischio iniziale):")
    if not righe:
        out.append("     nessun trade chiuso negli ultimi 7 giorni")
    for x in righe:
        pezzi = [f"{x['trade']} trade, {_plurale(x['vinti'], 'vinto', 'vinti')}, R medio {_r(x['r_medio'])}"]
        if x["ipotesi"]:
            pezzi.append("ipotesi " + ", ".join(x["ipotesi"]))
        if x["panchina"]:
            pezzi.append("in panchina con " + ", ".join(x["panchina"]))
        if x["keep"] is not None:
            pezzi.append(f"keep proposto {_k(x['keep'])}")
        if x["scala"]:
            pezzi.append(f"scala propria {x['scala']}")
        pezzi.append(_plurale(x["validate"], "validata", "validate")
                     + (f" ({x['declassate']} declassate)" if x["declassate"] else ""))
        out.append(f"     {x['strategia']}: " + " · ".join(pezzi))
    return out
