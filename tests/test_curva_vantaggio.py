"""LA CURVA DEL VANTAGGIO DEL SEGNALE (T2, 2 ott 2026).

Si verifica che la misura applichi la regola del diario («2 ottobre, mattina:
T2») senza sguardi avanti:
  * niente dopo l'orizzonte e niente dopo l'ingresso (per la mossa tipica)
    cambia il risultato; il prezzo d'ingresso e' l'ultima candela gia' chiusa;
  * un vantaggio piantato apposta (segnali subito prima delle salite) si vede;
  * segnali a caso su un cammino casuale danno quasi sempre «nessun vantaggio»;
  * lo short ha il segno giusto;
  * il margine (blocchi di giornate) e' riproducibile col seme;
  * una moneta che non e' in cache si salta e si conta.
"""
import random
from datetime import datetime, timezone

import numpy as np

from bot.core.models import Candle
from bot.learning import curva_vantaggio as cv

T0 = int(datetime(2026, 8, 1, tzinfo=timezone.utc).timestamp())
P = cv.PASSO_S
GIORNO = 86400


def _cammino(seme: int, giorni: int = 50, sigma: float = 0.002, spinte=None) -> list:
    """Coppie (open_time, close) da 15m. `spinte`: {indice della candela: deriva
    per candela} applicata per 16 candele da quell'indice in poi."""
    n = giorni * 96
    rng = np.random.default_rng(seme)
    passi = rng.normal(0.0, sigma, n)
    for k0, d in (spinte or {}).items():
        passi[k0 + 1:k0 + 17] += d
    prezzi = 100.0 * np.exp(np.cumsum(passi))
    return [(T0 + P * k, float(prezzi[k])) for k in range(n)]


def _ingresso(k: int, ritardo_s: int = 7) -> float:
    """L'ora d'ingresso subito dopo la chiusura della candela k (come il bot)."""
    return float(T0 + P * k + P + ritardo_s)


# --------------------------------------------------------------------------- #
# (a) niente sguardi avanti                                                    #
# --------------------------------------------------------------------------- #
def test_prezzo_d_ingresso_e_l_ultima_candela_gia_chiusa():
    c = _cammino(1, giorni=40)
    s = cv.Serie(c)
    k = 35 * 96 + 40
    # ingresso alle hh:07 della candela k+1: riferimento = candela k (chiusa)
    assert s.indice(_ingresso(k)) == k
    # ingresso esattamente alla chiusura della candela k: ancora la k
    assert s.indice(float(T0 + P * k + P)) == k
    # un secondo prima della chiusura: la k non e' chiusa, vale la k-1
    assert s.indice(float(T0 + P * k + P - 1)) == k - 1
    # cambiare la candela che CONTIENE l'ingresso non cambia il prezzo d'ingresso
    c2 = list(c)
    c2[k + 1] = (c2[k + 1][0], c2[k + 1][1] * 3)
    s2 = cv.Serie(c2)
    assert s2.indice(_ingresso(k)) == k and s2.close[k] == s.close[k]
    assert cv.misura(s2, k, "long") == cv.misura(s, k, "long")
    # dati finiti (o buco) prima dell'ingresso: niente prezzo vecchio al suo posto
    assert s.indice(float(T0 + P * len(c) + 3 * P)) is None
    assert s.indice(float(T0 - 10)) is None


def test_dopo_l_orizzonte_e_dopo_l_ingresso_niente_cambia_la_misura():
    c = _cammino(2, giorni=45)
    k = 35 * 96 + 10
    base = cv.Serie(c)
    m = cv.misura(base, k, "long")
    norma = base.mossa_tipica(k)
    # tutto cio' che sta DOPO l'ultima durata (96 candele) moltiplicato per 5
    dopo = [(t, x * 5 if i > k + 96 else x) for i, (t, x) in enumerate(c)]
    assert cv.misura(cv.Serie(dopo), k, "long") == m
    # la mossa tipica usa solo i 30 giorni PRIMA: cambiare tutto il dopo-ingresso
    # (anche le candele dentro le durate) non la tocca
    dopo_ingresso = [(t, x * (1 + 0.3 * ((i * 7919) % 13 - 6) / 6) if i > k else x)
                     for i, (t, x) in enumerate(c)]
    assert cv.Serie(dopo_ingresso).mossa_tipica(k) == norma
    # e nemmeno cio' che sta prima dei 30 giorni
    prima = [(t, x * 9 if t < T0 + P * k - 31 * GIORNO else x) for t, x in c]
    assert cv.Serie(prima).mossa_tipica(k) == norma


