# L'esame delle prove con la regola in vigore dal 27 novembre 2026 (decisione del proprietario)

Calcolato con `research/programma6/asticella.esame` dopo la decisione del proprietario del 27 novembre 2026 (`ASTICELLA.md`, sezione 7),
sul mazzo di oggi (= mazzo fino alla prova 169): 291 serie, 48 prove senza serie, **200 famiglie, 149 in V, deviazione di V 0,5798**
(con la regola di prima 154 in V e 0,6891). Script: `research/programma6/esame_27_novembre.py` (risultati interi in
`risultati_asticella/esame_27_novembre.json`); i numeri di G1, 168 e 169 sono controllati da `tests/test_esame_unico.py`.

**La regola nuova (in vigore)**: netto positivo, ogni anno solare positivo (media delle settimane × 52), **t robusto** di Newey e West con 4
settimane di ritardo da 3, **probabilità che non sia fortuna** da 0,80 calcolata sulle **settimane efficaci**, con N = famiglie di oggi e
la **V simmetrica** (fuori da V le famiglie con il t sotto −3 e sopra +3) **senza le serie della 157** bocciata dal revisore. È il numero
che la tabella di stamattina (`ESAME_NUMERI_2026-11-27.md`) chiamava «(d)». **Accanto, non ufficiali**: la **regola fino al 27 novembre**
(V senza le sole perdenti, t e settimane semplici: il numero «in vigore» della tabella di stamattina), (a) la regola nuova senza le serie
a incasso quasi fisso 157, 159 e 161 (N 198), il controllo con 13 settimane di ritardo.

Misure: per le prove 162-169 e le strategie in corso la serie del mazzo (per la 162-169 coincide con la misura pubblicata dalla prova;
per G1 con l'esame della prova 57). F5: la serie del mazzo è quella di prima della correzione delle parità (la F5 rifatta dal revisore
del 27 novembre ha Sharpe 1,88). F5 + M7 + K2: la serie del mazzo (301 settimane) e la misura del suo riesame (251 settimane fino al 19
ottobre, funding vero). G1: anche la misura del 12 novembre, quella dello 0,945. Le prove 164 e 166 non sono state eseguite e la 167 ha un
campione troppo piccolo (26 eventi): non hanno numeri.

## Le prove 162-169 e le strategie in corso (G1, G1 neutra, G11 e F5 nel paper; la miscela a tavolino), mazzo di oggi

