"""Esegue le varianti indicate, in serie: conta_trade, poi registrazione nel log, poi test, poi risultato.

Uso: python -m research.campagne.XRPUSDT.codice.esegui XRPUSDT-V01 XRPUSDT-V02 ...
Sotto i 70 trade la variante e' uno `scarto` (nessun budget, nessun test).
Il riepilogo di ogni variante va anche in data/insample/XRPUSDT/esiti.txt (fuori da git).
"""
import sys
import time

from research.src import dati
from research.campagne.XRPUSDT.codice import quadro as q
from research.campagne.XRPUSDT.codice.varianti import VARIANTI

CRITERIO = ("batte nettamente la (a) e la (b) con contro_baseline (t sopra la soglia della t di Student) "
            "e R medio dopo i costi positivo, sui dati di costruzione (sezione 8)")

META = {
    "I-01": {"fonte": "Liu e Tsyvinski, Risks and Returns of Cryptocurrency, NBER WP 24877, agosto 2018; Moskowitz, Ooi e Pedersen, Time Series Momentum, JFE 104(2), maggio 2012",
             "meccanismo": "momentum a una settimana: il rendimento dei 7 giorni prima prevede la settimana dopo"},
    "I-02": {"fonte": "Campbell, Grossman e Wang, Trading Volume and Serial Correlation in Stock Returns, QJE 108(4), novembre 1993",
             "meccanismo": "un movimento orario estremo con volume alto e' domanda di liquidita' e rientra"},
    "I-03": {"fonte": "Caporale e Plastun, Price overreactions in the cryptocurrency market, Journal of Economic Studies 46(5), 2019",
             "meccanismo": "dopo un giorno di sovrareazione il prezzo continua nella stessa direzione il giorno dopo"},
    "I-04": {"fonte": "Schmeling, Schrimpf e Todorov, Crypto carry, BIS Working Papers 1087, aprile 2023",
             "meccanismo": "funding estremo = leva affollata da una parte, che poi viene liquidata"},
    "I-05": {"fonte": "Caporale e Plastun, The day of the week effect in the cryptocurrency market, Finance Research Letters 31, dicembre 2019",
             "meccanismo": "rendimenti del lunedi' piu' alti"},
    "I-06": {"fonte": "Lo e MacKinlay, When Are Contrarian Profits Due to Stock Market Overreaction?, RFS 3(2), 1990; Sifat, Mohamad e Mohamed Shariff, Lead-Lag relationship between Bitcoin and Ethereum, RIBAF 50, dicembre 2019",
             "meccanismo": "BTC guida: XRP rimasto indietro recupera nella direzione di BTC"},
    "I-07": {"fonte": "Hudson e Urquhart, Technical trading and cryptocurrencies, Annals of Operations Research 297, 2021 (online 2019); Brock, Lakonishok e LeBaron, JF 47(5), dicembre 1992",
             "meccanismo": "rottura del canale di 20 barre: il trend continua"},
    "I-08": {"fonte": "Connors e Alvarez, Short Term Trading Strategies That Work, TradingMarkets, 2008",
             "meccanismo": "RSI(2) estremo dentro il trend della media a 200: rientro breve"},
    "I-09": {"fonte": "Bollinger, Bollinger on Bollinger Bands, McGraw-Hill, 2001",
             "meccanismo": "compressione della volatilita' seguita da rottura delle bande nella direzione della rottura"},
    "I-10": {"fonte": "Chordia e Subrahmanyam, Order imbalance and individual stock returns: Theory and evidence, JFE 72(3), giugno 2004",
             "meccanismo": "lo squilibrio degli ordini aggressivi persiste e prevede il rendimento successivo"},
    "I-11": {"fonte": "He, Manela, Ross e von Wachter, Fundamentals of Perpetual Futures, arXiv 2212.06888, dicembre 2022",
             "meccanismo": "il premio del perpetuo sul mark price rientra"},
    "I-12": {"fonte": "Osler, Currency Orders and Exchange Rate Dynamics, Journal of Finance 58(5), ottobre 2003",
             "meccanismo": "ordini di stop oltre i numeri tondi: attraversato il numero tondo il prezzo accelera"},
    "I-13": {"fonte": "Gao, Han, Li e Zhou, Market Intraday Momentum, JFE 129(2), agosto 2018; Wen, Bouri, Xu e Zhao, NAJEF 62, novembre 2022",
             "meccanismo": "la prima mezz'ora del giorno UTC prevede l'ultima mezz'ora"},
    "I-14": {"fonte": "Liu, Tsyvinski e Wu, Common Risk Factors in Cryptocurrency, NBER WP 25882, maggio 2019 (JF 77(2), 2022)",
             "meccanismo": "momentum relativo: XRP che ha battuto BTC negli ultimi 7 giorni continua a batterlo"},
    "I-15": {"fonte": "Crabel, Day Trading with Short Term Price Patterns and Opening Range Breakout, Traders Press, 1990",
             "meccanismo": "la prima rottura dell'intervallo delle prime due ore UTC indica la direzione della giornata"},
}

