"""Le schede di registrazione delle varianti di ipotesi.md, scritte PRIMA dei conteggi.

Per ogni variante: idea, fonte, meccanismo, previsione (testo e intervallo numerico
dell'R medio dopo i costi) e se si prevede che batta nettamente la (b). La
previsione e' quella di ipotesi.md, copiata qui perche' registra.py la scriva nel log.
"""

CRITERIO = ("batte nettamente la (a) e la (b) con contro_baseline sul periodo di costruzione "
            "e R medio dopo i costi positivo (sezione 8, Fase 2)")

F_LIU = "Yukun Liu e Aleh Tsyvinski, «Risks and Returns of Cryptocurrency», Review of Financial Studies 34(6), 2021 (NBER WP 24877, 2018)"
F_FAITH = "Curtis M. Faith, «Way of the Turtle», McGraw-Hill, 2007"
F_BROCK = "William Brock, Josef Lakonishok, Blake LeBaron, «Simple Technical Trading Rules and the Stochastic Properties of Stock Returns», Journal of Finance 47(5), 1992"
F_CONNORS = "Larry Connors e Cesar Alvarez, «Short Term Trading Strategies That Work», TradingMarkets Publishing, 2009"
F_CRABEL = "Toby Crabel, «Day Trading with Short Term Price Patterns and Opening Range Breakout», Traders Press, 1990"
F_SHEN = "Dehua Shen, Andrew Urquhart, Pengfei Wang, «Bitcoin intraday time-series momentum», The Financial Review 57(2), 2022 (online 26 ottobre 2021)"
F_LO = "Andrew W. Lo e A. Craig MacKinlay, «When Are Contrarian Profits Due to Stock Market Overreaction?», Review of Financial Studies 3(2), 1990"
F_CARRY = "Maik Schmeling, Andreas Schrimpf, Karamfil Todorov, «Crypto carry», BIS Working Papers 1087, aprile 2023"
F_LUNEDI = "Guglielmo Maria Caporale e Alex Plastun, «The day of the week effect in the cryptocurrency market», Finance Research Letters 31, 2019"
F_ANOMALO = "Guglielmo Maria Caporale e Alex Plastun, «Price overreactions in the cryptocurrency market», Journal of Economic Studies 46(5), 2019"
F_OSLER03 = "Carol L. Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation for the Predictive Success of Technical Analysis», Journal of Finance 58(5), 2003"
F_GERVAIS = "Simon Gervais, Ron Kaniel, Dan H. Mingelgrin, «The High-Volume Return Premium», Journal of Finance 56(3), 2001"
F_BP = "Markus K. Brunnermeier e Lasse Heje Pedersen, «Market Liquidity and Funding Liquidity», Review of Financial Studies 22(6), 2009"
F_OSLER00 = "Carol L. Osler, «Support for Resistance: Technical Analysis and Intraday Exchange Rates», FRBNY Economic Policy Review 6(2), luglio 2000"
F_CHORDIA = "Tarun Chordia e Avanidhar Subrahmanyam, «Order imbalance and individual stock returns: Theory and evidence», Journal of Financial Economics 72(3), 2004"
F_HESTON = "Steven L. Heston, Robert A. Korajczyk, Ronnie Sadka, «Intraday Patterns in the Cross-Section of Stock Returns», Journal of Finance 65(4), 2010"
F_WILLIAMS = "Larry Williams, «Long-Term Secrets to Short-Term Trading», John Wiley & Sons, 1999"


def _s(idea, fonte, meccanismo, regole, r_min, r_max, netta_b=False):
    return {"idea": idea, "fonte": fonte, "meccanismo": meccanismo, "regole": regole,
            "previsione": {"r_medio_min": r_min, "r_medio_max": r_max, "batte_nettamente_b": netta_b,
                           "testo": f"R medio dopo i costi fra {r_min:+.2f} e {r_max:+.2f}; "
                                    + ("batte" if netta_b else "non batte") + " nettamente la (b)"}}