def test_la_curva_intera_non_guarda_oltre_l_ultimo_futuro_usato():
    """Il caso sta entro 12 ore dal segnale e guarda 24 ore avanti: oltre
    l'ultimo segnale + 12 ore + 24 ore niente puo' cambiare l'esito."""
    c = _cammino(3, giorni=50)
    rng = random.Random(3)
    seg = [{"symbol": "AUSDT", "lato": rng.choice(["long", "short"]),
            "ts": _ingresso(rng.randrange(32 * 96, 44 * 96))} for _ in range(30)]
    righe, _ = cv.misura_segnali(seg, {"AUSDT": c})
    limite = max(s["ts"] for s in seg) + 12 * 3600 + GIORNO + P
    c2 = [(t, x * 4 if t > limite else x) for t, x in c]
    righe2, _ = cv.misura_segnali(seg, {"AUSDT": c2})
    assert righe == righe2
    assert cv.curva(righe) == cv.curva(righe2)


def test_buco_nella_serie_salta_l_ingresso_invece_di_misurarlo_storto():
    c = _cammino(4, giorni=40)
    k = 35 * 96
    bucata = [x for i, x in enumerate(c) if i != k + 48]        # manca la candela a 12 ore
    s = cv.Serie(bucata)
    assert cv.misura(s, s.indice(_ingresso(k)), "long").startswith("orizzonte oltre")
    # storia troppo corta per la mossa tipica (meno di 15 giorni prima)
    corta = cv.Serie(c)
    assert "mossa tipica" in cv.misura(corta, 10 * 96, "long")


def test_serie_accetta_le_candle_della_cache():
    c = _cammino(5, giorni=40)
    candle = [Candle(open_time=datetime.fromtimestamp(t, tz=timezone.utc), open=x, high=x,
                     low=x, close=x, volume=1.0) for t, x in c]
    a, b = cv.Serie(c), cv.Serie(candle)
    k = 36 * 96
    assert cv.misura(a, k, "short") == cv.misura(b, k, "short")
    # millisecondi come nelle righe grezze della cache
    ms = cv.Serie([(t * 1000, x) for t, x in c])
    assert cv.misura(ms, k, "long") == cv.misura(a, k, "long")


# --------------------------------------------------------------------------- #
# (b) un vantaggio piantato si vede; (c) il caso puro no                       #
# --------------------------------------------------------------------------- #
def _con_vantaggio(lato: str = "long"):
    """Una moneta per giorno di segnali: ogni giorno, alle 10 UTC, parte una
    spinta di 16 candele (+0,15% a candela); il segnale entra subito prima."""
    monete, seg = {}, []
    for g in range(32, 46):
        k = g * 96 + 40
        d = 0.0015 if lato == "long" else -0.0015
        sym = f"C{g % 5}USDT"
        monete.setdefault(sym, {})[k] = d
        seg.append({"symbol": sym, "lato": lato, "ts": _ingresso(k)})
    serie = {sym: _cammino(100 + int(sym[1]), giorni=50, spinte=sp)
             for sym, sp in monete.items()}
    return seg, serie


def test_vantaggio_piantato_da_c_e_un_vantaggio():
    seg, serie = _con_vantaggio("long")
    righe, saltati = cv.misura_segnali(seg, serie)
    assert len(righe) == len(seg) and not saltati
    curva = cv.curva(righe)
    v = cv.verdetto(curva)
    assert v["esito"] == cv.ESITO_VANTAGGIO
    assert 16 in v["sopra"]
    # la spinta dura 4 ore: la curva smette di salire li'
    assert v["picco"] == 16
    assert "ESITO" not in v["testo"] and "4 ore" in v["testo"]