PARAMETRI = {
    "XRPUSDT-V26": ("rendimento 7 giorni di XRP meno quello di BTC > 0; stop min(2 ATR14, 6%); tenuta 7", "R medio fra -0,10 e +0,15; non batte nettamente la (b)"),
    "XRPUSDT-V27": ("rendimento 7 giorni di XRP meno quello di BTC < 0; stop min(2 ATR14, 6%); tenuta 7", "R medio fra -0,15 e +0,10"),
    "XRPUSDT-V28": ("prima chiusura oraria 02-22 UTC sopra il massimo delle barre 00 e 01; uscita a fine giornata; stop min(1,5 ATR14, 6%); tenuta 22", "R medio fra -0,10 e +0,10"),
    "XRPUSDT-V29": ("prima chiusura oraria 02-22 UTC sotto il minimo delle barre 00 e 01; uscita a fine giornata; stop min(1,5 ATR14, 6%); tenuta 22", "R medio fra -0,10 e +0,10"),
    "XRPUSDT-V01": ("rendimento 7 giorni > 0; stop min(2 ATR14, 6%); tenuta 7", "R medio fra -0,10 e +0,15; non batte nettamente la (b)"),
    "XRPUSDT-V02": ("rendimento 7 giorni < 0; stop min(2 ATR14, 6%); tenuta 7", "R medio fra -0,15 e +0,10; non batte nettamente la (b)"),
    "XRPUSDT-V03": ("r < -2,5 sigma(168) e volume > 2 volte la media 168; stop min(1,5 ATR14, 6%); tenuta 12", "R medio fra -0,10 e +0,15"),
    "XRPUSDT-V04": ("r > +2,5 sigma(168) e volume > 2 volte la media 168; stop min(1,5 ATR14, 6%); tenuta 12", "R medio fra -0,15 e +0,10"),
    "XRPUSDT-V05": ("r > media30 + 1,5 sigma30; stop min(1,5 ATR14, 6%); tenuta 1", "R medio fra -0,10 e +0,15"),
    "XRPUSDT-V06": ("r < media30 - 1,5 sigma30; stop min(1,5 ATR14, 6%); tenuta 1", "R medio fra -0,15 e +0,10"),
    "XRPUSDT-V05b": ("r > media30 + 1,0 sigma30; stop min(1,5 ATR14, 6%); tenuta 1", "R medio fra -0,10 e +0,15"),
    "XRPUSDT-V06b": ("r < media30 - 1,0 sigma30; stop min(1,5 ATR14, 6%); tenuta 1", "R medio fra -0,15 e +0,10"),
    "XRPUSDT-V07": ("funding >= 0,0005; stop min(2 ATR14, 6%); tenuta 9", "R medio fra -0,15 e +0,15"),
    "XRPUSDT-V08": ("funding <= -0,0002; stop min(2 ATR14, 6%); tenuta 9", "R medio fra -0,15 e +0,15"),
    "XRPUSDT-V07b": ("funding >= 0,0003; stop min(2 ATR14, 6%); tenuta 9", "R medio fra -0,15 e +0,15"),
    "XRPUSDT-V08b": ("funding <= -0,0001; stop min(2 ATR14, 6%); tenuta 9", "R medio fra -0,15 e +0,15"),
    "XRPUSDT-V09": ("chiusura della domenica UTC -> long il lunedi'; stop min(1,5 ATR14, 6%); tenuta 1", "R medio fra -0,10 e +0,10; non batte nettamente la (b)"),
    "XRPUSDT-V10": ("BTC 1h > +1% e XRP 1h < 0,5 x BTC; stop min(1,5 ATR14, 6%); tenuta 4", "R medio fra -0,10 e +0,10"),
    "XRPUSDT-V11": ("BTC 1h < -1% e XRP 1h > 0,5 x BTC; stop min(1,5 ATR14, 6%); tenuta 4", "R medio fra -0,10 e +0,10"),
    "XRPUSDT-V12": ("close > massimo 20 barre prima; uscita close < minimo 10 barre prima; stop min(2 ATR14, 6%); tenuta 30", "R medio fra -0,10 e +0,20"),
    "XRPUSDT-V13": ("close < minimo 20 barre prima; uscita close > massimo 10 barre prima; stop min(2 ATR14, 6%); tenuta 30", "R medio fra -0,15 e +0,15"),
    "XRPUSDT-V14": ("close > media200 e RSI2 < 10; uscita close > media5; stop min(2,5 ATR14, 6%); tenuta 30", "R medio fra -0,10 e +0,15"),
    "XRPUSDT-V15": ("close < media200 e RSI2 > 90; uscita close < media5; stop min(2,5 ATR14, 6%); tenuta 30", "R medio fra -0,15 e +0,10"),
    "XRPUSDT-V16": ("larghezza bande al minimo di 480 barre in una delle 10 barre prima e close > banda superiore (20, 2); stop min(2 ATR14, 6%); tenuta 24", "R medio fra -0,15 e +0,15"),
    "XRPUSDT-V17": ("larghezza bande al minimo di 480 barre in una delle 10 barre prima e close < banda inferiore (20, 2); stop min(2 ATR14, 6%); tenuta 24", "R medio fra -0,15 e +0,15"),
    "XRPUSDT-V16b": ("larghezza bande al minimo di 240 barre in una delle 24 barre prima e close > banda superiore (20, 2); stop min(2 ATR14, 6%); tenuta 24", "R medio fra -0,15 e +0,15"),
    "XRPUSDT-V17b": ("larghezza bande al minimo di 240 barre in una delle 24 barre prima e close < banda inferiore (20, 2); stop min(2 ATR14, 6%); tenuta 24", "R medio fra -0,15 e +0,15"),
    "XRPUSDT-V18": ("squilibrio taker 4 barre > +0,10; stop min(1,5 ATR14, 6%); tenuta 4", "R medio fra -0,10 e +0,10"),
    "XRPUSDT-V19": ("squilibrio taker 4 barre < -0,10; stop min(1,5 ATR14, 6%); tenuta 4", "R medio fra -0,10 e +0,10"),
    "XRPUSDT-V18b": ("squilibrio taker 4 barre > +0,06; stop min(1,5 ATR14, 6%); tenuta 4", "R medio fra -0,10 e +0,10"),
    "XRPUSDT-V19b": ("squilibrio taker 4 barre < -0,06; stop min(1,5 ATR14, 6%); tenuta 4", "R medio fra -0,10 e +0,10"),
    "XRPUSDT-V20": ("premio last/mark > +0,0015; stop min(1,5 ATR14, 6%); tenuta 4", "R medio fra -0,10 e +0,10"),
    "XRPUSDT-V21": ("premio last/mark < -0,0015; stop min(1,5 ATR14, 6%); tenuta 4", "R medio fra -0,10 e +0,10"),
    "XRPUSDT-V20b": ("premio last/mark > +0,0010; stop min(1,5 ATR14, 6%); tenuta 4", "R medio fra -0,10 e +0,10"),
    "XRPUSDT-V21b": ("premio last/mark < -0,0010; stop min(1,5 ATR14, 6%); tenuta 4", "R medio fra -0,10 e +0,10"),
    "XRPUSDT-V22": ("close attraversa verso l'alto un numero tondo a due cifre significative; stop min(1,5 ATR14, 6%); tenuta 6", "R medio fra -0,10 e +0,10"),
    "XRPUSDT-V23": ("close attraversa verso il basso un numero tondo a due cifre significative; stop min(1,5 ATR14, 6%); tenuta 6", "R medio fra -0,10 e +0,10"),
    "XRPUSDT-V24": ("prima mezz'ora UTC > 0 -> long nell'ultima mezz'ora; stop min(1,5 ATR14, 6%); tenuta 1", "R medio fra -0,20 e +0,05"),
    "XRPUSDT-V25": ("prima mezz'ora UTC < 0 -> short nell'ultima mezz'ora; stop min(1,5 ATR14, 6%); tenuta 1", "R medio fra -0,20 e +0,05"),
}

