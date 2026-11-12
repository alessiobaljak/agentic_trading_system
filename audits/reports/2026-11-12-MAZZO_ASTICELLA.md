# Revisione del mazzo dello Sharpe corretto per famiglie (12 novembre 2026)

## Riepilogo e verdetto

**Verdetto: FAIL del mazzo così com'è nel commit `78235da`.** I numeri pubblicati si rifanno identici (anche con una formula
scritta da capo), la formula, il taglio e le soglie non sono cambiati, e il calcolo di G1 è lo stesso della revisione di G1. Ma il
mazzo non fa quello che dichiara («non è cambiato il modo di contare», «entra la variante che il registro conta») in tre punti, e
tutti e tre alzano i numeri:

1. **Bloccante.** Le prove con varianti contate ma senza serie salvata (108: 18 varianti, 111: 8, la chiamata coperta della 110: 1)
   sono state tolte. La regola scritta prima (`ASTICELLA.md:31-32`) dice che le prove senza serie «contano ognuna come un gruppo a
   sé (scelta prudente: N più alto)», ed è così per le prove 1 e 2B già dentro.
2. **Alto.** Le prove 81 e 82 sono entrate con tutte le fiammate, non con quelle «con i long affollati» che sono la loro regola: la
   82 così è identica alla 75 sulle 92 settimane in comune (un doppione), e la regola vera di 81 e 82 non c'è.
3. **Medio.** Le conferme 50 e 106 sono dentro, ma il registro non le conta e il mazzo di prima teneva fuori le conferme (7, 22,
   27, 38).

Con le tre correzioni: **G1 0,733** (pubblicato 0,769), **G1 a 280 USDT 0,658** (0,698), **F5 + M7 + K2 0,797 al 12 ottobre e
0,802 al 19 ottobre** (0,822), **C3 0,612** (0,646), **prova 152: 0,707, 0,645, 0,694** (0,744, 0,685, 0,732). Nessuna correzione
alza un numero. G1 resta sotto 0,80 in ogni caso; **la miscela passa da «sopra 0,80 con margine» a «sulla soglia»**, e al taglio 0,7
(che le regole chiedono di riportare) fa 0,755.

C'è poi un Alto che non tocca i numeri di oggi ma quelli di domani: `asticella.corretto_rivisto` conta solo le prove fino alla 48
più le serie che riceve; la 152 ci è cascata (0,88 invece di 0,744), e la **prova 153, in calcolo adesso, la chiama nello stesso
modo** (`research/programma7/novantunesima.py:253`, file non ancora committato).

Il brief non conteneva giudizi sul risultato; conteneva i numeri attesi, che ho usato solo come affermazioni da controllare.

## Oggetto

* Commit `78235da` (12 nov 2026 13:10): `research/programma6/asticella.py` (`serie_nuove`, `serie_programma7`, `_eventi_mancanti`,
  `FUORI_DAL_MAZZO`), `research/programma6/mazzo_asticella.py`, `research/programma6/MAZZO_ASTICELLA.md`,
  `risultati_asticella/mazzo_12_novembre.json`, `tests/test_asticella_mazzo.py`. Mazzo di prima: `asticella.py` al commit `366d72c`.
* Regola del calcolo: `research/programma6/ASTICELLA.md` (sezioni 3-5, 22-23 ottobre), decisione dell'11 novembre (N = famiglie,
  V con l'aggiunta del 23 ottobre), soglia 0,80 (9 novembre).
