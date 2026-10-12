"""Catalogo delle varianti di GALAUSDT: regole, fonte, previsione (ipotesi.md).

Ogni voce si scrive PRIMA della registrazione nel log e non si modifica dopo il test: un
cambiamento e' una variante nuova (ritocco) con il suo id.
"""

from __future__ import annotations

from research.campagne.GALAUSDT.codice import varianti as V

F_MOP = ("Moskowitz, Ooi, Pedersen, 'Time series momentum', Journal of Financial Economics 104(2), 2012; "
         "Liu, Tsyvinski, 'Risks and Returns of Cryptocurrency', NBER Working Paper 24877, 2018")
F_TURTLE = "Curtis M. Faith, 'Way of the Turtle', McGraw-Hill, 2007"
F_CONNORS = "Larry Connors, Cesar Alvarez, 'Short Term Trading Strategies That Work', TradingMarkets Publishing, 2008"
F_OSLER = ("Carol L. Osler, 'Stop-loss orders and price cascades in currency markets', "
           "Journal of International Money and Finance 24(2), 2005")
F_CARRY = "Maik Schmeling, Andreas Schrimpf, Karamfil Todorov, 'Crypto carry', BIS Working Papers 1087, aprile 2023"
F_LOMAC = ("Andrew W. Lo, A. Craig MacKinlay, 'When are contrarian profits due to stock market overreaction?', "
           "Review of Financial Studies 3(2), 1990")
F_CRABEL = ("Toby Crabel, 'Day Trading with Short Term Price Patterns and Opening Range Breakout', "
            "Traders Press, 1990")
F_LLORENTE = ("Llorente, Michaely, Saar, Wang, 'Dynamic Volume-Return Relation of Individual Stocks', "
              "Review of Financial Studies 15(4), 2002")
F_WILLIAMS = "Larry Williams, 'Long-Term Secrets to Short-Term Trading', Wiley, 1999"
F_DOW = ("Guglielmo Maria Caporale, Alex Plastun, 'The day of the week effect in the cryptocurrency market', "
         "Finance Research Letters 31, 2019")
F_GATEV = ("Gatev, Goetzmann, Rouwenhorst, 'Pairs Trading: Performance of a Relative-Value Arbitrage Rule', "
           "Review of Financial Studies 19(3), 2006")
F_OVER = ("Guglielmo Maria Caporale, Alex Plastun, 'Price overreactions in the cryptocurrency market', "
          "Journal of Economic Studies 46(5), 2019")
F_PUMP = ("Josh Kamps, Bennett Kleinberg, 'To the moon: defining and detecting cryptocurrency pump-and-dumps', "
          "Crime Science 7, 2018")


F_HKS = ("Steven L. Heston, Robert A. Korajczyk, Ronnie Sadka, 'Intraday Patterns in the Cross-Section of "
         "Stock Returns', Journal of Finance 65(4), 2010")
F_PERP = ("Songrun He, Asaf Manela, Omri Ross, Victor von Wachter, 'Fundamentals of Perpetual Futures', "
          "arXiv 2212.06888, dicembre 2022")
F_OSLER03 = ("Carol L. Osler, 'Currency Orders and Exchange Rate Dynamics: An Explanation for the Predictive "
             "Success of Technical Analysis', Journal of Finance 58(5), 2003")
F_GAO = "Lei Gao, Yufeng Han, Sophia Zhenzhen Li, Guofu Zhou, 'Market intraday momentum', Journal of Financial Economics 129(2), 2018"


def _prev(lo, hi, testo=""):
    return {"r_medio_min": lo, "r_medio_max": hi,
            "testo": testo or f"R medio dopo i costi fra {lo} e {hi}; t contro la (b) sotto la soglia"}