| Prova | **Esito con la regola nuova** | **Probabilità (in vigore)** | t robusto (4 rit.) | Settimane efficaci / settimane | Sharpe | Ogni anno positivo (somma; composto) | Regola fino al 27 novembre: probabilità | … t semplice | … esito | (a) senza 157, 159, 161 | Controllo 13 ritardi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 162 A | no: anni non positivi 2024; t robusto 0.14 sotto 3; probabilita' che non sia fortuna 0.01 sotto 0,80 | **0,012** | 0,14 | 119 / 137 | 0,09 | no (2024); composto no (2024) | 0,002 | 0,15 | no: anni non positivi 2024; t 0.15 sotto 3; probabilita' che non sia fortuna 0.00 sotto 0,80 | 0,012 | 0,013 (t 0,14, 116 sett.) |
| 162 B | no: netto non positivo; anni non positivi 2024,2025,2026; t robusto -9.35 sotto 3; probabilita' che non sia fortuna 0.00 sotto 0,80 | **0,000** | -9,35 | 117 / 138 | -6,23 | no (2024, 2025, 2026); composto no (2024, 2025, 2026) | 0,000 | -10,15 | no: netto non positivo; anni non positivi 2024,2025,2026; t -10.15 sotto 3; probabilita' che non sia fortuna 0.00 sotto 0,80 | 0,000 | 0,000 (t -11,67, 182 sett.) |
| 163 A | no: netto non positivo; anni non positivi 2025; t robusto -0.64 sotto 3; probabilita' che non sia fortuna 0.00 sotto 0,80 | **0,000** | -0,64 | 171 / 172 | -0,35 | no (2025); composto no (2025) | 0,000 | -0,64 | no: netto non positivo; anni non positivi 2025; t -0.64 sotto 3; probabilita' che non sia fortuna 0.00 sotto 0,80 | 0,000 | 0,000 (t -0,63, 167 sett.) |
| 163 B | no: anni non positivi 2025; t robusto 0.11 sotto 3; probabilita' che non sia fortuna 0.00 sotto 0,80 | **0,003** | 0,11 | 163 / 174 | 0,06 | no (2025); composto no (2025) | 0,000 | 0,12 | no: anni non positivi 2025; t 0.12 sotto 3; probabilita' che non sia fortuna 0.00 sotto 0,80 | 0,003 | 0,009 (t 0,10, 125 sett.) |
| 165 A | no: anni non positivi 2026; t robusto 0.31 sotto 3; probabilita' che non sia fortuna 0.01 sotto 0,80 | **0,012** | 0,31 | 134 / 124 | 0,19 | no (2026); composto no (2026) | 0,004 | 0,30 | no: anni non positivi 2026; t 0.30 sotto 3; probabilita' che non sia fortuna 0.00 sotto 0,80 | 0,012 | 0,008 (t 0,33, 154 sett.) |
| 165 B | no: anni non positivi 2026; t robusto 0.79 sotto 3; probabilita' che non sia fortuna 0.03 sotto 0,80 | **0,033** | 0,79 | 141 / 126 | 0,48 | no (2026); composto no (2024, 2026) | 0,014 | 0,75 | no: anni non positivi 2026; t 0.75 sotto 3; probabilita' che non sia fortuna 0.01 sotto 0,80 | 0,033 | 0,034 (t 0,79, 139 sett.) |
| 168 A | **sì** | **0,842** | 3,90 | 178 / 300 | 2,11 | sì; composto sì | 0,702 | 5,08 | no: probabilita' che non sia fortuna 0.70 sotto 0,80 | 0,842 | 0,811 (t 3,45, 138 sett.) |
| 168 B | **sì** | **0,852** | 3,96 | 178 / 300 | 2,14 | sì; composto sì | 0,722 | 5,13 | no: probabilita' che non sia fortuna 0.72 sotto 0,80 | 0,853 | 0,821 (t 3,47, 137 sett.) |
| 169 A | no: probabilita' che non sia fortuna 0.78 sotto 0,80 | **0,782** | 3,83 | 193 / 300 | 1,99 | sì; composto sì | 0,584 | 4,78 | no: probabilita' che non sia fortuna 0.58 sotto 0,80 | 0,783 | 0,759 (t 3,45, 157 sett.) |
| 169 B | **sì** | **0,851** | 4,11 | 199 / 300 | 2,10 | sì; composto sì | 0,692 | 5,05 | no: probabilita' che non sia fortuna 0.69 sotto 0,80 | 0,851 | 0,819 (t 3,62, 154 sett.) |
| G1 (prova 57) | no: probabilita' che non sia fortuna 0.76 sotto 0,80 | **0,765** | 3,72 | 186 / 300 | 1,97 | sì; composto sì | 0,561 | 4,73 | no: probabilita' che non sia fortuna 0.56 sotto 0,80 | 0,765 | 0,739 (t 3,31, 147 sett.) |
| G1 neutra (prova 88) | no: probabilita' che non sia fortuna 0.73 sotto 0,80 | **0,731** | 3,52 | 176 / 300 | 1,91 | sì; composto sì | 0,508 | 4,60 | no: probabilita' che non sia fortuna 0.51 sotto 0,80 | 0,731 | 0,701 (t 3,02, 130 sett.) |
| G11 (prova 69) | **sì** | **0,823** | 3,90 | 189 / 300 | 2,05 | sì; composto sì | 0,647 | 4,92 | no: probabilita' che non sia fortuna 0.65 sotto 0,80 | 0,823 | 0,786 (t 3,35, 139 sett.) |
| F5 (prova 24, serie del mazzo: quella di prima della correzione delle parità) | no: probabilita' che non sia fortuna 0.73 sotto 0,80 | **0,729** | 3,83 | 208 / 301 | 1,91 | sì; composto sì | 0,506 | 4,60 | no: probabilita' che non sia fortuna 0.51 sotto 0,80 | 0,730 | 0,719 (t 3,63, 187 sett.) |
| F5+M7+K2 (prova 28, serie del mazzo, 301 settimane) | **sì** | **0,866** | 4,44 | 219 / 301 | 2,16 | sì; composto sì | 0,724 | 5,20 | no: probabilita' che non sia fortuna 0.72 sotto 0,80 | 0,867 | 0,847 (t 4,09, 186 sett.) |
| F5+M7+K2 (misura del riesame della 28: 251 settimane fino al 19 ottobre, funding vero) | **sì** | **0,829** | 4,03 | 183 / 251 | 2,15 | sì; composto sì | 0,691 | 4,73 | no: probabilita' che non sia fortuna 0.69 sotto 0,80 | 0,829 | 0,809 (t 3,72, 155 sett.) |
| G1 (misura del 12 novembre, quella dello 0,945) | no: probabilita' che non sia fortuna 0.77 sotto 0,80 | **0,773** | 3,75 | 186 / 300 | 1,98 | sì; composto sì | 0,576 | 4,76 | no: probabilita' che non sia fortuna 0.58 sotto 0,80 | 0,773 | 0,747 (t 3,33, 147 sett.) |

