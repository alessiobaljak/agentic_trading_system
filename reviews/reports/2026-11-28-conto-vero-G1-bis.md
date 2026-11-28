# Riesame del 28 novembre 2026: la regola del 269 (sotto il valore minimo parte solo la chiusura intera)

### Riepilogo e verdetto
**APPROVE con una condizione** per il commit: il codice e il documento vanno bene così come sono (`demo_binance.py` 3cac1aeb, `docs/conto_vero.md`
dfd87e2d); nel commit va aggiunto il test del 274 (testo qui sotto, provato: passa sul codice di oggi e cade se il resto a mercato torna alla
regola vecchia). **Senza quel test: REQUEST CHANGES.** La regola vale uguale nei tre punti; l'inversione del 213 resta una chiusura intera; i
rifiuti restano contati; nient'altro cambia. Nuovi: 274 Medio (manca il test del resto a mercato), 275 Basso (testi). Il 269 è chiuso nel codice;
la scelta resta da far confermare ad Alessio insieme al riavvio (era la sua decisione 3 della revisione delle prove).

### Oggetto (branch, commit, file toccati, invarianti coinvolti)
- Branch `claude/brave-albattani-1b12fv`, modifica non committata sopra `3c0df1b` (in HEAD `demo_binance.py` 55ddb46e, `test_conto_vero_g1.py` a339cf45).
- Impronte (prime 8 cifre dell'md5): `bot/portafoglio/demo_binance.py` **3cac1aeb**, `tests/test_conto_vero_g1.py` **fdc96df8**, `docs/conto_vero.md` **dfd87e2d**.
- `git diff --stat`: 3 file, 24 righe in più e 17 in meno; nessun altro file del percorso toccato (`bot/risk/`, `firebase/`, `bot/main.py`,
  `bot/config.py`, `conto_vero.py`: diff vuoto).
- Invariante coinvolto: la regola dei minimi del demo e del conto vero (mappa, sezione 7).

### Checklist A–F
**A. Limiti fissi e interruttori** — NON APPLICABILE: `hard_limits.py`, `circuit_breakers.py`, `kill_switch.py`, Firestore e regole non toccati
(diff vuoto). Pulsanti e stop sul conto invariati.

**B. Ordini**
- Regola sotto il minimo nei tre punti: **OK**. `ordine_saltato` salta sotto il valore minimo tranne `chiude` (`demo_binance.py:347-355`);
  ordini limite con `obiettivo == 0.0` (`:382`); conto «sotto il minimo» con lo stesso controllo (`:407`); resto a mercato con `voluto == 0.0`
  (`:2053`), dove `voluto` è zero per le monete tolte perché `obiettivi` tiene solo i pesi diversi da zero (`:1874-1877`, `:2047`). Il conto vero
  usa gli stessi metodi (`conto_vero.py:350`, `:1063`; `chiudi_ordini` non ridefinito).
- «Solo riduzione» su ogni ordine sotto il minimo: **OK**. Se l'obiettivo è zero `riduce_soltanto` è vero (`:344`), quindi `reduceOnly` c'è
  sempre (`:386` → `:1834-1835`; `:2052`, `:2058-2059`). `-0.0 == 0.0` vale: anche un peso «meno zero» chiude.
- Inversione del 213 su una moneta che si può solo ridurre: **OK**, resta una chiusura intera. L'inversione non ha obiettivo zero, quindi si
  controlla l'ordine intero contro il minimo come prima (`:382`); se parte, diventa la chiusura `quantita_che_chiude` (posizione intera al passo,
  `:358-364`, `:1816-1831`) con «solo riduzione»; il resto a mercato mette `voluto = 0.0` (`:2048-2049`) e quindi chiude anche sotto il minimo.
  Il ripiego dopo -4140 è invariato (`:1849-1860`). Test `test_213_*` verdi. Nota (non nuova, invariata dal diff, coerente con la prova): un'
  inversione che in tutto resta sotto il minimo si salta, e la posizione piccola resta nel verso vecchio.
- Passi, quantità minima, identificativi, leva e margine: invariati.

**C. Stato e resilienza** — NON APPLICABILE (nessun cambio). **D. Separazione** — NON APPLICABILE (nessun cambio). **E. Segreti** — OK: nessun
segreto nel diff.

**F. Test**
- `python3 -B -m pytest tests/ -q -p no:cacheprovider`: **3134 passed in 177,73 s**, nessun fallimento.
- Mutazioni su una copia (`rev28nov_ter/`, script `mut269.py` nella cartella di lavoro): M1 limite torna a `riduce` → cade; M2 conto «sotto il
  minimo» torna a `riduce` → cade; **M3 resto a mercato torna a `riduce` → NON cade** (solo i 5 test che sulla copia falliscono già: git,
  dashboard, Firebase, requisiti); M4 resto a mercato salta anche la chiusura → cade; M5 e M6 (chiusura saltata o contata) → cadono.
  **PROBLEMA 274**.
