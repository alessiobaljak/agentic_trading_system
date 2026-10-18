# I-019 — regola congelata

Congelata prima di aprire V (REGOLE.md, sezione 4), sul commit `7d2188b9ba63a380c6a92b6ffa419d09ea1aaaec`. Le varianti, i valori e il codice qui sotto non si cambiano più per questa idea: V e R si calcolano con questi file, e un file con un'impronta diversa vuol dire un'idea nuova.

Soglia di V: p ≤ 0.05 / 3 = 0.01667; su R anche positivo togliendo il giorno migliore (REGOLE.md, 6ter).

## Le varianti

```json
{
 "I-019a": {
  "w": 4,
  "k": 3,
  "h": 72
 },
 "I-019b": {
  "w": 4,
  "k": 2,
  "h": 24
 },
 "I-019c": {
  "w": 4,
  "k": 2,
  "h": 72
 }
}
```

## Su C (da `C.json`)

| Variante | Trade | Netto | Intervallo al 95% | Caso (netto) |
|---|---|---|---|---|
| I-019a | 733 | +2.482% | +1.201; +3.783 | +1.695% |
| I-019b | 2103 | +0.836% | +0.361; +1.417 | +0.272% |
| I-019c | 1369 | +1.529% | +0.682; +2.424 | +1.079% |

## Impronte SHA-256 dei file del calcolo

| File | SHA-256 |
|---|---|
| `research/programma5/idee/I-019/scheda.md` | `2a01356ee5c7ce1cd0b8dbd3eadeb8154f2b49d71e8551262880803cd259cfe6` |
| `research/programma5/idee/I-019/calcolo.py` | `854dc96b7e3e54d22f0bd2a8d4f3e8d2139101f3382ffedee5a2e398756b0240` |
| `research/programma5/idee/I-019/esame.json` | `721242eec45fdbe47b384cf797f979cdf6837f8007376e5b1299c0e21efebf79` |
| `research/programma5/strumenti/motore5.py` | `f2ba6d8a5d5c77058aebfbf9aa731b2af7a950db8e08b363e83afe7d50d21bfc` |
| `research/programma5/strumenti/ore.py` | `33b77cc8d83953e693df5fec74a45ec50effe57fea54d8cf49f37416dc62ab4b` |
| `research/programma5/strumenti/eventi.py` | `4e761db8d3fcb442514e84efc8e9c618a168b2aa624158a5b2c46e05c43ac5e6` |
| `research/programma5/strumenti/idee_minuti.py` | `f5f3f6f67f3230b45274df920896e9608e8a3732353bd86962dcdfdc429a0a20` |
| `research/programma5/strumenti/idee_ore.py` | `ad10f194c9c686374ac2e5ebcab60d2a87093e5a42c712b3f74a3d44bf4c7943` |
| `research/programma5/strumenti/idee_ore2.py` | `2d2c7c91dee432174d5e8683705ce985e3f4a9905fb9487b3290a27db84d7f95` |
| `research/programma5/strumenti/idee_giorno.py` | `6869bf8f2c47223e05dc4b5c11cef4640df5689ea66d5ce5e144e68edcb59f5f` |
| `research/programma5/strumenti/esplosioni_oi.py` | `e1c14982f54ef15ee64776fb92e789d7e7b6e6c8549b2811f40c4ba42bb46aa4` |
| `research/programma5/strumenti/rapporto.py` | `e898fddc68ffca2e01dfe45e89ff14211ff85370b3dc3a60fadc8cecfc4f95b8` |
| `research/programma5/strumenti/esplorazione.py` | `987609399b1954c9f7b5722fc08be109b3cbd3fe33e272adb8ffccdad6f8a383` |
