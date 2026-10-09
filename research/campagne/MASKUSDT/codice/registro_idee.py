"""Metadati delle varianti delle idee nuove (ipotesi.md), letti da campagna.py. Uso: python campagna.py registro_idee <ID>..."""
import varianti_idee as v

F = {
    "I-01": "Moskowitz, Ooi, Pedersen, «Time Series Momentum», Journal of Financial Economics 104(2), 2012; Liu, Tsyvinski, «Risks and Returns of Cryptocurrency», Review of Financial Studies 34(6), 2021 (NBER 24877, 2018)",
    "I-02": "Brock, Lakonishok, LeBaron, «Simple Technical Trading Rules and the Stochastic Properties of Stock Returns», Journal of Finance 47(5), 1992",
    "I-03": "Jegadeesh, «Evidence of Predictable Behavior of Security Returns», Journal of Finance 45(3), 1990; Lehmann, «Fads, Martingales, and Market Efficiency», Quarterly Journal of Economics 105(1), 1990",
    "I-04": "Connors, Alvarez, «Short Term Trading Strategies That Work», TradingMarkets Publishing, 2009",
    "I-05": "Schmeling, Schrimpf, Todorov, «Crypto Carry», BIS Working Papers n. 1087, aprile 2023",
    "I-06": "Gervais, Kaniel, Mingelgrin, «The High-Volume Return Premium», Journal of Finance 56(3), 2001",
    "I-07": "Kamps, Kleinberg, «To the moon: defining and detecting cryptocurrency pump-and-dumps», Crime Science 7, 2018; Li, Shin, Wang, «Cryptocurrency Pump-and-Dump Schemes», SSRN 3267041, 2018",
    "I-08": "Sifat, Mohamad, Mohamed Shariff, «Lead-Lag relationship between Bitcoin and Ethereum: Evidence from hourly and daily data», Research in International Business and Finance 50, 2019; Ciaian, Rajcaniova, Kancs, «Virtual relationships», Journal of International Financial Markets, Institutions and Money 52, 2018",
    "I-09": "Bollinger, «Bollinger on Bollinger Bands», McGraw-Hill, 2001",
    "I-10": "Nison, «Japanese Candlestick Charting Techniques», New York Institute of Finance, 1991; Caginalp, Laurent, «The predictive power of price patterns», Applied Mathematical Finance 5(3-4), 1998",
    "I-11": "Crabel, «Day Trading with Short Term Price Patterns and Opening Range Breakout», Traders Press, 1990",
    "I-12": "Chordia, Subrahmanyam, «Order imbalance and individual stock returns: Theory and evidence», Journal of Financial Economics 72(3), 2004; Silantyev, «Order flow analysis of cryptocurrency markets», Digital Finance 1, 2019",
    "I-13": "Liu, Tsyvinski, Wu, «Common Risk Factors in Cryptocurrency», Journal of Finance 77(2), 2022",
    "I-14": "He, Manela, Ross, von Wachter, «Fundamentals of Perpetual Futures», arXiv 2212.06888, dicembre 2022",
}
M = {
    "I-01": "momento nel tempo a 7 giorni", "I-02": "rottura del canale di 48 ore",
    "I-03": "ritorno dopo una barra oraria estrema", "I-04": "ritracciamento a 2 periodi nel trend",
    "I-05": "funding estremo contro la folla con leva", "I-06": "premio del volume alto (attenzione)",
    "I-07": "scarico dopo il pump con volume anomalo", "I-08": "MASK in ritardo su BTC",
    "I-09": "compressione delle bande e rottura", "I-10": "martello e stella cadente agli estremi di 24 ore",
    "I-11": "rottura dell'intervallo 00-02 UTC", "I-12": "squilibrio degli ordini aggressivi",
    "I-13": "trend di BTC che trascina MASK", "I-14": "scarto fra last e mark price",
}


def _m(idea, vid, par, prev, lo, hi):
    return {"idea": idea, "famiglia": vid, "fonte": F[idea], "meccanismo": M[idea], "parametri": par,
            "previsione": f"R medio dopo i costi fra {lo} e {hi}; {prev}", "previsione_r": [lo, hi]}


