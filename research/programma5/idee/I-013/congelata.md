# I-013 — regola congelata

Congelata prima di aprire V (REGOLE.md, sezione 4), sul commit `07835e61b235ee358fb9ae4e6a53424fccb872bc`. Le varianti, i valori e il codice qui sotto non si cambiano più per questa idea: V e R si calcolano con questi file, e un file con un'impronta diversa vuol dire un'idea nuova.

Soglia di V: p ≤ 0,005 / 3 = 0.00167 (REGOLE.md, sezione 5).

## Le varianti

```json
{
 "I-013a": {
  "w": 4,
  "k": 3,
  "lato": "giu",
  "h": 1
 },
 "I-013b": {
  "w": 4,
  "k": 3,
  "lato": "giu",
  "h": 4
 },
 "I-013c": {
  "w": 4,
  "k": 3,
  "lato": "su",
  "h": 24
 }
}
```

## Su C (da `C.json`)

| Variante | Trade | Netto | Intervallo al 95% | Caso (netto) |
|---|---|---|---|---|
| I-013a | 854 | +0.345% | +0.062; +0.660 | -0.134% |
| I-013b | 854 | +0.803% | +0.189; +1.442 | -0.082% |
| I-013c | 982 | +1.578% | +0.595; +2.763 | +0.712% |

## Impronte SHA-256 dei file del calcolo

| File | SHA-256 |
|---|---|
| `research/programma5/idee/I-013/scheda.md` | `98c2f10fd9b13a3c63883bb9c716c7e2c6cc3afefd87d720cf4fb6f94fb6cdef` |
| `research/programma5/idee/I-013/calcolo.py` | `182d67e75d05f56c0e00296b00de8038672f08702bfa87f99fa133e30f7fab61` |
| `research/programma5/strumenti/motore5.py` | `f2ba6d8a5d5c77058aebfbf9aa731b2af7a950db8e08b363e83afe7d50d21bfc` |
| `research/programma5/strumenti/ore.py` | `33b77cc8d83953e693df5fec74a45ec50effe57fea54d8cf49f37416dc62ab4b` |
| `research/programma5/strumenti/eventi.py` | `4e761db8d3fcb442514e84efc8e9c618a168b2aa624158a5b2c46e05c43ac5e6` |
| `research/programma5/strumenti/idee_minuti.py` | `f5f3f6f67f3230b45274df920896e9608e8a3732353bd86962dcdfdc429a0a20` |
| `research/programma5/strumenti/idee_ore.py` | `ad10f194c9c686374ac2e5ebcab60d2a87093e5a42c712b3f74a3d44bf4c7943` |
| `research/programma5/strumenti/idee_giorno.py` | `6869bf8f2c47223e05dc4b5c11cef4640df5689ea66d5ce5e144e68edcb59f5f` |
| `research/programma5/strumenti/esplosioni_oi.py` | `e1c14982f54ef15ee64776fb92e789d7e7b6e6c8549b2811f40c4ba42bb46aa4` |
| `research/programma5/strumenti/rapporto.py` | `7ac82335da61a6f099e4d96b04c1bf6a33ce38712156f1e03a1a6caf4960a0a9` |
