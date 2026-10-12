"""Dati di registro di ogni variante (sezione 6): idea, fonte, meccanismo, parametri, previsione."""

F = {
    "I-01": "Moskowitz, Ooi, Pedersen, «Time series momentum», Journal of Financial Economics, maggio 2012; Liu, Tsyvinski, «Risks and Returns of Cryptocurrency», NBER WP 24877, agosto 2018",
    "I-02": "Shen, Urquhart, Wang, «Bitcoin intraday time-series momentum», Financial Review, online 26 ottobre 2021",
    "I-03": "Brock, Lakonishok, LeBaron, «Simple Technical Trading Rules and the Stochastic Properties of Stock Returns», Journal of Finance, dicembre 1992; Hudson, Urquhart, «Technical trading and cryptocurrencies», Annals of Operations Research, online 30 agosto 2019",
    "I-04": "Larry Williams, «Long-Term Secrets to Short-Term Trading», Wiley, 1999",
    "I-05": "Connors, Alvarez, «Short Term Trading Strategies That Work», TradingMarkets, 2008",
    "I-06": "Gervais, Kaniel, Mingelgrin, «The High-Volume Return Premium», Journal of Finance, giugno 2001",
    "I-07": "Bali, Cakici, Whitelaw, «Maxing out», Journal of Financial Economics, febbraio 2011; Grobys, Junttila, «Speculation and lottery-like demand in cryptocurrency markets», J. Int. Financial Markets, Institutions and Money, 2021 (online fine 2020)",
    "I-08": "He, Manela, Ross, von Wachter, «Fundamentals of Perpetual Futures», arXiv 2212.06888, dicembre 2022 (la direzione e' una mia deduzione dal meccanismo)",
    "I-09": "Caporale, Plastun, «The day of the week effect in the cryptocurrency market», Finance Research Letters, 2019 (CESifo WP 6716, ottobre 2017)",
    "I-10": "John Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001",
    "I-11": "Bruce N. Lehmann, «Fads, Martingales, and Market Efficiency», Quarterly Journal of Economics, febbraio 1990",
    "I-12": "Caporale, Plastun, «Price overreactions in the cryptocurrency market», Journal of Economic Studies, 2019 (CESifo WP 6861, gennaio 2018)",
    "I-13": "Chordia, Subrahmanyam, «Order imbalance and individual stock returns: Theory and evidence», Journal of Financial Economics, giugno 2004",
    "I-14": "Carol L. Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation for the Predictive Success of Technical Analysis», Journal of Finance, ottobre 2003",
    "I-16": "J. Welles Wilder Jr., «New Concepts in Technical Trading Systems», Trend Research, 1978",
    "I-15": "Toby Crabel, «Day Trading with Short Term Price Patterns and Opening Range Breakout», Traders Press, 1990",
}

CRITERIO = ("candidato in Fase 2: batte nettamente la (a) e la (b) (contro_baseline, sezione 8) "
            "e R medio dopo i costi positivo")


def m(idea, mecc, tf, dire, par, prev):
    return {"idea": idea, "fonte": F[idea], "meccanismo": mecc, "timeframe": tf, "direzione": dire,
            "parametri": par, "previsione": f"R medio dopo i costi fra {prev[0]} e {prev[1]}",
            "previsione_intervallo": list(prev), "criterio_successo": CRITERIO}