def test_segnali_a_caso_su_cammino_casuale_quasi_sempre_nessun_vantaggio():
    esiti = []
    for prova in range(12):
        serie = {f"C{m}": _cammino(2000 + 20 * prova + m, giorni=50) for m in range(10)}
        rng = random.Random(100 + prova)
        seg = [{"symbol": f"C{rng.randrange(10)}", "lato": rng.choice(["long", "short"]),
                "ts": rng.uniform(T0 + 31 * GIORNO, T0 + 47 * GIORNO)} for _ in range(100)]
        righe, _ = cv.misura_segnali(seg, serie)
        assert len(righe) == 100
        esiti.append(cv.verdetto(cv.curva(righe))["esito"])
    # 4 durate guardate insieme e 16 giornate: il caso puro a volte esce dal
    # margine (2 ott, 100 prove sintetiche da 220 segnali: 76 «nessun vantaggio»,
    # 8 «c'è un vantaggio», 16 «peggio del caso»). Qui la maggioranza, seme fisso.
    assert esiti.count(cv.ESITO_NESSUNO) >= 7
    assert esiti.count(cv.ESITO_VANTAGGIO) <= 3


# --------------------------------------------------------------------------- #
# (d) lo short                                                                 #
# --------------------------------------------------------------------------- #
def test_short_ha_il_segno_rovesciato():
    # sale dello 0,1% a candela, con 30 giorni di storia mossa (per la norma)
    c = _cammino(6, giorni=40)
    k = 36 * 96
    sale = [(t, x if i <= k else c[k][1] * 1.001 ** (i - k)) for i, (t, x) in enumerate(c)]
    s = cv.Serie(sale)
    lr, lz = cv.misura(s, k, "long")
    sr, sz = cv.misura(s, k, "short")
    assert all(x > 0 for x in lr) and lr == [-x for x in sr] and lz == [-x for x in sz]
    assert abs(lr[0] - (1.001 ** 4 - 1)) < 1e-12
    # uno short prima di una discesa piantata: anche li' «c'è un vantaggio»
    seg, serie = _con_vantaggio("short")
    righe, _ = cv.misura_segnali(seg, serie)
    assert all(r["s_r"][1] > 0 for r in righe)
    assert cv.verdetto(cv.curva(righe))["esito"] == cv.ESITO_VANTAGGIO
    # e gli stessi segnali girati in long fanno peggio del caso
    rovesci = [{**x, "lato": "long"} for x in seg]
    righe_l, _ = cv.misura_segnali(rovesci, serie)
    assert cv.verdetto(cv.curva(righe_l))["esito"] == cv.ESITO_PEGGIO


# --------------------------------------------------------------------------- #
# (e) il margine e' riproducibile                                              #
# --------------------------------------------------------------------------- #
def test_margine_a_blocchi_di_giornate_riproducibile_col_seme():
    serie = {f"C{m}": _cammino(50 + m, giorni=46) for m in range(4)}
    rng = random.Random(11)
    seg = [{"symbol": f"C{rng.randrange(4)}", "lato": rng.choice(["long", "short"]),
            "ts": rng.uniform(T0 + 31 * GIORNO, T0 + 44 * GIORNO)} for _ in range(50)]
    righe, _ = cv.misura_segnali(seg, serie)
    # stesso risultato anche mescolando l'ordine dei segnali (seme per segnale)
    righe_mescolate, _ = cv.misura_segnali(list(reversed(seg)), serie)
    chiave = lambda r: (r["ts"], r["symbol"])  # noqa: E731
    assert sorted(righe, key=chiave) == sorted(righe_mescolate, key=chiave)
    a, b = cv.curva(righe), cv.curva(righe)
    assert a == b
    assert cv.curva(righe, seme=7)["per_durata"][0]["ic"] != a["per_durata"][0]["ic"]
    # la media non dipende dal seme, solo il margine
    assert cv.curva(righe, seme=7)["per_durata"][0]["vantaggio"] == a["per_durata"][0]["vantaggio"]
    # il margine ricampiona le GIORNATE: con tutti i segnali in un giorno solo
    # non c'e' niente da ricampionare e la misura non si fa
    un_giorno = [{**r, "giorno": "2026-09-01"} for r in righe]
    c1 = cv.curva(un_giorno)
    assert c1["giorni"] == 1 and c1["per_durata"][0]["ic"] is None
    assert cv.verdetto(c1)["esito"] == cv.ESITO_NON_MISURABILE