## Chi passa ora e chi no

**Passano con la regola nuova** (tutte le altre condizioni erano già rispettate: netto positivo, ogni anno positivo anche sul conto
composto; il t robusto è sopra 3 per tutte):
* **168 A** 0,842 (t robusto 3,90, 178 settimane efficaci su 300) e **168 B** 0,852 (3,96, 178): con la regola di prima 0,702 e 0,722.
* **169 B** 0,851 (4,11, 199): con la regola di prima 0,692.
* Fra le strategie già in corso: **G11** 0,823 (3,90, 189; prima 0,647) e la miscela **F5 + M7 + K2** 0,866 (4,44, 219; prima 0,724;
  con la misura del riesame 0,829, prima 0,691).

**Non passano**: **169 A** 0,782 (t robusto 3,83: solo la probabilità è sotto 0,80); **G1** 0,765 sul mazzo di oggi (0,773 con la misura
del 12 novembre); **G1 neutra** 0,731; **F5** 0,729; le **162, 163, 165** per gli anni negativi e il t sotto 3 (la 162 B e la 163 A anche
per il netto negativo), con la probabilità fra 0,000 e 0,033.

**Perché cambia.** Due cose spingono in direzioni opposte. La V simmetrica toglie da V la famiglia grande di G1 (46 serie: G1, F5, G11,
la miscela, la 168, la 169 e le parenti) e altre 4 famiglie con il t sopra +3: la dispersione scende da 0,689 a 0,580 e la fortuna da
battere da 1,91 a 1,60 di Sharpe l'anno. Le settimane efficaci invece contano meno settimane per le serie con le settimane legate (G1 e
parenti: da 300 a 176-219) e abbassano la probabilità. Per la famiglia di G1 vince la prima: la probabilità sale da +0,13 a +0,22.

**La 169 resta «no» anche se la 169 B ora passa**: con le sue regole scritte prima (`research/programma7/CENTOSETTIMA_BIS.md`, l'esame di
allora) era non promettente (0,61 e 0,72), e il fallimento utile scritto prima scatta: B guadagna su G1 1,97 punti l'anno ma i cambi di
stato costano 1,32 l'anno, più della metà; A non guadagna su G1 (`research/programma7/RISULTATI_CENTOSETTIMA_BIS.md`).

