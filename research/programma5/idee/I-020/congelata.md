# I-020 — regola congelata

Congelata prima di aprire V (REGOLE.md, sezione 4), sul commit `ce7d9edafa27e40231186d0c496827bea51c15f5`. Le varianti, i valori e il codice qui sotto non si cambiano più per questa idea: V e R si calcolano con questi file, e un file con un'impronta diversa vuol dire un'idea nuova.

Prova solo su R (REGOLE.md, 6ter, punto 3): V è costruzione; su R p ≤ 0.005 / numero delle varianti portate su R, con tutte le condizioni di R e il giorno migliore tolto.

## Le varianti

```json
{
 "I-020a": {
  "k": 3,
  "m": 0.5,
  "H": 60
 },
 "I-020b": {
  "k": 3,
  "m": 0.5,
  "H": 240
 },
 "I-020c": {
  "k": 3,
  "m": 1,
  "H": 240
 }
}
```

## Su C (da `C.json`)

| Variante | Trade | Netto | Intervallo al 95% | Caso (netto) |
|---|---|---|---|---|
| I-020a | 6821 | +0.192% | +0.140; +0.246 | -0.079% |
| I-020b | 6649 | +0.208% | +0.149; +0.267 | -0.066% |
| I-020c | 6121 | +0.321% | +0.216; +0.429 | -0.057% |

## Impronte SHA-256 dei file del calcolo

| File | SHA-256 |
|---|---|
| `research/programma5/idee/I-020/scheda.md` | `18eeb70476dd834fa1cc4ab77abd697b61c3cb189f5e7b2b4f27bfd824dc5497` |
| `research/programma5/idee/I-020/calcolo.py` | `915d9cdf2adffd5f30dcb90d848ff9af27e1b970e4c5f2e113ceb440321c96ef` |
| `research/programma5/idee/I-020/esame.json` | `b23c01f338250518359a6c62e2c01b5f5934e92c87e27bec8a91cf7dbcf21de3` |
| `research/programma5/strumenti/motore5.py` | `f2ba6d8a5d5c77058aebfbf9aa731b2af7a950db8e08b363e83afe7d50d21bfc` |
| `research/programma5/strumenti/ore.py` | `33b77cc8d83953e693df5fec74a45ec50effe57fea54d8cf49f37416dc62ab4b` |
| `research/programma5/strumenti/eventi.py` | `4e761db8d3fcb442514e84efc8e9c618a168b2aa624158a5b2c46e05c43ac5e6` |
| `research/programma5/strumenti/idee_minuti.py` | `f5f3f6f67f3230b45274df920896e9608e8a3732353bd86962dcdfdc429a0a20` |
| `research/programma5/strumenti/idee_ore.py` | `ad10f194c9c686374ac2e5ebcab60d2a87093e5a42c712b3f74a3d44bf4c7943` |
| `research/programma5/strumenti/idee_ore2.py` | `2d2c7c91dee432174d5e8683705ce985e3f4a9905fb9487b3290a27db84d7f95` |
| `research/programma5/strumenti/scalping.py` | `6b5ad9a6c48ac15763d0c131a5b04587f0e5b31f70815a78f586ed0ca6cb3fc7` |
| `research/programma5/strumenti/idee_giorno.py` | `6869bf8f2c47223e05dc4b5c11cef4640df5689ea66d5ce5e144e68edcb59f5f` |
| `research/programma5/strumenti/esplosioni_oi.py` | `e1c14982f54ef15ee64776fb92e789d7e7b6e6c8549b2811f40c4ba42bb46aa4` |
| `research/programma5/strumenti/rapporto.py` | `e898fddc68ffca2e01dfe45e89ff14211ff85370b3dc3a60fadc8cecfc4f95b8` |
| `research/programma5/strumenti/esplorazione.py` | `987609399b1954c9f7b5722fc08be109b3cbd3fe33e272adb8ffccdad6f8a383` |
