# Il mazzo dello Sharpe corretto per famiglie (backlog P34, 12 novembre 2026)

Lo Sharpe corretto dell'esame conta le **famiglie** di prove simili (`asticella.py`: `gruppi`, `per_v`, `TAGLIO` 0,5; decisione
dell'11 novembre). Il mazzo delle serie (`le_prove` fino alla 48, `serie_nuove` e `serie_programma7` dopo) si fermava alla prova 102
(riesami `audits/reports/2026-11-12-RIESAME_PROVA55.md` e `2026-11-12-RIESAME_PROVA96.md`). Il 12 novembre sono state aggiunte le prove
dalla 103 alla 152 e quelle prima della 103 che mancavano (commit `78235da`); la revisione dello stesso giorno
(`audits/reports/2026-11-12-MAZZO_ASTICELLA.md`, FAIL) ha trovato tre punti che non facevano ciò che era dichiarato, corretti qui.

**Cosa non cambia**: soglie, `TAGLIO`, formule. **Il modo di contare è quello scritto in `ASTICELLA.md`, sezione 3**: le varianti che
il registro conta senza una serie salvata contano ognuna come un gruppo a sé (come le prove 1 e 2B). La prima versione del 12
novembre le aveva tolte e diceva «modo di contare invariato»: non era vero, ed è stato corretto.

Le funzioni (`asticella.py`):
* `corretto_famiglie(nuove, candidate)`: **l'esame di oggi** per ogni prova nuova (mazzo completo, N = famiglie, V con l'aggiunta del
  23 ottobre).
* `mazzo(nuove)`: le serie del mazzo completo e gli Sharpe delle varianti senza serie; `senza_serie()`: queste ultime.
* `corretto_rivisto`: resta com'è, ma **non è l'esame di oggi** (conta le prove fino alla 48 più le serie che riceve): serve ai riesami
  «fino alla prova N». La 152 l'ha usata e ha scritto 0,88 invece di 0,73.
* `FUORI_DAL_MAZZO` (cartelle con una serie lasciate fuori) e `DIFFERENZE_DAL_REGISTRO` (prove dove il mazzo conta diverso dal
  registro), ognuna con il perché. Il test `tests/test_asticella_mazzo.py` confronta il mazzo con il registro prova per prova, controlla
  che ogni cartella con una serie sia letta e che le prove a eventi usino le operazioni che il registro dice.

Trattamento: le prove a portafoglio con la loro serie settimanale netta; le prove a eventi con il portafoglio della prova 41
(`quarantunesima.portafoglio`: 5% a evento, al massimo 20 aperte, settimana dell'uscita), solo le operazioni con il rendimento e con
il filtro della loro regola. Delle prove con più file entrano le varianti che il registro conta; controlli, versi opposti descrittivi e
copie di G1 restano fuori. Quando il file dà solo il giorno, l'entrata è la mezzanotte del giorno (sposta al massimo la settimana di
qualche uscita). Le conferme (che il registro non conta) restano fuori, come prima le 7, 22, 27, 38.

## I numeri

Rifatti con `python3 -m research.programma6.mazzo_asticella` (esito in `risultati_asticella/mazzo_12_novembre.json`; `corretto_famiglie`
dà gli stessi numeri). Le misure delle candidate sono quelle dei loro esami, invariate: G1 e G1 a 280 USDT da
`audits/repro/g1_parte2_2026-11-12_esito_misure.json`, la miscela da `audits/repro/prova28_2026-11-11_esito.json` (voce 11), C3
corretta da `audits/repro/prova55_2026-11-12_esito_base.json`, la 152 da `programma7/risultati_novantesima/risultati.json`.

