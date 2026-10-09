"""Fase 5: verifiche dello scettico, solo costruzione. Non sono varianti.

1. Correttezza del codice delle uscite a orario: orari d'ingresso e d'uscita dei trade di V07, V15, V26.
2. «E' solo il mercato» per la famiglia piu' vicina al caso (V24): la stessa regola sulle candele
   giornaliere last di BTCUSDT, costruzione (senza mark e senza funding di BTC, non scaricati:
   solo contesto), con la sua (b).
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune as C  # noqa: E402
import indicatori as I  # noqa: E402
import varianti as VV  # noqa: E402
from research.src import motore  # noqa: E402

for vid in ("V07", "V15", "V26"):
    spec = VV.VARIANTI[vid]
    ctx = C.contesto(spec["tf"], "costruzione", VV.extra_per)
    prep = spec["prepara"](ctx.candele, ctx.extra)
    ris = motore.esegui(ctx.candele, None, ctx.mark, ctx.funding, C.fabbrica(prep, ctx.candele, ctx.liq, "variante")(), C.PARAMETRI)
    ing = Counter(I.utc(t.ts_entrata).strftime("%H:%M") for t in ris.trades)
    usc = Counter((I.utc(t.ts_uscita).strftime("%H:%M"), t.esito) for t in ris.trades)
    stesso_giorno = sum(1 for t in ris.trades if I.utc(t.ts_entrata).date() == I.utc(t.ts_uscita - 1).date())
    print(vid, "ingressi (ora:conteggio)", dict(sorted(ing.items())[:6]), "...")
    print("   uscite piu' frequenti", usc.most_common(4), "| trade chiusi nello stesso giorno UTC", stesso_giorno, "su", len(ris.trades))

# 2. la regola di V24 su BTCUSDT
btc = C.fino_a_costruzione(C.candele_last("1d", "BTCUSDT"))
ctx_btc = C.Contesto("1d", btc, btc, [], C.liquida(btc), {})
out = C.valuta(ctx_btc, VV.VARIANTI["V24"]["prepara"], "costruzione")
m = out["metriche"]
print("V24 su BTCUSDT: trade", m["trade"], "R medio", round(m["r_medio"], 4), "per anno",
      {k: round(v, 3) for k, v in m["r_medio_per_anno"].items()},
      "t contro la (b)", round(out["baseline_b"]["t"], 2), "media (b)", round(out["baseline_b"]["media"], 4),
      "t contro la (a)", round(out["baseline_a"]["t"], 2))
C.scrivi_json(C.CARTELLA_DATI / "fase5_btc_v24.json", out)
