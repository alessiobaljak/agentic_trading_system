# J-004 — regola congelata

Congelata prima di aprire V (REGOLE.md, sezione 4), sul commit `a382af3e9f1178c822ea3da6cc4dcef7f14566be`. Le varianti, i valori e il codice qui sotto non si cambiano più per questa idea: V e R si calcolano con questi file, e un file con un'impronta diversa vuol dire un'idea nuova.

Prova su V2, una volta (REGOLE.md, sezioni 7 e 7bis): p ≤ 0,005 / 3 = 0.00167, costi doppi, senza il giorno migliore, tutte e due le metà, 60% delle monete con almeno 20 trade, almeno 200 trade; solo sulle monete fuori dalla fase 1.

## Le varianti

```json
{
 "J-004a": {
  "cella": "F1 w24 k3 giu h24",
  "verso": "contro"
 },
 "J-004b": {
  "cella": "F1 w4 k5 giu h24",
  "verso": "contro"
 },
 "J-004c": {
  "cella": "F1 w24 k3 giu h72",
  "verso": "contro"
 }
}
```

## Su C2 (da `C2.json`)

| Variante | Trade | Netto | Intervallo al 95% | Caso (netto) |
|---|---|---|---|---|
| J-004a | 268 | +4.668% | +2.181; +7.248 | -0.231% |
| J-004b | 252 | +4.555% | +1.729; +7.481 | -0.188% |
| J-004c | 250 | +4.363% | +1.443; +7.059 | -0.456% |

## Impronte SHA-256 dei file del calcolo

| File | SHA-256 |
|---|---|
| `research/programma5/idee/J-004/scheda.md` | `fea4bb64881db4ccf5711607a9a76591075c8b40af232c12c4b79262d66952cf` |
| `research/programma5/idee/J-004/calcolo.py` | `3965534251df1642a7e2f2228e715bb3034ef6671658d14eb68e1ca93e7ebe4e` |
| `research/programma5/idee/J-004/esame.json` | `aab53fa6eaeaf98cc133449c4a08bd35272a141f9ba641e4a2588ad209c3a2d2` |
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
