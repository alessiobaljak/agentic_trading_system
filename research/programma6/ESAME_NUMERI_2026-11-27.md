# L'esame delle prove sul mazzo di oggi: numero in vigore e i quattro numeri accanto (27 novembre 2026)

Calcolato con la funzione unica `research/programma6/asticella.esame` (correzioni dell'audit del 26 novembre, compito «esame»), sul mazzo
di oggi **dopo le correzioni dei dati** (le prove senza serie con le loro settimane, la 68 G10 con le settimane ferme, le settimane vuote
tolte coppia per coppia): 291 serie, 48 prove senza serie, **200 famiglie, 154 in V, deviazione 0,6891**. Script e risultati interi:
lo script della sessione del 27 novembre (`scratchpad/correzioni/esame/tabella.py`, non nel repository: i numeri si rifanno con `asticella.esame`). Numeri controllati da `tests/test_esame_unico.py`.

**Il numero in vigore** è l'esame delle decisioni del 9, 11 e 23 novembre: netto positivo, ogni anno solare positivo (media delle
settimane × 52), t da 3, probabilità che non sia fortuna da 0,80 (N = famiglie di oggi, V senza le famiglie con il t sotto −3).
**I quattro numeri accanto NON sono ufficiali** (le regole le decide il proprietario): (a) senza le serie a incasso quasi fisso 157, 159 e
161 (famiglie rifatte, N 198); (b) V simmetrica (fuori da V anche le famiglie con il t sopra +3) e senza le serie della 157 bocciata dal
revisore; (c) t robusto di Newey e West con 4 settimane di ritardo (fra parentesi 13) e probabilità con le settimane efficaci; (d) (b) e
(c) insieme. «Pubblicato» è il numero scritto dalla prova (con il mazzo e il conto di allora).

