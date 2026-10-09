"""Registra ed esegue le varianti indicate (in serie): conta_trade, registrazione o scarto, test, risultato.

Uso: python esegui.py V01 V02 ...   (oppure un id di ritocco definito in ritocchi.py)
Ogni registrazione si scrive nel log PRIMA del test; il risultato in una voce separata dopo.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune as C  # noqa: E402
import registro as R  # noqa: E402
import varianti as VV  # noqa: E402

try:
    import ritocchi as RT  # noqa: E402
    TUTTE = {**VV.VARIANTI, **RT.RITOCCHI}
except ImportError:
    TUTTE = dict(VV.VARIANTI)

_NUM = r"([+-]?\d+(?:,\d+)?)"


def _f(s):
    return float(s.replace(",", "."))


def intervalli_previsione(testo):
    mr = re.search(r"R medio fra " + _NUM + " e " + _NUM, testo)
    mt = re.search(r"t contro la \(b\) fra " + _NUM + " e " + _NUM, testo)
    return ((_f(mr.group(1)), _f(mr.group(2))) if mr else None,
            (_f(mt.group(1)), _f(mt.group(2))) if mt else None)


def prossimo_n():
    return 1 + sum(1 for v in R.voci() if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante")


def esegui(vid):
    spec = TUTTE[vid]
    lid = f"LINKUSDT-{vid}"
    voci = R.voci()
    if any(v.get("id") == lid and v.get("tipo") in ("risultato", "scarto") for v in voci):
        print(vid, "gia' fatta: salto")
        return
    ctx = C.contesto(spec["tf"], "costruzione", VV.extra_per)
    gia = [v for v in voci if v.get("id") == lid and v.get("tipo") == "registrazione"]
    if gia:
        # registrata ma senza risultato (esecuzione interrotta): stesso test, nessuna nuova registrazione
        print(vid, "registrata senza risultato: eseguo il test registrato")
        _test(vid, spec, lid, ctx)
        return
    conteggio = C.conta(ctx, spec["prepara"])
    base = {"id": lid, "idea": spec["idea"], "famiglia": spec.get("famiglia", lid), "ritocco_di": spec.get("ritocco_di"),
            "fonte": VV.FONTI[spec["idea"]], "meccanismo": spec["meccanismo"], "timeframe": spec["tf"],
            "direzione": spec["direzione"], "parametri": spec["parametri"], "periodo": "costruzione",
            "trade_stimati": conteggio["trade"], "conta_trade": conteggio}
    if spec.get("cosa_cambia"):
        base["cosa_cambia_e_perche"] = spec["cosa_cambia"]
    if conteggio["trade"] < C.TRADE_MINIMI_COSTRUZIONE:
        R.aggiungi(dict(base, tipo="scarto", motivo=f"trade stimati {conteggio['trade']} sotto il minimo di costruzione (70): non si testa, non consuma budget"))
        print(vid, "scarto", conteggio["trade"])
        return
    R.aggiungi(dict(base, tipo="registrazione", tipo_test="variante", previsione=spec["previsione"],
                    criterio_successo=VV.CRITERIO, variante_n=prossimo_n()))
    _test(vid, spec, lid, ctx)


def _test(vid, spec, lid, ctx):
    out = C.valuta(ctx, spec["prepara"], "costruzione")
    C.scrivi_json(C.CARTELLA_DATI / f"risultato_{vid}.json", out)
    m = out["metriche"]
    rr, tr = intervalli_previsione(spec["previsione"])
    tb = out["baseline_b"].get("t")
    tb_num = tb if isinstance(tb, (int, float)) else float("-inf")
    corretta = None
    if rr and tr:
        corretta = bool(rr[0] <= m["r_medio"] <= rr[1] and tr[0] <= tb_num <= tr[1])
    voce = {"id": lid, "tipo": "risultato",
            "metriche": {k: m[k] for k in ("profit_factor", "trade", "r_medio", "r_medio_per_anno", "trade_per_anno",
                                            "r_medio_senza_3_migliori", "drawdown_max", "rendimento_totale", "win_rate",
                                            "ridotti", "violazioni_liquidazione", "esiti", "durata_media_ore")},
             "blocco": out.get("blocco"), "baseline_a": out.get("baseline_a"), "baseline_b": out.get("baseline_b"),
             "percentile_caso": out.get("percentile_caso"), "buy_and_hold_per_anno": out["buy_and_hold_per_anno"],
             "valutabile": out.get("valutabile"), "candidato": out.get("candidato", False),
             "n_buchi_dati": out["n_buchi_dati"], "n_funding_in_buco": out["n_funding_in_buco"],
             "previsione_corretta": corretta}
    R.aggiungi(voce)
    print(vid, "trade", m["trade"], "r", round(m["r_medio"], 4), "t_a", out["baseline_a"].get("t"),
          "t_b", tb, "candidato", out.get("candidato"), "prev_ok", corretta, flush=True)


if __name__ == "__main__":
    for v in sys.argv[1:]:
        esegui(v)