| | Prima (fino alla 102) | Pubblicato (`78235da`) | **Corretto, taglio 0,5** | Taglio 0,3 | Taglio 0,7 | Revisore |
|---|---|---|---|---|---|---|
| Serie nel mazzo | 137 | 267 | **265** | 265 | 265 | 265 |
| Varianti senza serie (gruppi a sé) | 18 | 18 | **46** | 46 | 46 | 45 |
| Famiglie (N) | 80 | 165 | **191** | 141 | 227 | 191 |
| Famiglie in V (t sopra −3) | 69 | 146 | 146 | 99 | 182 | 147 |
| Deviazione degli Sharpe in V | 0,628 | 0,625 | 0,621 | 0,640 | 0,656 | 0,631 |
| **G1** (prova 57) | 0,867 | 0,769 | **0,755** | 0,764 | 0,638 | 0,733 |
| **G1 a 280 USDT** (conto A, prova 148) | 0,814 | 0,698 | **0,682** | 0,693 | 0,557 | 0,658 |
| **F5 + M7 + K2** al 12 ottobre | 0,890 | 0,822 | **0,812** | 0,819 | **0,731** | 0,797 |
| F5 + M7 + K2 al 19 ottobre | 0,893 | 0,826 | **0,817** | 0,823 | 0,736 | 0,802 |
| **C3 corretta** al 5 ottobre | 0,752 | 0,646 | **0,632** | 0,641 | 0,527 | 0,612 |
| **152 V1 / V2 / V3** | 0,849 / 0,802 / 0,840 | 0,744 / 0,685 / 0,732 | **0,729 / 0,669 / 0,717** | 0,739 / 0,679 / 0,727 | 0,609 / 0,544 / 0,595 | 0,707 / 0,645 / 0,694 |

* **Perché i numeri non coincidono con quelli del revisore (circa +0,02).** Il revisore ha applicato le tre correzioni (81 e 82
  filtrate, conferme fuori, 108, 111 e CC come gruppi a sé) ma non le due basse. Con le sue stesse correzioni rifaccio i suoi numeri
  identici (G1 0,7331, miscela 0,7971). La differenza viene quasi tutta dalla **settimana della 110**: rimessa nella settimana in cui la
  vendita si chiude (convenzione del mazzo: la settimana dell'uscita), la serie della vendita della volatilità entra nella famiglia del
  ritorno alla media a 4 ore della 149 su Bitcoin ed Ether (correlazione 0,60 e 0,58). Così le famiglie diventano 190 invece di 191, e la
  sua famiglia a Sharpe +1,19 esce da V: la deviazione scende da 0,631 a 0,621. Effetto: G1 +0,023, miscela +0,016. È l'unica correzione
  che alza i numeri: senza di lei la miscela è a 0,797, sotto 0,80. La 151 come gruppo a sé toglie 0,001 (va in N: con lo Sharpe −1,27,
  il t sulle 300 settimane del programma è −3,05, quindi resta fuori da V). Le tre domeniche della 139 non cambiano nulla.
* **I tagli (ASTICELLA.md, sezione 4: «se il verdetto cambiasse solo a uno dei tagli, lo si dice»).** La miscela F5 + M7 + K2 sta
  sopra 0,80 ai tagli 0,5 (0,812) e 0,3 (0,819), **sotto al taglio 0,7 (0,731)**. G1, G1 a 280 USDT, C3 e la 152 sono sotto 0,80 a
  tutti e tre i tagli.
* **La 152 com'è scritta nella prova** (0,882 / 0,841 / 0,875) viene da `corretto_rivisto`: 56 famiglie (prove fino alla 48 più le
  sue tre serie) e V di tutte le famiglie, senza l'aggiunta. Non è calcolata come G1; la colonna «prima» la rifà come G1.
* **C3**: il riesame metteva nel mazzo la serie di C3 corretta, che non è salvata. Qui c'è la serie del file della prova 55: con il
  mazzo di prima dà 0,7519, contro lo 0,7517 del riesame.

### G1 secondo quali prove si contano (decisione di metodo del proprietario, non presa qui)