META = {
    "DOGEUSDT-001": m("I-01", "momento della serie storica a una settimana", "1d", "long",
                      {"ingresso": "close/close[-7]-1 > 0", "uscita": "a tempo dopo 3 barre", "stop": "2,5 ATR14", "target": None}, (-0.05, 0.15)),
    "DOGEUSDT-002": m("I-01", "momento della serie storica a una settimana", "1d", "short",
                      {"ingresso": "close/close[-7]-1 < 0", "uscita": "a tempo dopo 3 barre", "stop": "2,5 ATR14", "target": None}, (-0.05, 0.15)),
    "DOGEUSDT-003": m("I-02", "la prima mezz'ora del giorno UTC prevede l'ultima", "30m", "long",
                      {"ingresso": "barra 00:00-00:30 chiusa sopra l'apertura; segnale alla chiusura della 23:00-23:30", "uscita": "a tempo dopo 1 barra", "stop": "2 ATR14", "target": None}, (-0.15, 0.0)),
    "DOGEUSDT-004": m("I-02", "la prima mezz'ora del giorno UTC prevede l'ultima", "30m", "short",
                      {"ingresso": "barra 00:00-00:30 chiusa sotto l'apertura; segnale alla chiusura della 23:00-23:30", "uscita": "a tempo dopo 1 barra", "stop": "2 ATR14", "target": None}, (-0.15, 0.0)),
    "DOGEUSDT-005": m("I-03", "rottura del canale di 50 barre", "4h", "long",
                      {"ingresso": "close > massimo degli high delle 50 barre prima", "uscita": "a tempo dopo 30 barre", "stop": "2 ATR14", "target": None}, (-0.05, 0.15)),
    "DOGEUSDT-006": m("I-03", "rottura del canale di 50 barre", "4h", "short",
                      {"ingresso": "close < minimo dei low delle 50 barre prima", "uscita": "a tempo dopo 30 barre", "stop": "2 ATR14", "target": None}, (-0.05, 0.15)),
    "DOGEUSDT-007": m("I-04", "rottura di volatilita' dall'apertura del giorno UTC", "1h", "long",
                      {"ingresso": "prima chiusura oraria del giorno sopra apertura + 0,5 x escursione di ieri, non dopo la barra 22:00", "uscita": "chiusura della barra 23:00", "stop": "2 ATR14", "target": None}, (-0.10, 0.10)),
    "DOGEUSDT-008": m("I-04", "rottura di volatilita' dall'apertura del giorno UTC", "1h", "short",
                      {"ingresso": "prima chiusura oraria del giorno sotto apertura - 0,5 x escursione di ieri, non dopo la barra 22:00", "uscita": "chiusura della barra 23:00", "stop": "2 ATR14", "target": None}, (-0.10, 0.10)),
    "DOGEUSDT-009": m("I-05", "rimbalzo dopo l'ipervenduto in trend (RSI a 2 barre)", "4h", "long",
                      {"ingresso": "close > SMA200 e RSI2 < 10", "uscita": "close > SMA5", "stop": "3 ATR14", "target": None}, (-0.10, 0.10)),
    "DOGEUSDT-010": m("I-05", "ritorno dopo l'ipercomprato in trend ribassista (RSI a 2 barre)", "4h", "short",
                      {"ingresso": "close < SMA200 e RSI2 > 90", "uscita": "close < SMA5", "stop": "3 ATR14", "target": None}, (-0.10, 0.10)),
    "DOGEUSDT-011": m("I-06", "premio del volume alto (visibilita')", "1d", "long",
                      {"ingresso": "volume USDT > 1,5 x media dei 20 giorni prima", "uscita": "a tempo dopo 5 barre", "stop": "2,5 ATR14", "target": None}, (-0.10, 0.15)),
    "DOGEUSDT-012": m("I-06", "sconto del volume basso", "1d", "short",
                      {"ingresso": "volume USDT < 0,6 x media dei 20 giorni prima", "uscita": "a tempo dopo 5 barre", "stop": "2,5 ATR14", "target": None}, (-0.10, 0.15)),
    "DOGEUSDT-013": m("I-07", "domanda da lotteria dopo un salto giornaliero", "1d", "short",
                      {"ingresso": "massimo dei rendimenti giornalieri delle ultime 7 barre >= 10%", "uscita": "a tempo dopo 3 barre", "stop": "2,5 ATR14", "target": None}, (-0.15, 0.10)),
    "DOGEUSDT-014": m("I-07", "assenza di salti: niente premio da lotteria", "1d", "long",
                      {"ingresso": "massimo dei rendimenti giornalieri delle ultime 7 barre < 3%", "uscita": "a tempo dopo 3 barre", "stop": "2,5 ATR14", "target": None}, (-0.15, 0.10)),
    "DOGEUSDT-015": m("I-08", "funding estremo: long a leva affollati", "8h", "short",
                      {"ingresso": "ultimo funding >= 0,0005", "uscita": "a tempo dopo 3 barre", "stop": "2 ATR14", "target": None}, (-0.10, 0.10)),
    "DOGEUSDT-016": m("I-08", "funding negativo: short a leva affollati", "8h", "long",
                      {"ingresso": "ultimo funding < 0", "uscita": "a tempo dopo 3 barre", "stop": "2 ATR14", "target": None}, (-0.10, 0.10)),
    "DOGEUSDT-017": m("I-09", "effetto del lunedi'", "1d", "long",
                      {"ingresso": "segnale alla chiusura della domenica UTC", "uscita": "a tempo dopo 1 barra", "stop": "2 ATR14", "target": None}, (-0.10, 0.10)),
    "DOGEUSDT-018": m("I-10", "uscita dalla strettoia delle bande di Bollinger", "4h", "long",
                      {"ingresso": "ampiezza 4sd/SMA20 <= 20 percentile delle ultime 120 e close > SMA20 + 2sd", "uscita": "a tempo dopo 12 barre", "stop": "2 ATR14", "target": None}, (-0.10, 0.10)),
    "DOGEUSDT-019": m("I-10", "uscita dalla strettoia delle bande di Bollinger", "4h", "short",
                      {"ingresso": "ampiezza 4sd/SMA20 <= 20 percentile delle ultime 120 e close < SMA20 - 2sd", "uscita": "a tempo dopo 12 barre", "stop": "2 ATR14", "target": None}, (-0.10, 0.10)),
    "DOGEUSDT-020": m("I-11", "inversione dopo una barra oraria estrema (fornitura di liquidita')", "1h", "long",
                      {"ingresso": "rendimento della barra < -3 deviazioni standard delle 168 barre prima", "uscita": "a tempo dopo 6 barre", "stop": "2 ATR14", "target": None}, (-0.10, 0.15)),
    "DOGEUSDT-021": m("I-11", "inversione dopo una barra oraria estrema (fornitura di liquidita')", "1h", "short",
                      {"ingresso": "rendimento della barra > +3 deviazioni standard delle 168 barre prima", "uscita": "a tempo dopo 6 barre", "stop": "2 ATR14", "target": None}, (-0.10, 0.15)),
    "DOGEUSDT-022": m("I-12", "inerzia dopo un giorno anomalo", "1d", "long",
                      {"ingresso": "rendimento del giorno > media + 1,5 sd dei 30 giorni prima", "uscita": "a tempo dopo 1 barra", "stop": "2 ATR14", "target": None}, (-0.10, 0.10)),
    "DOGEUSDT-023": m("I-12", "inerzia dopo un giorno anomalo", "1d", "short",
                      {"ingresso": "rendimento del giorno < media - 1,5 sd dei 30 giorni prima", "uscita": "a tempo dopo 1 barra", "stop": "2 ATR14", "target": None}, (-0.10, 0.10)),
    "DOGEUSDT-024": m("I-13", "squilibrio degli ordini aggressivi del giorno", "1d", "long",
                      {"ingresso": "taker_buy_quote_volume / quote_volume del giorno > 0,5", "uscita": "a tempo dopo 1 barra", "stop": "2 ATR14", "target": None}, (-0.10, 0.10)),
    "DOGEUSDT-025": m("I-13", "squilibrio degli ordini aggressivi del giorno", "1d", "short",
                      {"ingresso": "taker_buy_quote_volume / quote_volume del giorno < 0,5", "uscita": "a tempo dopo 1 barra", "stop": "2 ATR14", "target": None}, (-0.10, 0.10)),
    "DOGEUSDT-026": m("I-14", "attraversamento di un numero tondo e ordini stop", "1h", "long",
                      {"ingresso": "close attraversa verso l'alto un multiplo di 0,01", "uscita": "a tempo dopo 6 barre", "stop": "2 ATR14", "target": None}, (-0.10, 0.10)),
    "DOGEUSDT-027": m("I-14", "attraversamento di un numero tondo e ordini stop", "1h", "short",
                      {"ingresso": "close attraversa verso il basso un multiplo di 0,01", "uscita": "a tempo dopo 6 barre", "stop": "2 ATR14", "target": None}, (-0.10, 0.10)),
    "DOGEUSDT-028": m("I-15", "rottura del giorno stretto (NR4)", "1h", "long",
                      {"ingresso": "giorno precedente NR4 e prima chiusura oraria sopra il suo massimo, non dopo la barra 22:00", "uscita": "chiusura della barra 23:00", "stop": "2 ATR14", "target": None}, (-0.10, 0.10)),
    "DOGEUSDT-029": m("I-15", "rottura del giorno stretto (NR4)", "1h", "short",
                      {"ingresso": "giorno precedente NR4 e prima chiusura oraria sotto il suo minimo, non dopo la barra 22:00", "uscita": "chiusura della barra 23:00", "stop": "2 ATR14", "target": None}, (-0.10, 0.10)),
    "DOGEUSDT-030": m("I-16", "incrocio dei movimenti direzionali con trend forte", "4h", "long",
                      {"ingresso": "+DI14 incrocia sopra -DI14 nella barra e ADX14 > 25", "uscita": "-DI > +DI alla chiusura", "stop": "2,5 ATR14", "target": None}, (-0.10, 0.15)),
    "DOGEUSDT-031": m("I-16", "incrocio dei movimenti direzionali con trend forte", "4h", "short",
                      {"ingresso": "-DI14 incrocia sopra +DI14 nella barra e ADX14 > 25", "uscita": "+DI > -DI alla chiusura", "stop": "2,5 ATR14", "target": None}, (-0.10, 0.15)),
}


