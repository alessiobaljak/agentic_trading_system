import sys
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np, pandas as pd
from research.programma6 import esecuzione as es, dati as d6, quarta as qa, seconda as sc
for s, L in [('CRVUSDT','2021-03-25'),('SUSHIUSDT','2021-03-11'),('COTIUSDT','2021-08-26'),('1000SHIBUSDT','2021-09-09'),('ZENUSDT','2021-09-16'),('CVCUSDT','2021-11-03'),('GALAUSDT','2021-11-16'),('SANDUSDT','2022-05-26'),('CELRUSDT','2022-08-16'),('INJUSDT','2022-09-20'),('HBARUSDT','2022-10-13'),('LDOUSDT','2022-11-17'),('LITUSDT','2022-12-06'),('EGLDUSDT','2022-12-07'), ('ADAUSDT','2021-03-18'), ('DOGEUSDT','2021-06-03')]:
    b = d6.barre(s, '1h')
    c = es.ore_di(s)
    z = qa.ore(s)
    g = int(pd.Timestamp(L).timestamp()//86400) + 1
    h0 = g*24
    print(s, L, 'p6 pkl:', (sc.data(b['minuto'].min()//1440) if not b.empty else '-'), 'ore_di inizio', sc.data(c.index.min()//24) if len(c) else '-',
          'h0 in ore_di', h0 in c.index, '| zip ore inizio', sc.data(z.index.min()//24) if len(z) else '-', 'h0 in zip', (h0 in z.index) if len(z) else False)