Mazzo corretto, stessa regola (N = famiglie, V con l'aggiunta); le varianti senza serie entrano se la loro prova è nel taglio.

| Prove contate | Serie | Famiglie | G1 | G1 a 280 USDT | Revisore (G1) |
|---|---|---|---|---|---|
| Fino alla 57 (quando G1 è stata trovata) | 102 | 65 | **0,945** | 0,915 | 0,946 (con la conferma 50; senza 0,945) |
| Fino alla 57 più le varianti della famiglia di G1 provate dopo (61, 63, 69, 86, 88, 89, 92, 93, 94, 124, 142, 148, 152) | 120 | 64 | **0,947** | 0,917 | 0,947 |
| Fino alla 148 (prima della scelta del demo dell'8 novembre) | 200 | 159 | **0,683** | 0,604 | 0,731 |
| Tutte | 265 | 191 | **0,755** | 0,682 | 0,733 |

Fino alla 148 il revisore usava il mazzo pubblicato, cioè senza le 27 varianti senza serie di 108, 111 e 110 e senza le altre correzioni:
qui ci sono, e G1 scende a 0,683. Il numero con tutte le prove è più alto di quello fino alla 148 perché le 60 varianti della 149, con
Sharpe vicini a zero (più la 110 che entra in una loro famiglia), abbassano la dispersione V.

## Le prove nel mazzo

### Prima della 103 (mancavano)

| Prova | Nel mazzo | File (in `research/`) | Trattamento |
|---|---|---|---|
| 50 | — | `programma6/risultati_cinquantesima/settimane_F5_101_150.csv.gz` | **fuori**: conferma, il registro non la conta (`FUORI_DAL_MAZZO`) |
| 75 | 75 G16 | `programma7/risultati_diciottesima/eventi_G16.csv` | eventi al minuto (3.494) |
| 76 | 76 G17 | `programma7/risultati_diciannovesima/eventi_G17.csv` | eventi al minuto (393) |
| 77 | 77 G18 | `programma7/risultati_ventesima/settimane_G18.csv.gz` | portafoglio |
| 78 | 78 G19 | `programma7/risultati_ventunesima/eventi_G19.csv` | eventi al minuto (11.638) |
| 79 | 79 P9A | `programma9/risultati_prima/settimane_79_P9A.csv.gz` | portafoglio; le serie «solo ...» fuori |
| 80 | 80 P9B | `programma9/risultati_prima/settimane_80_P9B.csv.gz` | portafoglio; «solo la leva pulita» fuori |
| 81 | 81 P9C | `programma9/risultati_seconda/eventi_P9C.csv` | eventi al minuto, **solo con i long affollati** (funding da 0,0001: 409 su 697) |
| 82 | 82 P9C lunga | `programma9/risultati_terza/eventi_P9C_lunga.csv` | eventi al minuto, **solo con i long affollati** (2.389 su 3.964) |
| 83 | 83 P9D | `programma9/risultati_quarta/eventi_N3B_funding.csv` | eventi, funding da 0,0001 (461), per i giorni della colonna |
| 85 | 85 G21 | `programma7/risultati_ventitreesima/settimane_G21.csv.gz` | portafoglio |
| 87 | 87 PC | `programma7/risultati_venticinquesima/settimane_PC.csv.gz` | portafoglio |
| 89 | 89 F5C (già dentro) | — | il registro conta 2 (anche il controllo col fattore mescolato): nel mazzo solo F5C (`DIFFERENZE_DAL_REGISTRO`) |
| 90 | 90 N3V | `programma7/risultati_ventottesima/eventi_N3V.csv` | eventi, gruppo A «davvero nuove» (327 nel file; il registro dice 326) |
| 91 | 91 N3B2 | `programma7/risultati_ventinovesima/eventi_N3B2.csv` | eventi (630 nel file rifatto; il registro dice ancora 604) |
| 96 | 96 G22 | `programma7/risultati_trentaquattresima/eventi_G22.csv` | eventi, dall'ora dopo il comunicato per 6 ore (46) |
| 98 | 98 G23 | `programma7/risultati_trentaseiesima/eventi_G23.csv` | eventi, come la 96 (67) |
| 99 | 99 G24 | `programma7/risultati_trentasettesima/operazioni_G24.csv` | eventi, dalle 02:00 UTC per 24 ore (445) |

### Dalla 103 alla 152

File in `research/programma7/`. Fra parentesi le operazioni usate, uguali a quelle del registro.

| Prova | Nel mazzo | File | Trattamento, e cosa resta fuori |
|---|---|---|---|
| 103 | 103 LV | `risultati_quarantunesima/eventi_LV.csv` | eventi, solo i tagli della leva (200), dall'ora `h0` all'ora `h1` |
| 104 | 104 G26 | `risultati_quarantaduesima/eventi_G26_{2021-2022,2023-2024,2025-2026}.csv` | eventi al minuto, i tre periodi insieme (stessa regola) |
| 105 | 105 CB | `risultati_quarantatreesima/eventi_CB.csv` | eventi (104), per le ore della colonna `ore` |
| 106 | — | `risultati_quarantaquattresima/eventi_CBO.csv` | **fuori**: conferma, il registro non la conta (`FUORI_DAL_MAZZO`) |
| 107 | 107 G13C | `risultati_quarantacinquesima/eventi_G13C.csv` | eventi (77), per le ore della colonna `ore` |
| 108 | 108 `<indicatore> <1m o 5m>` (18) | `risultati_quarantaseiesima/esame.json` | **gruppi a sé senza serie**: Sharpe non salvato, −0,11% a operazione con p 1,00 → t molto sotto −3, in N e non in V (valore convenzionale −10) |
| 109 | 109 GR-L, 109 GR-N | `risultati_quarantasettesima/settimane_GR-L.csv.gz`, `settimane_GR-N.csv.gz` | portafoglio |
| 110 | 110 SS; 110 CC | `risultati_quarantottesima/settimane_SS.csv.gz`; `esame.json` | SS: portafoglio, **spostata di una settimana** (il file la mette al lunedì prima del venerdì di vendita; la vendita si chiude il venerdì dopo). CC: gruppo a sé con lo Sharpe di `esame.json` (−0,25, mensile) |
| 111 | 111 `<figura> <1m o 5m>` (8) | `risultati_quarantanovesima/esame.json` | **gruppi a sé senza serie**, come la 108 |
| 112 | 112 LQ | `risultati_cinquantesima/settimane_LQ.csv.gz` | il portafoglio della prova (già quello della 41); `eventi_C1`, `eventi_C2` sono i controlli |
| 113 | 113 N3G | `risultati_cinquantunesima/eventi_N3G.csv`, durate da `programma6/risultati_trentaduesima/eventi_N3B.csv` | eventi, solo le monete gratis (87) |
| 114 | 114 KP | `risultati_cinquantaduesima/settimane_KP.csv.gz` | portafoglio; verso opposto fuori |
| 115 | 115 BL | `risultati_cinquantatreesima/eventi_BL.csv` | eventi, BNB, 24 ore (65) |
| 116 | 116 VU | `risultati_cinquantaquattresima/settimane_VU.csv.gz` | portafoglio; verso opposto fuori |
| 117 | 117 EMI, 117 EWIL | `risultati_cinquantacinquesima/settimane_EMI.csv.gz`, `settimane_EWIL.csv.gz` | portafoglio; versi opposti fuori |
| 118 | 118 MV | `risultati_cinquantaseiesima/settimane_MV.csv.gz` | portafoglio; verso opposto fuori |
| 119 | 119 CU | `risultati_cinquantasettesima/settimane_CU.csv.gz` | portafoglio; verso opposto fuori |
| 120 | — | — | sospesa prima di qualunque risultato; il registro non la conta |
| 121 | 121 RR | `risultati_cinquantanovesima/settimane_RR.csv.gz` | portafoglio; «solo long» fuori |
| 122 | 122 RRE | `risultati_sessantesima/settimane_RRE.csv.gz` | portafoglio; «solo short» fuori |
| 123 | 123 RRB | `risultati_sessantunesima/settimane_RRB.csv.gz` | portafoglio; «solo long» fuori |
| 124 | 124 G1M | `risultati_sessantaduesima/settimane_G1M.csv.gz` | portafoglio; G1 rifatta per confronto fuori |
| 125 | 125 PA, 125 AV | `risultati_sessantatreesima/settimane_PA.csv.gz`, `settimane_AV.csv.gz` | portafoglio; PA e AV insieme (non contata) fuori |
| 126 | 126 GT | `risultati_sessantaquattresima/eventi_GT.csv` | eventi (167), per le ore della colonna `ore` |
| 127 | 127 RA | `risultati_sessantacinquesima/settimane_RA.csv.gz` | portafoglio; i controlli fuori |
| 128 | 128 BP | `risultati_sessantaseiesima/eventi_BP.csv` | eventi (818), dall'ora dopo il segnale per 4 ore |
| 129 | 129 IM | `risultati_sessantasettesima/eventi_IM.csv` | eventi (80), 4 giorni dall'ultimo giorno del mese |
| 130 | 130 TE | `risultati_sessantottesima/eventi_TE.csv` | eventi (116), dall'ora dopo per 24 ore |
| 131 | 131 DA, 131 DB | `risultati_sessantanovesima/settimane_DA.csv.gz`, `settimane_DB.csv.gz` | portafoglio |
| 132 | 132 FM | `risultati_settantesima/settimane_FM.csv.gz` | portafoglio; confronti fuori |
| 133 | 133 QO | `risultati_settantunesima/operazioni_primo.csv.gz` | eventi (23.969), 4 ore; il controllo col settimo minuto fuori |
| 134 | 134 PM | `risultati_settantaduesima/picchi_PM.csv` | eventi, solo i picchi con la bandiera (668) |
| 135 | 135 HL | `risultati_settantatreesima/settimane_HL.csv.gz` | portafoglio; confronti fuori |
| 136 | 136 NT | `risultati_settantaquattresima/eventi_tondi.csv.gz` | eventi (3.483), 60 minuti; il controllo fuori |
| 137 | 137 HLI | `risultati_settantacinquesima/settimane_HLI_101-200.csv.gz` | portafoglio; confronti fuori |
| 138 | 138 GA1, 138 GA2 | `risultati_settantaseiesima/settimane_GA1.csv.gz`, `settimane_GA2.csv.gz` | portafoglio |
| 139 | 139 CF | `risultati_settantasettesima/settimane_CF.csv` | portafoglio; **le 3 settimane etichettate di domenica passano al lunedì dopo** (che nel file manca); i confronti fuori |
| 140 | 140 QH | `risultati_settantottesima/eventi_QH.csv` | eventi (63), per le ore della colonna `ore` |
| 141 | 141 FS | `risultati_settantanovesima/eventi_FS.csv` | eventi (3.896), 7 giorni (le uscite a −30% non hanno l'ora nel file) |
| 142 | 142 G1S | `risultati_ottantesima/settimane_G1S.csv.gz` | portafoglio; G1 rifatta fuori |
| 143 | 143 SM | `risultati_ottantunesima/settimane_SM.csv.gz` | portafoglio |
| 144 | 144 FP | `risultati_ottantaduesima/settimane_FP.csv.gz` | portafoglio; confronti fuori |
| 145 | 145 NV | `risultati_ottantatreesima/settimane_NV.csv.gz` | portafoglio |
| 146 | 146 AT | `risultati_ottantaquattresima/eventi_AT.csv` | eventi (28), per le ore della colonna `ore` |
| 147 | 147 GA2C | `risultati_ottantacinquesima/settimane_GA2C.csv.gz` | portafoglio, 8 settimane (la prova è di 8 settimane); GA2 sul 2026 fuori |
| 148 | 148 B | `risultati_ottantaseiesima/giorni.csv.gz`, colonna «B, 280 USDT», sommata per settimana | B è la sola regola nuova; A, A2 e gli altri capitali fuori |
| 149 | 149 `<moneta>_<intervallo>_<A, B o C>` (60) | `risultati_ottantasettesima/settimane.csv.gz` | le 60 varianti |
| 150 | 150 v7, 150 v30 | `risultati_ottantottesima/settimane_v7.csv.gz`, `settimane_v30.csv.gz` | portafoglio |
| 151 | 151 WE | `risultati_ottantanovesima/settimane.csv` | **gruppo a sé** con lo Sharpe della sua serie nel periodo (−1,27 su 19 settimane): fermata dalle sue regole per dati troppo corti |
| 152 | 152 V1, 152 V2, 152 V3 | `risultati_novantesima/settimane_conto1.csv.gz` | le tre varianti; G1 nello stesso file fuori |
| 153 | — | — | **saltata**: in calcolo il 12 novembre (`DIFFERENZE_DAL_REGISTRO`); il controllo delle cartelle fallisce quando salverà una serie fuori dal mazzo |

Riassunto: dalla 49 alla 152 ogni prova entra con tante varianti quante ne conta il registro (176 serie e 28 varianti senza serie),
tranne la 89 (il controllo fuori) e le conferme 50 e 106 (il registro non le conta). In tutto il mazzo: 265 serie e 46 varianti
senza serie (18 delle prove 1 e 2B).

Aperto (dalla revisione, non deciso qui): se le serie molto corte (147, 8 settimane; 151) debbano entrare; quante famiglie per 108 e
111 (oggi 26, come dice la regola scritta; il revisore propone anche 13 o 2); il segnale a una settimana fra 109 GR-N e 136 NT; il
registro da aggiornare per le prove 90 e 91.
