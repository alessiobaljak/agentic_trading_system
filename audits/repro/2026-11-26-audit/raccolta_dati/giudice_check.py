import sys, json
from collections import defaultdict
from datetime import datetime, timezone, timedelta
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.trader_copiati import giudice_balene as gb
lun = datetime(2026, 11, 30, tzinfo=timezone.utc)
pos, prezzi = gb.giri(lun - timedelta(days=28), lun)
dd = {d["indirizzo"]: d for d in json.load(open(sys.argv[1]))}
ore = sorted(pos)
per = defaultdict(list)
for t in ore:
    for ind, v in pos[t].items():
        per[ind].append((t, *v))
righe = []
for ind, d in dd.items():
    if d["fuori"]:
        continue
    serie = per[ind]
    merc_saltate = 0.0; somma_gp = 0.0; n_salt = 0; val_salt = 0.0; val_tot = 0.0
    for (t0, c0, p0), (t1, _, _) in zip(serie, serie[1:]):
        if t1 - t0 > gb.SALTO_MAX or not p0:
            continue
        pr0, pr1 = prezzi.get(t0, {}), prezzi.get(t1, {})
        rb = [pr1[m] / pr0[m] - 1 for m in gb.PANIERE if m in pr0 and m in pr1 and pr0[m]]
        rp = sum(rb) / len(rb) if rb else None
        for m, (q, v) in p0.items():
            val_tot += abs(q * pr0.get(m, 0))
            if m not in pr0 or m not in pr1 or not pr0[m] or rp is None:
                n_salt += 1
                if m in pr0 and rp is not None:
                    merc_saltate += q * pr0[m] * rp
                    val_salt += abs(q * pr0[m])
                continue
            r = pr1[m] / pr0[m] - 1
            somma_gp += q * pr0[m] * (r - rp)
    c = d["conto_medio"]
    righe.append((ind[:10], round(d["propria"] / c * 100, 2), round(somma_gp / c * 100, 2), round(-merc_saltate / c * 100, 2), n_salt, round(100 * val_salt / val_tot, 3) if val_tot else 0))
print("conto | propria % (script) | somma per moneta % | parte del mercato delle monete saltate % | intervalli-moneta saltati | quota valore saltato %")
for r in righe:
    print(r)
