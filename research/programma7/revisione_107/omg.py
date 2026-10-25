import sys; sys.path.insert(0,'/tmp/revisore107')
from candele import *
for s, d0, d1 in [('OMGUSDT','2024-12-15 20:00','2024-12-16 14:00'), ('OMGUSDT','2025-01-31 05:00','2025-01-31 12:00'), ('MAVIAUSDT','2024-12-16 05:00','2024-12-16 12:00'), ('CTKUSDT','2024-04-01 05:00','2024-04-01 12:00')]:
    v = orev(s)
    h0 = int(pd.Timestamp(d0, tz='UTC').timestamp()//3600); h1 = int(pd.Timestamp(d1, tz='UTC').timestamp()//3600)
    x = v.loc[h0:h1].copy(); x.index = [f(h) for h in x.index]
    print('==', s); print(x.to_string())