Misure: per le prove dalla 162 alla 169 e per le strategie del paper, la serie del mazzo (per la 162-169 coincide con la misura pubblicata
dalla prova; per G1 con l'esame della prova 57). Per la miscela F5+M7+K2 la serie del mazzo è quella di prima della correzione delle parità
(301 settimane): accanto c'è la misura del suo riesame (251 settimane fino al 19 ottobre, funding vero), quella dei numeri già visti dal
proprietario (0,705-0,714). Per G1 c'è anche la misura del 12 novembre, quella dello 0,945.

| Prova | Sharpe | Settimane | t semplice | t robusto 4 rit. (13) | Ogni anno positivo (somma, in vigore; composto) | **In vigore** | (a) senza 157, 159, 161 | (b) V simmetrica senza 157 | (c) settimane efficaci 4 rit. (13) | (d) b + c 4 rit. (13) | Pubblicato | Esito in vigore |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 162 A | 0,09 | 137 | 0,15 | 0,14 (0,14) | no (2024); composto no (2024) | **0,002** | 0,004 | 0,008 | 0,003 (0,004) | 0,012 (0,013) | 0,002 | no: anni non positivi 2024; t 0.15 sotto 3; probabilita' che non sia fortuna 0.00 sotto 0,80 |
| 162 B | -6,23 | 138 | -10,15 | -9,35 (-11,67) | no (2024, 2025, 2026); composto no (2024, 2025, 2026) | **0,000** | 0,000 | 0,000 | 0,000 (0,000) | 0,000 (0,000) | 0,000 | no: netto non positivo; anni non positivi 2024,2025,2026; t -10.15 sotto 3; probabilita' che non sia fortuna 0.00 sotto 0,80 |
| 163 A | -0,35 | 172 | -0,64 | -0,64 (-0,63) | no (2025); composto no (2025) | **0,000** | 0,000 | 0,000 | 0,000 (0,000) | 0,000 (0,000) | 0,000 | no: netto non positivo; anni non positivi 2025; t -0.64 sotto 3; probabilita' che non sia fortuna 0.00 sotto 0,80 |
| 163 B | 0,06 | 174 | 0,12 | 0,11 (0,10) | no (2025); composto no (2025) | **0,000** | 0,001 | 0,003 | 0,001 (0,002) | 0,003 (0,009) | 0,000 | no: anni non positivi 2025; t 0.12 sotto 3; probabilita' che non sia fortuna 0.00 sotto 0,80 |
| 165 A | 0,19 | 124 | 0,30 | 0,31 (0,33) | no (2026); composto no (2026) | **0,004** | 0,009 | 0,015 | 0,003 (0,002) | 0,012 (0,008) | 0,005 | no: anni non positivi 2026; t 0.30 sotto 3; probabilita' che non sia fortuna 0.00 sotto 0,80 |
| 165 B | 0,48 | 126 | 0,75 | 0,79 (0,79) | no (2026); composto no (2024, 2026) | **0,014** | 0,026 | 0,041 | 0,010 (0,010) | 0,033 (0,034) | 0,015 | no: anni non positivi 2026; t 0.75 sotto 3; probabilita' che non sia fortuna 0.01 sotto 0,80 |
| 168 A | 2,11 | 300 | 5,08 | 3,90 (3,45) | sì; composto sì | **0,702** | 0,835 | 0,904 | 0,658 (0,640) | 0,842 (0,811) | 0,730 | no: probabilita' che non sia fortuna 0.70 sotto 0,80 |
| 168 B | 2,14 | 300 | 5,13 | 3,96 (3,47) | sì; composto sì | **0,722** | 0,849 | 0,913 | 0,675 (0,654) | 0,852 (0,821) | 0,749 | no: probabilita' che non sia fortuna 0.72 sotto 0,80 |
| 169 A | 1,99 | 300 | 4,78 | 3,83 (3,45) | sì; composto sì | **0,584** | 0,741 | 0,835 | 0,567 (0,561) | 0,782 (0,759) | 0,615 | no: probabilita' che non sia fortuna 0.58 sotto 0,80 |
| 169 B | 2,10 | 300 | 5,05 | 4,11 (3,62) | sì; composto sì | **0,692** | 0,828 | 0,899 | 0,658 (0,640) | 0,851 (0,819) | 0,720 | no: probabilita' che non sia fortuna 0.69 sotto 0,80 |
| G1 (prova 57) | 1,97 | 300 | 4,73 | 3,72 (3,31) | sì; composto sì | **0,561** | 0,723 | 0,820 | 0,548 (0,543) | 0,765 (0,739) | — | no: probabilita' che non sia fortuna 0.56 sotto 0,80 |
| G1 neutra (prova 88) | 1,91 | 300 | 4,60 | 3,52 (3,02) | sì; composto sì | **0,508** | 0,681 | 0,789 | 0,506 (0,505) | 0,731 (0,701) | — | no: probabilita' che non sia fortuna 0.51 sotto 0,80 |
| G11 (prova 69) | 2,05 | 300 | 4,92 | 3,90 (3,35) | sì; composto sì | **0,647** | 0,797 | 0,878 | 0,617 (0,601) | 0,823 (0,786) | — | no: probabilita' che non sia fortuna 0.65 sotto 0,80 |
| F5 (prova 24, serie del mazzo: quella di prima della correzione delle parità; la F5 rifatta dal revisore del 27 novembre ha Sharpe 1,88) | 1,91 | 301 | 4,60 | 3,83 (3,63) | sì; composto sì | **0,506** | 0,666 | 0,769 | 0,505 (0,505) | 0,729 (0,719) | — | no: probabilita' che non sia fortuna 0.51 sotto 0,80 |
| F5+M7+K2 (prova 28, serie del mazzo) | 2,16 | 301 | 5,20 | 4,44 (4,09) | sì; composto sì | **0,724** | 0,842 | 0,904 | 0,694 (0,680) | 0,866 (0,847) | — | no: probabilita' che non sia fortuna 0.72 sotto 0,80 |
| F5+M7+K2 (misura del riesame della 28: 251 settimane fino al 19 ottobre) | 2,15 | 251 | 4,73 | 4,03 (3,72) | sì; composto sì | **0,691** | 0,803 | 0,867 | 0,665 (0,652) | 0,829 (0,809) | — | no: probabilita' che non sia fortuna 0.69 sotto 0,80 |
| G1 (misura del 12 novembre, quella dello 0,945) | 1,98 | 300 | 4,76 | 3,75 (3,33) | sì; composto sì | **0,576** | 0,735 | 0,829 | 0,560 (0,553) | 0,773 (0,747) | — | no: probabilita' che non sia fortuna 0.58 sotto 0,80 |

* Nessuna prova passa l'esame in vigore. Le varianti della famiglia di G1 (168, 169) sono «no» solo per la probabilità. Chi passerebbe
  (stesse altre condizioni; per (c) e (d) con il t robusto da 3): con (a) 168 A, 168 B, 169 B e la miscela (0,835 / 0,849 / 0,828; miscela
  0,842, con la misura del riesame 0,803); con (b) anche 169 A, G1 e G11 (G1 neutra 0,789 e F5 0,769 no); con (c) nessuna; con (d) 168 A,
  168 B, 169 B, G11 e la miscela. **Riserva** (`ASTICELLA.md`, sezioni 5 e 6): queste regole nascono dopo aver visto i numeri; se il proprietario ne sceglie una,
  vale per le prove nuove e da sola non convalida le candidate già viste. La 169 resta «no» anche per le sue regole scritte prima
  (fallimento utile: le spese dei cambi superano metà del guadagno su G1, `RISULTATI_CENTOSETTIMA_BIS.md`).
* G1, G1 neutra, G11, F5 e la miscela sono già nel paper: il loro numero sul mazzo di oggi è solo un confronto. Per G1 vale lo 0,945 di
  quando è stata scelta (tabella sotto).
* La 165 B ha la somma del 2024 positiva ma il conto composto negativo (unico caso nella tabella): è il punto dell'audit sugli anni.

**G1 con il mazzo di quando è stata scelta (prova 57)**: N 65 famiglie (`asticella.mazzo(fino_alla=57)`). Le prove a incasso quasi fisso
non c'erano, quindi (a) è uguale al numero in vigore.

| G1 sul mazzo fino alla 57 | In vigore | (a) | (b) | (c) 4 rit. (13) | (d) 4 rit. (13) | t semplice | t robusto 4 (13) | settimane efficaci 4 (13) |
|---|---|---|---|---|---|---|---|---|
| misura del 12 novembre (lo 0,945 della decisione del 23 novembre) | **0,945** | 0,945 | 0,971 | 0,896 (0,868) | 0,931 (0,906) | 4,76 | 3,75 (3,33) | 186 (147) |
| misura della prova 57 (la serie del mazzo) | **0,941** | 0,941 | 0,968 | 0,891 (0,863) | 0,928 (0,903) | 4,73 | 3,72 (3,31) | 186 (147) |
Mazzo fino alla 57: 102 serie, N 65, in V 58 (con la regola simmetrica 57), deviazione 0,5667 (simmetrica 0,5184).

**I tre mazzi e lo Sharpe che serve oggi per arrivare a 0,80** (rendimenti normali; `asticella.sharpe_minimo`). Sotto un anno di dati
decide il t da 3, non la probabilità.

| Mazzo | Famiglie (N) | In V | Deviazione di V | Fortuna da battere (Sharpe l'anno) | Sharpe per 0,80 su 300 / 150 / 100 / 52 / 22 settimane |
|---|---|---|---|---|---|
| in vigore | 200 | 154 | 0,6891 | 1,91 | 2,27 / 2,42 / 2,53 / 2,79 / 3,30 |
| (a) senza 157, 159 e 161 | 198 | 152 | 0,6271 | 1,73 | 2,09 / 2,24 / 2,36 / 2,61 / 3,12 |
| (b) V simmetrica, senza 157 | 200 | 149 | 0,5798 | 1,60 | 1,96 / 2,11 / 2,23 / 2,48 / 2,98 |
| t da 3 (Sharpe che serve) | — | — | — | — | 1,25 / 1,77 / 2,16 / 3,00 / 4,61 |

**Di quanto cambiano i numeri con le correzioni dei dati del punto 1** (stesso mazzo di oggi, stesse misure): solo la 151 e la 153 B
entrano in V (N resta 200; in V da 152 a 154; deviazione da 0,6776 a 0,6891). Le correzioni della G10 e dei vuoti della 149 da sole
non spostano niente (stesse 200 famiglie, stessa V: controllato).

| Candidata | Prima delle correzioni (mazzo di oggi) | Dopo | Differenza |
|---|---|---|---|
| 57 G1 | 0,5929 | 0,5615 | -0,0314 |
| 88 G1N | 0,5406 | 0,5077 | -0,0329 |
| 69 G11 | 0,6770 | 0,6466 | -0,0304 |
| 24 F5 | 0,5366 | 0,5064 | -0,0302 |
| 28 F5+M7+K2 | 0,7487 | 0,7244 | -0,0243 |
| 162 A | 0,0021 | 0,0018 | -0,0003 |
| 162 B | 0,0000 | 0,0000 | -0,0000 |
| 163 A | 0,0000 | 0,0000 | -0,0000 |
| 163 B | 0,0005 | 0,0004 | -0,0001 |
| 165 A | 0,0050 | 0,0044 | -0,0007 |
| 165 B | 0,0154 | 0,0136 | -0,0018 |
| 168 A | 0,7296 | 0,7020 | -0,0276 |
| 168 B | 0,7487 | 0,7222 | -0,0266 |
| 169 A | 0,6145 | 0,5835 | -0,0310 |
| 169 B | 0,7200 | 0,6918 | -0,0281 |


**Due varianti di (b) che il verificatore dell'audit chiede di portare al proprietario** (non nella funzione; script `esame/nota_b.py`):
* tenere in V la famiglia della candidata (così il suo stesso t non le abbassa la soglia): G1 0,776,
  168 A 0,873, 168 B 0,885, miscela (riesame)
  0,838, G1 del 12 novembre 0,786; lo Sharpe che
  serve su 300 settimane diventa 2,02 (contro 1,96 di (b) e 2,27 in vigore);
* togliere da V anche la 55 C3 (pure lei «FAIL del calcolo»): sposta il numero in vigore di 0,001 al massimo (G1 0,562,
  168 B 0,722); con (b) niente, perché la sua famiglia (quella di G1) è già fuori da V.
