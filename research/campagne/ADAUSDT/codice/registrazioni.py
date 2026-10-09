"""Testi delle registrazioni (regola 2: ipotesi, previsione, parametri, criterio, trade stimati).
Scritti prima di contare i trade; il numero di trade lo aggiunge run.py con conta_trade."""

CRIT = "batte nettamente la (a) e la (b) (contro_baseline) e R medio dopo i costi positivo"

F01 = "Moskowitz, Ooi, Pedersen, «Time Series Momentum», Journal of Financial Economics 104(2), 2012; Liu, Tsyvinski, «Risks and Returns of Cryptocurrency», NBER WP 24877, 2018"
F02 = "Curtis M. Faith, «Way of the Turtle», McGraw-Hill, 2007"
F03 = "Detzel, Liu, Strauss, Zhou, Zhu, «Learning and Predictability via Technical Analysis: Evidence from Bitcoin and Stocks with Hard-to-Value Fundamentals», Financial Management 50(1), 2021 (SSRN 2018); Brock, Lakonishok, LeBaron, «Simple Technical Trading Rules...», Journal of Finance 47(5), 1992"
F04 = "Caporale, Plastun, «Price overreactions in the cryptocurrency market», Journal of Economic Studies 46(5), 2019 (CESifo WP 6861, 2018)"
F05 = "Wen, Bouri, Xu, Zhao, «Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both», North American Journal of Economics and Finance 62, 2022; Gao, Han, Li, Zhou, «Market Intraday Momentum», Journal of Financial Economics 129(2), 2018"
F06 = "Lo, MacKinlay, «When Are Contrarian Profits Due to Stock Market Overreaction?», Review of Financial Studies 3(2), 1990; Mohamad, Sifat, Shariff, «Lead-lag relationship between Bitcoin and Ethereum: Evidence from hourly and daily data», Research in International Business and Finance 50, 2019"
F07 = "He, Manela, Ross, von Wachter, «Fundamentals of Perpetual Futures», arXiv 2212.06888, dicembre 2022"
F08 = "John Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001"
F09 = "Larry Connors, Cesar Alvarez, «Short Term Trading Strategies That Work», TradingMarkets, 2009"
F10 = "Gervais, Kaniel, Mingelgrin, «The High-Volume Return Premium», Journal of Finance 56(3), 2001"
F11 = "Carol L. Osler, «Currency Orders and Exchange Rate Dynamics: An Explanation for the Predictive Success of Technical Analysis», Journal of Finance 58(5), 2003"
F12 = "Avellaneda, Lee, «Statistical arbitrage in the U.S. equities market», Quantitative Finance 10(7), 2010"
F13 = "Toby Crabel, «Day Trading with Short Term Price Patterns and Opening Range Breakout», Traders Press, 1990"

F14 = "Chordia, Subrahmanyam, «Order imbalance and individual stock returns: Theory and evidence», Journal of Financial Economics 72(3), 2004"
F15 = "Stefan Nagel, «Evaporating Liquidity», Review of Financial Studies 25(7), 2012 (NBER WP 17653, 2011); Lehmann, «Fads, Martingales, and Market Efficiency», Quarterly Journal of Economics 105(1), 1990"


def r(idea, fonte, mecc, regole, prev, **k):
    d = {"idea": idea, "fonte": fonte, "meccanismo": mecc, "regole": regole, "previsione": prev,
         "criterio_successo": CRIT}
    d.update(k)
    return d


