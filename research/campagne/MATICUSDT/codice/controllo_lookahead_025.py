"""Ricerca di un lookahead nel candidato MATICUSDT-025 dopo il crollo col ritardo (Fase 4, punto 6).

1. Controllo del codice a mano (scritto nel log).
2. Controllo meccanico: ricalcola il segnale alla barra i usando SOLO le barre 0..i (serie
   troncata), per un campione di barre, e confronta con l'array calcolato su tutta la serie: se un
   valore cambia, l'array usa barre future.
3. Profilo del rendimento dopo i segnali: rendimento medio (short, in %) di ciascuna delle 12 barre
   dopo la barra di segnale (barra i+1 = la prima in posizione). Se il movimento sta quasi tutto
   nella prima ora, il crollo col ritardo e' un effetto che svanisce in fretta, non un errore.
Solo dati di costruzione.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candidato_025 as cand  # noqa: E402
import quadro  # noqa: E402

s = quadro.carica("1h")
reg = cand.fabbrica()(s)
segnali = np.flatnonzero(reg.ingresso & ~s.vietato)

# 2. troncamento: per 40 barre di segnale e 40 barre senza segnale, ricalcolo su serie troncata
rng = np.random.default_rng(0)
senza = np.setdiff1d(np.arange(1000, s.n), segnali)
campione = list(rng.choice(segnali, 40, replace=False)) + list(rng.choice(senza, 40, replace=False))
diversi = 0
for i in campione:
    i = int(i)
    t = quadro.Serie(tf=s.tf, periodo=s.periodo, candele=s.candele[:i + 1], mark=s.mark[:i + 1], funding=s.funding,
                     ms_barra=s.ms_barra, ts=s.ts[:i + 1], o=s.o[:i + 1], h=s.h[:i + 1], l=s.l[:i + 1], c=s.c[:i + 1],
                     v=s.v[:i + 1], qv=s.qv[:i + 1], btc_c=s.btc_c[:i + 1], btc_o=s.btc_o[:i + 1],
                     vietato=s.vietato[:i + 1])
    t.indice_di_ts = {int(x): k for k, x in enumerate(t.ts)}
    rt = cand.fabbrica()(t)
    if bool(rt.ingresso[i]) != bool(reg.ingresso[i]) or not np.isclose(rt.stop[i], reg.stop[i], equal_nan=True):
        diversi += 1

# 3. profilo dopo i segnali (rendimento dello short di ogni barra successiva, open->close, in %)
profilo = {}
for k in range(1, 13):
    idx = segnali + k
    idx = idx[idx < s.n]
    profilo[f"barra_i+{k}"] = round(float(np.mean(-(s.c[idx] / s.o[idx] - 1)) * 100), 4)
casuale = round(float(np.mean(-(s.c[1:] / s.o[1:] - 1)) * 100), 4)
out = {"barre_controllate": len(campione), "segnali_diversi_su_serie_troncata": diversi,
       "segnali": int(len(segnali)), "profilo_short_pct": profilo, "media_short_pct_di_una_barra_qualunque": casuale}
(Path(__file__).resolve().parents[1] / "esiti" / "verifica_025_lookahead.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out))