ESITI = dati.RADICE_DEFAULT / "data" / "insample" / "XRPUSDT" / "esiti.txt"


def scrivi_esito(riga: str) -> None:
    with open(ESITI, "a", encoding="utf-8") as f:
        f.write(riga + "\n")


def esegui(vid: str, meta_extra=None) -> None:
    v = VARIANTI[vid]
    idea = v.descrizione["idea"]
    meta = dict(META[idea])
    regole, previsione = PARAMETRI.get(vid, (None, None))
    if meta_extra:
        meta.update(meta_extra)
        regole = meta.pop("regole", regole)
        previsione = meta.pop("previsione", previsione)
    par = q.parametri()
    t0 = time.time()
    c = q.conta(v, par)
    base = {"id": vid, "idea": idea, "fonte": meta["fonte"], "meccanismo": meta["meccanismo"],
            "timeframe": v.tf, "direzione": v.direzione, "parametri": {"regole": regole, "tenuta_barre": v.tenuta},
            "periodo": "costruzione", "trade_stimati": c["trade"], "conta_trade": c}
    if c["trade"] < q.TRADE_MINIMI_COSTRUZIONE:
        q.scrivi_log({**base, "tipo": "scarto", "motivo": f"sotto i trade minimi di costruzione ({c['trade']} < 70)"})
        scrivi_esito(f"{vid} SCARTO trade {c['trade']}")
        return
    n = q.prossimo_variante_n()
    q.scrivi_log({**base, "tipo": "registrazione", "tipo_test": "variante", "famiglia": meta.get("famiglia", vid),
                  "ritocco_di": meta.get("ritocco_di"), "previsione": previsione, "criterio_successo": CRITERIO,
                  "variante_n": n, **({"cosa_cambia": meta["cosa_cambia"]} if "cosa_cambia" in meta else {})})
    s = q.serie(v.tf)
    r = q.valuta(v, s, par)
    assert r["metriche"]["trade"] == c["trade"], (r["metriche"]["trade"], c["trade"])
    voce = {"id": vid, "tipo": "risultato", "metriche": r["metriche"], "blocco": r.get("blocco"),
            "baseline_a": r.get("baseline_a"), "baseline_b": r.get("baseline_b"),
            "percentile_caso": r.get("percentile_caso"), "buy_and_hold_per_anno": r.get("buy_and_hold_per_anno"),
            "valutabile": r.get("valutabile"), "candidato": r.get("candidato"), "t_contro_b": r.get("t_contro_b"),
            "secondi": round(time.time() - t0, 1)}
    q.scrivi_log(voce)
    m = r["metriche"]
    scrivi_esito(f"{vid} n={n} trade={m['trade']} R={m['r_medio']:.3f} PF={m['profit_factor']:.2f} "
                 f"a: t={r['baseline_a'].get('t', float('nan')):.2f} netta={r['baseline_a'].get('netta')} | "
                 f"b: media={r['baseline_b'].get('media', float('nan')):.3f} t={r['baseline_b'].get('t', float('nan')):.2f} "
                 f"netta={r['baseline_b'].get('netta')} | perc={r.get('percentile_caso')} candidato={r.get('candidato')} "
                 f"R_anno={ {k: round(x, 3) for k, x in m['r_medio_per_anno'].items()} } senza3={m['r_medio_senza_3_migliori']} "
                 f"btc={m.get('btc_in_direzione_medio')} xrp={m.get('xrp_in_direzione_medio')}")


