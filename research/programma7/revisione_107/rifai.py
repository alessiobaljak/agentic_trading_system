"""Ripete la prova 107 (eventi, operazione, controllo, esame) con varianti, senza scrivere nel repository."""
import sys; sys.path.insert(0,'/tmp/revisore107')
from candele import *
import json
import numpy as np, pandas as pd
from research.programma7 import quarantacinquesima as q
from research.programma7 import quindicesima as g13
from research.programma6 import seconda as sc
from research.programma6 import trentesima as tr
from research.programma6 import esecuzione as es
from corretti import eventi_corretti

pan = sc.pannello()
t0 = pan['t0']; giorni = np.arange(pan['close'].shape[0]) + t0
jb = pan['simboli'].index('BTCUSDT'); fb = pd.Series(pan['funding'][:, jb], index=giorni)
cb = es.ore_di('BTCUSDT')
_ore = {}
def candele(s):
    if s not in _ore: _ore[s] = es.ore_di(s)
    return _ore[s]
def fund(s):
    return pd.Series(pan['funding'][:, pan['simboli'].index(s)], index=giorni)

def corri(ev, nome, controllo=True, operazione=g13.operazione, log=True):
    rng = np.random.default_rng(q.SEME)
    righe_ev, controlli = [], []
    for s, ms_a, ms_c, ida in ev:
        h_e, h_u = ms_a // 3_600_000 + 1, ms_c // 3_600_000 - 1
        if h_u - h_e < q.MIN_ORE: continue
        righe_ev.append((s, h_e, h_u, ida, ms_a))
        durata = h_u - h_e
        cand = np.arange(h_e - 365 * 24, h_e - 30 * 24 - durata)
        for h in rng.choice(cand, size=q.CONTROLLI, replace=False):
            controlli.append((s, int(h), int(h) + durata))
    righe = []
    for s, h_e, h_u, ida, ms_a in righe_ev:
        con = operazione(candele(s), cb, fund(s), fb, h_e, h_u, True)
        senza = operazione(candele(s), cb, fund(s), fb, h_e, h_u, False)
        if con and senza:
            righe.append({"data": sc.data(h_e // 24), "annuncio": int((h_e // 24 + 3) // 7), "simbolo": s, "id_annuncio": ida,
                          "h_e": h_e, "h_u": h_u, "ore": con["ore"], "r": con["r"], "fermata": con["fermata"], "r_senza": senza["r"]})
    df = pd.DataFrame(righe)
    out = {'df': df}
    if controllo:
        cr = []
        for s, a, b in controlli:
            op = g13.operazione(candele(s), cb, fund(s), fb, a, b, True)
            if op: cr.append({"simbolo": s, "r": op["r"]})
        co = pd.DataFrame(cr); out['co'] = co
    e_con, e_senza = tr.esame(df, 'r'), tr.esame(df, 'r_senza')
    out['e_con'], out['e_senza'] = e_con, e_senza
    if log:
        b, bs = e_con['boot'], e_senza['boot']
        print(f"[{nome}] eventi {b['eventi']} (settimane {b['annunci']}) con uscita {100*b['media']:+.2f}% p {b['p']:.4f} | senza 5 migl {100*e_con['senza_5_migliori']:+.2f}% | mediana {100*e_con['mediana']:+.2f}% | fermate {100*df['fermata'].mean():.0f}% | senza uscita {100*bs['media']:+.2f}% p {bs['p']:.4f} | per anno " + ", ".join(f"{a} {100*v['media']:+.2f}% ({v['eventi']})" for a, v in e_con['per_anno'].items()) + (f" | controllo {100*co['r'].mean():+.2f}% (n {len(co)} su {len(controlli)})" if controllo else ''))
    return out

if __name__ == '__main__':
    ev = q.eventi(set(pan['simboli']))
    o = corri(ev, 'originale')
    pub = pd.read_csv('/home/user/agentic_trading_system/research/programma7/risultati_quarantacinquesima/eventi_G13C.csv')
    print('uguale al pubblicato:', np.allclose(o['df']['r'].to_numpy(), pub['r'].to_numpy()), len(o['df']), len(pub))
    evc = [(s, a, cc, i) for s, a, c, i, cc, nota in eventi_corretti(pan) if cc is not None]
    oc = corri(evc, 'chiusure corrette')
    oc['df'].to_csv('/tmp/revisore107/eventi_corretti.csv', index=False)
    oc['co'].to_csv('/tmp/revisore107/controllo_corretti.csv', index=False)
    o['df'].to_csv('/tmp/revisore107/eventi_originali.csv', index=False)
    m = o['df'].merge(oc['df'], on=['simbolo','id_annuncio'], suffixes=('_pub','_corr'))
    d = m[(m['r_pub']-m['r_corr']).abs()>1e-9]
    print(d[['simbolo','ore_pub','ore_corr','r_pub','r_corr','r_senza_pub','r_senza_corr','fermata_corr']].round(3).to_string())
    print('somma differenze r:', (m['r_pub']-m['r_corr']).sum()/len(m))