def _allentata(da, nota, tf=None, **par):
    x = dict(META[da])
    x["parametri"] = {**x["parametri"], **par}
    if tf:
        x["timeframe"] = tf
    x["allentata_da"] = da
    x["nota"] = nota + " (variante dell'idea nuova allentata dopo uno scarto, senza risultati: regola 6)"
    return x


META.update({
    "DOGEUSDT-032": _allentata("DOGEUSDT-005", "canale 20 barre, uscita dopo 12", ingresso="close > massimo degli high delle 20 barre prima", uscita="a tempo dopo 12 barre"),
    "DOGEUSDT-033": _allentata("DOGEUSDT-006", "canale 20 barre, uscita dopo 12", ingresso="close < minimo dei low delle 20 barre prima", uscita="a tempo dopo 12 barre"),
    "DOGEUSDT-034": _allentata("DOGEUSDT-018", "a 1h con gli stessi parametri in barre", tf="1h"),
    "DOGEUSDT-035": _allentata("DOGEUSDT-019", "a 1h con gli stessi parametri in barre", tf="1h"),
    "DOGEUSDT-036": _allentata("DOGEUSDT-022", "soglia 1 deviazione", ingresso="rendimento del giorno > media + 1 sd dei 30 giorni prima"),
    "DOGEUSDT-037": _allentata("DOGEUSDT-023", "soglia 1 deviazione", ingresso="rendimento del giorno < media - 1 sd dei 30 giorni prima"),
    "DOGEUSDT-038": _allentata("DOGEUSDT-030", "a 1h", tf="1h"),
    "DOGEUSDT-039": _allentata("DOGEUSDT-031", "a 1h", tf="1h"),
})