- Rifiuti contati: codice invariato (`:1844-1868` con il peso, `:2063-2068` e `:2079-2083` per i resti); test dei rifiuti verdi. **OK**.

### Problemi
**274 — Medio — `tests/test_conto_vero_g1.py` (manca); codice `demo_binance.py:2053`**
- Il terzo punto della modifica (il resto a mercato) non ha un test per le riduzioni: se domani qualcuno rimette `riduce` a `:2053`, la suite
  resta verde (mutazione M3).
- Guasto concreto: una riduzione a limite eseguita in parte lascia un resto di pochi dollari; il bot lo manda a mercato «solo riduzione». Nessun
  rischio per i soldi («solo riduzione» non apre), ma il conto torna a fare in silenzio la regola giudicata peggiore (1,92 invece di 1,94) proprio
  dove passano molti ordini (sul demo circa il 58% del valore va a mercato, `audits/reports/2026-11-28-G1_CONTO_VERO_250.md:106`).
- Correzione (sessione principale), dopo `test_minimo_demo_chiude_la_posizione_sotto_il_minimo_anche_con_il_resto_a_mercato`; usa solo nomi già
  importati nel file. Provata sulla copia: passa con il codice di oggi, cade con M3 (parte `MARKET` 0.052 `reduceOnly`).

```python
def test_minimo_il_resto_a_mercato_di_una_riduzione_sotto_il_minimo_si_salta(tmp_path):
    """269: la riduzione da circa 2.000 a circa 1.000 USDT corti parte a limite; se dopo l'ora ne mancano 2,6 USDT (sotto i 5), il
    resto a mercato si salta come all'apertura: parte a mercato solo la chiusura intera."""
    finto = _Demo()
    finto.posizioni = {"AUSDT": 0.0, "BUSDT": -40.0}
    d, fb = _demo_semplice(tmp_path, finto, pesi={"BUSDT": -0.1})          # obiettivo −19,997: si compra 20,002 «solo riduzione»
    d.tick(T0)
    o = _ordini_di(finto, "BUSDT")
    assert [(q["side"], q["type"], q["quantity"], q.get("reduceOnly")) for q in o] == [("BUY", "LIMIT", "20.002", "true")]
    finto.posizioni["BUSDT"] = -20.05                                      # eseguito in parte: ne mancano 0,052 (2,6 USDT)
    n = len(finto.chiamate)
    d.tick(T0 + 3601)
    assert not [q for q in _ordini_di(finto, "BUSDT", n) if q["type"] == "MARKET"]
```

**275 — Basso — `bot/portafoglio/demo_binance.py:65-67`, `:352-353`**
- Il testo in testa al file dice ancora «le chiusure e le riduzioni sotto il valore minimo di Binance partono»; nella spiegazione di
  `ordine_saltato` la frase «1,92 e +51,8% l'anno contro +57,1% con anche le riduzioni» si può leggere al contrario (il +57,1% è delle sole
  chiusure, `audits/reports/2026-11-28-G1_CONTO_VERO_250.md:19`).
- Guasto: chi legge il file per capire cosa fa il conto vero trova due regole diverse.
- Correzione: «la chiusura intera sotto il valore minimo parte con «solo riduzione»; le riduzioni sotto il minimo si saltano (269)» a `:65-67`;
  «1,92 e +51,8% l'anno con anche le riduzioni, contro 1,94 e +57,1% delle sole chiusure» a `:352-353`. Solo testo: si può fare in questo commit
  (l'impronta cambia; la controllo alla revisione dell'accensione) o dopo.

### Invarianti modificati
- Minimi (demo e conto vero): **prima** (codice del 28 nov, non ancora riavviato) chiusure e riduzioni sotto il valore minimo partivano «solo
  riduzione»; **ora** solo la chiusura intera (obiettivo zero), le riduzioni si saltano come le aperture e gli aumenti
  (`demo_binance.py:347-355`, `:382`, `:407`, `:2053`). È la regola giudicata dalla prova (1,94). Mappa aggiornata (sezione 7).
- Nessun limite fisso cambiato.

### Decisioni per Alessio
1. Confermare la regola scelta dalla sessione principale: sotto il minimo si chiudono solo le posizioni da togliere del tutto; le riduzioni
   piccole si saltano (con G1 a 250 USDT: 1,94 e +57,1% l'anno, contro 1,92 e +51,8% con anche le riduzioni e 1,91 saltando tutto). Era la sua
   decisione 3 della revisione delle prove; va detta insieme alla richiesta di riavvio.
2. Restano quelle del rapporto `reviews/reports/2026-11-28-conto-vero-G1.md` (riavvio, accensione).

### Domande aperte
- Nessuna nuova. Resta aperta quella di prima: Binance accetta davvero la chiusura «solo riduzione» sotto i 5 USDT? Si vede sul demo alla prima
  mezzanotte dopo il riavvio (`/demo_binance/ribilanciamenti/{giorno}/rifiutati`).