CATALOGO = {
    # ---- controllo positivo (nota, non variante) ----
    "CONTROLLO-1": {"classe": V.ControlloLookahead, "tf": "1h", "direzione": "long", "parametri": {},
                    "idea": "controllo", "fonte": "lezioni/metodo.md", "meccanismo": "lookahead dichiarato",
                    "regole": "long se la barra SUCCESSIVA chiude sopra la sua apertura; stop 2 ATR(14) max 6%; uscita dopo 1 barra",
                    "previsione": _prev(0.1, 5.0, "batte nettamente la (b); col ritardo di una barra crolla")},
    # ---- I-01 ----
    "GALAUSDT-001": {"classe": V.MomentumSerie, "tf": "4h", "direzione": "long", "parametri": {},
                     "idea": "I-01", "fonte": F_MOP,
                     "meccanismo": "sotto-reazione e inseguimento della tendenza: il rendimento di 7 giorni che diventa positivo continua",
                     "regole": "4h; ingresso quando il rendimento delle ultime 42 barre passa da <=0 a >0; uscita quando torna <=0; stop 2 ATR(14) max 6%; nessun target",
                     "previsione": _prev(-0.20, 0.10)},
    "GALAUSDT-002": {"classe": V.MomentumSerie, "tf": "4h", "direzione": "short", "parametri": {},
                     "idea": "I-01", "fonte": F_MOP,
                     "meccanismo": "sotto-reazione e inseguimento della tendenza: il rendimento di 7 giorni che diventa negativo continua",
                     "regole": "4h; ingresso quando il rendimento delle ultime 42 barre passa da >=0 a <0; uscita quando torna >=0; stop 2 ATR(14) max 6%; nessun target",
                     "previsione": _prev(-0.20, 0.10)},
    # ---- I-02 ----
    "GALAUSDT-003": {"classe": V.Donchian, "tf": "4h", "direzione": "long", "parametri": {},
                     "idea": "I-02", "fonte": F_TURTLE,
                     "meccanismo": "rottura del massimo di 20 barre: ordini in rottura e stop oltre il massimo spingono il prezzo",
                     "regole": "4h; ingresso alla chiusura sopra il massimo delle 20 barre precedenti; uscita alla chiusura sotto il minimo delle 10 barre precedenti; stop 2 ATR(20) max 6%; nessun target",
                     "previsione": _prev(-0.20, 0.15)},
    "GALAUSDT-004": {"classe": V.Donchian, "tf": "4h", "direzione": "short", "parametri": {},
                     "idea": "I-02", "fonte": F_TURTLE,
                     "meccanismo": "rottura del minimo di 20 barre: ordini in rottura e stop sotto il minimo spingono il prezzo",
                     "regole": "4h; ingresso alla chiusura sotto il minimo delle 20 barre precedenti; uscita alla chiusura sopra il massimo delle 10 barre precedenti; stop 2 ATR(20) max 6%; nessun target",
                     "previsione": _prev(-0.20, 0.15)},
    # ---- I-03 ----
    "GALAUSDT-005": {"classe": V.ConnorsRSI2, "tf": "4h", "direzione": "long", "parametri": {},
                     "idea": "I-03", "fonte": F_CONNORS,
                     "meccanismo": "eccesso di breve contro la tendenza (domanda di liquidita' in fretta) che rientra",
                     "regole": "4h; close > media semplice 200 barre e RSI(2) < 10; uscita alla chiusura sopra la media semplice a 5 barre; stop 3 ATR(14) max 6%; nessun target",
                     "previsione": _prev(-0.15, 0.15)},
    "GALAUSDT-006": {"classe": V.ConnorsRSI2, "tf": "4h", "direzione": "short", "parametri": {},
                     "idea": "I-03", "fonte": F_CONNORS,
                     "meccanismo": "eccesso di breve contro la tendenza (rimbalzo dentro il ribasso) che rientra",
                     "regole": "4h; close < media semplice 200 barre e RSI(2) > 90; uscita alla chiusura sotto la media semplice a 5 barre; stop 3 ATR(14) max 6%; nessun target",
                     "previsione": _prev(-0.15, 0.15)},
    # ---- I-04 ----
    "GALAUSDT-007": {"classe": V.FalsaRottura, "tf": "1h", "direzione": "long", "parametri": {},
                     "idea": "I-04", "fonte": F_OSLER,
                     "meccanismo": "spazzata degli stop sotto il minimo di 2 giorni senza altri venditori: rientro",
                     "regole": "1h; minimo della barra sotto il minimo delle 48 barre precedenti e close sopra quel minimo; stop al minimo della barra meno 0,5 ATR(24) (max 6%); target 2 R; uscita dopo 24 barre",
                     "previsione": _prev(-0.20, 0.10)},
    "GALAUSDT-008": {"classe": V.FalsaRottura, "tf": "1h", "direzione": "short", "parametri": {},
                     "idea": "I-04", "fonte": F_OSLER,
                     "meccanismo": "spazzata degli stop sopra il massimo di 2 giorni senza altri compratori: rientro",
                     "regole": "1h; massimo della barra sopra il massimo delle 48 barre precedenti e close sotto quel massimo; stop al massimo della barra piu' 0,5 ATR(24) (max 6%); target 2 R; uscita dopo 24 barre",
                     "previsione": _prev(-0.20, 0.10)},
    # ---- I-05 ----
    "GALAUSDT-009": {"classe": V.FundingEstremo, "tf": "8h", "direzione": "short", "parametri": {},
                     "idea": "I-05", "fonte": F_CARRY,
                     "meccanismo": "funding alto = long a leva affollati: il prezzo poi scende",
                     "regole": "8h; ultimo funding regolato > 85o percentile dei 90 regolamenti precedenti e > 0; uscita dopo 3 barre; stop 2 ATR(14) max 6%",
                     "previsione": _prev(-0.15, 0.10)},
    "GALAUSDT-010": {"classe": V.FundingEstremo, "tf": "8h", "direzione": "long", "parametri": {},
                     "idea": "I-05", "fonte": F_CARRY,
                     "meccanismo": "funding molto negativo = short a leva affollati: il prezzo poi sale",
                     "regole": "8h; ultimo funding regolato < 15o percentile dei 90 regolamenti precedenti e < 0; uscita dopo 3 barre; stop 2 ATR(14) max 6%",
                     "previsione": _prev(-0.15, 0.10)},
    # ---- I-06 ----
    "GALAUSDT-011": {"classe": V.RitardoBTC, "tf": "1h", "direzione": "long", "parametri": {},
                     "idea": "I-06", "fonte": F_LOMAC,
                     "meccanismo": "l'informazione comune arriva prima su BTC: GALAUSDT recupera in ritardo",
                     "regole": "1h; rendimento BTC nella barra > 2 deviazioni standard delle 168 barre precedenti e rendimento GALAUSDT < rendimento BTC; uscita dopo 3 barre; stop 2 ATR(24) max 6%",
                     "previsione": _prev(-0.25, 0.05)},
    "GALAUSDT-012": {"classe": V.RitardoBTC, "tf": "1h", "direzione": "short", "parametri": {},
                     "idea": "I-06", "fonte": F_LOMAC,
                     "meccanismo": "l'informazione comune arriva prima su BTC: GALAUSDT scende in ritardo",
                     "regole": "1h; rendimento BTC nella barra < -2 deviazioni standard delle 168 barre precedenti e rendimento GALAUSDT > rendimento BTC; uscita dopo 3 barre; stop 2 ATR(24) max 6%",
                     "previsione": _prev(-0.25, 0.05)},
    # ---- I-07 ----
    "GALAUSDT-013": {"classe": V.NR7, "tf": "4h", "direzione": "long", "parametri": {},
                     "idea": "I-07", "fonte": F_CRABEL,
                     "meccanismo": "compressione della volatilita' seguita da espansione nella direzione della rottura",
                     "regole": "4h; barra precedente la piu' stretta delle ultime 7 e close sopra il suo massimo; stop al minimo della barra stretta (max 6%); target 2 R; uscita dopo 12 barre",
                     "previsione": _prev(-0.20, 0.10)},
    "GALAUSDT-014": {"classe": V.NR7, "tf": "4h", "direzione": "short", "parametri": {},
                     "idea": "I-07", "fonte": F_CRABEL,
                     "meccanismo": "compressione della volatilita' seguita da espansione nella direzione della rottura",
                     "regole": "4h; barra precedente la piu' stretta delle ultime 7 e close sotto il suo minimo; stop al massimo della barra stretta (max 6%); target 2 R; uscita dopo 12 barre",
                     "previsione": _prev(-0.20, 0.10)},
    # ---- I-08 ----
    "GALAUSDT-015": {"classe": V.VolumeContinuazione, "tf": "1h", "direzione": "long", "parametri": {},
                     "idea": "I-08", "fonte": F_LLORENTE,
                     "meccanismo": "rialzo con volume alto = commercio informato: continua",
                     "regole": "1h; rendimento della barra > 2 deviazioni standard delle 168 precedenti e volume USDT > 2 volte la media delle 168 precedenti; uscita dopo 6 barre; stop 2 ATR(24) max 6%",
                     "previsione": _prev(-0.20, 0.10)},
    "GALAUSDT-016": {"classe": V.VolumeContinuazione, "tf": "1h", "direzione": "short", "parametri": {},
                     "idea": "I-08", "fonte": F_LLORENTE,
                     "meccanismo": "ribasso con volume alto = commercio informato: continua",
                     "regole": "1h; rendimento della barra < -2 deviazioni standard delle 168 precedenti e volume USDT > 2 volte la media delle 168 precedenti; uscita dopo 6 barre; stop 2 ATR(24) max 6%",
                     "previsione": _prev(-0.20, 0.10)},
    # ---- I-09 ----
    "GALAUSDT-017": {"classe": V.RotturaWilliams, "tf": "1h", "direzione": "long", "parametri": {},
                     "idea": "I-09", "fonte": F_WILLIAMS,
                     "meccanismo": "rottura di volatilita' dall'apertura del giorno: il movimento continua fino a fine giornata",
                     "regole": "1h; prima chiusura del giorno UTC sopra apertura delle 00:00 + 0,5 x range del giorno prima (non alla barra delle 23); stop 0,5 x range del giorno prima dal close (max 6%); uscita all'apertura delle 00:00",
                     "previsione": _prev(-0.20, 0.10)},
    "GALAUSDT-018": {"classe": V.RotturaWilliams, "tf": "1h", "direzione": "short", "parametri": {},
                     "idea": "I-09", "fonte": F_WILLIAMS,
                     "meccanismo": "rottura di volatilita' dall'apertura del giorno: il movimento continua fino a fine giornata",
                     "regole": "1h; prima chiusura del giorno UTC sotto apertura delle 00:00 - 0,5 x range del giorno prima (non alla barra delle 23); stop 0,5 x range del giorno prima dal close (max 6%); uscita all'apertura delle 00:00",
                     "previsione": _prev(-0.20, 0.10)},
    # ---- I-10 ----
    "GALAUSDT-019": {"classe": V.Lunedi, "tf": "1d", "direzione": "long", "parametri": {},
                     "idea": "I-10", "fonte": F_DOW,
                     "meccanismo": "rendimenti anomali del lunedi'",
                     "regole": "1d; long all'apertura del lunedi' (segnale alla chiusura della domenica); uscita dopo 1 barra; stop 2 ATR(14) max 6%",
                     "previsione": _prev(-0.20, 0.10)},
    # ---- I-11 ----
    "GALAUSDT-020": {"classe": V.ValoreRelativo, "tf": "4h", "direzione": "long", "parametri": {},
                     "idea": "I-11", "fonte": F_GATEV,
                     "meccanismo": "lo scarto GALAUSDT/BTC allargato oltre 2 deviazioni standard si richiude",
                     "regole": "4h; z dello scarto log(GALA)-log(BTC) sulle 42 barre < -2; uscita quando z >= 0 o dopo 18 barre; stop 2 ATR(14) max 6%",
                     "previsione": _prev(-0.20, 0.10)},
    "GALAUSDT-021": {"classe": V.ValoreRelativo, "tf": "4h", "direzione": "short", "parametri": {},
                     "idea": "I-11", "fonte": F_GATEV,
                     "meccanismo": "lo scarto GALAUSDT/BTC allargato oltre 2 deviazioni standard si richiude",
                     "regole": "4h; z dello scarto log(GALA)-log(BTC) sulle 42 barre > 2; uscita quando z <= 0 o dopo 18 barre; stop 2 ATR(14) max 6%",
                     "previsione": _prev(-0.20, 0.10)},
    # ---- I-12 ----
    "GALAUSDT-022": {"classe": V.GiornoAnomalo, "tf": "1d", "direzione": "long", "parametri": {},
                     "idea": "I-12", "fonte": F_OVER,
                     "meccanismo": "dopo un giorno di rialzo anomalo il giorno dopo continua",
                     "regole": "1d; rendimento del giorno (close/open) > media + 2 deviazioni standard dei 30 giorni precedenti; long il giorno dopo, uscita dopo 1 barra; stop 2 ATR(14) max 6%",
                     "previsione": _prev(-0.20, 0.20)},
    "GALAUSDT-023": {"classe": V.GiornoAnomalo, "tf": "1d", "direzione": "short", "parametri": {},
                     "idea": "I-12", "fonte": F_OVER,
                     "meccanismo": "dopo un giorno di ribasso anomalo il giorno dopo continua",
                     "regole": "1d; rendimento del giorno < media - 2 deviazioni standard dei 30 giorni precedenti; short il giorno dopo, uscita dopo 1 barra; stop 2 ATR(14) max 6%",
                     "previsione": _prev(-0.20, 0.20)},
    # ---- I-13 ----
    "GALAUSDT-024": {"classe": V.PompaScarico, "tf": "1h", "direzione": "short", "parametri": {},
                     "idea": "I-13", "fonte": F_PUMP,
                     "meccanismo": "pompa organizzata: dopo il salto di prezzo e volume il prezzo ricade",
                     "regole": "1h; rendimento della barra > 3 deviazioni standard delle 168 precedenti e volume USDT > 3 volte la media delle 168 precedenti; short; uscita dopo 24 barre; stop 2 ATR(24) max 6%",
                     "previsione": _prev(-0.30, 0.20)},
    # ---- varianti allentate dopo gli scarti (ipotesi.md, 18:39 UTC) ----
    "GALAUSDT-025": {"classe": V.Donchian, "tf": "2h", "direzione": "long", "parametri": {},
                     "idea": "I-02", "fonte": F_TURTLE,
                     "meccanismo": "rottura del massimo di 20 barre: ordini in rottura e stop oltre il massimo spingono il prezzo",
                     "regole": "2h; ingresso alla chiusura sopra il massimo delle 20 barre precedenti; uscita alla chiusura sotto il minimo delle 10 barre precedenti; stop 2 ATR(20) max 6%; nessun target",
                     "previsione": _prev(-0.20, 0.15)},
    "GALAUSDT-026": {"classe": V.Donchian, "tf": "2h", "direzione": "short", "parametri": {},
                     "idea": "I-02", "fonte": F_TURTLE,
                     "meccanismo": "rottura del minimo di 20 barre: ordini in rottura e stop sotto il minimo spingono il prezzo",
                     "regole": "2h; ingresso alla chiusura sotto il minimo delle 20 barre precedenti; uscita alla chiusura sopra il massimo delle 10 barre precedenti; stop 2 ATR(20) max 6%; nessun target",
                     "previsione": _prev(-0.20, 0.15)},
    "GALAUSDT-028": {"classe": V.FundingEstremo, "tf": "8h", "direzione": "short", "parametri": {"quantile": 0.70},
                     "idea": "I-05", "fonte": F_CARRY,
                     "meccanismo": "funding alto = long a leva affollati: il prezzo poi scende",
                     "regole": "8h; ultimo funding regolato > 70o percentile dei 90 regolamenti precedenti e > 0; uscita dopo 3 barre; stop 2 ATR(14) max 6%",
                     "previsione": _prev(-0.15, 0.10)},
    # ---- idee nuove I-14 .. I-17 ----
    "GALAUSDT-029": {"classe": V.PeriodicitaOraria, "tf": "1h", "direzione": "long", "parametri": {},
                     "idea": "I-14", "fonte": F_HKS,
                     "meccanismo": "flussi ripetuti alla stessa ora: l'ora che ha reso nelle ultime 20 giornate rende ancora",
                     "regole": "1h; z = media/(dev/radice 20) dei rendimenti dell'ora successiva nelle ultime 20 giornate > 1,5; long per 1 barra; stop 2 ATR(24) max 6%",
                     "previsione": _prev(-0.20, 0.05)},
    "GALAUSDT-030": {"classe": V.PeriodicitaOraria, "tf": "1h", "direzione": "short", "parametri": {},
                     "idea": "I-14", "fonte": F_HKS,
                     "meccanismo": "flussi ripetuti alla stessa ora: l'ora che ha perso nelle ultime 20 giornate perde ancora",
                     "regole": "1h; z dei rendimenti dell'ora successiva nelle ultime 20 giornate < -1,5; short per 1 barra; stop 2 ATR(24) max 6%",
                     "previsione": _prev(-0.20, 0.05)},
    "GALAUSDT-031": {"classe": V.ScartoMark, "tf": "1h", "direzione": "long", "parametri": {},
                     "idea": "I-15", "fonte": F_PERP,
                     "meccanismo": "il perpetuo sotto il mark piu' del solito si riallinea salendo",
                     "regole": "1h; z dello scarto (close last - close mark)/close mark rispetto alle 168 barre precedenti < -2; uscita dopo 2 barre; stop 2 ATR(24) max 6%",
                     "previsione": _prev(-0.20, 0.05)},
    "GALAUSDT-032": {"classe": V.ScartoMark, "tf": "1h", "direzione": "short", "parametri": {},
                     "idea": "I-15", "fonte": F_PERP,
                     "meccanismo": "il perpetuo sopra il mark piu' del solito si riallinea scendendo",
                     "regole": "1h; z dello scarto last-mark rispetto alle 168 barre precedenti > 2; uscita dopo 2 barre; stop 2 ATR(24) max 6%",
                     "previsione": _prev(-0.20, 0.05)},
    "GALAUSDT-033": {"classe": V.NumeriTondi, "tf": "1h", "direzione": "short", "parametri": {},
                     "idea": "I-16", "fonte": F_OSLER03,
                     "meccanismo": "ordini di presa di profitto sui numeri tondi: il rialzo si ferma e torna indietro",
                     "regole": "1h; L = primo multiplo di u=10^floor(log10 close prec.)/2 sopra il close precedente; massimo >= L e close < L; stop L + 0,5 ATR(24) (max 6%); target 2 R; uscita dopo 24 barre",
                     "previsione": _prev(-0.20, 0.10)},
    "GALAUSDT-034": {"classe": V.NumeriTondi, "tf": "1h", "direzione": "long", "parametri": {},
                     "idea": "I-16", "fonte": F_OSLER03,
                     "meccanismo": "ordini di presa di profitto sui numeri tondi: il ribasso si ferma e torna indietro",
                     "regole": "1h; L = primo multiplo di u sotto il close precedente; minimo <= L e close > L; stop L - 0,5 ATR(24) (max 6%); target 2 R; uscita dopo 24 barre",
                     "previsione": _prev(-0.20, 0.10)},
    "GALAUSDT-035": {"classe": V.MomentumGiornata, "tf": "30m", "direzione": "long", "parametri": {},
                     "idea": "I-17", "fonte": F_GAO,
                     "meccanismo": "la prima mezz'ora della giornata UTC predice l'ultima",
                     "regole": "30m; alla chiusura della barra delle 23:00, long se la barra delle 00:00 dello stesso giorno ha close > open; uscita dopo 1 barra; stop 2 ATR(48) max 6%",
                     "previsione": _prev(-0.30, 0.05)},
    "GALAUSDT-036": {"classe": V.MomentumGiornata, "tf": "30m", "direzione": "short", "parametri": {},
                     "idea": "I-17", "fonte": F_GAO,
                     "meccanismo": "la prima mezz'ora della giornata UTC predice l'ultima",
                     "regole": "30m; alla chiusura della barra delle 23:00, short se la barra delle 00:00 dello stesso giorno ha close < open; uscita dopo 1 barra; stop 2 ATR(48) max 6%",
                     "previsione": _prev(-0.30, 0.05)},
    # ---- ritocchi (regola 6), nell'ordine del t contro la (b) ----
    "GALAUSDT-037": {"classe": V.RitardoBTC, "tf": "1h", "direzione": "long", "parametri": {"atr_min_rel": 0.0146},
                     "idea": "I-06", "fonte": F_LOMAC, "famiglia": "GALAUSDT-011", "ritocco_di": "GALAUSDT-011",
                     "cosa_cambia": "aggiunto il filtro ATR(24)/close > 1,46% (soglia del terzile basso dell'ATR relativo dei trade di 011 in costruzione): nel terzile basso R medio -0,034 contro +0,105 e +0,130 negli altri due (nota GALAUSDT-N008); con stop stretti i costi pesano di piu' in R",
                     "meccanismo": "l'informazione comune arriva prima su BTC: GALAUSDT recupera in ritardo",
                     "regole": "come GALAUSDT-011 (1h; BTC > 2 dev. std delle 168 barre precedenti e GALAUSDT < BTC nella barra; uscita dopo 3 barre; stop 2 ATR(24) max 6%) piu' il filtro ATR(24)/close > 0,0146",
                     "previsione": _prev(-0.05, 0.20, "R medio fra -0,05 e +0,20; t contro la (b) vicino alla soglia, probabile ancora sotto (il filtro toglie un terzo dei trade e alza l'errore)")},
    "GALAUSDT-038": {"classe": V.RitardoBTC, "tf": "1h", "direzione": "long", "parametri": {"k_stop": 3.0},
                     "idea": "I-06", "fonte": F_LOMAC, "famiglia": "GALAUSDT-011", "ritocco_di": "GALAUSDT-011",
                     "cosa_cambia": "stop da 2 a 3 ATR(24) (max 6%). Dopo 037 l'ordine del t contro la (b) mette ancora 011 in testa (1,945; 015 1,844; 037 1,811). In 011 i 16 stop costano -1,05 R ciascuno e le uscite a tempo rendono +0,19 R (nota GALAUSDT-N008); il filtro di volatilita' (037) non ha aiutato. Uno stop piu' largo abbassa il costo di un giro in R (circa da 0,05 a 0,03 R) e gli stop toccati dal rumore delle 3 ore",
                     "meccanismo": "l'informazione comune arriva prima su BTC: GALAUSDT recupera in ritardo",
                     "regole": "come GALAUSDT-011 (1h; BTC > 2 dev. std delle 168 barre precedenti e GALAUSDT < BTC nella barra; uscita dopo 3 barre) con stop 3 ATR(24) max 6%",
                     "previsione": _prev(-0.02, 0.12, "R medio fra -0,02 e +0,12 (R piu' piccolo perche' il rischio per trade e' piu' largo); t contro la (b) simile a 011, sotto la soglia")},
}


def crea_variante(vid: str):
    voce = CATALOGO[vid]
    var = voce["classe"](**voce.get("parametri", {}))
    var.id, var.tf, var.direzione = vid, voce["tf"], voce["direzione"]
    return var
