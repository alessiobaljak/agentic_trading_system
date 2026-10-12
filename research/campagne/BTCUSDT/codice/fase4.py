"""Fase 4: verifiche dei candidati sui dati di costruzione.

I candidati si ricostruiscono qui in forma parametrica (per la robustezza e i timeframe
adiacenti). Prima di ogni verifica si controlla che il costruttore, con i parametri del
candidato e sul suo timeframe, dia ESATTAMENTE gli stessi trade della variante registrata.

Ogni verifica si registra nel log prima di eseguirla (tipo_test "verifica", verifica_di)
e il risultato si aggiunge dopo. Uso: python fase4.py V10 [V11 ...]
"""
from __future__ import annotations

import math
import sys
from datetime import datetime, timezone

import numpy as np

import quadro
import varianti
from comune import SIMBOLO, aggiungi_log, motore, parametri, voci_log
from quadro import Variante, arr, barre_tenute, nan
from research.src.motore import Segnale

GIORNO = 86_400_000
MINIMO = 70


# ---------------------------------------------------------------------------
# Costruttori parametrici
# ---------------------------------------------------------------------------

def williams(direzione, tf, k=0.5, vid="X"):
    """I-06 su un timeframe qualunque: giorno UTC, range di ieri da tutte le sue barre,
    un ingresso al giorno, nessun segnale sull'ultima barra del giorno, uscita alla chiusura
    dell'ultima barra del giorno, stop all'apertura del giorno."""
    ms = quadro.MS[tf]
    per_giorno = GIORNO // ms

    def prepara(candele):
        giorni = {}
        for c in candele:
            d = giorni.setdefault(c.ts // GIORNO, {"open": None, "high": -math.inf, "low": math.inf, "n": 0})
            if c.ts % GIORNO == 0:
                d["open"] = c.open
            d["high"] = max(d["high"], c.high)
            d["low"] = min(d["low"], c.low)
            d["n"] += 1
        return giorni

    def livelli(stato, storia):
        g = storia[-1].ts // GIORNO
        oggi, ieri = stato.get(g), stato.get(g - 1)
        if oggi is None or ieri is None or oggi["open"] is None or ieri["n"] != per_giorno:
            return None
        return oggi["open"], ieri["high"] - ieri["low"]

    def ultima(ts):
        return ts % GIORNO == GIORNO - ms

    def condizione(stato, storia):
        liv = livelli(stato, storia)
        if liv is None:
            return None
        ts = storia[-1].ts
        if ultima(ts):
            return False
        o, rng = liv
        inizio = ts - ts % GIORNO
        oltre = (lambda x: x > o + k * rng) if direzione == "long" else (lambda x: x < o - k * rng)
        if not oltre(storia[-1].close):
            return False
        j = len(storia) - 2
        while j >= 0 and storia[j].ts >= inizio:
            if oltre(storia[j].close):
                return False
            j -= 1
        return True

    def segnale(stato, storia):
        liv = livelli(stato, storia)
        return None if liv is None else Segnale(direzione, stop=liv[0])

    def uscita(stato, storia, pos):
        return "chiudi" if ultima(storia[-1].ts) else None

    return Variante(vid, tf, direzione, prepara, condizione, segnale, uscita)


def mezzora(tf="30m", stop_pct=0.01, tenuta_min=30, inizio_min=30, filtro_giornata=True, vol=None,
            fine_settimana=False, vid="X", ora_segnale_min=None):
    """Famiglia I-10 (short): il primo periodo del giorno (inizio_min minuti) in calo ->
    short sull'ultimo periodo (tenuta_min minuti). ``vol`` = dict(barre, quantile, giorni,
    minimo) per il filtro di volatilita' di V32/V35. Su 30m con i default e' V31."""
    ms = quadro.MS[tf]
    n_primo = max(1, round(inizio_min * 60_000 / ms))
    n_tenuta = max(1, round(tenuta_min * 60_000 / ms))
    ts_segnale = GIORNO - n_tenuta * ms - ms  # apertura dell'ultima barra prima dell'ultimo periodo
    if ora_segnale_min is not None:  # solo per il test placebo della Fase 5
        ts_segnale = ora_segnale_min * 60_000

    def prepara(candele):
        prima = {}
        per_ts_ = {c.ts: c for c in candele}
        for c in candele:
            if c.ts % GIORNO == 0:
                ultima_p = per_ts_.get(c.ts + (n_primo - 1) * ms)
                if ultima_p is not None and all((c.ts + j * ms) in per_ts_ for j in range(n_primo)):
                    prima[c.ts // GIORNO] = (c.open, ultima_p.close)
        stato = {"prima": prima, "vol": {}, "soglia": {}}
        if vol:
            c = arr(candele, "close")
            lr = np.zeros(c.size)
            lr[1:] = np.diff(np.log(c))
            s1 = np.cumsum(np.insert(lr, 0, 0.0))
            s2 = np.cumsum(np.insert(lr * lr, 0, 0.0))
            n = vol["barre"]
            storico = []
            for i, x in enumerate(candele):
                if x.ts % GIORNO != ts_segnale or i < n:
                    continue
                m = (s1[i + 1] - s1[i + 1 - n]) / n
                v = math.sqrt(max((s2[i + 1] - s2[i + 1 - n]) / n - m * m, 0.0) * n / (n - 1))
                prec = [w for t, w in storico if t >= x.ts - vol["giorni"] * GIORNO]
                if len(prec) >= vol["minimo"]:
                    stato["soglia"][x.ts] = float(np.quantile(prec, vol["quantile"]))
                stato["vol"][x.ts] = v
                storico.append((x.ts, v))
        return stato

    def condizione(stato, storia):
        ts = storia[-1].ts
        if vol and (not stato["soglia"] or ts < min(stato["soglia"])):
            return None
        if ts % GIORNO != ts_segnale:
            return False
        p = stato["prima"].get(ts // GIORNO)
        if p is None:
            return None
        if not p[1] < p[0]:
            return False
        if filtro_giornata and not storia[-1].close < p[0]:
            return False
        if vol:
            if ts not in stato["soglia"]:
                return None
            if not stato["vol"][ts] <= stato["soglia"][ts]:
                return False
        if fine_settimana and datetime.fromtimestamp(ts / 1000, tz=timezone.utc).weekday() < 5:
            return False
        return True

    def segnale(stato, storia):
        return Segnale("short", stop=storia[-1].close * (1 + stop_pct))

    def uscita(stato, storia, pos):
        return "chiudi" if barre_tenute(storia, pos, ms) >= n_tenuta else None

    return Variante(vid, tf, "short", prepara, condizione, segnale, uscita)


VOL_V32 = dict(barre=960, quantile=0.5, giorni=365, minimo=300)
VOL_V35 = dict(barre=960, quantile=0.75, giorni=365, minimo=300)

COSTRUTTORI = {
    "V10": (williams, dict(direzione="long", tf="1h", k=0.5)),
    "V11": (williams, dict(direzione="short", tf="1h", k=0.5)),
    "V32": (mezzora, dict(vol=VOL_V32)),
    "V33": (mezzora, dict(fine_settimana=True)),
    "V35": (mezzora, dict(vol=VOL_V35)),
}


def costruisci(vid, **cambi):
    f, base = COSTRUTTORI[vid]
    p = dict(base)
    for k, v in cambi.items():
        if k == "vol":
            p["vol"] = dict(p["vol"], **v)
        else:
            p[k] = v
    return f(vid=vid, **p), p


def stessi_trade(vid):
    """Il costruttore con i parametri del candidato da' gli stessi trade della variante."""
    a = varianti.TUTTE[vid]()
    b, _ = costruisci(vid)
    candele, mark, funding = quadro.costruzione(a.tf)
    ta = motore.esegui(candele, None, mark, funding, a.fabbrica(candele)(), parametri()).trades
    tb = motore.esegui(candele, None, mark, funding, b.fabbrica(candele)(), parametri()).trades
    return [(t.ts_entrata, t.ts_uscita, round(t.r, 9)) for t in ta] == [(t.ts_entrata, t.ts_uscita, round(t.r, 9)) for t in tb]


# ---------------------------------------------------------------------------
# Casi di verifica
# ---------------------------------------------------------------------------

def _arrotonda(x):
    return int(math.floor(x + 0.5))


def _intero(valore):
    giu, su = _arrotonda(0.8 * valore), _arrotonda(1.2 * valore)
    if giu == valore:
        giu = valore - 1
    if su == valore:
        su = valore + 1
    return giu, su


def casi_robustezza(vid):
    """Ogni parametro numerico +-20%, uno alla volta (Fase 4, punto 1)."""
    casi = []
    if vid in ("V10", "V11"):
        casi += [("k 0,4", dict(k=0.4)), ("k 0,6", dict(k=0.6))]
        return casi
    casi += [("stop 0,8%", dict(stop_pct=0.008)), ("stop 1,2%", dict(stop_pct=0.012))]
    casi += [("tenuta 60 minuti (2 barre)", dict(tenuta_min=60))]  # 1 barra: round(0,8)=round(1,2)=1 -> 0 (impossibile) e 2
    if vid in ("V32", "V35"):
        q = COSTRUTTORI[vid][1]["vol"]["quantile"]
        g, s = _intero(960)
        casi += [(f"volatilita' {g} barre", dict(vol=dict(barre=g))), (f"volatilita' {s} barre", dict(vol=dict(barre=s)))]
        casi += [(f"quantile {0.8 * q:.2f}", dict(vol=dict(quantile=0.8 * q))),
                 (f"quantile {min(1.2 * q, 1.0):.2f}", dict(vol=dict(quantile=min(1.2 * q, 1.0))))]
        g, s = _intero(365)
        casi += [(f"finestra {g} giorni", dict(vol=dict(giorni=g))), (f"finestra {s} giorni", dict(vol=dict(giorni=s)))]
        g, s = _intero(300)
        casi += [(f"minimo {g} valori", dict(vol=dict(minimo=g))), (f"minimo {s} valori", dict(vol=dict(minimo=s)))]
    return casi


def casi_timeframe(vid):
    """Timeframe adiacenti (Fase 4, punto 2): parametri in barre convertiti in tempo."""
    if vid in ("V10", "V11"):
        return [("30m", dict(tf="30m")), ("2h", dict(tf="2h"))]
    out = [("15m", dict(tf="15m"))]
    vol = COSTRUTTORI[vid][1].get("vol")
    out[0][1].update({"vol": dict(barre=1920)} if vol else {})
    uno = dict(tf="1h")
    if vol:
        uno["vol"] = dict(barre=480)
    out.append(("1h (primo e ultimo periodo diventano un'ora: mezz'ora arrotondata a 1 barra)", uno))
    return out


def _ridotto(e):
    a, b = e.get("baseline_a", {}), e.get("baseline_b", {})
    m = e["metriche"]
    return {"trade": m["trade"], "r_medio": m["r_medio"], "r_medio_per_anno": m["r_medio_per_anno"],
            "trade_per_anno": m["trade_per_anno"], "r_medio_senza_3_migliori": m["r_medio_senza_3_migliori"],
            "violazioni_liquidazione": m["violazioni_liquidazione"], "esiti": m["esiti"],
            "baseline_a": {k: a.get(k) for k in ("media", "t", "netta", "valutabile")},
            "baseline_b": {k: b.get(k) for k in ("media", "t", "soglia", "netta", "valutabile", "errore_minimo")},
            "percentile_caso": e.get("percentile_caso")}


def _id_verifica(vid, nome):
    esistenti = [v["id"] for v in voci_log() if v.get("tipo") == "registrazione" and v.get("verifica_di") == f"{SIMBOLO}-{vid}"]
    return f"{SIMBOLO}-{vid}-F{len(esistenti) + 1:02d}"


def verifica(vid, nome, crea, par=None, tf=None, criterio="", conta_prima=False, base=None):
    lid = _id_verifica(vid, nome)
    v = crea()
    conteggio = quadro.conta(v, par=par, tf=tf) if conta_prima else None
    aggiungi_log({"id": lid, "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": f"{SIMBOLO}-{vid}",
                  "verifica": nome, "periodo": "costruzione", "criterio_successo": criterio,
                  "trade_stimati": conteggio["trade"] if conteggio else (base["metriche"]["trade"] if base else None)})
    if conteggio and conteggio["trade"] < MINIMO:
        voce = {"id": lid, "tipo": "risultato", "conta": False,
                "commento": f"sotto i trade minimi ({conteggio['trade']}): si dichiara e non conta"}
        aggiungi_log(voce)
        return voce
    e = quadro.valuta_costruzione(v, par=par, tf=tf)
    voce = {"id": lid, "tipo": "risultato", "conta": True, **_ridotto(e)}
    aggiungi_log(voce)
    return voce


def fase4(vid):
    assert stessi_trade(vid), f"{vid}: il costruttore non riproduce la variante"
    base_reg = [v for v in voci_log() if v.get("id") == f"{SIMBOLO}-{vid}" and v.get("tipo") == "risultato"][-1]
    t0 = base_reg["baseline_b"]["t"]
    esiti = {}

    # 1. robustezza
    rob = []
    for nome, cambi in casi_robustezza(vid):
        r = verifica(vid, f"robustezza: {nome}", lambda c=cambi: costruisci(vid, **c)[0], conta_prima=True,
                     criterio="caso contato se >= 70 trade; t contro la (b) ricalcolata > 0; in almeno meta' dei casi contati batte nettamente la (b)")
        rob.append(r)
    contati = [r for r in rob if r.get("conta")]
    falliti_nv = [r for r in contati if not r["baseline_b"].get("valutabile")]
    pos = [r for r in contati if r["baseline_b"].get("valutabile") and r["baseline_b"]["t"] > 0]
    nette = [r for r in contati if r["baseline_b"].get("netta")]
    esiti["robustezza"] = bool(len(contati) * 2 >= len(rob) and not falliti_nv and len(pos) == len(contati)
                               and len(nette) * 2 >= len(contati))

    # 2. timeframe adiacenti
    tfr = []
    for nome, cambi in casi_timeframe(vid):
        c = dict(cambi)
        tf = c["tf"]
        r = verifica(vid, f"timeframe adiacente {nome}", lambda c=c: costruisci(vid, **c)[0], tf=tf, conta_prima=True,
                     criterio="sui timeframe con >= 70 trade il t contro la (b) ricalcolata resta positivo; non valutabile = fallito")
        tfr.append(r)
    esiti["timeframe_adiacenti"] = all((not r.get("conta")) or (r["baseline_b"].get("valutabile") and r["baseline_b"]["t"] > 0) for r in tfr)

    v = varianti.TUTTE[vid]
    # 6. ritardo
    r = verifica(vid, "ritardo di una barra", v, par=parametri(ritardo_barre=1),
                 criterio=f"t contro la (b) ricalcolata col ritardo > 0 e >= meta' di {t0}")
    esiti["ritardo"] = bool(r["baseline_b"].get("valutabile") and r["baseline_b"]["t"] > 0 and r["baseline_b"]["t"] >= t0 / 2)
    # 8. costi doppi
    r = verifica(vid, "costi doppi", v, par=parametri(moltiplicatore_costi=2.0),
                 criterio="batte nettamente la (b) ricalcolata a costi doppi e R medio a costi doppi > 0")
    esiti["costi_doppi"] = bool(r["baseline_b"].get("netta") and r["r_medio"] > 0)
    # 5. regola intra-barra opposta
    r = verifica(vid, "regola intra-barra opposta (target prima)", v, par=parametri(riempimento_intrabarra="target_prima"),
                 criterio="si dichiara la differenza")
    esiti["intrabarra_opposta_r_medio"] = r["r_medio"]

    # 4, 5, 7 dai numeri del test di Fase 2
    m = base_reg["metriche"]
    bmedia = base_reg["baseline_b"]["media"]
    anni = [a for a, n in m["trade_per_anno"].items() if n >= 10]
    sopra = [a for a in anni if m["r_medio_per_anno"][a] > bmedia]
    esiti["stabilita_temporale"] = {"anni_con_10_trade": anni, "anni_sopra_la_b": sopra, "superata": len(sopra) * 2 > len(anni)}
    esiti["pochi_trade_estremi"] = {"r_senza_3_migliori": m["r_medio_senza_3_migliori"], "media_b": bmedia,
                                    "superata": m["r_medio_senza_3_migliori"] is not None and m["r_medio_senza_3_migliori"] > bmedia}
    esiti["liquidazione"] = {"violazioni": m["violazioni_liquidazione"], "superata": m["violazioni_liquidazione"] == 0}
    passa = all([esiti["robustezza"], esiti["timeframe_adiacenti"], esiti["ritardo"], esiti["costi_doppi"],
                 esiti["stabilita_temporale"]["superata"], esiti["pochi_trade_estremi"]["superata"],
                 esiti["liquidazione"]["superata"]])
    aggiungi_log({"id": f"{SIMBOLO}-{vid}-F", "tipo": "nota", "argomento": f"esito della Fase 4 di {vid}",
                  "esiti": esiti, "passa_la_fase_4": passa})
    print(vid, passa, esiti, flush=True)


if __name__ == "__main__":
    for vid in sys.argv[1:]:
        fase4(vid)
