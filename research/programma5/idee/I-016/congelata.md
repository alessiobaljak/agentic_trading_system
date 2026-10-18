# I-016 — regola congelata

Congelata prima di aprire V (REGOLE.md, sezione 4), sul commit `2d08e31ca0d02e21570e5e9c3592b0c23ecc9be9`. Le varianti, i valori e il codice qui sotto non si cambiano più per questa idea: V e R si calcolano con questi file, e un file con un'impronta diversa vuol dire un'idea nuova.

Soglia di V: p ≤ 0,005 / 3 = 0.00167 (REGOLE.md, sezione 5).

## Le varianti

```json
{
 "I-016a": {
  "k": 6,
  "H": 240
 },
 "I-016b": {
  "k": 4,
  "H": 240
 },
 "I-016c": {
  "k": 3,
  "H": 15
 }
}
```

## Su C (da `C.json`)

| Variante | Trade | Netto | Intervallo al 95% | Caso (netto) |
|---|---|---|---|---|
| I-016a | 916 | +1.687% | +0.929; +2.488 | -0.105% |
| I-016b | 2509 | +0.810% | +0.445; +1.212 | -0.053% |
| I-016c | 6713 | +0.172% | +0.056; +0.295 | -0.103% |

## Impronte SHA-256 dei file del calcolo

| File | SHA-256 |
|---|---|
| `research/programma5/idee/I-016/scheda.md` | `07e39f303e6c4d5277600592ad3a1562f3bed75a5b6610c6d574676e2e559ddb` |
| `research/programma5/idee/I-016/calcolo.py` | `3a413d50f11245e51b66c77c83e3f2f1915ef99f86f2c9801536edb6e58c4c2e` |
| `research/programma5/strumenti/motore5.py` | `f2ba6d8a5d5c77058aebfbf9aa731b2af7a950db8e08b363e83afe7d50d21bfc` |
| `research/programma5/strumenti/ore.py` | `33b77cc8d83953e693df5fec74a45ec50effe57fea54d8cf49f37416dc62ab4b` |
| `research/programma5/strumenti/eventi.py` | `4e761db8d3fcb442514e84efc8e9c618a168b2aa624158a5b2c46e05c43ac5e6` |
| `research/programma5/strumenti/idee_minuti.py` | `f5f3f6f67f3230b45274df920896e9608e8a3732353bd86962dcdfdc429a0a20` |
| `research/programma5/strumenti/idee_ore.py` | `ad10f194c9c686374ac2e5ebcab60d2a87093e5a42c712b3f74a3d44bf4c7943` |
| `research/programma5/strumenti/idee_giorno.py` | `6869bf8f2c47223e05dc4b5c11cef4640df5689ea66d5ce5e144e68edcb59f5f` |
| `research/programma5/strumenti/esplosioni_oi.py` | `e1c14982f54ef15ee64776fb92e789d7e7b6e6c8549b2811f40c4ba42bb46aa4` |
| `research/programma5/strumenti/rapporto.py` | `7ac82335da61a6f099e4d96b04c1bf6a33ce38712156f1e03a1a6caf4960a0a9` |
