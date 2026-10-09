"""Conta, registra e testa le varianti, IN SERIE, nell'ordine dato sulla riga di comando.

Per ogni etichetta: conta_trade una volta sola sulle regole registrate; sotto 70 trade la variante
e' uno scarto (nessun test, nessun budget); altrimenti si scrive la registrazione nel log e SOLO
DOPO si esegue il test di costruzione, il cui esito va in una voce ``risultato`` separata.
Uso: ``python lancia.py I-01-L I-01-S ...``. L'esito sintetico va anche in
data/insample/BNBUSDT/esiti.txt (fuori da git), perche' il guardiano non lascia leggere l'uscita
dei comandi in background.
"""
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune as C  # noqa: E402
import registro  # noqa: E402
import varianti as V  # noqa: E402

ESITI = C.dati.RADICE_DEFAULT / "data" / "insample" / "BNBUSDT" / "esiti.txt"
CRITERIO = ("candidato se batte nettamente la (a) e la (b) con contro_baseline (sezione 8) e l'R medio "
            "dopo i costi e' positivo; minimo 70 trade in costruzione")

F = {
    "I-01": "Moskowitz, Ooi, Pedersen, «Time Series Momentum», Journal of Financial Economics 104(2), 2012; Liu, Tsyvinski, «Risks and Returns of Cryptocurrency», NBER WP 24877, 2018",
    "I-02": "Curtis M. Faith, «Way of the Turtle», McGraw-Hill, 2007",
    "I-03": "Larry Connors, Cesar Alvarez, «Short Term Trading Strategies That Work», TradingMarkets, 2008",
    "I-04": "Caporale, Plastun, «The day of the week effect in the cryptocurrency market», Finance Research Letters 31, 2019",
    "I-05": "Schmeling, Schrimpf, Todorov, «Crypto carry», BIS Working Paper 1087, aprile 2023",
    "I-06": "John Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001",
    "I-07": "Gervais, Kaniel, Mingelgrin, «The High-Volume Return Premium», Journal of Finance 56(3), 2001",
    "I-08": "Caporale, Plastun, «Price overreactions in the cryptocurrency market», Journal of Economic Studies 46(5), 2019",
    "I-09": "Chordia, Subrahmanyam, «Order imbalance and individual stock returns», Journal of Financial Economics 72(3), 2004",
    "I-10": "Brock, Lakonishok, LeBaron, «Simple Technical Trading Rules and the Stochastic Properties of Stock Returns», Journal of Finance 47(5), 1992",
    "I-11": "Shen, Urquhart, Wang, «Bitcoin intraday time series momentum», Financial Review 57(2), 2022",
    "I-12": "Brunnermeier, Pedersen, «Market Liquidity and Funding Liquidity», Review of Financial Studies 22(6), 2009",
    "I-13": "Lakonishok, Smidt, «Are Seasonal Anomalies Real? A Ninety-Year Perspective», Review of Financial Studies 1(4), 1988",
    "I-14": "Alan Moreira, Tyler Muir, «Volatility-Managed Portfolios», Journal of Finance 72(4), 2017",
    "I-15": "J. Welles Wilder, «New Concepts in Technical Trading Systems», Trend Research, 1978",
    "I-16": "Yakov Amihud, «Illiquidity and stock returns: cross-section and time-series effects», Journal of Financial Markets 5(1), 2002",
    "I-17": "Amaya, Christoffersen, Jacobs, Vasquez, «Does realized skewness predict the cross-section of equity returns?», Journal of Financial Economics 118(1), 2015",
    "I-18": "Carol L. Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation for the Predictive Success of Technical Analysis», Journal of Finance 58(5), 2003",
}