* Periodo delle serie: `asticella.periodo`, dal 4 gennaio 2021 al 5 ottobre 2026, settimane al lunedì; prove a eventi con il
  portafoglio della prova 41 (5% a evento, al massimo 20 aperte, settimana dell'uscita, fino al 28 settembre 2026).
* Candidate e loro misure: dagli esiti dei loro esami (`audits/repro/g1_parte2_2026-11-12_esito_misure.json`,
  `prova28_2026-11-11_esito.json`, `prova55_2026-11-12_esito_base.json`, `programma7/risultati_novantesima/risultati.json`).
* Riproduzione: `audits/repro/mazzo_2026-11-12.py` (parti `cache`, `numeri`, `copertura`, `allinea`, `eventi`, `sensi`, `sensi2`,
  `regola_scritta`, `varianti_g1`, `fino57`), esiti in `audits/repro/mazzo_2026-11-12_esito_*.json`. Uso:
  `PYTHONPATH=. python3 audits/repro/mazzo_2026-11-12.py <parte> <cartella temporanea>` (prima `cache`).

## Checklist A–F (adattata a un calcolo d'esame)

### A. Dati (le serie lette)

* **Colonna netta — OK.** Tutte le serie a portafoglio aggiunte hanno la colonna `netto` (o, per la 54, la prima colonna, che è
  `netto`); 149 e 152 sono nette (`ottantasettesima.py:154,255`, `novantesima.py:278`); la 148 somma per settimana la colonna
  «B, 280 USDT» del conto netto (`ottantaseiesima.py:163,186`). Per le prove a eventi la colonna `r` è netta e nel verso della
  strategia: la media di `r` sulle righe usate coincide con il registro per 25 prove su 27 (per esempio 136 −0,176% dopo i costi,
  prima −0,056%; 75 −0,88%; 113 +12,11%); le due che non coincidono sono 81 e 82 (sotto). Comando: parte `eventi`.
* **Sharpe delle serie aggiunte contro il registro — OK** (parte `sharpe_registro`, le 70 serie aggiunte fuori dalla 149): uguali o spiegati dal periodo (117 EMI −0,155 sul
  periodo dell'esame, file `settimane_EMI`, non l'opposto, −0,190).
* **Varianti e filtri — PROBLEMA (Alto).** 81 e 82: `asticella.py:341-346` legge `eventi_P9C.csv` (697 righe) e
  `eventi_P9C_lunga.csv` (3.964) interi; la regola prende solo il funding ≥ 0,01% per 8 ore (`programma9/seconda.py:24,93-94`,
  `programma9/terza.py:31-32,40-41`: 409 e 2.389 righe). Sharpe della 82 nel mazzo −1,68, nella prova −1,31.
* **Settimane al lunedì — PROBLEMA (Basso).** 139 CF ha 3 settimane etichettate di domenica (27 dic 2020, 9 lug 2023, 16 nov 2025:
  `settantasettesima.py:69`, rapporto del lunedì + 6); 110 SS è etichettata una settimana prima (sotto, punto B).
* **Periodo — OK.** Tutte le serie passano da `asticella.periodo`; le prove a eventi finiscono al 28 settembre 2026 come quelle già
  dentro (`quarantunesima.py:31,36,139`). La 104 mette insieme i tre periodi (2021-2022 decide, gli altri descrittivi): stessa
  regola, scelta accettabile (Basso).
* **Righe perse — OK.** Nessuna durata mancante o assurda (la 113 prende le durate dalla 32 senza buchi); 3 durate nulle nella 75 e
  22 nella 78 (entrata e uscita nella stessa ora): trascurabili. Il tetto delle 20 aperte salta 4.833 operazioni della 78, 999 della
  141, 61 della 128: è la regola del portafoglio della 41, uguale per tutte.

### B. Tempi

* **Etichetta della settimana — PROBLEMA (Basso).** 110 SS: la vendita del venerdì g0 si chiude il venerdì dopo, ma l'etichetta è il
  lunedì prima di g0 (`quarantottesima.py:129-131`, `g0 - 4`): quasi tutto il guadagno o la perdita cade nella settimana dopo. Si
  vede nelle correlazioni: con la tendenza del Bitcoin a 4 ore della 149 −0,06 alla stessa settimana, −0,61 spostando SS di una
  settimana (parte `allinea`). Oggi non cambia le famiglie (SS sta da sola in ogni caso).
* **Gemelle di G1 allineate — OK.** 148 B, 152, 124, 142, 61, 93, 92, 69: correlazione massima alla stessa settimana (148 B 0,756
  contro 0,14 e 0,17 a una settimana).
* **Segnale non verificato (NON VERIFICABILE).** 109 GR-N e 136 NT: −0,32 alla stessa settimana, +0,37 a una settimana; non ho
  trovato la causa nel codice della 109 (`quarantasettesima.py:145-148`, etichetta giusta). Da guardare, non tocca le famiglie.
* **Ore d'entrata alla mezzanotte** quando il file dà solo il giorno (105, 106, 107, 126, 134, 140, 146, 83, 90, 91, 113, 141):
  approssimazione dichiarata (`MAZZO_ASTICELLA.md:14-16`), sposta al massimo la settimana di qualche uscita. OK, Basso.

### C. Costi

* **Netto dopo i costi — OK** (punto A). L'esame non simula ordini: punti su commissioni, liquidazione, filtri del conto non si
  applicano a questa revisione.

### D. Misure

* **Annualizzazione — OK.** `asticella.sharpe` usa √52 sulle settimane; `terza.sharpe_corretto` divide per √52 (`terza.py:327-333`).
* **Formula — OK.** Riscritta da capo nel repro (`dsr`, Bailey e López de Prado 2014: soglia √V·((1−γ)·Φ⁻¹(1−1/N) + γ·Φ⁻¹(1−1/(N·e))),
  denominatore √(1 − asimmetria·SR + (curtosi−1)/4·SR²), curtosi non in eccesso): uguale a `te.sharpe_corretto` alla quarta cifra
  per tutte le candidate, prima e dopo (parte `numeri`, campi `repo` e `corretto`).
* **Tagli 0,3 e 0,7 — PROBLEMA (Medio).** `ASTICELLA.md:35,46-48`: si riportano sempre, e «se il verdetto cambiasse solo a uno dei
  tagli, lo si dice». `MAZZO_ASTICELLA.md` non li riporta. Con il mazzo pubblicato: taglio 0,3 → 115 famiglie, miscela 0,839, G1
  0,793; taglio 0,7 → 200 famiglie, miscela **0,755**, G1 0,673. La miscela cambia esito a uno dei tagli.

### E. Conto delle prove (il cuore di questa revisione)

* **Registro contro mazzo, prova per prova — PROBLEMA.** Registro: 104 prove dalla 49 alla 152, **205** varianti contate (somma
  della riga «Totale nel conto», `REGISTRO.md:184`, 312 in tutto; l'unico allineamento con la somma conta le conferme 0 e «1 a
  eventi + 1 portafoglio» 1). Mazzo: **178** serie. Differenze (parte `copertura`):
  * 108 (18) e 111 (8): fuori, «nessuna serie salvata» (`MAZZO_ASTICELLA.md:104,107`). C'è solo `esame.json` (per variante:
    −0,11% a operazione dopo i costi, p 1,00). **Contro `ASTICELLA.md:31-32`** → Bloccante 1.
  * 110: CC fuori, «serie non salvata» (`MAZZO_ASTICELLA.md:106`); c'è la serie mensile `mesi_CC.csv` e lo Sharpe in `esame.json`
    (`CC_opzioni` −0,254 su 66 mesi, la parte che la chiamata coperta aggiunge al tenere la moneta, come dicono le regole, `programma7/QUARANTOTTESIMA.md:21-23`). Stessa regola → Bloccante 1.
  * 151 (1): fuori «per dati troppo corti» (`asticella.py:310-312`), mentre la 147 con 8 settimane è dentro (`MAZZO_ASTICELLA.md:143`).
    Nessuna regola scritta lo decide → Medio, decisione per Alessio.
  * 89: il registro conta 2 (F5C e il controllo, come dicono le sue regole, `VENTISETTESIMA.md:23-24`), il mazzo 1 (il controllo fuori,
    come dice il brief). Da dichiarare (Basso).
  * 50 e 106: «conferma» nel registro (0 nel conto), dentro il mazzo → Medio 3. La 50 è quasi uguale alla 51 (correlazione 0,9994).