SCHEDE = {
    "I-01a": _s("I-01", F_LIU, "momentum di una settimana (attenzione degli investitori)",
                "1d long: chiusura/chiusura di 7 barre prima - 1 > 0; esce dopo 7 barre; stop al 6%", -0.05, 0.20),
    "I-01b": _s("I-01", F_LIU, "momentum di una settimana (attenzione degli investitori)",
                "1d short: rendimento di 7 barre < 0; esce dopo 7 barre; stop al 6%", -0.25, 0.05),
    "I-02a": _s("I-02", F_FAITH, "rottura del canale di Donchian, Sistema 1 in barre",
                "4h long: chiusura > massimo delle 20 barre precedenti; esce con chiusura < minimo delle 10 precedenti; stop a 2 ATR(20) al massimo 6%", -0.05, 0.15),
    "I-02b": _s("I-02", F_FAITH, "rottura del canale di Donchian, Sistema 1 in barre",
                "4h short: chiusura < minimo delle 20 barre precedenti; esce con chiusura > massimo delle 10 precedenti; stop a 2 ATR(20) al massimo 6%", -0.15, 0.10),
    "I-03a": _s("I-03", F_BROCK, "prezzo sopra la media mobile di 50 giorni (aggiustamento lento)",
                "1d long: chiusura > media di 50 chiusure; esce con chiusura < media; stop al 6%", -0.10, 0.30),
    "I-03b": _s("I-03", F_BROCK, "prezzo sotto la media mobile di 50 giorni",
                "1d short: chiusura < media di 50; esce con chiusura > media; stop al 6%", -0.30, 0.10),
    "I-04a": _s("I-04", F_CONNORS, "eccesso di breve contro il trend lungo (premio di liquidita')",
                "4h long: chiusura > media di 200 e RSI(2) < 10; esce con chiusura > media di 5; stop a 3 ATR(14) al massimo 6%", -0.05, 0.15),
    "I-04b": _s("I-04", F_CONNORS, "eccesso di breve contro il trend lungo (premio di liquidita')",
                "4h short: chiusura < media di 200 e RSI(2) > 90; esce con chiusura < media di 5; stop a 3 ATR(14) al massimo 6%", -0.15, 0.10),
    "I-05a": _s("I-05", F_CRABEL, "rottura dopo la contrazione dell'escursione (NR7)",
                "4h long: barra precedente NR7 e chiusura > suo massimo; stop sul suo minimo al massimo 6%; esce dopo 6 barre", -0.10, 0.10),
    "I-05b": _s("I-05", F_CRABEL, "rottura dopo la contrazione dell'escursione (NR7)",
                "4h short: barra precedente NR7 e chiusura < suo minimo; stop sul suo massimo al massimo 6%; esce dopo 6 barre", -0.10, 0.10),
    "I-06a": _s("I-06", F_SHEN, "momentum intragiornaliero: la prima mezz'ora prevede l'ultima",
                "30m long: alla chiusura della barra 23:00 UTC, se la barra 00:00 del giorno ha chiusura > apertura; esce dopo 1 barra; stop a 2 ATR(14) al massimo 6%", -0.15, 0.00),
    "I-06b": _s("I-06", F_SHEN, "momentum intragiornaliero: la prima mezz'ora prevede l'ultima",
                "30m short: come I-06a con la barra 00:00 in discesa", -0.15, 0.00),
    "I-07a": _s("I-07", F_LO, "il grande (BTC) anticipa il piccolo (ETH)",
                "1h long: BTC sale oltre l'1% nella barra ed ETH sale meno della meta'; esce dopo 2 barre; stop a 2 ATR(14) al massimo 6%", -0.10, 0.10),
    "I-07b": _s("I-07", F_LO, "il grande (BTC) anticipa il piccolo (ETH)",
                "1h short: BTC scende oltre l'1% ed ETH scende meno della meta'; esce dopo 2 barre; stop a 2 ATR(14) al massimo 6%", -0.10, 0.10),
    "I-08a": _s("I-08", F_CARRY, "leva affollata misurata dal funding: funding alto, poi crolli",
                "8h short: ultimo settlement >= 0,05%; esce dopo 9 barre; stop a 2 ATR(14) al massimo 6%", -0.20, 0.15),
    "I-08b": _s("I-08", F_CARRY, "leva affollata misurata dal funding: funding negativo, poi rimbalzo",
                "8h long: ultimo settlement < 0; esce dopo 9 barre; stop a 2 ATR(14) al massimo 6%", -0.15, 0.15),
    "I-09a": _s("I-09", F_LUNEDI, "effetto del lunedi'",
                "1d long: si entra all'apertura del lunedi' UTC; esce dopo 1 barra; stop al 6%", -0.10, 0.15),
    "I-10a": _s("I-10", F_ANOMALO, "continuazione dopo un giorno anomalo positivo",
                "1d long: rendimento del giorno > 0 e > media + 1 deviazione standard dei 30 giorni prima; esce dopo 1 barra; stop al 6%", -0.10, 0.15),
    "I-10b": _s("I-10", F_ANOMALO, "continuazione dopo un giorno anomalo negativo",
                "1d short: rendimento < 0 e < media - 1 deviazione standard; esce dopo 1 barra; stop al 6%", -0.15, 0.10),
    "I-11a": _s("I-11", F_OSLER03, "stop ammassati oltre i numeri tondi: passaggio verso l'alto",
                "1h long: chiusura che passa un livello tondo verso l'alto (multipli di 10 sotto 1000, di 100 sopra); esce dopo 4 barre; stop a 1,5 ATR(14) al massimo 6%", -0.10, 0.10),
    "I-11b": _s("I-11", F_OSLER03, "stop ammassati oltre i numeri tondi: passaggio verso il basso",
                "1h short: chiusura che passa un livello tondo verso il basso; esce dopo 4 barre; stop a 1,5 ATR(14) al massimo 6%", -0.10, 0.10),
    "I-12a": _s("I-12", F_GERVAIS, "volume insolitamente alto: visibilita' e domanda",
                "1d long: volume del giorno (volume x chiusura) fra i 5 piu' alti dei 50 giorni; esce dopo 10 barre; stop al 6%", -0.20, 0.20),
    "I-12b": _s("I-12", F_GERVAIS, "volume insolitamente basso: meno visibilita'",
                "1d short: volume fra i 5 piu' bassi dei 50 giorni; esce dopo 10 barre; stop al 6%", -0.20, 0.15),
    "I-13a": _s("I-13", F_BP, "vendite forzate e ritorno della liquidita'",
                "1h long: chiusura - apertura < -2 ATR(24) precedente e volume > 3 volte la media di 24 barre; esce dopo 6 barre; stop al minimo meno 0,5 ATR al massimo 6%", -0.10, 0.20),
    "I-13b": _s("I-13", F_BP, "acquisti forzati (chiusura degli short) e ritorno",
                "1h short: chiusura - apertura > +2 ATR(24) e volume > 3 volte la media; esce dopo 6 barre; stop al massimo piu' 0,5 ATR al massimo 6%", -0.15, 0.10),
    "I-14a": _s("I-14", F_OSLER00, "resistenza al massimo del giorno prima",
                "1h short: massimo della barra > massimo del giorno UTC prima e chiusura sotto; stop al massimo della barra piu' 0,25 ATR al massimo 6%; esce dopo 6 barre", -0.15, 0.10),
    "I-14b": _s("I-14", F_OSLER00, "supporto al minimo del giorno prima",
                "1h long: minimo della barra < minimo del giorno UTC prima e chiusura sopra; stop al minimo della barra meno 0,25 ATR al massimo 6%; esce dopo 6 barre", -0.10, 0.15),
    "I-15a": _s("I-15", F_CHORDIA, "squilibrio degli ordini: piu' acquisti a mercato, poi rialzo il giorno dopo",
                "1d long: quota taker buy / volume del giorno > media dei 30 giorni precedenti; esce dopo 1 barra; stop al 6%", -0.10, 0.10),
    "I-15b": _s("I-15", F_CHORDIA, "squilibrio degli ordini: piu' vendite a mercato, poi ribasso il giorno dopo",
                "1d short: quota taker buy < media dei 30 giorni precedenti; esce dopo 1 barra; stop al 6%", -0.10, 0.10),
    "I-16a": _s("I-16", F_HESTON, "periodicita' intragiornaliera: l'ora migliore dei 20 giorni passati",
                "1h long: la prossima ora e' quella con la media piu' alta degli ultimi 20 rendimenti di ogni ora, se > 0; esce dopo 1 barra; stop a 2 ATR(14) al massimo 6%", -0.12, 0.00),
    "I-16b": _s("I-16", F_HESTON, "periodicita' intragiornaliera: l'ora peggiore dei 20 giorni passati",
                "1h short: la prossima ora e' quella con la media piu' bassa, se < 0; esce dopo 1 barra; stop a 2 ATR(14) al massimo 6%", -0.12, 0.00),
    "I-17a": _s("I-17", F_WILLIAMS, "rottura di volatilita' verso l'alto dall'apertura del giorno",
                "1h long: prima barra del giorno (apertura 00-22 UTC) con chiusura > apertura del giorno + 0,5 x escursione di ieri; esce alla chiusura della barra delle 23; stop all'apertura del giorno al massimo 6%", -0.10, 0.15),
    "I-17b": _s("I-17", F_WILLIAMS, "rottura di volatilita' verso il basso dall'apertura del giorno",
                "1h short: prima barra del giorno con chiusura < apertura del giorno - 0,5 x escursione di ieri; esce alla chiusura della barra delle 23; stop all'apertura del giorno al massimo 6%", -0.15, 0.10),
}