# etichetta: (idea, fabbrica, meccanismo, parametri, (r_min, r_max), batte_b_previsto)
SPEC = {
    "I-01-L": ("I-01", lambda vid: V.i01("long", vid), "momentum a serie temporale settimanale",
               {"rendimento_7_giorni": "> 0", "uscita": "7 barre", "stop": "2 ATR(14)"}, (-0.05, 0.10), False),
    "I-01-S": ("I-01", lambda vid: V.i01("short", vid), "momentum a serie temporale settimanale",
               {"rendimento_7_giorni": "< 0", "uscita": "7 barre", "stop": "2 ATR(14)"}, (-0.10, 0.05), False),
    "I-02-L": ("I-02", lambda vid: V.i02("long", vid), "rottura del canale di Donchian",
               {"ingresso": "close > max high 20 barre precedenti", "uscita": "close < min low 10 precedenti", "stop": "2 ATR(20)"}, (-0.10, 0.10), False),
    "I-02-S": ("I-02", lambda vid: V.i02("short", vid), "rottura del canale di Donchian",
               {"ingresso": "close < min low 20 barre precedenti", "uscita": "close > max high 10 precedenti", "stop": "2 ATR(20)"}, (-0.10, 0.10), False),
    "I-03-1h": ("I-03", lambda vid: V.i03("1h", vid), "inversione di breve in tendenza (RSI 2)",
                {"ingresso": "close > SMA200 e RSI2 < 5", "uscita": "close > SMA5", "stop": "2,5 ATR(14)"}, (-0.15, 0.05), False),
    "I-03-4h": ("I-03", lambda vid: V.i03("4h", vid), "inversione di breve in tendenza (RSI 2)",
                {"ingresso": "close > SMA200 e RSI2 < 5", "uscita": "close > SMA5", "stop": "2,5 ATR(14)"}, (-0.10, 0.10), False),
    "I-04-L": ("I-04", lambda vid: V.i04(vid), "effetto del lunedi'",
               {"ingresso": "chiusura della domenica", "uscita": "1 barra", "stop": "2 ATR(14)"}, (-0.05, 0.05), False),
    "I-05-S": ("I-05", lambda vid: V.i05("short", vid), "funding estremo, affollamento dei long",
               {"ingresso": "funding > 90 percentile dei 90 settlement precedenti", "uscita": "3 barre", "stop": "2 ATR(14)"}, (-0.10, 0.10), False),
    "I-05-L": ("I-05", lambda vid: V.i05("long", vid), "funding estremo, affollamento degli short",
               {"ingresso": "funding < 10 percentile dei 90 settlement precedenti", "uscita": "3 barre", "stop": "2 ATR(14)"}, (-0.10, 0.10), False),
    "I-06-L": ("I-06", lambda vid: V.i06("long", vid), "rottura dopo compressione delle bande",
               {"ingresso": "min larghezza 6 barre <= min 120 barre e close > banda sup.", "uscita": "close < SMA20", "stop": "2 ATR(14)"}, (-0.10, 0.10), False),
    "I-06-S": ("I-06", lambda vid: V.i06("short", vid), "rottura dopo compressione delle bande",
               {"ingresso": "min larghezza 6 barre <= min 120 barre e close < banda inf.", "uscita": "close > SMA20", "stop": "2 ATR(14)"}, (-0.10, 0.10), False),
    "I-07-L": ("I-07", lambda vid: V.i07(vid), "premio del volume alto",
               {"ingresso": "volume >= 90 percentile degli ultimi 50 giorni", "uscita": "5 barre", "stop": "2 ATR(14)"}, (-0.05, 0.10), False),
    "I-08-L": ("I-08", lambda vid: V.i08("long", vid), "continuazione dopo sovrareazione",
               {"ingresso": "r24 > media180 + 2 dev std", "uscita": "6 barre", "stop": "2 ATR(14)"}, (-0.10, 0.10), False),
    "I-08-S": ("I-08", lambda vid: V.i08("short", vid), "continuazione dopo sovrareazione",
               {"ingresso": "r24 < media180 - 2 dev std", "uscita": "6 barre", "stop": "2 ATR(14)"}, (-0.10, 0.10), False),
    "I-09-L": ("I-09", lambda vid: V.i09("long", vid), "squilibrio degli ordini aggressivi",
               {"ingresso": "squilibrio 6 barre >= 90 percentile di 180", "uscita": "6 barre", "stop": "2 ATR(14)"}, (-0.10, 0.10), False),
    "I-09-S": ("I-09", lambda vid: V.i09("short", vid), "squilibrio degli ordini aggressivi",
               {"ingresso": "squilibrio 6 barre <= 10 percentile di 180", "uscita": "6 barre", "stop": "2 ATR(14)"}, (-0.10, 0.10), False),
    "I-10-L": ("I-10", lambda vid: V.i10("long", vid), "incrocio della media a 50",
               {"ingresso": "incrocio al rialzo della SMA50", "uscita": "close < SMA50", "stop": "2 ATR(14)"}, (-0.15, 0.05), False),
    "I-10-S": ("I-10", lambda vid: V.i10("short", vid), "incrocio della media a 50",
               {"ingresso": "incrocio al ribasso della SMA50", "uscita": "close > SMA50", "stop": "2 ATR(14)"}, (-0.15, 0.05), False),
    "I-11-L": ("I-11", lambda vid: V.i11("long", vid), "momento infragiornaliero",
               {"ingresso": "barra 00:00 UTC in salita, ingresso 23:30", "uscita": "1 barra", "stop": "2 ATR(14)"}, (-0.20, 0.0), False),
    "I-11-S": ("I-11", lambda vid: V.i11("short", vid), "momento infragiornaliero",
               {"ingresso": "barra 00:00 UTC in discesa, ingresso 23:30", "uscita": "1 barra", "stop": "2 ATR(14)"}, (-0.20, 0.0), False),
    "I-12-3": ("I-12", lambda vid: V.i12(3.0, vid), "rimbalzo dopo caduta forzata",
               {"ingresso": "close - open < -3 ATR(14) precedente", "uscita": "12 barre", "stop": "2 ATR(14)"}, (-0.10, 0.15), False),
    "I-12-2": ("I-12", lambda vid: V.i12(2.0, vid), "rimbalzo dopo caduta forzata",
               {"ingresso": "close - open < -2 ATR(14) precedente", "uscita": "12 barre", "stop": "2 ATR(14)"}, (-0.10, 0.15), False),
    "I-13-L": ("I-13", lambda vid: V.i13(vid), "cambio del mese",
               {"ingresso": "vigilia dell'ultimo giorno del mese", "uscita": "4 barre", "stop": "2 ATR(14)"}, (-0.05, 0.05), False),
    "I-06-L1h": ("I-06", lambda vid: V.i06("long", vid, "1h"), "rottura dopo compressione delle bande",
                 {"timeframe": "1h", "ingresso": "min larghezza 6 barre <= min 120 barre e close > banda sup.", "uscita": "close < SMA20", "stop": "2 ATR(14)"}, (-0.15, 0.05), False),
    "I-06-S1h": ("I-06", lambda vid: V.i06("short", vid, "1h"), "rottura dopo compressione delle bande",
                 {"timeframe": "1h", "ingresso": "min larghezza 6 barre <= min 120 barre e close < banda inf.", "uscita": "close > SMA20", "stop": "2 ATR(14)"}, (-0.15, 0.05), False),
    "I-07-L80": ("I-07", lambda vid: V.i07(vid, 0.8), "premio del volume alto",
                 {"ingresso": "volume >= 80 percentile degli ultimi 50 giorni", "uscita": "5 barre", "stop": "2 ATR(14)"}, (-0.05, 0.10), False),
    "I-14-L": ("I-14", lambda vid: V.i14(vid), "volatilita' bassa, rendimento per rischio piu' alto",
               {"ingresso": "dev std rendimenti 42 barre <= 33 percentile delle ultime 540", "uscita": "6 barre", "stop": "2 ATR(14)"}, (-0.10, 0.10), False),
    "I-15-L": ("I-15", lambda vid: V.i15("long", vid), "forza della tendenza (ADX)",
               {"ingresso": "ADX(14) sale sopra 25 con +DI > -DI", "uscita": "-DI > +DI", "stop": "2 ATR(14)"}, (-0.10, 0.10), False),
    "I-15-S": ("I-15", lambda vid: V.i15("short", vid), "forza della tendenza (ADX)",
               {"ingresso": "ADX(14) sale sopra 25 con -DI > +DI", "uscita": "+DI > -DI", "stop": "2 ATR(14)"}, (-0.10, 0.10), False),
    "I-16-L": ("I-16", lambda vid: V.i16(vid), "shock di illiquidita'",
               {"ingresso": "illiquidita' di Amihud 6 barre >= 90 percentile di 180", "uscita": "6 barre", "stop": "2 ATR(14)"}, (-0.10, 0.10), False),
    "I-17-L": ("I-17", lambda vid: V.i17(vid), "asimmetria realizzata negativa",
               {"ingresso": "asimmetria rendimenti 42 barre <= 10 percentile delle ultime 540", "uscita": "42 barre", "stop": "2 ATR(14)"}, (-0.10, 0.15), False),
    "I-08-L15": ("I-08", lambda vid: V.i08("long", vid, 1.5), "continuazione dopo sovrareazione",
                 {"ingresso": "r24 > media180 + 1,5 dev std", "uscita": "6 barre", "stop": "2 ATR(14)"}, (-0.10, 0.10), False),
    "I-08-S15": ("I-08", lambda vid: V.i08("short", vid, 1.5), "continuazione dopo sovrareazione",
                 {"ingresso": "r24 < media180 - 1,5 dev std", "uscita": "6 barre", "stop": "2 ATR(14)"}, (-0.10, 0.10), False),
    "I-15-L20": ("I-15", lambda vid: V.i15("long", vid, 20.0), "forza della tendenza (ADX)",
                 {"ingresso": "ADX(14) sale sopra 20 con +DI > -DI", "uscita": "-DI > +DI", "stop": "2 ATR(14)"}, (-0.10, 0.10), False),
    "I-15-S20": ("I-15", lambda vid: V.i15("short", vid, 20.0), "forza della tendenza (ADX)",
                 {"ingresso": "ADX(14) sale sopra 20 con -DI > +DI", "uscita": "+DI > -DI", "stop": "2 ATR(14)"}, (-0.10, 0.10), False),
    "I-17-L20": ("I-17", lambda vid: V.i17(vid, 0.2), "asimmetria realizzata negativa",
                 {"ingresso": "asimmetria rendimenti 42 barre <= 20 percentile delle ultime 540", "uscita": "42 barre", "stop": "2 ATR(14)"}, (-0.10, 0.15), False),
    "I-18-L": ("I-18", lambda vid: V.i18("long", vid), "ordini di stop oltre i numeri tondi",
               {"ingresso": "close attraversa al rialzo il primo numero tondo sopra la chiusura precedente", "uscita": "6 barre", "stop": "2 ATR(14)"}, (-0.15, 0.05), False),
    "I-18-S": ("I-18", lambda vid: V.i18("short", vid), "ordini di stop oltre i numeri tondi",
               {"ingresso": "close attraversa al ribasso il primo numero tondo sotto la chiusura precedente", "uscita": "6 barre", "stop": "2 ATR(14)"}, (-0.15, 0.05), False),
}


