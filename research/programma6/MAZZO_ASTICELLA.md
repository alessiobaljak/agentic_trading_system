# Il mazzo dello Sharpe corretto per famiglie (backlog P34, 12 novembre 2026)

Lo Sharpe corretto dell'esame conta le **famiglie** di prove simili (`asticella.py`: `gruppi`, `per_v`, `TAGLIO` 0,5; decisione
dell'11 novembre). Il mazzo delle serie (`le_prove` fino alla 48, `serie_nuove` e `serie_programma7` dopo) si fermava alla prova 102
(riesami `audits/reports/2026-11-12-RIESAME_PROVA55.md` e `2026-11-12-RIESAME_PROVA96.md`). Il 12 novembre sono state aggiunte le prove
dalla 103 alla 152 e quelle prima della 103 che mancavano. **Non sono cambiati** soglie, `TAGLIO`, formule né il modo di contare:
solo il mazzo. Le prove con una serie salvata e lasciate fuori apposta sono in `asticella.FUORI_DAL_MAZZO`; il test
`tests/test_asticella_mazzo.py` fallisce se una cartella di risultati dalla prova 49 in poi ha una serie o degli eventi e non è né nel
mazzo né lì.

Trattamento, come per le prove già dentro: le prove a portafoglio con la loro serie settimanale netta; le prove a eventi con il
portafoglio della prova 41 (`quarantunesima.portafoglio`: 5% a evento, al massimo 20 aperte, settimana dell'uscita), solo gli eventi
con il rendimento calcolato. Delle prove con più file entra la variante (o le varianti) che il registro conta; i controlli, i versi
opposti descrittivi e le copie di G1 rifatte per confronto restano fuori. Per gli eventi l'ora d'entrata e d'uscita viene dal file;
quando il file dà solo il giorno si usa la mezzanotte del giorno (approssimazione di qualche ora: cambia solo in quale settimana cade
l'uscita, raramente).

## I numeri, prima e dopo

Rifatti con `python3 -m research.programma6.mazzo_asticella` (esito in `risultati_asticella/mazzo_12_novembre.json`). Le misure delle
candidate (Sharpe, settimane, asimmetria, curtosi) sono quelle dei loro esami, invariate: G1 e G1 a 280 USDT da
`audits/repro/g1_parte2_2026-11-12_esito_misure.json` (come `g1_parte2_2026-11-12.py misure`), la miscela da
`audits/repro/prova28_2026-11-11_esito.json` (voce 11, «gruppi_23_ottobre»), C3 corretta da
`audits/repro/prova55_2026-11-12_esito_base.json`, la 152 da `programma7/risultati_novantesima/risultati.json`. Regola di oggi:
N = famiglie, V con l'aggiunta del 23 ottobre.

| | Mazzo di prima | Mazzo completo |
|---|---|---|
| Serie nel mazzo (più 18 prove senza serie, prove 1 e 2B) | 137 | **267** |
| Famiglie (N) | 80 | **165** |
| Famiglie nella varianza V (t sopra −3) | 69 | 146 |
| Deviazione degli Sharpe delle famiglie in V | 0,628 | 0,625 |
| **G1** (conto pieno, prova 57) | 0,867 | **0,769** |
| **G1 a 280 USDT** (conto A della prova 148) | 0,814 | **0,698** |
| **F5 + M7 + K2** al 12 ottobre (come il riesame dell'11 novembre) | 0,890 | **0,822** |
| F5 + M7 + K2 al 19 ottobre (funding tutto vero) | 0,893 (riesame: 0,894) | 0,826 |
| **C3 corretta** al 5 ottobre (riesame della 55) | 0,752 | **0,646** |
| **152 V1** (tetto 20%), regola di oggi | 0,849 | **0,744** |
| **152 V2**, regola di oggi | 0,802 | **0,685** |
| **152 V3**, regola di oggi | 0,840 | **0,732** |

Note sui numeri:

* **La 152 com'è scritta nella prova (0,88, 0,84, 0,87) non era calcolata come G1.** `novantesima.py:256` chiama
  `asticella.corretto_rivisto` con le sole tre serie della 152; `corretto_rivisto` non legge `serie_nuove`, quindi conta il mazzo
  fino alla prova 48 più le tre varianti (**56 famiglie**), e il numero riportato è quello con V di tutte le famiglie, non con
  l'aggiunta. Rifatto così oggi dà ancora 0,882, 0,841, 0,875 (invariato per costruzione: il mazzo nuovo non entra). Nella colonna
  «prima» della tabella la 152 è calcolata come G1 (mazzo di prima più le sue tre serie, 140 serie, 80 famiglie). `corretto_rivisto`
  non è stata toccata: il riesame della 55 la usa per rifare il mazzo «fino alla 55».
* **C3**: il riesame metteva nel mazzo la serie di C3 corretta, che non è salvata; qui nel mazzo c'è la serie del file della prova 55.
  Con il mazzo di prima dà 0,7519 contro lo 0,7517 del riesame.
* G1 e la miscela con il mazzo di prima si riproducono: 0,8673 (riesame di G1 0,867), 0,890 (riesame della 28: 0,891, misure
  arrotondate a 4 cifre nel file d'esito).

Quanto pesa ogni parte delle aggiunte (G1; G1 a 280 USDT; miscela al 12 ottobre; C3):

| Mazzo | Serie | Famiglie | G1 | G1 a 280 | Miscela | C3 |
|---|---|---|---|---|---|---|
| Completo | 267 | 165 | 0,769 | 0,698 | 0,822 | 0,646 |
| Senza le 60 varianti della 149 (una moneta, un intervallo, una strategia) | 207 | 134 | 0,734 | 0,659 | 0,798 | 0,612 |
| Senza le 17 prove prima della 103 (solo 103-152 aggiunte) | 250 | 153 | 0,816 | 0,753 | 0,855 | 0,695 |
| Senza le 6 a portafoglio prima della 103 (50, 77, 79, 80, 85, 87) | 261 | 161 | 0,766 | 0,695 | 0,820 | 0,643 |
| Senza la 147 (8 settimane) | 266 | 164 | 0,766 | 0,696 | 0,820 | 0,644 |

Le 60 varianti della 149 fanno 31 famiglie loro, con Sharpe vicini a zero: alzano N ma abbassano V, e il numero corretto sale.

## Le prove aggiunte (130 serie da 63 prove)

### Prima della 103 (mancavano)

| Prova | Nel mazzo | File (in `research/`) | Trattamento |
|---|---|---|---|
| 50 | 50 F5 101-150 | `programma6/risultati_cinquantesima/settimane_F5_101_150.csv.gz` | portafoglio (conferma di F5 sulle monete 101-150) |
| 75 | 75 G16 | `programma7/risultati_diciottesima/eventi_G16.csv` | eventi, entrata e uscita al minuto |
| 76 | 76 G17 | `programma7/risultati_diciannovesima/eventi_G17.csv` | eventi, al minuto |
| 77 | 77 G18 | `programma7/risultati_ventesima/settimane_G18.csv.gz` | portafoglio (`operazioni_G18` sono le sue operazioni) |
| 78 | 78 G19 | `programma7/risultati_ventunesima/eventi_G19.csv` | eventi, al minuto |
| 79 | 79 P9A | `programma9/risultati_prima/settimane_79_P9A.csv.gz` | portafoglio; le serie «solo ...» (scomposizioni) fuori |
| 80 | 80 P9B | `programma9/risultati_prima/settimane_80_P9B.csv.gz` | portafoglio; «solo la leva pulita» fuori |
| 81 | 81 P9C | `programma9/risultati_seconda/eventi_P9C.csv` | eventi, al minuto |
| 82 | 82 P9C lunga | `programma9/risultati_terza/eventi_P9C_lunga.csv` | eventi, al minuto |
| 83 | 83 P9D | `programma9/risultati_quarta/eventi_N3B_funding.csv` | eventi, solo con il funding ≥ 0,01% per 8 ore (461), per i giorni della colonna |
| 85 | 85 G21 | `programma7/risultati_ventitreesima/settimane_G21.csv.gz` | portafoglio |
| 87 | 87 PC | `programma7/risultati_venticinquesima/settimane_PC.csv.gz` | portafoglio |
| 90 | 90 N3V | `programma7/risultati_ventottesima/eventi_N3V.csv` | eventi, solo il gruppo A «davvero nuove» (327: la regola da sola dell'esame) |
| 91 | 91 N3B2 | `programma7/risultati_ventinovesima/eventi_N3B2.csv` | eventi, per i giorni della colonna |
| 96 | 96 G22 | `programma7/risultati_trentaquattresima/eventi_G22.csv` | eventi, dall'ora dopo il comunicato per 6 ore |
| 98 | 98 G23 | `programma7/risultati_trentaseiesima/eventi_G23.csv` | eventi, come la 96 |
| 99 | 99 G24 | `programma7/risultati_trentasettesima/operazioni_G24.csv` | eventi, dalle 02:00 UTC del giorno per 24 ore |

Con queste, tutte le prove dalla 49 alla 102 sono nel mazzo.

### Dalla 103 alla 152

File in `research/programma7/`.

| Prova | Nel mazzo | File | Trattamento, e cosa resta fuori |
|---|---|---|---|
| 103 | 103 LV | `risultati_quarantunesima/eventi_LV.csv` | eventi, solo i tagli della leva (200), dall'ora `h0` all'ora `h1`; aumenti e righe uguali fuori |
| 104 | 104 G26 | `risultati_quarantaduesima/eventi_G26_{2021-2022,2023-2024,2025-2026}.csv` | eventi, al minuto, i tre periodi insieme (stessa regola) |
| 105 | 105 CB | `risultati_quarantatreesima/eventi_CB.csv` | eventi, dal giorno della colonna `data` per le ore della colonna `ore` |
| 106 | 106 CBO | `risultati_quarantaquattresima/eventi_CBO.csv` | eventi, come la 105 (conferma) |
| 107 | 107 G13C | `risultati_quarantacinquesima/eventi_G13C.csv` | eventi, per le ore della colonna `ore` |
| 108 | — | — | **esclusa**: nessuna serie salvata (18 varianti, solo i numeri in `esame.json`) |
| 109 | 109 GR-L, 109 GR-N | `risultati_quarantasettesima/settimane_GR-L.csv.gz`, `settimane_GR-N.csv.gz` | portafoglio |
| 110 | 110 SS | `risultati_quarantottesima/settimane_SS.csv.gz` | portafoglio; **CC esclusa**: la sua serie non è salvata (`settimane_SS.csv` sono le operazioni di SS) |
| 111 | — | — | **esclusa**: nessuna serie salvata (8 varianti) |
| 112 | 112 LQ | `risultati_cinquantesima/settimane_LQ.csv.gz` | il portafoglio della prova (già quello della 41 sugli eventi); `eventi_C1`, `eventi_C2` sono i controlli |
| 113 | 113 N3G | `risultati_cinquantunesima/eventi_N3G.csv`, durate da `programma6/risultati_trentaduesima/eventi_N3B.csv` | eventi, solo le monete gratis (87: la regola da sola dell'esame) |
| 114 | 114 KP | `risultati_cinquantaduesima/settimane_KP.csv.gz` | portafoglio; il verso opposto (descrittivo) fuori |
| 115 | 115 BL | `risultati_cinquantatreesima/eventi_BL.csv` | eventi, BNB, 24 ore dall'entrata |
| 116 | 116 VU | `risultati_cinquantaquattresima/settimane_VU.csv.gz` | portafoglio; verso opposto fuori |
| 117 | 117 EMI, 117 EWIL | `risultati_cinquantacinquesima/settimane_EMI.csv.gz`, `settimane_EWIL.csv.gz` | portafoglio; versi opposti fuori |
| 118 | 118 MV | `risultati_cinquantaseiesima/settimane_MV.csv.gz` | portafoglio; verso opposto fuori |
| 119 | 119 CU | `risultati_cinquantasettesima/settimane_CU.csv.gz` | portafoglio; verso opposto fuori |
| 120 | — | — | **esclusa**: sospesa prima di qualunque risultato (la SEC rifiuta lo scarico) |
| 121 | 121 RR | `risultati_cinquantanovesima/settimane_RR.csv.gz` | portafoglio; «solo long» fuori |
| 122 | 122 RRE | `risultati_sessantesima/settimane_RRE.csv.gz` | portafoglio; «solo short» fuori |
| 123 | 123 RRB | `risultati_sessantunesima/settimane_RRB.csv.gz` | portafoglio; «solo long» fuori |
| 124 | 124 G1M | `risultati_sessantaduesima/settimane_G1M.csv.gz` | portafoglio; G1 rifatta per confronto fuori |
| 125 | 125 PA, 125 AV | `risultati_sessantatreesima/settimane_PA.csv.gz`, `settimane_AV.csv.gz` | portafoglio; PA e AV insieme (non contata) fuori |
| 126 | 126 GT | `risultati_sessantaquattresima/eventi_GT.csv` | eventi, per le ore della colonna `ore` |
| 127 | 127 RA | `risultati_sessantacinquesima/settimane_RA.csv.gz` | portafoglio; i controlli (sempre comprata, sempre venduta, una sola finestra) fuori |
| 128 | 128 BP | `risultati_sessantaseiesima/eventi_BP.csv` | eventi, dall'ora dopo il segnale per 4 ore |
| 129 | 129 IM | `risultati_sessantasettesima/eventi_IM.csv` | eventi, 4 giorni dall'ultimo giorno del mese |
| 130 | 130 TE | `risultati_sessantottesima/eventi_TE.csv` | eventi, dall'ora dopo l'emissione per 24 ore |
| 131 | 131 DA, 131 DB | `risultati_sessantanovesima/settimane_DA.csv.gz`, `settimane_DB.csv.gz` | portafoglio |
| 132 | 132 FM | `risultati_settantesima/settimane_FM.csv.gz` | portafoglio; G1 sulle stesse monete e media dei ranghi (confronti) fuori |
| 133 | 133 QO | `risultati_settantunesima/operazioni_primo.csv.gz` | eventi (netto di ogni operazione, 4 ore); il controllo col settimo minuto fuori |
| 134 | 134 PM | `risultati_settantaduesima/picchi_PM.csv` | eventi, solo i 668 picchi con la bandiera, per le ore della colonna `ore` |
| 135 | 135 HL | `risultati_settantatreesima/settimane_HL.csv.gz` | portafoglio; confronti fuori |
| 136 | 136 NT | `risultati_settantaquattresima/eventi_tondi.csv.gz` | eventi, 60 minuti dal passaggio; il controllo fuori |
| 137 | 137 HLI | `risultati_settantacinquesima/settimane_HLI_101-200.csv.gz` | portafoglio; sulle prime 100 e G1 sulle stesse monete (confronti) fuori |
| 138 | 138 GA1, 138 GA2 | `risultati_settantaseiesima/settimane_GA1.csv.gz`, `settimane_GA2.csv.gz` | portafoglio |
| 139 | 139 CF | `risultati_settantasettesima/settimane_CF.csv` | portafoglio; Bitcoin tenuto, al contrario, solo long fuori |
| 140 | 140 QH | `risultati_settantottesima/eventi_QH.csv` | eventi, per le ore della colonna `ore` |
| 141 | 141 FS | `risultati_settantanovesima/eventi_FS.csv` | eventi, 7 giorni (le 266 uscite a −30% non hanno l'ora nel file: contate al 7° giorno) |
| 142 | 142 G1S | `risultati_ottantesima/settimane_G1S.csv.gz` | portafoglio; G1 rifatta fuori |
| 143 | 143 SM | `risultati_ottantunesima/settimane_SM.csv.gz` | portafoglio |
| 144 | 144 FP | `risultati_ottantaduesima/settimane_FP.csv.gz` | portafoglio; momento semplice e metà a salti (confronti) fuori |
| 145 | 145 NV | `risultati_ottantatreesima/settimane_NV.csv.gz` | portafoglio |
| 146 | 146 AT | `risultati_ottantaquattresima/eventi_AT.csv` | eventi (28), per le ore della colonna `ore` |
| 147 | 147 GA2C | `risultati_ottantacinquesima/settimane_GA2C.csv.gz` | portafoglio, 8 settimane (la prova è di 8 settimane); GA2 sul 2026 (confronto) fuori |
| 148 | 148 B | `risultati_ottantaseiesima/giorni.csv.gz`, colonna «B, 280 USDT», sommata per settimana | B è la sola regola nuova; A, A2 e gli altri capitali sono G1 eseguita in altri modi: fuori |
| 149 | 149 `<moneta>_<intervallo>_<A, B o C>` (60) | `risultati_ottantasettesima/settimane.csv.gz` | le 60 varianti |
| 150 | 150 v7, 150 v30 | `risultati_ottantottesima/settimane_v7.csv.gz`, `settimane_v30.csv.gz` | portafoglio |
| 151 | — | `risultati_ottantanovesima/settimane.csv` | **esclusa** (in `FUORI_DAL_MAZZO`): fermata dalle sue regole per dati troppo corti (23 settimane), nessun esame |
| 152 | 152 V1, 152 V2, 152 V3 | `risultati_novantesima/settimane_conto1.csv.gz` | le tre varianti; G1 nello stesso file (copia della 57) fuori |
| 153 | — | — | **saltata**: in calcolo il 12 novembre. Non è in `FUORI_DAL_MAZZO`: quando salverà una serie, il test fallisce finché non entra |

Riassunto: delle 50 prove dalla 103 alla 152 ne entrano 46 (113 serie); restano fuori 108, 111 e 120 (nessuna serie) e 151 (dati troppo
corti), più la variante CC della 110 (serie non salvata). Prima della 103 entrano 17 prove (17 serie).
