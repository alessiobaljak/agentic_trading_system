# M-001 — registrazione per la prova in avanti

Registrata il 18 ottobre 2026 **prima di calcolare qualunque cosa sul periodo A** (REGOLE.md, sezione 9), sul commit
`7d74270a1b36381516798d015dabf0ae187675c8`. Procedura: M-001c (finestra di 12 mesi, 10 celle; `idee/M-001/scheda.md`), **com'era su W**, sulle 24 monete della fase 2. Calcolo: `research/programma5/avanti/avanti.py`. Le procedure registrate insieme sono 3
(M-001c, M-002, M-003): soglia di p 0,05 / 3 = 0,0167. Verdetto a 400 trade chiusi o al 2027-03-31.

Unico cambio di codice dopo l'esame su W: in `strumenti/motore5.py` la tabella dei periodi ha in più il periodo
WA (e il caricatore del premio è com'era). Il controllo `riprova_W.py` rifà M-001c su W con il codice di oggi e dà **gli
stessi 18.435 trade** (`riprova_W.txt`): il cambio non tocca quello che la procedura fa.

## Impronte SHA-256 dei file della prova

| File | SHA-256 |
|---|---|
| `research/programma5/strumenti/meta.py` | `b08a2c08c78b0bf5f9ef5797895469cd18d073f2b382d7baca1ab9545898603f` |
| `research/programma5/strumenti/meta2.py` | `e19d3d56f8e60a937a1d3189fe6cfba8603592c88ff5eddab22058b3761f9d9d` |
| `research/programma5/strumenti/motore5.py` | `bfb135485fd2c191115e447f11e340e19fb1e959ba9aa44f84c62fcac0f12fb0` |
| `research/programma5/strumenti/ore.py` | `33b77cc8d83953e693df5fec74a45ec50effe57fea54d8cf49f37416dc62ab4b` |
| `research/programma5/strumenti/esplora_fase2.py` | `64566f81e0169caa17f13bc3395cb58563d2edb5bb44c23533ea17f2b305ba5e` |
| `research/programma5/strumenti/esplora_calendario.py` | `d1ff8f0c19f73ca39ceeb6e05bebe5bf027ca82665aed371082f0811d2f92376` |
| `research/programma5/strumenti/fase2.py` | `70e7e7b3af44f75db93e6b0cbbb024ce8d29f00ae630b57d34230f453f8c2ac1` |
| `research/programma5/avanti/avanti.py` | `0c9754e7e62c083274924280c6f2fa1af8a989c9f5c38beff0ebda691c44b8ea` |
| `research/programma5/universo_top100.json` | `ae68368792b49fa6018b44afd40aa86dd34212fc981c680f789877e5000f7bde` |