def scrivi_esito(testo: str) -> None:
    with ESITI.open("a", encoding="utf-8") as f:
        f.write(testo + "\n")


def prossimi_numeri():
    voci = registro.leggi()
    numeri = [int(v["id"].split("-")[1]) for v in voci if v["id"].split("-")[1].isdigit()]
    n_var = sum(1 for v in voci if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante")
    return (max(numeri) + 1 if numeri else 1), n_var + 1


def esegui_etichetta(etichetta: str) -> None:
    idea, fab, mecc, par, (rmin, rmax), batte_b = SPEC[etichetta]
    num, var_n = prossimi_numeri()
    vid = f"BNBUSDT-{num:03d}"
    v = fab(vid)
    conteggio = C.conta(v)
    comune_voce = {"id": vid, "idea": idea, "etichetta": etichetta, "famiglia": vid, "ritocco_di": None,
                   "fonte": F[idea], "meccanismo": mecc, "timeframe": v.tf, "direzione": v.direzione,
                   "parametri": par, "periodo": "costruzione", "trade_stimati": conteggio["trade"],
                   "conteggio": conteggio}
    if conteggio["trade"] < 70:
        registro.aggiungi(dict(comune_voce, tipo="scarto",
                               motivo=f"conta_trade {conteggio['trade']} trade, sotto il minimo di 70 in costruzione"))
        scrivi_esito(f"{vid} {etichetta} SCARTO {conteggio['trade']} trade")
        return
    previsione = (f"R medio dopo i costi fra {rmin:+.2f} e {rmax:+.2f}; "
                  + ("batte nettamente la (b)" if batte_b else "non batte nettamente la (b)"))
    registro.aggiungi(dict(comune_voce, tipo="registrazione", tipo_test="variante", previsione=previsione,
                           criterio_successo=CRITERIO, variante_n=var_n))
    res = C.valuta(v)
    m = res["metriche"]
    netta_b = bool(res.get("baseline_b", {}).get("netta"))
    corretta = bool(rmin <= m["r_medio"] <= rmax and netta_b == batte_b)
    commento = (f"{'candidato' if res.get('candidato') else 'non candidato'}; "
                f"{'valutabile' if res.get('valutabile') else 'NON valutabile'}; "
                f"(a) netta {res.get('baseline_a', {}).get('netta')}, (b) netta {netta_b}, R medio {m['r_medio']:+.3f}")
    registro.aggiungi({"id": vid, "tipo": "risultato", "etichetta": etichetta,
                       "metriche": m, "blocco": res.get("blocco"), "durata_media_barre": res.get("durata_media_barre"),
                       "baseline_a": res.get("baseline_a"), "baseline_b": res.get("baseline_b"),
                       "percentile_caso": res.get("percentile_caso"),
                       "buy_and_hold_per_anno": res.get("buy_and_hold_per_anno"),
                       "btc_stessa_finestra": res.get("btc_stessa_finestra"),
                       "valutabile": res.get("valutabile"), "candidato": res.get("candidato"),
                       "previsione_corretta": corretta, "commento": commento})
    scrivi_esito(f"{vid} {etichetta} n={m['trade']} " + C.compatto(res))


if __name__ == "__main__":
    for e in sys.argv[1:]:
        try:
            esegui_etichetta(e)
        except Exception:
            scrivi_esito(f"ERRORE {e}\n" + traceback.format_exc())
            raise
    scrivi_esito("LOTTO FINITO " + " ".join(sys.argv[1:]))
