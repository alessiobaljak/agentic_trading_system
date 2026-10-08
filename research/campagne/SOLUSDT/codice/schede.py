"""Le schede delle varianti per il log (le stesse regole di ipotesi.md e varianti.py).

  python schede.py registra <ID> <variante_n>   registrazione (prima del test) con trade_stimati da conta_<ID>.json
  python schede.py scarto <ID>                  scarto per trade sotto il minimo
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
import registro  # noqa: E402

BOZZE = comune.dati.RADICE_DEFAULT / "data" / "insample" / comune.SIMBOLO / "bozze"
CRITERIO = ("batte nettamente la baseline (a) e la (b) con contro_baseline in costruzione e R medio dopo i "
            "costi positivo (sezione 8)")

F = {
    "I-01": "T. J. Moskowitz, Y. H. Ooi, L. H. Pedersen, 'Time series momentum', Journal of Financial Economics 104(2), maggio 2012; Y. Liu, A. Tsyvinski, 'Risks and Returns of Cryptocurrency', NBER Working Paper 24877, agosto 2018",
    "I-02": "M. Covel, 'The Complete TurtleTrader', HarperCollins, 2007; C. Faith, 'Way of the Turtle', McGraw-Hill, 2007",
    "I-03": "W. Brock, J. Lakonishok, B. LeBaron, 'Simple Technical Trading Rules and the Stochastic Properties of Stock Returns', Journal of Finance 47(5), dicembre 1992",
    "I-04": "L. Connors, C. Alvarez, 'Short Term Trading Strategies That Work', TradingMarkets Publishing, 2008",
    "I-05": "B. N. Lehmann, 'Fads, Martingales, and Market Efficiency', Quarterly Journal of Economics 105(1), febbraio 1990; S. Nagel, 'Evaporating Liquidity', Review of Financial Studies 25(7), luglio 2012",
    "I-06": "J. Y. Campbell, S. J. Grossman, J. Wang, 'Trading Volume and Serial Correlation in Stock Returns', Quarterly Journal of Economics 108(4), novembre 1993",
    "I-07": "T. Crabel, 'Day Trading with Short Term Price Patterns and Opening Range Breakout', Traders Press, 1990",
    "I-08": "G. M. Caporale, A. Plastun, 'The day of the week effect in the cryptocurrency market', Finance Research Letters 31, dicembre 2019",
    "I-09": "L. Gao, Y. Han, S. Z. Li, G. Zhou, 'Market intraday momentum', Journal of Financial Economics 129(2), agosto 2018; D. Shen, A. Urquhart, P. Wang, 'Bitcoin intraday time series momentum', The Financial Review 57(2), 2022",
    "I-10": "M. Schmeling, A. Schrimpf, K. Todorov, 'Crypto carry', BIS Working Paper 1087, aprile 2023",
    "I-11": "K. Hou, 'Industry Information Diffusion and the Lead-lag Effect in Stock Returns', Review of Financial Studies 20(4), luglio 2007",
    "I-12": "S. Gervais, R. Kaniel, D. H. Mingelgrin, 'The High-Volume Return Premium', Journal of Finance 56(3), giugno 2001",
    "I-13": "C. L. Osler, 'Currency Orders and Exchange Rate Dynamics: An Explanation for the Predictive Success of Technical Analysis', Journal of Finance 58(5), ottobre 2003",
}

S = {
    "SOLUSDT-001": ("I-01", "momentum della serie a 7 giorni", "long", {"condizione": "rendimento close-su-close 7 barre > 0", "stop": "2 ATR(14) sotto il close", "target": None, "uscita": "a tempo dopo 7 barre"}, "R medio fra 0 e +0,15; t contro la (b) fra 0 e 2"),
    "SOLUSDT-002": ("I-01", "momentum della serie a 7 giorni", "short", {"condizione": "rendimento close-su-close 7 barre < 0", "stop": "2 ATR(14) sopra il close", "target": None, "uscita": "a tempo dopo 7 barre"}, "R medio fra -0,1 e +0,1"),
    "SOLUSDT-003": ("I-02", "rottura del canale di 20 barre (tartarughe)", "long", {"condizione": "close > massimo degli high delle 20 barre precedenti", "stop": "2 ATR(20) sotto il close", "target": None, "uscita": "chiudi quando close < minimo dei low delle 10 barre precedenti"}, "R medio fra -0,05 e +0,25; win rate sotto 45%"),
    "SOLUSDT-004": ("I-02", "rottura del canale di 20 barre (tartarughe)", "short", {"condizione": "close < minimo dei low delle 20 barre precedenti", "stop": "2 ATR(20) sopra il close", "target": None, "uscita": "chiudi quando close > massimo degli high delle 10 barre precedenti"}, "R medio fra -0,1 e +0,2"),
    "SOLUSDT-005": ("I-03", "incrocio del close sopra 1,01 x SMA50, tenuta fissa", "long", {"condizione": "close[i-1] <= 1,01 SMA50[i-1] e close[i] > 1,01 SMA50[i]", "stop": "3 ATR(14) sotto", "target": None, "uscita": "a tempo dopo 60 barre"}, "R medio fra -0,05 e +0,2"),
    "SOLUSDT-006": ("I-04", "RSI(2) sotto 5 sopra la SMA200 (Connors)", "long", {"condizione": "close > SMA200 e RSI(2) < 5", "stop": "3 ATR(14) sotto", "target": None, "uscita": "chiudi quando close > SMA5"}, "R medio fra -0,05 e +0,15; win rate sopra 60%"),
    "SOLUSDT-007": ("I-04", "RSI(2) sopra 95 sotto la SMA200 (Connors)", "short", {"condizione": "close < SMA200 e RSI(2) > 95", "stop": "3 ATR(14) sopra", "target": None, "uscita": "chiudi quando close < SMA5"}, "R medio fra -0,1 e +0,1"),
    "SOLUSDT-008": ("I-05", "inversione dopo una barra oltre 3 sigma", "long", {"condizione": "rendimento della barra < -3 sigma dei rendimenti delle 168 barre precedenti", "stop": "2 ATR(14) sotto", "target": None, "uscita": "a tempo dopo 6 barre"}, "R medio fra -0,1 e +0,1"),
    "SOLUSDT-009": ("I-05", "inversione dopo una barra oltre 3 sigma", "short", {"condizione": "rendimento della barra > +3 sigma dei rendimenti delle 168 barre precedenti", "stop": "2 ATR(14) sopra", "target": None, "uscita": "a tempo dopo 6 barre"}, "R medio fra -0,15 e +0,05"),
    "SOLUSDT-010": ("I-06", "inversione dei cali con volume alto", "long", {"condizione": "rendimento < -2 sigma(90 barre precedenti) e volume > 2 x media del volume delle 42 barre precedenti", "stop": "2 ATR(14) sotto", "target": None, "uscita": "a tempo dopo 6 barre"}, "R medio fra -0,1 e +0,15"),
    "SOLUSDT-011": ("I-07", "NR7 e rottura confermata alla chiusura", "long", {"condizione": "barra i-1 NR7 (escursione minima fra le barre i-7..i-1) e close[i] > high[i-1]", "stop": "low[i-1]", "target": None, "uscita": "a tempo dopo 6 barre"}, "R medio fra -0,1 e +0,1"),
    "SOLUSDT-012": ("I-07", "NR7 e rottura confermata alla chiusura", "short", {"condizione": "barra i-1 NR7 e close[i] < low[i-1]", "stop": "high[i-1]", "target": None, "uscita": "a tempo dopo 6 barre"}, "R medio fra -0,1 e +0,1"),
    "SOLUSDT-013": ("I-08", "lunedi' (giorno della settimana)", "long", {"condizione": "la barra di segnale e' la domenica UTC (ingresso all'apertura del lunedi')", "stop": "2 ATR(14) sotto", "target": None, "uscita": "a tempo dopo 1 barra"}, "R medio fra -0,05 e +0,1"),
    "SOLUSDT-014": ("I-09", "prima mezz'ora UTC -> ultima mezz'ora", "long", {"condizione": "alla chiusura della barra 23:00-23:30 UTC, close > open della barra 00:00-00:30 dello stesso giorno", "stop": "2 ATR(14) sotto", "target": None, "uscita": "a tempo dopo 1 barra"}, "R medio fra -0,1 e +0,05"),
    "SOLUSDT-015": ("I-09", "prima mezz'ora UTC -> ultima mezz'ora", "short", {"condizione": "alla chiusura della barra 23:00-23:30 UTC, close < open della barra 00:00-00:30 dello stesso giorno", "stop": "2 ATR(14) sopra", "target": None, "uscita": "a tempo dopo 1 barra"}, "R medio fra -0,1 e +0,05"),
    "SOLUSDT-016": ("I-10", "funding estremo positivo: long affollati", "short", {"condizione": "media degli ultimi 3 tassi di funding (istante <= chiusura della barra) > 0,0005", "stop": "2 ATR(14) sopra", "target": None, "uscita": "a tempo dopo 3 barre"}, "R medio fra -0,1 e +0,2"),
    "SOLUSDT-017": ("I-10", "funding estremo negativo: short affollati", "long", {"condizione": "media degli ultimi 3 tassi di funding < -0,0005", "stop": "2 ATR(14) sotto", "target": None, "uscita": "a tempo dopo 3 barre"}, "R medio fra -0,1 e +0,2"),
    "SOLUSDT-018": ("I-11", "BTC guida, SOL segue", "long", {"condizione": "rendimento di BTC della barra > 2 sigma_BTC(168 barre precedenti) e rendimento di SOL della barra < quello di BTC", "stop": "2 ATR(14) sotto", "target": None, "uscita": "a tempo dopo 3 barre"}, "R medio fra -0,1 e +0,1"),
    "SOLUSDT-019": ("I-11", "BTC guida, SOL segue", "short", {"condizione": "rendimento di BTC < -2 sigma_BTC(168) e rendimento di SOL > quello di BTC", "stop": "2 ATR(14) sopra", "target": None, "uscita": "a tempo dopo 3 barre"}, "R medio fra -0,1 e +0,1"),
    "SOLUSDT-020": ("I-12", "giorno di volume alto", "long", {"condizione": "volume > 90 percentile del volume delle 49 barre precedenti", "stop": "2 ATR(14) sotto", "target": None, "uscita": "a tempo dopo 5 barre"}, "R medio fra -0,1 e +0,15"),
    "SOLUSDT-021": ("I-13", "attraversamento di un numero tondo", "long", {"condizione": "close[i-1] < L <= close[i], L multiplo di 5 x 10^(k-1), k = parte intera di log10(close[i-1])", "stop": "2 ATR(14) sotto", "target": None, "uscita": "a tempo dopo 4 barre"}, "R medio fra -0,1 e +0,1"),
    "SOLUSDT-022": ("I-13", "attraversamento di un numero tondo", "short", {"condizione": "close[i-1] > L >= close[i], stesso passo", "stop": "2 ATR(14) sopra", "target": None, "uscita": "a tempo dopo 4 barre"}, "R medio fra -0,1 e +0,1"),
}

S.update({
    "SOLUSDT-004b": ("I-02", "rottura del canale di 20 barre (tartarughe), su 2h", "short", {"condizione": "close < minimo dei low delle 20 barre precedenti", "stop": "2 ATR(20) sopra il close", "target": None, "uscita": "chiudi quando close > massimo degli high delle 10 barre precedenti"}, "R medio fra -0,1 e +0,2"),
    "SOLUSDT-005b": ("I-03", "incrocio del close sopra 1,01 x SMA50, tenuta fissa, su 2h", "long", {"condizione": "close[i-1] <= 1,01 SMA50[i-1] e close[i] > 1,01 SMA50[i]", "stop": "3 ATR(14) sotto", "target": None, "uscita": "a tempo dopo 120 barre (10 giorni)"}, "R medio fra -0,05 e +0,2"),
    "SOLUSDT-006b": ("I-04", "RSI(2) sotto 10 sopra la SMA200 (Connors)", "long", {"condizione": "close > SMA200 e RSI(2) < 10", "stop": "3 ATR(14) sotto", "target": None, "uscita": "chiudi quando close > SMA5"}, "R medio fra -0,05 e +0,15"),
    "SOLUSDT-007b": ("I-04", "RSI(2) sopra 90 sotto la SMA200 (Connors)", "short", {"condizione": "close < SMA200 e RSI(2) > 90", "stop": "3 ATR(14) sopra", "target": None, "uscita": "chiudi quando close < SMA5"}, "R medio fra -0,1 e +0,1"),
    "SOLUSDT-010b": ("I-06", "inversione dei cali con volume alto (soglia di volume 1,5)", "long", {"condizione": "rendimento < -2 sigma(90 barre precedenti) e volume > 1,5 x media del volume delle 42 barre precedenti", "stop": "2 ATR(14) sotto", "target": None, "uscita": "a tempo dopo 6 barre"}, "R medio fra -0,1 e +0,15"),
    "SOLUSDT-017b": ("I-10", "funding negativo: short affollati (soglia -0,0001)", "long", {"condizione": "media degli ultimi 3 tassi di funding < -0,0001", "stop": "2 ATR(14) sotto", "target": None, "uscita": "a tempo dopo 3 barre"}, "R medio fra -0,1 e +0,2"),
    "SOLUSDT-020b": ("I-12", "giorno di volume alto (80 percentile)", "long", {"condizione": "volume > 80 percentile del volume delle 49 barre precedenti", "stop": "2 ATR(14) sotto", "target": None, "uscita": "a tempo dopo 3 barre"}, "R medio fra -0,1 e +0,15"),
})

TF = {k: v for k, v in {
    "SOLUSDT-004b": "2h", "SOLUSDT-005b": "2h", "SOLUSDT-006b": "4h", "SOLUSDT-007b": "4h", "SOLUSDT-010b": "4h",
    "SOLUSDT-017b": "8h", "SOLUSDT-020b": "1d",
    "SOLUSDT-001": "1d", "SOLUSDT-002": "1d", "SOLUSDT-003": "4h", "SOLUSDT-004": "4h", "SOLUSDT-005": "4h",
    "SOLUSDT-006": "4h", "SOLUSDT-007": "4h", "SOLUSDT-008": "1h", "SOLUSDT-009": "1h", "SOLUSDT-010": "4h",
    "SOLUSDT-011": "4h", "SOLUSDT-012": "4h", "SOLUSDT-013": "1d", "SOLUSDT-014": "30m", "SOLUSDT-015": "30m",
    "SOLUSDT-016": "8h", "SOLUSDT-017": "8h", "SOLUSDT-018": "1h", "SOLUSDT-019": "1h", "SOLUSDT-020": "1d",
    "SOLUSDT-021": "1h", "SOLUSDT-022": "1h"}.items()}

# ritocchi: (famiglia, ritocco_di, cosa cambia e perche')
EXTRA = {
    "SOLUSDT-023": ("SOLUSDT-015", "SOLUSDT-015",
                    "aggiunge il filtro 'close della barra di segnale sotto la SMA di 200 barre (30m, circa 4 giorni)'. "
                    "Perche': studio dei fallimenti di 015 sui dati di costruzione (voce SOLUSDT-N020): sotto la media "
                    "R medio +0,017 su 193 trade, sopra -0,046 su 173; la forza della prima mezz'ora non separa (terzili "
                    "+0,005 / -0,046 / +0,003). Stesso timeframe, direzione, meccanismo, stop e uscita."),
}
S["SOLUSDT-023"] = ("I-09", "prima mezz'ora UTC -> ultima mezz'ora, solo sotto la SMA200", "short",
                    {"condizione": "alla chiusura della barra 23:00-23:30 UTC, close < open della barra 00:00-00:30 dello stesso giorno, e close < SMA200 (30m)",
                     "stop": "2 ATR(14) sopra", "target": None, "uscita": "a tempo dopo 1 barra"},
                    "R medio fra -0,02 e +0,03; t contro la (b) fra 1 e 3 (il filtro e' scelto sui dati di costruzione: il t in costruzione e' gonfiato, giudica la validazione)")
EXTRA["SOLUSDT-024"] = ("SOLUSDT-015", "SOLUSDT-015",
                        "aggiunge il filtro 'giorno UTC in calo dall'apertura delle 00:00 al close della barra di segnale "
                        "(23:30)'. Perche': secondo studio dei fallimenti di 015 sui dati di costruzione (voce SOLUSDT-N021): "
                        "giorno in rialzo R -0,033 su 158 trade, in calo +0,003 su 208; e' il momentum dell'intera giornata, "
                        "lo stesso meccanismo della fonte (Gao et al. 2018). Non usa la media di 200 barre di 023. Stesso "
                        "timeframe, direzione, stop e uscita.")
S["SOLUSDT-024"] = ("I-09", "prima mezz'ora UTC -> ultima mezz'ora, solo nei giorni in calo", "short",
                    {"condizione": "alla chiusura della barra 23:00-23:30 UTC, close < open della barra 00:00-00:30 dello stesso giorno, e close della barra di segnale < open della barra 00:00", "stop": "2 ATR(14) sopra", "target": None, "uscita": "a tempo dopo 1 barra"},
                    "R medio fra -0,02 e +0,02; t contro la (b) fra 1 e 2,5 (filtro scelto sui dati di costruzione)")
TF_EXTRA = {"SOLUSDT-023": "30m", "SOLUSDT-024": "30m"}
TF.update(TF_EXTRA)


def scheda(vid):
    idea, mecc, direz, par, prev = S[vid]
    return idea, mecc, direz, par, prev


def trade_stimati(vid):
    return json.loads((BOZZE / f"conta_{vid}.json").read_text())["conta_trade"]["trade"]


def principale(comando, vid, n=None):
    idea, mecc, direz, par, prev = scheda(vid)
    famiglia, ritocco_di, cambia = EXTRA.get(vid, (vid, None, None))
    voce = {"id": vid, "idea": idea, "fonte": F[idea], "meccanismo": mecc, "timeframe": TF[vid], "direzione": direz,
            "parametri": par, "periodo": "costruzione", "trade_stimati": trade_stimati(vid)}
    if comando == "registra":
        voce.update({"tipo": "registrazione", "tipo_test": "variante", "famiglia": famiglia, "ritocco_di": ritocco_di,
                     "previsione": prev, "criterio_successo": CRITERIO, "variante_n": int(n)})
        if cambia:
            voce["cosa_cambia"] = cambia
    elif comando == "scarto":
        voce.update({"tipo": "scarto", "famiglia": famiglia, "ritocco_di": ritocco_di,
                     "motivo": f"trade stimati con conta_trade {voce['trade_stimati']} sotto il minimo di costruzione (70): non si testa, non consuma budget"})
    registro.aggiungi(voce)
    print("aggiunta", vid, voce["tipo"], voce["trade_stimati"])


if __name__ == "__main__":
    if sys.argv[1] == "scarto":
        for v in sys.argv[2:]:
            principale("scarto", v)
    else:
        principale(sys.argv[1], sys.argv[2], sys.argv[3])