def test_vantaggio_e_media_segnali_meno_media_caso():
    righe = [{"giorno": f"2026-09-0{g}", "lato": "long", "s_z": [g, 0, 0, 0],
              "c_z": [1, 0, 0, 0], "s_r": [g / 100, 0, 0, 0], "c_r": [0.01, 0, 0, 0]}
             for g in (1, 2, 3)]
    c = cv.curva(righe, n_boot=200)
    r = c["per_durata"][0]
    assert r["segnali"] == 2 and r["caso"] == 1 and r["vantaggio"] == 1
    assert abs(r["vantaggio_pct"] - 1.0) < 1e-12
    assert r["ic"][0] >= 0 - 1e-12 and r["ic"][1] <= 2 + 1e-12


# --------------------------------------------------------------------------- #
# il verdetto, esattamente come la regola                                      #
# --------------------------------------------------------------------------- #
def _cv(ic_e_v, sale=(None, None, None, None)):
    return {"n": 100, "giorni": 16, "per_durata": [
        {"h": h, "durata": cv.durata_testo(h), "vantaggio": v, "vantaggio_pct": v,
         "ic": ic, "sale_dopo": su} for h, (ic, v), su in zip(cv.ORIZZONTI, ic_e_v, sale)]}


def test_verdetto_segue_la_regola():
    dentro = ((-0.1, 0.1), 0.0)
    assert cv.verdetto(_cv([dentro] * 4))["esito"] == cv.ESITO_NESSUNO
    v = cv.verdetto(_cv([dentro, ((0.01, 0.2), 0.1), ((0.02, 0.3), 0.15), ((-0.1, 0.3), 0.12)],
                        sale=(False, True, False, None)))
    assert v["esito"] == cv.ESITO_VANTAGGIO and v["picco"] == 48 and v["sopra"] == [16, 48]
    # se fra 4 e 12 ore la curva NON sale oltre il margine, il punto e' 4 ore anche se a
    # 12 ore la media e' piu' alta (revisione del 2 ott: la media piu' alta e' rumore)
    v = cv.verdetto(_cv([dentro, ((0.01, 0.2), 0.1), ((0.02, 0.3), 0.15), ((-0.1, 0.3), 0.12)],
                        sale=(False, False, False, None)))
    assert v["picco"] == 16
    assert "12 ore" in v["testo"] and "sale ancora" not in v["testo"]
    # picco all'ultima durata: lo si dice (potrebbe salire oltre)
    v = cv.verdetto(_cv([dentro, dentro, dentro, ((0.01, 0.3), 0.2)]))
    assert v["picco"] == 96 and "sale ancora" in v["testo"]
    v = cv.verdetto(_cv([((-0.3, -0.01), -0.1), dentro, dentro, dentro]))
    assert v["esito"] == cv.ESITO_PEGGIO and v["sotto"] == [4]
    # sopra e sotto insieme: c'e' un vantaggio, ma il peggio si dice per primo
    v = cv.verdetto(_cv([((-0.3, -0.01), -0.1), ((0.01, 0.2), 0.1), dentro, dentro]))
    assert v["esito"] == cv.ESITO_VANTAGGIO
    assert v["testo"].index("peggio") < v["testo"].index(cv.ESITO_VANTAGGIO)
    assert cv.verdetto({"n": 0, "giorni": 0, "per_durata": []})["esito"] == cv.ESITO_NON_MISURABILE


# --------------------------------------------------------------------------- #
# (f) i trade del paper e la cache che manca                                   #
# --------------------------------------------------------------------------- #
def _trade(sym="AUSDT", tf="15m", lato="long", k=36 * 96, **extra):
    return {"symbol": sym, "timeframe": tf, "direction": lato, "strategy": "gen_a",
            "entry_time": datetime.fromtimestamp(_ingresso(k), tz=timezone.utc).isoformat(),
            **extra}