def _ritocco(da, famiglia, cosa, perche, prev, **par):
    x = dict(META[da])
    x.pop("allentata_da", None)
    x.pop("nota", None)
    x["parametri"] = {**x["parametri"], **par}
    x.update({"ritocco_di": da, "famiglia": famiglia, "cosa_cambia": cosa, "perche": perche,
              "previsione": f"R medio dopo i costi fra {prev[0]} e {prev[1]}", "previsione_intervallo": list(prev)})
    return x


META["DOGEUSDT-040"] = _ritocco("DOGEUSDT-035", "DOGEUSDT-035", "uscita a tempo dopo 24 barre invece di 12",
                                "le uscite a tempo hanno R medio +0,54 e i trade migliori arrivano a fine finestra; la fonte dice che l'espansione dopo la strettoia dura",
                                (0.0, 0.20), uscita="a tempo dopo 24 barre")
META["DOGEUSDT-041"] = _ritocco("DOGEUSDT-035", "DOGEUSDT-035", "stop 3 ATR invece di 2",
                                "l'ATR dentro una strettoia e' basso per costruzione: lo stop a 2 ATR e' stretto per l'espansione; 35 stop su 133 trade",
                                (-0.05, 0.15), stop="3 ATR14")
META["DOGEUSDT-042"] = _ritocco("DOGEUSDT-041", "DOGEUSDT-035", "strettoia misurata sulle ultime 480 barre invece di 120",
                                "la fonte chiama strettoia un minimo di ampiezza su un periodo lungo; 120 barre a 1h sono 5 giorni",
                                (-0.05, 0.15), ingresso="ampiezza 4sd/SMA20 <= 20 percentile delle ultime 480 e close < SMA20 - 2sd")
META["DOGEUSDT-043"] = _ritocco("DOGEUSDT-041", "DOGEUSDT-035", "soglia della strettoia al 10 percentile invece del 20",
                                "strettoia piu' estrema, piu' vicina all'ampiezza al minimo della fonte, senza allungare la finestra",
                                (-0.05, 0.15), ingresso="ampiezza 4sd/SMA20 <= 10 percentile delle ultime 120 e close < SMA20 - 2sd")
META["DOGEUSDT-044"] = _ritocco("DOGEUSDT-041", "DOGEUSDT-035", "stop 4 ATR invece di 3",
                                "stesso motivo del ritocco 2 (ATR basso dentro la strettoia), un passo oltre",
                                (-0.05, 0.15), stop="4 ATR14")