* **Doppioni — PROBLEMA (Alto 2).** 82 «P9C lunga» = 75 G16 identiche sulle 92 settimane comuni (parte `copertura`, `gemelle`).
  Le altre coppie sopra 0,98 sono varianti di G1 e di F5 che il registro conta una per una (normale: si raggruppano nelle famiglie).
* **Controlli e versi opposti — OK** per le prove a portafoglio aggiunte (i file scelti sono quelli che le prove stesse passavano
  a `corretto_rivisto`, per esempio `settantacinquesima.py:59` «137 HLI» 101-200; 117 EMI e EWIL non gli opposti) e per le prove a
  eventi con un filtro (83 funding 461 righe, 90 gruppo A 327, 103 tagli 200, 113 gratis 87, 134 bandiera 668: tutti come il registro).
* **Effetto delle correzioni** (parti `sensi`, `sensi2`, `regola_scritta`; N = famiglie, V con l'aggiunta):

| Mazzo | Famiglie | G1 | G1 280 | Miscela 12 ott | Miscela 19 ott | C3 | 152 V1 / V2 / V3 |
|---|---|---|---|---|---|---|---|
| Pubblicato | 165 | 0,769 | 0,698 | 0,822 | 0,826 | 0,646 | 0,744 / 0,685 / 0,732 |
| Solo 81 e 82 con il loro filtro | 165 | 0,760 | 0,688 | 0,815 | — | 0,637 | 0,734 |
| e senza le conferme 50 e 106 | 164 | 0,755 | 0,683 | 0,812 | — | 0,632 | 0,729 |
| Solo la regola scritta (108, 111, CC come gruppi a sé) | 192 | 0,748 | 0,675 | 0,808 | 0,812 | 0,626 | 0,722 / 0,662 / 0,710 |
| **Tutte e tre le correzioni** | 191 | **0,733** | **0,658** | **0,797** | **0,802** | **0,612** | **0,707 / 0,645 / 0,694** |
| Tutte e tre, ma 108 e 111 come 13 famiglie (una per indicatore, come la prova 1) | 178 | 0,745 | 0,672 | 0,805 | 0,810 | 0,623 | 0,719 |
| Tutte e tre, 108 e 111 come 2 famiglie, e la 151 dentro | 168 | 0,741 | 0,667 | 0,802 | — | 0,619 | 0,715 |
| Pubblicato, taglio 0,3 / 0,7 | 115 / 200 | 0,793 / 0,673 | 0,726 / 0,593 | 0,839 / 0,755 | — | 0,671 / 0,557 | 0,770 / 0,644 |

  Per 108 e 111 lo Sharpe di ogni variante non è salvato, ma con −0,11% a operazione e p 1,00 il t è molto sotto −3: contano in N
  e non in V, qualunque sia il valore (nel repro −10).
* **Rapporto parametri e operazioni, finestre che avanzano**: non si applicano.

### F. Riproducibilità e parità

* **Numeri pubblicati — OK, identici.** Prima: 137 serie, 80 famiglie, 69 in V, deviazione 0,628; G1 0,8673, 280 USDT 0,8141,
  miscela 0,8903 / 0,8935, C3 0,7519, 152 0,8496 / 0,8027 / 0,8408 (con le sue tre serie 0,8488 / 0,8017 / 0,8399). Dopo: 267 serie,
  165 famiglie, 146 in V, 0,625; **G1 0,7688, 280 USDT 0,6982, miscela 0,8218 / 0,8261, C3 0,6460, 152 0,7441 / 0,6849 / 0,7321**.
  La 152 «come nella prova»: 56 famiglie, 0,882 / 0,841 / 0,875 (V di tutte le famiglie, senza l'aggiunta). Comando: parte `numeri`.
* **Stesso calcolo della revisione di G1 — OK.** `audits/reports/2026-11-12-G1_CONTO_VERO.md:16-19,167-170`: 137 serie più 18 senza
  serie, 80 gruppi, N = gruppi, V con l'aggiunta, misure di G1 (1,98, 300 settimane, asimmetria 0,545, curtosi 4,04) e di A a 280:
  0,8673 e 0,8141, gli stessi del «prima» del mazzo. Le varianti d'ordine della revisione con il mazzo nuovo (stima con l'asimmetria e
  la curtosi del caso base, che sul mazzo di prima ridà i numeri della revisione entro 0,002; parte `varianti_g1`): A tutto a mercato
  0,769 → **0,641**, A limite oltre lo 0,05% 0,734 → **0,601**; G1 tutto a mercato 0,795 → 0,671.
* **Due calcoli dello stesso numero — PROBLEMA (Alto).** `asticella.corretto_rivisto` (`asticella.py:173-192`) usa `le_prove()` più le
  serie che riceve; chi le passa senza `serie_nuove()` ottiene il mazzo fino alla 48 (56 famiglie). `novantesima.py:256` (152) e
  `novantunesima.py:253` (153, in calcolo) lo fanno. `MAZZO_ASTICELLA.md:44-49` lo dice ma lascia la funzione com'è.
* **Il test di guardia passa con gli errori — PROBLEMA (Medio).** `python -m pytest tests/test_asticella_mazzo.py -q` → 1 passato.
  Controlla solo che ogni cartella con file `settimane|eventi|operazioni|giorni|picchi` sia letta (`test_asticella_mazzo.py:12,34-35`):
  non vede le prove senza quei file (108, 111), i file mensili (`mesi_CC.csv`), i filtri (81, 82), i doppioni, le conferme.
* **Scelte fatte prima o dopo i numeri — NON VERIFICABILE.** Elenco, esclusioni e numeri sono nello stesso commit; la tabella «quanto
  pesa ogni parte» mostra che gli scenari sono stati calcolati.

## Problemi

1. **Bloccante — le prove senza serie tolte invece di contarle come gruppi a sé.** 108 (18 varianti), 111 (8) e la chiamata coperta
   della 110 sono fuori; `ASTICELLA.md:31-32` (scritta prima) le conta «ognuna come un gruppo a sé», come le prove 1 e 2B nel mazzo.
   Il commit dichiara invariato il modo di contare (`MAZZO_ASTICELLA.md:6`). Effetto da solo: miscela 0,822 → 0,808, G1 0,769 →
   0,748; con le altre due correzioni la miscela va a 0,797 (12 ottobre). Riprodurre: parte `regola_scritta`. Correzione: aggiungere
   le 27 varianti come prove senza serie (CC con lo Sharpe di `esame.json`, 108 e 111 con uno Sharpe sotto la soglia di −3 dichiarato
   o, meglio, rifacendo le serie settimanali); oppure far decidere ad Alessio se contarle 26, 13 o 2 (sotto).
2. **Alto — 81 e 82 con la variante sbagliata, e un doppione.** `asticella.py:341-346` legge interi `eventi_P9C.csv` e
   `eventi_P9C_lunga.csv`; la regola è il funding ≥ 0,0001 (`programma9/seconda.py:24,93-94`; `terza.py:31-32`). La 82 diventa
   identica alla 75 sulle 92 settimane comuni. Effetto: miscela −0,007, G1 −0,009. Riprodurre: parti `copertura`, `eventi`, `sensi`.
   Correzione: filtrare `funding_8h.notna() & funding_8h >= 0.0001` come le prove.
3. **Alto — `corretto_rivisto` resta una trappola, e la 153 ci sta cadendo.** `asticella.py:173-192`; `novantunesima.py:253`. Un
   numero della 153 calcolato così conterà 56 famiglie invece di 165 o più (per la 152: 0,88 invece di 0,744). Correzione: dentro
   `corretto_rivisto` unire sempre `serie_nuove()` (senza doppioni di nome), con un parametro esplicito per il riesame «fino alla
   55»; rifare il numero della 153 prima di scriverlo nel registro.
4. **Medio — le conferme 50 e 106 nel mazzo.** Il registro non le conta; il mazzo di prima teneva fuori 7, 22, 27, 38. Effetto
   −0,003 / −0,005. Correzione: toglierle, o decidere che le conferme contano e aggiungere anche 7, 22, 27, 38 (va scritto in
   `ASTICELLA.md`).
5. **Medio — tagli 0,3 e 0,7 non riportati** (`ASTICELLA.md:35,46-48`): al taglio 0,7 la miscela fa 0,755 (sotto 0,80).
6. **Medio — test di guardia troppo debole** (`tests/test_asticella_mazzo.py`). Correzione: confrontare con il registro il numero
   di varianti di ogni prova (con le conferme e i controlli dichiarati), cercare doppioni esatti, leggere anche i `mesi_*`.
7. **Medio — 151 fuori e 147 dentro.** Due serie corte trattate in modo opposto senza regola scritta; con la 151 dentro (Sharpe −1,27 su
   19 settimane) la miscela scende di 0,010. Decisione per Alessio.
8. **Basso — 110 SS etichettata una settimana prima** (`quarantottesima.py:131`: dovrebbe essere `g0 + 3`, il lunedì dopo il venerdì
   di vendita). File della prova, non del mazzo.
9. **Basso — 139 CF con 3 settimane di domenica** (`settantasettesima.py:69`).
10. **Basso — registro non aggiornato**: riga 91 «604 operazioni» (file rifatto il 12 novembre, `4d5b49c`: 630, +1,63%); riga 90 326
    contro 327 nel file. La riga 89 conta il controllo (2), il mazzo no (1): scriverlo in `MAZZO_ASTICELLA.md`.
11. **Basso — il segnale fra 109 GR-N e 136 NT a una settimana**: non spiegato.

## Problemi tornati da audit precedenti

* Catalogo, voce 32 (prove non nel mazzo): **in parte risolta** — 63 prove entrate; restano fuori 27 varianti contate (problema 1)
  e la 151.
* Voce 16 (due modi di contare): **tornata in un'altra forma** — la 152 ha pubblicato 0,88 con `corretto_rivisto` (56 famiglie, V di
  tutte le famiglie), la 153 sta per farlo (problema 3).