NO = "non batte nettamente la (b)"
VARIANTI = {
    "MASKUSDT-001": (v.I01L, _m("I-01", "MASKUSDT-001", {"rendimento_barre": 42, "soglia": 0, "stop_atr": 2, "target": None, "uscita_barre": 18}, NO, -0.15, 0.10)),
    "MASKUSDT-002": (v.I01S, _m("I-01", "MASKUSDT-002", {"rendimento_barre": 42, "soglia": 0, "stop_atr": 2, "target": None, "uscita_barre": 18}, NO, -0.10, 0.15)),
    "MASKUSDT-003": (v.I02L, _m("I-02", "MASKUSDT-003", {"canale_barre": 48, "stop_atr": 2, "target": None, "uscita_barre": 24}, NO, -0.15, 0.05)),
    "MASKUSDT-004": (v.I02S, _m("I-02", "MASKUSDT-004", {"canale_barre": 48, "stop_atr": 2, "target": None, "uscita_barre": 24}, NO, -0.10, 0.10)),
    "MASKUSDT-005": (v.I03L, _m("I-03", "MASKUSDT-005", {"deviazioni": 3, "finestra_dev": 168, "stop_atr": 2, "target_rapporto": 1, "uscita_barre": 6}, "forse batte la (b)", -0.10, 0.10)),
    "MASKUSDT-006": (v.I03S, _m("I-03", "MASKUSDT-006", {"deviazioni": 3, "finestra_dev": 168, "stop_atr": 2, "target_rapporto": 1, "uscita_barre": 6}, NO, -0.15, 0.05)),
    "MASKUSDT-007": (v.I04L, _m("I-04", "MASKUSDT-007", {"media_trend": 200, "rsi_barre": 2, "rsi_soglia": 10, "media_uscita": 5, "stop_atr": 3, "uscita_max_barre": 48}, NO, -0.10, 0.05)),
    "MASKUSDT-008": (v.I04S, _m("I-04", "MASKUSDT-008", {"media_trend": 200, "rsi_barre": 2, "rsi_soglia": 90, "media_uscita": 5, "stop_atr": 3, "uscita_max_barre": 48}, NO, -0.10, 0.05)),
    "MASKUSDT-009": (v.I05S, _m("I-05", "MASKUSDT-009", {"percentile": 90, "settlement_precedenti": 270, "funding_minimo": 0, "stop_atr": 2, "uscita_barre": 3}, NO, -0.10, 0.15)),
    "MASKUSDT-010": (v.I05L, _m("I-05", "MASKUSDT-010", {"percentile": 10, "settlement_precedenti": 270, "funding_massimo": 0.0001, "stop_atr": 2, "uscita_barre": 3}, NO, -0.15, 0.15)),
    "MASKUSDT-011": (v.I06L, _m("I-06", "MASKUSDT-011", {"finestra_barre": 6, "riferimento_barre": 294, "multiplo": 2.5, "stop_atr": 3, "uscita_barre": 30}, NO, -0.20, 0.10)),
    "MASKUSDT-012": (v.I07S, _m("I-07", "MASKUSDT-012", {"finestra_barre": 3, "deviazioni": 3, "multiplo_volume": 3, "riferimento_barre": 168, "stop_atr": 2, "uscita_barre": 24}, NO, -0.15, 0.15)),
    "MASKUSDT-012b": (v.I07Sb, _m("I-07", "MASKUSDT-012b", {"finestra_barre": 3, "deviazioni": 2.5, "multiplo_volume": 2, "riferimento_barre": 168, "stop_atr": 2, "uscita_barre": 24}, NO, -0.15, 0.15)),
    "MASKUSDT-013": (v.I08L, _m("I-08", "MASKUSDT-013", {"deviazioni_btc": 2, "finestra_dev": 168, "frazione_mask": 0.5, "stop_atr": 2, "uscita_barre": 4}, NO, -0.15, 0.05)),
    "MASKUSDT-014": (v.I08S, _m("I-08", "MASKUSDT-014", {"deviazioni_btc": 2, "finestra_dev": 168, "frazione_mask": 0.5, "stop_atr": 2, "uscita_barre": 4}, NO, -0.15, 0.05)),
    "MASKUSDT-015": (v.I09L, _m("I-09", "MASKUSDT-015", {"bande_barre": 20, "bande_dev": 2, "percentile_larghezza": 20, "finestra_percentile": 500, "barre_compressione": 10, "stop_atr": 2, "target_rapporto": 2, "uscita_barre": 48}, NO, -0.15, 0.10)),
    "MASKUSDT-016": (v.I09S, _m("I-09", "MASKUSDT-016", {"bande_barre": 20, "bande_dev": 2, "percentile_larghezza": 20, "finestra_percentile": 500, "barre_compressione": 10, "stop_atr": 2, "target_rapporto": 2, "uscita_barre": 48}, NO, -0.15, 0.10)),
    "MASKUSDT-017": (v.I10L, _m("I-10", "MASKUSDT-017", {"ombra_su_corpo": 2, "ombra_opposta_max": 0.25, "estremo_barre": 24, "stop_atr": 2, "target_rapporto": 1, "uscita_barre": 12}, NO, -0.15, 0.05)),
    "MASKUSDT-018": (v.I10S, _m("I-10", "MASKUSDT-018", {"ombra_su_corpo": 2, "ombra_opposta_max": 0.25, "estremo_barre": 24, "stop_atr": 2, "target_rapporto": 1, "uscita_barre": 12}, NO, -0.15, 0.05)),
    "MASKUSDT-019": (v.I11L, _m("I-11", "MASKUSDT-019", {"intervallo_ore_utc": [0, 1], "rottura_ore_utc": [2, 11], "stop_atr": 1.5, "uscita": "chiusura della barra delle 23 UTC"}, NO, -0.15, 0.05)),
    "MASKUSDT-020": (v.I11S, _m("I-11", "MASKUSDT-020", {"intervallo_ore_utc": [0, 1], "rottura_ore_utc": [2, 11], "stop_atr": 1.5, "uscita": "chiusura della barra delle 23 UTC"}, NO, -0.15, 0.05)),
    "MASKUSDT-021": (v.I12L, _m("I-12", "MASKUSDT-021", {"finestra_barre": 3, "percentile": 90, "finestra_percentile": 500, "stop_atr": 2, "uscita_barre": 6}, NO, -0.15, 0.05)),
    "MASKUSDT-022": (v.I12S, _m("I-12", "MASKUSDT-022", {"finestra_barre": 3, "percentile": 10, "finestra_percentile": 500, "stop_atr": 2, "uscita_barre": 6}, NO, -0.15, 0.05)),
    "MASKUSDT-023": (v.I13L, _m("I-13", "MASKUSDT-023", {"media_btc_barre": 42, "pendenza_barre": 6, "stop_atr": 2, "uscita_barre": 18}, NO, -0.15, 0.10)),
    "MASKUSDT-024": (v.I14S, _m("I-14", "MASKUSDT-024", {"percentile": 95, "finestra_percentile": 720, "stop_atr": 2, "uscita_barre": 8}, NO, -0.15, 0.05)),
    "MASKUSDT-025": (v.I14L, _m("I-14", "MASKUSDT-025", {"percentile": 5, "finestra_percentile": 720, "stop_atr": 2, "uscita_barre": 8}, NO, -0.15, 0.05)),
}