def test_segnali_dai_trade_conta_timeframe_ed_esplorativi():
    trades = [_trade(), _trade(esplorativa=True, exit_reason="manual"), _trade(tf="1h"),
              _trade(tf=""), _trade(lato="boh"), {"symbol": "X", "timeframe": "15m"}]
    seg, conti = cv.segnali_dai_trade(trades)
    # senza timeframe registrato vale quello del bot (15m), come in bot/main.py
    assert len(seg) == 3 and conti["letti"] == 6 and conti["del_timeframe"] == 5
    assert conti["altri_timeframe"] == {"1h": 1}
    assert conti["esplorativi"] == 1 and conti["senza_dati"] == 2
    assert seg[0]["ts"] == _ingresso(36 * 96)


def test_moneta_non_in_cache_si_salta_e_si_conta(capsys):
    from scripts import curva_vantaggio as sc

    c = _cammino(8, giorni=40)
    candele = {"AUSDT": [Candle(open_time=datetime.fromtimestamp(t, tz=timezone.utc), open=x,
                                high=x, low=x, close=x, volume=1.0) for t, x in c]}
    chiesti = []

    def carica(sym, tf, giorni):
        chiesti.append((sym, tf, giorni))
        if sym == "ROTTAUSDT":
            raise OSError("file illeggibile")
        return candele.get(sym)

    trades = [_trade(k=35 * 96 + j * 13) for j in range(6)] + [
        _trade(sym="BUSDT"), _trade(sym="BUSDT", k=35 * 96), _trade(sym="ROTTAUSDT")]
    ora = float(T0 + 40 * GIORNO)
    r = sc.stampa(trades, carica=carica, ora=ora)
    assert r["saltati"]["moneta non in cache"] == 3
    assert r["curva"]["n"] == 6
    # una lettura per moneta, solo 15m, con i giorni che coprono la mossa tipica
    assert sorted(x[0] for x in chiesti) == ["AUSDT", "BUSDT", "ROTTAUSDT"]
    assert all(x[1] == "15m" and x[2] >= cv.GIORNI_NORMA + 5 for x in chiesti)
    out = capsys.readouterr().out
    assert "LA CURVA DEL VANTAGGIO DEL SEGNALE (T2)" in out
    assert "moneta non in cache: 3" in out
    assert "parte informativa del motore" in out.lower() and "non ancora" in out
    assert out.strip().splitlines()[-1].startswith("ESITO (regola del 2 ott): ")


def test_nessun_trade_non_rompe_la_sezione(capsys):
    from scripts import curva_vantaggio as sc

    r = sc.stampa([], carica=lambda *a: None)
    assert r["verdetto"]["esito"] == cv.ESITO_NON_MISURABILE
    assert capsys.readouterr().out.strip().splitlines()[-1].startswith("ESITO (regola del 2 ott)")


def test_mfe_report_chiama_la_sezione_in_coda_e_fail_open():
    import inspect

    import scripts.mfe_report as mfe

    src = inspect.getsource(mfe.main)
    assert src.index("stampa_tp_aperti") < src.index("stampa_curva")
    blocco = src[src.index("from scripts.curva_vantaggio"):]
    assert "except Exception" in blocco.split("return 0")[0]


def test_direzione_scelta_dal_passato_non_inganna_il_caso():
    """Prezzi a caso: nessun vantaggio, anche se la direzione segue le ultime 4 ore.
    Col caso a ±12 ore (prima della revisione del 2 ott 2026) usciva «peggio del
    caso» 6 volte su 6."""
    esiti = []
    for prova in range(6):
        serie = {f"C{m}": _cammino(3000 + 20 * prova + m, giorni=50) for m in range(10)}
        rng = random.Random(300 + prova)
        seg = []
        for _ in range(150):
            sym, k = f"C{rng.randrange(10)}", rng.randrange(31 * 96, 47 * 96)
            c = serie[sym]
            seg.append({"symbol": sym, "lato": "long" if c[k][1] > c[k - 16][1] else "short",
                        "ts": _ingresso(k)})
        righe, _ = cv.misura_segnali(seg, serie)
        esiti.append(cv.verdetto(cv.curva(righe))["esito"])
    assert esiti.count(cv.ESITO_PEGGIO) <= 2
