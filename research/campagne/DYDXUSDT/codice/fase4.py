"""Fase 4: le verifiche sui dati di costruzione del candidato DYDXUSDT-008, ognuna registrata prima.

    python research/campagne/DYDXUSDT/codice/fase4.py <gruppo>

Gruppi: robustezza, timeframe, ritardo_costi_intrabarra.
Criteri (PROTOCOLLO.md, Fase 4, «Quando una verifica e' superata»).
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
import registro  # noqa: E402
from comune import Spec  # noqa: E402
from varianti import segnale_atr, uscita_tempo  # noqa: E402

CARTELLA = Path(__file__).resolve().parent.parent
CANDIDATO = "DYDXUSDT-008"
T_B_BASE = 2.2168935870928923  # t contro la (b) del candidato in costruzione (log, risultato DYDXUSDT-008)


def crea_i08(k_btc=2.0, finestra=168, k_stop=2.0, uscita=3, n_atr=14, minimo=100):
    def crea(ctx):
        b = ctx.btc
        rb = np.full(ctx.n, np.nan)
        rb[1:] = b[1:] / b[:-1] - 1.0
        sd = np.full(ctx.n, np.nan)
        for i in range(finestra + 1, ctx.n):
            w = rb[i - finestra:i]
            if np.isfinite(w).sum() >= minimo:
                sd[i] = np.nanstd(w)
        risc = finestra + 2
        sig = segnale_atr(ctx, "long", k_stop, risc, n_atr)

        def cond(i):
            if i < risc or not (np.isfinite(rb[i]) and np.isfinite(sd[i]) and sd[i] > 0):
                return False
            rd = ctx.c[i] / ctx.c[i - 1] - 1.0
            return rb[i] > k_btc * sd[i] and rd < rb[i]
        return Spec(sig, cond, uscita_tempo(ctx, uscita))
    return crea


def prossimo_id():
    n = sum(1 for v in registro.voci() if v.get("tipo") == "registrazione" and v.get("tipo_test") == "verifica"
            and v.get("verifica_di") == CANDIDATO)
    return f"{CANDIDATO}-V{n + 1:02d}"


def verifica(nome, tf, crea, par=None, descrizione="", criterio="", conta=True):
    par = par or comune.parametri()
    id_ = prossimo_id()
    stima = comune.conta(tf, crea, par)["trade"] if conta else None
    registro.aggiungi({"id": id_, "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": CANDIDATO,
                       "verifica": nome, "timeframe": tf, "descrizione": descrizione, "criterio_successo": criterio,
                       "periodo": "costruzione", "trade_stimati": stima})
    if stima is not None and stima < comune.TRADE_MINIMI_COSTRUZIONE:
        voce = registro.aggiungi({"id": id_, "tipo": "risultato", "verifica": nome,
                                  "esito": f"sotto i trade minimi ({stima}): si dichiara e non conta"})
        return {"id": id_, "nome": nome, "conta": False, "trade": stima}
    ris = comune.pubblico(comune.valuta(tf, crea, par))
    m, b, a = ris["metriche"], ris.get("baseline_b", {}), ris.get("baseline_a", {})
    sint = {"id": id_, "nome": nome, "conta": True, "trade": m["trade"], "r_medio": m["r_medio"],
            "r_medio_per_anno": m["r_medio_per_anno"], "trade_per_anno": m["trade_per_anno"],
            "senza3": m["r_medio_senza_3_migliori"], "t_b": b.get("t"), "netta_b": b.get("netta"),
            "media_b": b.get("media"), "soglia_b": b.get("soglia"), "t_a": a.get("t"), "netta_a": a.get("netta"),
            "valutabile": ris.get("valutabile"), "violazioni_liquidazione": m["n_violazioni_liquidazione"],
            "ridotti": m["n_ridotti"], "esiti": m["esiti"], "stop_medio_pct": m["stop_medio_pct"],
            "quota_stop_oltre_6pct": m["quota_stop_oltre_6pct"], "funding_totale": m["funding_totale"]}
    registro.aggiungi({"id": id_, "tipo": "risultato", "verifica": nome, "metriche": m, "baseline_a": a,
                       "baseline_b": b, "percentile_caso": ris.get("percentile_caso")})
    print(json.dumps(registro._pulisci(sint), ensure_ascii=False), flush=True)
    return sint


def robustezza():
    casi = [("k_btc", 1.6), ("k_btc", 2.4), ("finestra", 134), ("finestra", 202), ("k_stop", 1.6), ("k_stop", 2.4),
            ("uscita", 2), ("uscita", 4), ("n_atr", 11), ("n_atr", 17), ("minimo", 80), ("minimo", 120)]
    out = []
    for p, v in casi:
        out.append(verifica(f"robustezza {p}={v}", "1h", crea_i08(**{p: v}),
                            descrizione=f"parametro {p} spostato a {v} (20% o arrotondamento della Fase 4), il resto uguale",
                            criterio="nei casi che contano t(b) > 0 in tutti e netta in almeno meta'"))
    contano = [x for x in out if x["conta"]]
    ok = (len(contano) >= len(casi) / 2 and all((x.get("t_b") or -1e9) > 0 and x.get("valutabile") for x in contano)
          and sum(bool(x.get("netta_b")) for x in contano) >= len(contano) / 2)
    return {"robustezza": {"casi": len(casi), "contano": len(contano), "t_b_positivo": sum((x.get("t_b") or -1) > 0 for x in contano),
                           "netti": sum(bool(x.get("netta_b")) for x in contano), "superata": ok}}


def timeframe():
    out = [
        verifica("timeframe 30m", "30m", crea_i08(finestra=336, uscita=6, n_atr=28, minimo=200),
                 descrizione="30m: finestra 336 barre (168 ore), uscita 6 barre (3 ore), ATR 28 barre, minimo 200 valori; soglie in deviazioni standard e stop in ATR uguali",
                 criterio="t(b) > 0 (se ha i trade minimi)"),
        verifica("timeframe 2h", "2h", crea_i08(finestra=84, uscita=2, n_atr=7, minimo=50),
                 descrizione="2h: finestra 84 barre, uscita round(1,5)=2 barre, ATR 7 barre, minimo 50 valori",
                 criterio="t(b) > 0 (se ha i trade minimi)"),
    ]
    contano = [x for x in out if x["conta"]]
    ok = all((x.get("t_b") or -1e9) > 0 and x.get("valutabile") for x in contano)
    return {"timeframe": {"casi": [(x["nome"], x["trade"], x.get("t_b")) for x in out], "superata": ok}}


def ritardo_costi_intrabarra():
    crea = crea_i08()
    r = verifica("ritardo di una barra", "1h", crea, comune.parametri(ritardo_barre=1),
                 descrizione="esecuzione ritardata di una barra; (b) ricalcolata col ritardo",
                 criterio=f"t(b) > 0 e >= meta' di {T_B_BASE:.3f}", conta=False)
    c = verifica("costi doppi", "1h", crea, comune.parametri(moltiplicatore_costi=2.0),
                 descrizione="commissione, slippage e funding (se costo) raddoppiati; (b) a costi doppi",
                 criterio="batte nettamente la (b) a costi doppi e R medio a costi doppi > 0")
    x = verifica("regola intra-barra opposta", "1h", crea, comune.parametri(riempimento_intrabarra="target_prima"),
                 descrizione="target prima dello stop nella stessa barra (il candidato non ha target: atteso identico)",
                 criterio="si dichiara la differenza", conta=False)
    return {"ritardo": {"t_b": r.get("t_b"), "superata": bool((r.get("t_b") or -1) > 0 and r.get("t_b") >= T_B_BASE / 2)},
            "costi_doppi": {"t_b": c.get("t_b"), "netta": c.get("netta_b"), "r_medio": c.get("r_medio"),
                            "superata": bool(c.get("netta_b") and (c.get("r_medio") or -1) > 0)},
            "intrabarra_opposta": {"r_medio": x.get("r_medio"), "t_b": x.get("t_b")}}


def crea_i08_senza_ritardo_dydx(k_btc=2.0, finestra=168):
    """Fase 5, test dello scettico: la regola senza la condizione «DYDX ha seguito meno di BTC»."""
    def crea(ctx):
        base = crea_i08(k_btc=k_btc, finestra=finestra)(ctx)
        b = ctx.btc
        rb = np.full(ctx.n, np.nan)
        rb[1:] = b[1:] / b[:-1] - 1.0

        def cond(i):
            if not base.condizione(i) and not (i >= finestra + 2 and np.isfinite(rb[i])):
                return False
            # stessa condizione su BTC, senza il confronto con DYDX
            return _condizione_btc(ctx, i, rb, k_btc, finestra)
        return Spec(base.segnale, cond, base.esci)
    return crea


def _condizione_btc(ctx, i, rb, k_btc, finestra, minimo=100):
    if i < finestra + 2 or not np.isfinite(rb[i]):
        return False
    w = rb[i - finestra:i]
    if np.isfinite(w).sum() < minimo:
        return False
    sd = np.nanstd(w)
    return bool(sd > 0 and rb[i] > k_btc * sd)


def scettico():
    s = verifica("scettico: senza la condizione sul ritardo di DYDX", "1h", crea_i08_senza_ritardo_dydx(),
                 descrizione="stessa regola di 008 ma entra dopo ogni ora di BTC oltre 2 deviazioni standard, che DYDX abbia seguito o no",
                 criterio="se R e t(b) sono simili a 008, il vantaggio viene dal movimento di BTC e non dal ritardo di DYDX (il meccanismo dichiarato)")
    return {"scettico": s}


if __name__ == "__main__":
    if sys.argv[1] == "scettico":
        print("ESITO", json.dumps(registro._pulisci(scettico()), ensure_ascii=False))
        sys.exit(0)
    gruppo = sys.argv[1]
    esito = {"robustezza": robustezza, "timeframe": timeframe, "ritardo_costi_intrabarra": ritardo_costi_intrabarra}[gruppo]()
    print("ESITO", json.dumps(registro._pulisci(esito), ensure_ascii=False))
    (comune.RADICE_REPO / "research" / "data" / "insample" / "DYDXUSDT" / f"fase4_{gruppo}.json").write_text(
        json.dumps(registro._pulisci(esito), ensure_ascii=False, indent=1))