**Riserva** (`ASTICELLA.md`, sezione 7): i due modi nascono dopo aver visto i numeri delle prove 162-169. Il calcolo di oggi da solo non
convalida le prove già viste che ora passano: la **168 A e B va dal revisore delle prove** (backtest-auditor) prima del paper. G11 è già
nel paper e il suo stato non cambia; la miscela (PASS tecnico al riesame, misurata a tavolino ogni settimana dall'11 novembre) ora
passerebbe, ma un suo passaggio al paper passa prima dal revisore, con la stessa riserva. La regola giudica le prove nuove, dalla 170 in
poi.

**Altre cose viste**:
* (a) senza le prove a incasso quasi fisso sposta quasi niente (al massimo +0,0005): con la V simmetrica le famiglie della 159 e della
  161 (con la 97 CC) erano già fuori da V (t sopra +3) e la 157 è tolta come bocciata; cambia solo N (198).
* Il controllo con 13 settimane di ritardo abbassa la probabilità della famiglia di G1 di 0,01-0,04: con 13 ritardi la 168 A (0,811),
  la 168 B (0,821), la 169 B (0,819) e la miscela (0,847; riesame 0,809) restano sopra 0,80, G11 scende a 0,786.
* La 165 ha più settimane efficaci che settimane (134 su 124, 141 su 126): le sue settimane tendono ad alternarsi (correlazione
  negativa con quelle prima), e il t robusto è un po' più alto di quello semplice. Non cambia il suo esito.
* G1 resta «sì» con lo sconto di quando è stata scelta (mazzo fino alla 57): 0,931 con la regola nuova, 0,945 con quella di allora.

## G1 con il mazzo di quando è stata scelta (prova 57)

N 65 famiglie (`asticella.mazzo(fino_alla=57)`, 102 serie); in V 57 con la regola nuova (deviazione 0,5184), 58 con quella di prima
(0,5667). Le prove a incasso quasi fisso non c'erano, quindi (a) è uguale al numero in vigore.

| Prova | **Esito con la regola nuova** | **Probabilità (in vigore)** | t robusto (4 rit.) | Settimane efficaci / settimane | Sharpe | Ogni anno positivo (somma; composto) | Regola fino al 27 novembre: probabilità | … t semplice | … esito | (a) senza 157, 159, 161 | Controllo 13 ritardi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G1 sul mazzo fino alla 57, misura del 12 novembre (lo 0,945 della decisione del 23 novembre) | **sì** | **0,931** | 3,75 | 186 / 300 | 1,98 | sì; composto sì | 0,945 | 4,76 | **sì** | 0,931 | 0,906 (t 3,33, 147 sett.) |
| G1 sul mazzo fino alla 57, misura della prova 57 (la serie del mazzo) | **sì** | **0,928** | 3,72 | 186 / 300 | 1,97 | sì; composto sì | 0,941 | 4,73 | **sì** | 0,928 | 0,903 (t 3,31, 147 sett.) |

## Lo Sharpe che serve oggi

Rendimenti normali, `asticella.sharpe_minimo` (con la regola nuova: la V in vigore e le settimane efficaci; per una serie con le settimane
non legate le settimane efficaci sono le settimane). La riga «settimane legate come G1» usa il rapporto di G1 (0,62: 186 settimane
efficaci su 300). Sotto un anno di dati decide il t da 3, non la probabilità.

| Mazzo | Famiglie (N) | In V | Deviazione di V | Fortuna da battere (Sharpe l'anno) | Sharpe per 0,80 su 300 / 150 / 100 / 52 / 22 settimane | t da 3: Sharpe che serve |
|---|---|---|---|---|---|---|
| regola nuova (in vigore) | 200 | 149 | 0,5798 | 1,60 | 1,96 / 2,11 / 2,23 / 2,48 / 2,98 | 1,25 / 1,77 / 2,16 / 3,00 / 4,61 |
| regola nuova, serie con le settimane legate come G1 (rapporto 0,62) | 200 | 149 | 0,5798 | 1,60 | 2,06 / 2,25 / 2,40 / 2,73 / 3,38 | 1,59 / 2,24 / 2,75 / 3,81 / 5,86 |
| (a) regola nuova senza 157, 159, 161 | 198 | 149 | 0,5802 | 1,60 | 1,96 / 2,11 / 2,23 / 2,48 / 2,98 | 1,25 / 1,77 / 2,16 / 3,00 / 4,61 |
| regola fino al 27 novembre | 200 | 154 | 0,6891 | 1,91 | 2,27 / 2,42 / 2,53 / 2,79 / 3,30 | 1,25 / 1,77 / 2,16 / 3,00 / 4,61 |

**Nota della verifica indipendente (27 novembre 2026)**: numeri rifatti da capo, tutti uguali. Se la famiglia della candidata restasse in V
(domanda aperta, sezione 7 di `ASTICELLA.md`): 168 A 0,810, 168 B 0,822, 169 B 0,818, miscela (serie del mazzo) 0,838 passano ancora;
**G11 0,787 e la miscela misurata al riesame 0,7998 no**; G1 alla 57 0,896, G1 oggi 0,724, 169 A 0,743. Il «sì» di G11 e della miscela
dipende quindi da questa scelta, quello della 168 no.
