"""Prima e ultima barra di last, mark e BTC per timeframe (dichiarazione della Fase 0)."""
from datetime import date, datetime, timezone

from research.src import dati


def g(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


for tf in ["15m", "1h", "1d"]:
    last = dati.carica_candele("XRPUSDT", tf, date(2020, 1, 1), date(2023, 12, 31))
    mark = dati.carica_candele("XRPUSDT", tf, date(2020, 1, 1), date(2023, 12, 31), tipo="markPriceKlines")
    btc = dati.carica_candele("BTCUSDT", tf, date(2020, 1, 1), date(2023, 12, 31))
    print(tf, "last", g(last[0].ts), g(last[-1].ts), len(last), "| mark", g(mark[0].ts), g(mark[-1].ts), len(mark),
          "| btc", g(btc[0].ts), g(btc[-1].ts), len(btc))
