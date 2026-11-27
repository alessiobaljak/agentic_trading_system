import sys
sys.path.insert(0, '/home/user/agentic_trading_system')
import numpy as np
from research.programma6 import asticella as a, terza as te
serie, soli = a.mazzo()
gr = a.gruppi(serie, a.TAGLIO)
g110 = [g for g in gr if '110 SS' in g['membri']]
print('famiglia di 110 SS:', [(round(g['sharpe'],2), g['membri']) for g in g110])
print('110 SS da sola: Sharpe', round(a.sharpe(serie['110 SS'].dropna()),2), 'settimane', int(serie['110 SS'].notna().sum()))
