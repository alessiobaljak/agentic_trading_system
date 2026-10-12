"""Fase 0: barre anomale (volume zero, massimo uguale al minimo, ombre oltre il 25% dalla chiusura
precedente) sulle serie tenute dell'intero in-sample. Solo dati."""

import json

from research.campagne.TRBUSDT.codice import banco

if __name__ == "__main__":
    out = {}
    for tf in ["15m", "1h", "4h", "1d"]:
        cs = banco.carica(tf, "validazione")["candele"]
        zero = sum(1 for c in cs if c.volume == 0)
        piatte = sum(1 for c in cs if c.high == c.low)
        ombre = []
        for p, c in zip(cs, cs[1:]):
            if c.high / p.close - 1 > 0.25 or 1 - c.low / p.close > 0.25:
                ombre.append((c.ts, round(c.high / p.close - 1, 3), round(1 - c.low / p.close, 3)))
        out[tf] = {"barre": len(cs), "volume_zero": zero, "massimo_uguale_minimo": piatte,
                   "ombre_oltre_25pct": len(ombre), "esempi": ombre[:10]}
    with open(banco.CARTELLA / "fase0_anomalie.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out))
