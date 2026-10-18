# I-017 — regola congelata

Congelata prima di aprire V (REGOLE.md, sezione 4), sul commit `7d2188b9ba63a380c6a92b6ffa419d09ea1aaaec`. Le varianti, i valori e il codice qui sotto non si cambiano più per questa idea: V e R si calcolano con questi file, e un file con un'impronta diversa vuol dire un'idea nuova.

Prova solo su R (REGOLE.md, 6ter, punto 3): V è costruzione; su R p ≤ 0.005 / numero delle varianti portate su R, con tutte le condizioni di R e il giorno migliore tolto.

## Le varianti

```json
{
 "I-017c1": {
  "tipo": "limite",
  "k": 6,
  "H": 240
 },
 "I-017c2": {
  "tipo": "limite",
  "k": 4,
  "H": 240
 },
 "I-017c3": {
  "tipo": "crollo",
  "w": 24,
  "k": 3,
  "h": 4
 },
 "I-017c4": {
  "tipo": "crollo",
  "w": 4,
  "k": 5,
  "h": 12
 },
 "I-017c5": {
  "tipo": "sconto",
  "w": 4,
  "k": 3,
  "h": 4
 },
 "I-017c6": {
  "tipo": "sconto",
  "w": 1,
  "k": 3,
  "h": 4
 },
 "I-017c7": {
  "tipo": "premio_basso",
  "q": 0.01,
  "h": 4
 }
}
```

## Su C (da `C.json`)

| Variante | Trade | Netto | Intervallo al 95% | Caso (netto) |
|---|---|---|---|---|
| I-017c1 | 916 | +1.687% | +0.929; +2.488 | -0.105% |
| I-017c2 | 2509 | +0.810% | +0.445; +1.212 | -0.053% |
| I-017c3 | 327 | +2.320% | +0.993; +3.899 | -0.151% |
| I-017c4 | 283 | +2.511% | +1.195; +3.746 | -0.362% |
| I-017c5 | 602 | +1.257% | +0.536; +2.026 | -0.179% |
| I-017c6 | 758 | +1.189% | +0.407; +2.007 | -0.169% |
| I-017c7 | 2737 | +0.280% | +0.040; +0.545 | -0.132% |

## Impronte SHA-256 dei file del calcolo

| File | SHA-256 |
|---|---|
| `research/programma5/idee/I-017/scheda.md` | `f18bdc1df33484417be8dd0894498ead72bc01b1c9d9d4cccff7aabe75d25bb9` |
| `research/programma5/idee/I-017/calcolo.py` | `98b32bd9bd393610a88849986b62ac784b94d4f32e6eb4d7defd3a193858b5ea` |
| `research/programma5/idee/I-017/esame.json` | `b23c01f338250518359a6c62e2c01b5f5934e92c87e27bec8a91cf7dbcf21de3` |
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
