# J-001 — regola congelata

Congelata prima di aprire V (REGOLE.md, sezione 4), sul commit `a382af3e9f1178c822ea3da6cc4dcef7f14566be`. Le varianti, i valori e il codice qui sotto non si cambiano più per questa idea: V e R si calcolano con questi file, e un file con un'impronta diversa vuol dire un'idea nuova.

Prova su V2, una volta (REGOLE.md, sezioni 7 e 7bis): p ≤ 0,005 / 3 = 0.00167, costi doppi, senza il giorno migliore, tutte e due le metà, 60% delle monete con almeno 20 trade, almeno 200 trade.

## Le varianti

```json
{
 "J-001a": {
  "cella": "G1 w24 k3 su h24",
  "verso": "segue"
 },
 "J-001b": {
  "cella": "G1 w24 k3 su h12",
  "verso": "segue"
 },
 "J-001c": {
  "cella": "G1 w24 k3 su h72",
  "verso": "segue"
 }
}
```

## Su C2 (da `C2.json`)

| Variante | Trade | Netto | Intervallo al 95% | Caso (netto) |
|---|---|---|---|---|
| J-001a | 360 | +1.738% | +0.784; +2.711 | +0.187% |
| J-001b | 360 | +0.801% | +0.178; +1.434 | -0.080% |
| J-001c | 286 | +2.667% | +1.026; +4.365 | +1.004% |

## Impronte SHA-256 dei file del calcolo

| File | SHA-256 |
|---|---|
| `research/programma5/idee/J-001/scheda.md` | `6d5b7c35afdab4955657b4adbb7ebb17a794b0de2df7c97c51c974741a1fdbac` |
| `research/programma5/idee/J-001/calcolo.py` | `b2cf11dabb170aa35fdea05b204c86fda0eaeae0d603264d20bdca7e7e29371d` |
| `research/programma5/idee/J-001/esame.json` | `579b49e71b9ac4b32da81b890195ce2b9693926707cc48e86db4b1daa9921346` |
| `research/programma5/strumenti/motore5.py` | `8d1e30ab0be6d81c3b7c3faf186a4e547dcc93c03df1764eecefb1b597f96b9b` |
| `research/programma5/strumenti/ore.py` | `33b77cc8d83953e693df5fec74a45ec50effe57fea54d8cf49f37416dc62ab4b` |
| `research/programma5/strumenti/eventi.py` | `4e761db8d3fcb442514e84efc8e9c618a168b2aa624158a5b2c46e05c43ac5e6` |
| `research/programma5/strumenti/idee_minuti.py` | `f5f3f6f67f3230b45274df920896e9608e8a3732353bd86962dcdfdc429a0a20` |
| `research/programma5/strumenti/idee_ore.py` | `ad10f194c9c686374ac2e5ebcab60d2a87093e5a42c712b3f74a3d44bf4c7943` |
| `research/programma5/strumenti/idee_ore2.py` | `2d2c7c91dee432174d5e8683705ce985e3f4a9905fb9487b3290a27db84d7f95` |
| `research/programma5/strumenti/scalping.py` | `6b5ad9a6c48ac15763d0c131a5b04587f0e5b31f70815a78f586ed0ca6cb3fc7` |
| `research/programma5/strumenti/idee_fase2.py` | `6d47620b83a7db57d6ec8e63db55f6ec49ade80fe38ca0c96cfb22b95f4bc51b` |
| `research/programma5/strumenti/esplora_fase2.py` | `64566f81e0169caa17f13bc3395cb58563d2edb5bb44c23533ea17f2b305ba5e` |
| `research/programma5/strumenti/esplora_calendario.py` | `d1ff8f0c19f73ca39ceeb6e05bebe5bf027ca82665aed371082f0811d2f92376` |
| `research/programma5/strumenti/esplora_limiti.py` | `6d35500871c2003340e3ca2bc57c88a0b703612a6d9a401c504dbc4809bc6a37` |
| `research/programma5/strumenti/fase2.py` | `70e7e7b3af44f75db93e6b0cbbb024ce8d29f00ae630b57d34230f453f8c2ac1` |
| `research/programma5/strumenti/idee_giorno.py` | `6869bf8f2c47223e05dc4b5c11cef4640df5689ea66d5ce5e144e68edcb59f5f` |
| `research/programma5/strumenti/esplosioni_oi.py` | `e1c14982f54ef15ee64776fb92e789d7e7b6e6c8549b2811f40c4ba42bb46aa4` |
| `research/programma5/strumenti/rapporto.py` | `cb4c818555c42f2b0e5d77edf25326b3de87b3ad0c3b7a894cd3828798d2d762` |
| `research/programma5/strumenti/esplorazione.py` | `987609399b1954c9f7b5722fc08be109b3cbd3fe33e272adb8ffccdad6f8a383` |