#: Ritocchi (regola 6): ognuno registrato con ritocco_di, famiglia, cosa cambia e perche', previsione.
RITOCCHI = {
    "XRPUSDT-V21r1": {
        "ritocco_di": "XRPUSDT-V21", "famiglia": "XRPUSDT-V21",
        "cosa_cambia": "aggiunto un filtro: nessun ingresso se la barra del segnale e' scesa oltre il 10% "
                       "(close[i]/close[i-1]-1 >= -0,10). Perche': studio dei fallimenti (nota Fase 3): le 9 entrate "
                       "dopo cadute oltre il 12% sono tutte stop pieni; un premio negativo durante un crollo non rientra.",
        "regole": "premio last/mark < -0,0015 e rendimento della barra del segnale >= -10%; stop min(1,5 ATR14, 6%); tenuta 4",
        "previsione": "circa 220-230 trade; R medio fra 0,00 e +0,10; t contro la (b) fra 1,5 e 2,5: puo' superare "
                      "la soglia solo di poco, e il filtro e' costruito su 9-19 trade, quindi va letto come fragile",
    },
    "XRPUSDT-V21r2": {
        "ritocco_di": "XRPUSDT-V21r1", "famiglia": "XRPUSDT-V21",
        "cosa_cambia": "tenuta da 4 a 8 barre, il resto uguale a V21r1. Perche': studio dei fallimenti (note Fase 3 di "
                       "V21 e V21r1): il movimento medio dopo l'ingresso, senza stop, cresce fino alla sesta-settima "
                       "chiusura (+0,25 R) mentre l'uscita e' alla quarta; i trade usciti a tempo valgono +0,37 R, gli stop -1,05 R.",
        "regole": "premio last/mark < -0,0015 e rendimento della barra del segnale >= -10%; stop min(1,5 ATR14, 6%); tenuta 8",
        "previsione": "meno trade (circa 200-215); R medio fra 0,00 e +0,12; t contro la (b) fra 1,0 e 2,5: tenendo di "
                      "piu' crescono anche gli stop, e il guadagno medio in piu' (circa 0,06 R) e' piccolo rispetto al rumore",
    },
    "XRPUSDT-V21r3": {
        "ritocco_di": "XRPUSDT-V21r1", "famiglia": "XRPUSDT-V21",
        "cosa_cambia": "soglia del premio da -0,0015 a -0,0020, il resto uguale a V21r1 (tenuta 4). Perche': studio dei "
                       "fallimenti di V21 (codice/fallimenti.py, premio al segnale): i 189 trade con premio arrotondato "
                       "a -0,2% (fra -0,15% e -0,25%) hanno R medio -0,034, quelli oltre -0,25% sono positivi.",
        "regole": "premio last/mark < -0,0020 e rendimento della barra del segnale >= -10%; stop min(1,5 ATR14, 6%); tenuta 4",
        "previsione": "meno trade, forse vicino o sotto i 70 (allora scarto); se sopra: R medio fra 0,00 e +0,20, t contro "
                      "la (b) fra 1,0 e 2,5 (meno trade = errore piu' grande)",
    },
}

if __name__ == "__main__":
    for vid in sys.argv[1:]:
        esegui(vid, RITOCCHI.get(vid))