REG = {
    "ADAUSDT-001": r("I-01", F01, "sotto-reazione e attenzione: il rendimento della settimana passata continua",
                     "4h long: ingresso se rendimento 42 barre > 0; uscita dopo 42 barre; stop 3 ATR(14)",
                     "R medio dopo i costi fra -0,05 e +0,10; t contro la (b) fra -1 e +1,5 (la (b) long cattura gran parte del trend 2021); non netta. Costo di un giro ~0,015 R piu' funding dei long"),
    "ADAUSDT-002": r("I-01", F01, "sotto-reazione al ribasso: la settimana negativa continua",
                     "4h short: ingresso se rendimento 42 barre < 0; uscita dopo 42 barre; stop 3 ATR(14)",
                     "R medio fra -0,10 e +0,05; t contro la (b) fra -1 e +1,5; non netta"),
    "ADAUSDT-003": r("I-02", F02, "ordini oltre i massimi recenti: la rottura del massimo di 20 barre prosegue",
                     "4h long: chiusura > massimo delle 20 barre precedenti; uscita chiusura < minimo delle 10 precedenti; stop 2 ATR(14)",
                     "R medio fra -0,10 e +0,10, R asimmetrico (molti piccoli stop, pochi guadagni grandi); t contro la (b) fra -1 e +1,5; non netta"),
    "ADAUSDT-004": r("I-02", F02, "ordini oltre i minimi recenti: la rottura del minimo di 20 barre prosegue",
                     "4h short: chiusura < minimo delle 20 barre precedenti; uscita chiusura > massimo delle 10 precedenti; stop 2 ATR(14)",
                     "R medio fra -0,15 e +0,05; t contro la (b) fra -1 e +1; non netta"),
    "ADAUSDT-005": r("I-03", F03, "apprendimento dal prezzo: il passaggio sopra la media a 20 giorni predice rialzi",
                     "1d long: chiusura passa sopra la media semplice 20 (precedente sotto o uguale); uscita alla prima chiusura sotto la media; stop 3 ATR(14)",
                     "probabile scarto per trade minimi (incroci giornalieri poche decine); se testata: R medio fra -0,05 e +0,15, non netta"),
    "ADAUSDT-006": r("I-04", F04, "inerzia dopo una reazione eccessiva al rialzo",
                     "1d long: chiusura/apertura-1 > media+1 dev. std dei rendimenti assoluti dei 30 giorni precedenti; uscita dopo 1 barra; stop 2 ATR(14)",
                     "R medio fra -0,10 e +0,10; t contro la (b) fra -1 e +1 (la fonte stessa non distingue la strategia dal caso); non netta"),
    "ADAUSDT-007": r("I-04", F04, "inerzia dopo una reazione eccessiva al ribasso",
                     "1d short: chiusura/apertura-1 < -(media+1 dev. std); uscita dopo 1 barra; stop 2 ATR(14)",
                     "R medio fra -0,10 e +0,10; non netta"),
    "ADAUSDT-008": r("I-05", F05, "momento infragiornaliero: prima mezz'ora positiva, ultima mezz'ora positiva",
                     "30m long: alla chiusura della barra delle 23:00, se la barra 00:00-00:30 dello stesso giorno ha chiusura>apertura; uscita dopo 1 barra; stop 1,5 ATR(48)",
                     "R lordo vicino a 0, R dopo i costi fra -0,12 e -0,02 (costo di un giro ~0,09 R); non netta"),
    "ADAUSDT-009": r("I-05", F05, "momento infragiornaliero: prima mezz'ora negativa, ultima mezz'ora negativa",
                     "30m short: come 008 con la prima mezz'ora negativa",
                     "R dopo i costi fra -0,12 e -0,02; non netta"),
    "ADAUSDT-010": r("I-06", F06, "ritardo di ADA dopo un'ora forte di BTC al rialzo",
                     "1h long: rendimento orario BTC > 1,5 dev. std delle 168 ore e rendimento ADA < BTC; uscita dopo 3 barre; stop 2 ATR(14)",
                     "R medio fra -0,08 e +0,05 (il riallineamento probabilmente avviene entro l'ora); t contro la (b) fra -1 e +1,5; non netta"),
    "ADAUSDT-011": r("I-06", F06, "ritardo di ADA dopo un'ora forte di BTC al ribasso",
                     "1h short: rendimento orario BTC < -1,5 dev. std e rendimento ADA > BTC; uscita dopo 3 barre; stop 2 ATR(14)",
                     "R medio fra -0,08 e +0,05; non netta"),
    "ADAUSDT-012": r("I-07", F07, "long affollati che pagano funding alto: il prezzo scende",
                     "8h short: ultimo funding entro la chiusura > 0,0003 e >= 90° percentile dei 90 precedenti; uscita dopo 3 barre; stop 2,5 ATR(14)",
                     "R medio fra -0,10 e +0,10 (funding alto segue i rialzi, che spesso continuano); se trade sotto 70, scarto; non netta"),
    "ADAUSDT-013": r("I-07", F07, "short affollati che pagano funding negativo: il prezzo sale",
                     "8h long: ultimo funding < 0 e <= 10° percentile dei 90 precedenti; uscita dopo 3 barre; stop 2,5 ATR(14)",
                     "R medio fra -0,05 e +0,15; probabile scarto per trade (funding negativo raro prima del 2022); non netta"),
    "ADAUSDT-014": r("I-08", F08, "dopo la compressione la rottura della banda alta prosegue",
                     "4h long: compressione (ampiezza <= minimo 120 barre) in una delle ultime 6 barre e chiusura > banda alta (20, 2); uscita chiusura < media 20; stop 2 ATR(14)",
                     "R medio fra -0,10 e +0,15; probabile vicino al minimo di trade; non netta"),
    "ADAUSDT-015": r("I-08", F08, "dopo la compressione la rottura della banda bassa prosegue",
                     "4h short: compressione e chiusura < banda bassa; uscita chiusura > media 20; stop 2 ATR(14)",
                     "R medio fra -0,10 e +0,10; non netta"),
    "ADAUSDT-016": r("I-09", F09, "liquidita' fornita nei ritracciamenti brevi dentro una tendenza al rialzo",
                     "1d long: chiusura > media 200 e RSI(2) < 5; uscita chiusura > media 5; stop 3 ATR(14)",
                     "quasi certamente scarto per trade minimi (riscaldamento di 200 giorni); se testata R medio fra -0,05 e +0,15"),
    "ADAUSDT-017": r("I-09", F09, "liquidita' fornita nei ritracciamenti brevi dentro una tendenza al rialzo",
                     "4h long: chiusura > media 200 e RSI(2) < 5; uscita chiusura > media 5; stop 3 ATR(14)",
                     "R medio fra -0,05 e +0,10, molti piccoli guadagni e rare perdite grandi; t contro la (b) fra 0 e +2; non netta"),
    "ADAUSDT-018": r("I-10", F10, "visibilita' dopo un volume insolito senza grande movimento",
                     "1d long: volume USDT > 90° percentile dei 50 giorni precedenti e |rendimento| < 1 dev. std dei 30 giorni; uscita dopo 5 barre; stop 3 ATR(14)",
                     "probabile scarto per trade; se testata R medio fra -0,10 e +0,15, non netta"),
    "ADAUSDT-019": r("I-10", F10, "visibilita' dopo un volume insolito senza grande movimento",
                     "4h long: volume USDT > 90° percentile delle 300 barre precedenti e |rendimento| < 1 dev. std delle 180; uscita dopo 30 barre; stop 3 ATR(14)",
                     "R medio fra -0,10 e +0,10; t contro la (b) fra -1 e +1; non netta"),
    "ADAUSDT-020": r("I-11", F11, "stop ammassati oltre i numeri tondi: dopo l'attraversamento al rialzo il movimento accelera",
                     "1h long: attraversamento al rialzo di un livello tondo (passo 0,5 x 10^floor(log10 p)); uscita dopo 12 barre; stop 1,5 ATR(14)",
                     "R medio dopo i costi fra -0,10 e +0,03 (costo ~0,06 R); non netta"),
    "ADAUSDT-021": r("I-11", F11, "stop ammassati sotto i numeri tondi: dopo l'attraversamento al ribasso il movimento accelera",
                     "1h short: attraversamento al ribasso; uscita dopo 12 barre; stop 1,5 ATR(14)",
                     "R medio dopo i costi fra -0,10 e +0,03; non netta"),
    "ADAUSDT-022": r("I-12", F12, "il residuo di ADA rispetto a BTC torna verso zero (ADA rimasta indietro recupera)",
                     "1h long: s-score del residuo cumulato 24h (beta 720h) < -2; uscita s > -0,5 o dopo 24 barre; stop 2 ATR(14)",
                     "R medio fra -0,10 e +0,05 (senza copertura il movimento di BTC domina); non netta"),
    "ADAUSDT-023": r("I-12", F12, "il residuo di ADA rispetto a BTC torna verso zero (ADA andata avanti ripiega)",
                     "1h short: s-score > 2; uscita s < 0,5 o dopo 24 barre; stop 2 ATR(14)",
                     "R medio fra -0,10 e +0,05; non netta"),
    "ADAUSDT-024": r("I-13", F13, "la rottura del massimo della prima ora UTC prosegue nella giornata",
                     "15m long: chiusura passa sopra il massimo delle barre 00:00-01:00, barra prima delle 20:00; stop al minimo della prima ora; uscita a fine giornata",
                     "R medio dopo i costi fra -0,10 e +0,05; non netta"),
    "ADAUSDT-026": r("I-14", F14, "squilibrio persistente degli acquisti aggressivi: il prezzo continua a salire",
                     "1h long: squilibrio taker 24 barre > 90° percentile delle 720 precedenti; uscita dopo 24 barre; stop 2 ATR(14)",
                     "R medio fra -0,10 e +0,05; t contro la (b) fra -1,5 e +1; non netta"),
    "ADAUSDT-027": r("I-14", F14, "squilibrio persistente delle vendite aggressive: il prezzo continua a scendere",
                     "1h short: squilibrio taker 24 barre < 10° percentile delle 720 precedenti; uscita dopo 24 barre; stop 2 ATR(14)",
                     "R medio fra -0,10 e +0,05; non netta"),
    "ADAUSDT-028": r("I-15", F15, "premio per la liquidita' dopo un calo eccessivo di 24 ore",
                     "4h long: rendimento 6 barre < -2 dev. std dei rendimenti a 6 barre delle 360 precedenti; uscita dopo 6 barre; stop 3 ATR(14)",
                     "R medio fra -0,10 e +0,15, varianza alta; t contro la (b) fra -1 e +1,5; non netta"),
    "ADAUSDT-029": r("I-15", F15, "premio per la liquidita' dopo un rialzo eccessivo di 24 ore",
                     "4h short: rendimento 6 barre > +2 dev. std; uscita dopo 6 barre; stop 3 ATR(14)",
                     "R medio fra -0,15 e +0,10; non netta"),
    "ADAUSDT-030": r("I-04", F04, "inerzia dopo una reazione eccessiva al rialzo (soglia allentata)",
                     "1d long: chiusura/apertura-1 > media+0,5 dev. std dei rendimenti assoluti dei 30 giorni precedenti; uscita dopo 1 barra; stop 2 ATR(14)",
                     "R medio fra -0,10 e +0,10; non netta"),
    "ADAUSDT-031": r("I-04", F04, "inerzia dopo una reazione eccessiva al ribasso (soglia allentata)",
                     "1d short: chiusura/apertura-1 < -(media+0,5 dev. std); uscita dopo 1 barra; stop 2 ATR(14)",
                     "R medio fra -0,10 e +0,10; non netta"),
    "ADAUSDT-032": r("I-08", F08, "dopo la compressione (minimo di 60 barre) la rottura della banda alta prosegue",
                     "4h long: compressione (ampiezza <= minimo 60 barre) in una delle ultime 6 barre e chiusura > banda alta (20, 2); uscita chiusura < media 20; stop 2 ATR(14)",
                     "R medio fra -0,10 e +0,15; non netta"),
    "ADAUSDT-033": r("I-08", F08, "dopo la compressione (minimo di 60 barre) la rottura della banda bassa prosegue",
                     "4h short: compressione (60 barre) e chiusura < banda bassa; uscita chiusura > media 20; stop 2 ATR(14)",
                     "R medio fra -0,10 e +0,10; non netta"),
    "ADAUSDT-025": r("I-13", F13, "la rottura del minimo della prima ora UTC prosegue nella giornata",
                     "15m short: chiusura passa sotto il minimo della prima ora, prima delle 20:00; stop al massimo della prima ora; uscita a fine giornata",
                     "R medio dopo i costi fra -0,10 e +0,05; non netta"),
}