* Voce 12 (file di risultati usati come ingredienti): non toccata dal commit; il mazzo legge le serie salvate così come sono (per la
  28 quelle di prima della correzione delle parità, revisione dell'11 novembre). Non rimisurata qui.
* Voce 20 (eventi della 32 letti prima della correzione oraria): 83, 90, 113 usano le liste di eventi della 32 di prima (613); il mazzo
  le prende come le prove le hanno calcolate, che è giusto per contare le prove fatte.

## Segnalazioni per live-path-reviewer

Nessuna: il commit non tocca il percorso degli ordini.

## Decisioni per Alessio

1. **Domanda di metodo: le prove fatte dopo che una strategia è stata trovata devono entrare nel suo Sharpe corretto?** (G1 è la prova
   57; oggi il mazzo arriva alla 152.)
   * *Che cosa fa la letteratura* (da quanto ricordo, non ho potuto rileggere gli articoli in questa sessione). Bailey e López de Prado
     (2014, «The Deflated Sharpe Ratio») correggono lo Sharpe per la **scelta**: N e V sono le prove fra cui la strategia è stata
     scelta, e chiedono di registrarle tutte. López de Prado (2018-2020, e con Lewis 2019) stima N come numero di gruppi di prove
     simili, ed è il metodo del repository. In quella logica le prove fatte **dopo** la scelta non hanno gonfiato lo Sharpe di G1 e non
     ci entrerebbero, salvo che la scelta venga rifatta (per esempio quando si decide di nuovo fra G1 e le sue varianti, o fra tutte le
     strategie per i soldi veri). Harvey, Liu e Zhu (2016) alzano la soglia dei fattori nuovi con il numero di prove fatte fino al
     momento della scoperta: un'asticella che cresce nel tempo, letta alla data di ogni scoperta.
   * *Che cosa fa oggi il repository*: ogni candidata, vecchia o nuova, si misura con tutte le prove fatte fino a oggi; quindi lo
     Sharpe corretto di G1 cambia a ogni prova nuova, anche se non ha niente a che fare con G1 (e non sempre in giù: le 60 varianti
     della 149, quasi tutte a Sharpe vicino a zero, abbassano la dispersione e lo alzano).
   * *Quanto varrebbe G1* (stessa regola di oggi; parte `fino57`):

| Prove nel mazzo | Famiglie | G1 | G1 a 280 USDT |
|---|---|---|---|
| Fino alla 57 (quando G1 è stata trovata) | 65 | **0,946** | **0,916** |
| Fino alla 57 più le varianti di G1 provate dopo (61, 63, 69, 88, 92, 93, 94, 124, 142, 148, 152) | 64 | 0,947 | 0,918 |
| Fino alla 148 (le prove fatte prima della scelta del demo dell'8 novembre) | 133 | 0,731 | 0,656 |
| Tutte, come pubblicato il 12 novembre | 165 | 0,769 | 0,698 |
| Tutte, con le correzioni di questa revisione | 191 | 0,733 | 0,658 |

   * Le scelte possibili: (a) fino alla scoperta, come la letteratura sul singolo risultato; (b) fino alla scoperta più le varianti della
     stessa strategia provate dopo; (c) fino alla data di ogni scelta (demo, soldi veri), perché quella è una scelta fra tutte le prove
     fatte; (d) tutte fino a oggi, come ora. Con (a) o (b) G1 è sopra 0,80 (e appena sotto lo 0,95 che le sue regole dicevano,
     `PRIMA.md:27`); con (c) o (d) è sotto. Le regole di G1 sono state scritte con una soglia diversa da quella di oggi (catalogo,
     voce 29). Non decido io: va scritto prima del prossimo calcolo, e vale per tutte le candidate.
2. **Come contare le prove senza serie** (108, 111): una famiglia per variante contata (26, come le prove 1 e 2B; la regola scritta),
   una per indicatore (13, come la prova 1 che contava 9 famiglie su tre intervalli), o una per prova (2). Miscela con le altre
   correzioni: 0,797 / 0,805 / circa 0,80; G1: 0,733 / 0,745 / circa 0,74. Oppure rifare le serie settimanali di 108 e 111.
3. **Le conferme contano?** Il registro dice di no; il mazzo nuovo le mette (50, 106).
4. **Le serie corte** (147: 8 settimane, 151: 19) entrano? Uno Sharpe su poche settimane è molto rumoroso e allarga V.
5. **F5 + M7 + K2 con le correzioni è sulla soglia** (0,797 al 12 ottobre, 0,802 al 19 ottobre; 0,755 al taglio 0,7): è il caso del
   «qualche punto sotto» dell'8 novembre.

## Domande aperte

1. Chi corregge `corretto_rivisto` e il numero della prova 153 prima che venga scritto nel registro? Il file `novantunesima.py:253`
   non è ancora committato: se il numero esce così, conterà 56 famiglie invece di 165 o più.
2. Le esclusioni del mazzo (108, 111, CC, 151) e l'inclusione delle conferme sono state decise prima o dopo aver visto i numeri degli
   scenari? Dal repository non si vede (stesso commit).
3. La miscela F5 + M7 + K2 resta «misurata ogni settimana senza ritocchi» (decisione dell'11 novembre) anche se il suo Sharpe corretto,
   con le correzioni, scende sulla soglia di 0,80? Chi la usa come candidata (l'allocatore) deve sapere che 0,822 non regge.
4. Il segnale a una settimana fra 109 GR-N e 136 NT ha una causa nel codice di una delle due prove? Non l'ho trovata.
