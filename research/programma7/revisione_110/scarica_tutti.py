import sys; sys.path.insert(0,'/tmp/revisore110/script')
import deribit as d, datetime as dt, csv
rows=list(csv.DictReader(open('/tmp/revisore110/dati/base.csv')))
n=0
for r in rows:
    g=dt.date.fromisoformat(r['data'])
    t0=int(dt.datetime(g.year,g.month,g.day,8,0,tzinfo=dt.timezone.utc).timestamp()*1000)
    tr=d.trades_window(r['moneta'],t0,t0+3600_000)
    n+=1
    if n%50==0: print(n, r['moneta'], r['data'], len(tr), flush=True)
print("FINE", flush=True)
