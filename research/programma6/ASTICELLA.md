# Programma 6 — l'asticella rivista: lo Sharpe corretto come lo prescrivono i suoi autori

Scritto il 22 ottobre 2026, mattina, **prima di ricalcolare**, su richiesta del proprietario: «riguarda questa asticella
[...] non sto dicendo di non avere un'asticella ma di essere sicuri che la stiamo usando nella maniera corretta».

> **L'esame in vigore oggi** (27 novembre 2026) non è più quello delle sezioni 3-5 con la soglia 0,95: probabilità che non sia fortuna
> da **0,80** (9 novembre), N = **famiglie** del mazzo completo (11 novembre), sconto **una volta sola** quando una strategia viene
> scelta (23 novembre), t dello Sharpe da 3 e ogni anno positivo. È scritto in una funzione sola, `asticella.esame`, con accanto i
> numeri non ufficiali da mostrare al proprietario: sezione 6. Le sezioni 1-5 restano com'erano, per la storia.

## 1. Cosa abbiamo fatto finora

Lo «Sharpe corretto» è il Deflated Sharpe Ratio (Bailey e López de Prado, *Journal of Portfolio Management* 2014): la
probabilità che lo Sharpe vero della strategia sia sopra il massimo che N prove senza vantaggio darebbero per caso. Il
massimo per caso dipende da due numeri: **N**, quante prove indipendenti, e **V**, quanto variano gli Sharpe delle prove.
Noi abbiamo messo **N = tutte le prove contate una per una** (107) e **V = la varianza degli Sharpe di tutte le 107**.

## 2. Cosa prescrivono gli autori (e dove sbagliamo)

1. **N è il numero di prove indipendenti, non di prove.** Varianti molto simili (le 34 strategie di TradingView, le versioni
   di F, le combinazioni che contengono F5) sono quasi la stessa prova. López de Prado (2019, «A Data Science Solution to the
   Multiple-Testing Crisis in Financial Research», *Journal of Financial Data Science*; 2020, *Machine Learning for Asset
   Managers*, cap. 8) prescrive di **raggruppare le prove per somiglianza dei rendimenti** e usare come N il numero di gruppi.
2. **V è la varianza degli Sharpe dei gruppi**, non delle prove una per una: ogni gruppo diventa una strategia (la media dei
   suoi membri) e si misura il suo Sharpe. Contando le prove una per una, le famiglie con tante varianti pesano di più e le
   strategie che perdono per costruzione (per esempio le regole di TradingView a 4 ore con il 40-58% l'anno di spese) allargano
   V e alzano l'asticella anche per strategie che con loro non hanno niente a che fare.

Il livello del 95% resta: è il livello standard. La revisione non tocca le altre condizioni dell'esame (intervallo sopra zero,
anni, ultimo anno, costi doppi, trimestri, più del Bitcoin).

## 3. La procedura corretta (fissata qui, prima del calcolo)

* **Le serie**: i rendimenti netti settimanali di ogni prova a portafoglio salvati nei `risultati_*` (quelli giornalieri
  sommati per settimana); per le prove a operazioni senza serie salvata (34, 35, 37, 39, 40, 41, 43, 45-I2) la serie si
  ricostruisce dalle operazioni salvate con il loro portafoglio; le prove senza nessuna serie (le famiglie della prova 1 e
  della 2B, i rimbalzi 4-5) contano **ognuna come un gruppo a sé** con il suo Sharpe pubblicato (scelta prudente: N più alto).
* **La somiglianza**: la correlazione dei rendimenti settimanali sulle settimane comuni (almeno 52).
* **I gruppi**: raggruppamento gerarchico a legame medio con la distanza √((1 − ρ)/2), tagliato a **ρ = 0,5** (stanno nello
  stesso gruppo le prove con correlazione media almeno 0,5). Si riportano anche i tagli a 0,3 e 0,7, solo per capire.
* **Gli Sharpe dei gruppi**: lo Sharpe della media a pesi uguali dei membri sulle loro settimane.
* **N** = numero di gruppi; **V** = varianza degli Sharpe dei gruppi; lo Sharpe corretto di ogni candidata con il suo Sharpe,
  le sue settimane, la sua asimmetria e curtosi (come `terza.sharpe_corretto`), soglia **0,95**.
* Per confronto, una seconda asticella pubblicata e diversa: il **t dello Sharpe** (Sharpe × √anni) contro **3,0**, la soglia
  che Harvey, Liu e Zhu (*Review of Financial Studies* 2016) chiedono ai fattori nuovi perché se ne provano tanti.
* **Si accetta quello che viene**: se una candidata passa, è validata sul passato con questa asticella; se no, no. Nel registro
  restano scritti tutti e due i valori, quello di prima e quello rivisto, con questo file.

## 4. Riserva

La revisione arriva dopo aver visto F5 a 0,52 con il calcolo di prima. Per questo la procedura è quella pubblicata dagli autori,
con un solo valore scelto qui (il taglio a 0,5) e i tagli 0,3 e 0,7 riportati accanto: se il verdetto cambiasse solo a uno dei
tagli, lo si dice.

## 5. Aggiunta del 23 ottobre, mattina: le prove che perdono di sicuro

Scritta **dopo** aver visto il calcolo della prova 55 e **prima** di calcolare la regola qui sotto.

**Cosa è successo.** Con le cinque serie dello scalping (prova 54: Sharpe dei portafogli da −2,4 a −13,6, perché pagano i costi
su migliaia di operazioni con una regolarità quasi perfetta) la deviazione degli Sharpe dei gruppi passa da **0,62 a 2,56** e
lo Sharpe corretto rivisto di **ogni** candidata diventa **0,00**, anche quello di F5 (0,87 senza quelle serie). Il massimo
«per caso» con quella deviazione è uno Sharpe di circa 6: nessuna strategia vera ci arriva. Un'asticella che si può alzare a
piacere provando idee che perdono per costruzione non misura più il rischio di aver trovato una strategia per fortuna, che è il
suo unico scopo: il teorema su cui poggia (Bailey e López de Prado, la «False Strategy Theorem») calcola il massimo che
danno prove **senza vantaggio**, cioè con Sharpe vero zero; una prova con il t dello Sharpe a −20 non è una prova senza
vantaggio, è una prova che perde di sicuro, e non può essere lei il massimo fortunato.

**La regola, da qui in avanti.** Un gruppo il cui t dello Sharpe (Sharpe × √(settimane/52), sulle settimane della sua serie
media; per le prove senza serie, sulle 300 settimane del programma) è **sotto −3** (la soglia di Harvey, Liu e Zhu, dalla parte
delle perdite) **conta in N ma non in V**. Tutto il resto resta come nella sezione 3. Si riportano sempre tutti e due i valori:
quello della sezione 3 e quello con questa aggiunta.

*27 novembre 2026 (audit del 26 novembre, esame-4)*: «per le prove senza serie, sulle 300 settimane del programma» pensava alle prove 1
e 2B, che coprono tutto il periodo. Da oggi ogni prova senza serie usa le **sue** settimane (151: 19, 153: 196, 110: 286, 108 e 111:
143; le 300 restano per le 1 e 2B): la 151 (t −0,77 invece di −3,05) e la 153 B (−2,45 invece di −3,03) entrano in V. Effetto nella
sezione 6.

**Riserva, fissata qui.** La regola nasce dopo aver visto F5 (0,87), F5 + M7 + K2 (0,90) e C3 (0,80 senza le serie dello
scalping). Per questo **non può validare le candidate già viste**: se con questa regola una di loro supera 0,95, lo si scrive,
ma resta «non validata sul passato» e la sua prova resta il paper. La regola vale per giudicare le prove dalla 56 in poi.

## 6. L'esame in vigore in una funzione sola, e i numeri accanto (27 novembre 2026, audit del 26 novembre)

Scritto dopo l'audit del sistema (`audits/reports/2026-11-26-AUDIT_SISTEMA.md`, problemi esame-1 … esame-10 e punti ciechi 1-2).
**Nessuna regola dell'esame cambia qui**: i cambi di regola li decide il proprietario.

**L'esame in vigore** (`asticella.esame`; decisioni del 9, 11 e 23 novembre in `docs/decisioni_del_proprietario.md`): una prova è
«PROMETTENTE» se il netto è positivo, **ogni anno solare è positivo** (media delle settimane × 52, gli anni parziali compresi, come
`terza.esame`), il **t dello Sharpe** (Sharpe × √(settimane/52)) è almeno **3** e la **probabilità che non sia fortuna**
(`terza.sharpe_corretto`, N = famiglie del mazzo di oggi, V senza le famiglie con il t sotto −3, sezioni 3 e 5) è almeno **0,80**.
Stessa probabilità di `corretto_famiglie`. Una strategia già scelta si giudica con lo sconto una volta sola, con il mazzo di quando è
stata scelta (`asticella.mazzo(fino_alla=57)` per G1: 102 serie, 65 famiglie, **0,945**); il numero sul mazzo di oggi per lei è solo
un confronto. Le prove nuove chiamano `esame(nuove, candidate)` al posto di `corretto_famiglie` più una regola scritta a mano.

**Due correzioni dei dati del mazzo** (problemi esame-4 ed esame-8), che valgono per i conti da oggi in poi:
* le prove senza serie con le loro settimane (sezione 5, nota del 27 novembre);
* la 68 G10 con le settimane senza operazioni a zero, come le altre prove a eventi (301 settimane invece delle 150 operate: Sharpe
  −1,35 invece di −1,94; resta fuori da V); le settimane vuote (NaN) tolte coppia per coppia nelle correlazioni (`correlazioni`: le 12
  serie della 149 su APT e MATIC prima davano correlazione 0 con ogni serie piena).

Effetto sul mazzo di oggi (291 serie, 48 prove senza serie): N resta **200**; in V da **152 a 154** famiglie; deviazione di V da
**0,6776 a 0,6891**; la fortuna da battere da 1,87 a 1,91 di Sharpe l'anno. La seconda correzione da sola non sposta niente (stesse 200
famiglie, stessa V). I numeri pubblicati scendono di circa 0,03: G1 0,593 → 0,561, 168 A 0,730 → 0,702, 168 B 0,749 → 0,722, 169 A
0,615 → 0,584, 169 B 0,720 → 0,692; G1 alla 57 resta 0,945 (alla 57 queste prove non c'erano). Nessun verdetto cambia: erano già
tutti sotto 0,80. Questi numeri sono controllati da `tests/test_esame_unico.py` (mazzo fino alla prova 169).

**I numeri accanto, NON ufficiali** (si scrivono nel risultato di ogni prova finché il proprietario non decide; ognuno cambia una cosa
sola rispetto all'esame in vigore):
* **(a)** senza le serie a incasso quasi fisso (prove 157, 159 e 161), con le famiglie rifatte senza di loro: la regola del 15 novembre
  (`docs/backlog.md`, P34: «si scrivono con e senza»);
* **(b)** la dispersione V **simmetrica**: fuori da V anche le famiglie con il t sopra +3 (restano in N), perché il motivo della sezione 5
  («il teorema guarda prove senza vantaggio») vale anche per loro; e senza le serie della 157, il calcolo bocciato dal revisore
  (`audits/reports/2026-11-15-PROVA157.md`);
* **(c)** il **t robusto** di Newey e West con 4 settimane di ritardo (13 come controllo) e la probabilità con le **settimane efficaci**
  (settimane × varianza semplice / varianza di lungo periodo della serie della candidata) al posto delle settimane: le settimane di G1 e
  delle parenti sono legate fra loro (correlazione 0,19 con la settimana prima), e il t semplice le conta come indipendenti;
* **(d)** (b) e (c) insieme;
* ogni anno anche sul **conto composto** (esame-9): un anno con la somma positiva può essere una perdita sul conto.

Sul mazzo di oggi la 168 B fa 0,722 in vigore, 0,849 (a), 0,913 (b), 0,675 (c, t robusto 3,96, 178 settimane efficaci) e 0,852 (d);
G1 alla 57 fa 0,945 in vigore e 0,896 con le settimane efficaci (186). **Riserva, come nella sezione 5**: queste regole nascono dopo
aver visto i numeri; se il proprietario ne adotta una, vale per le prove nuove e non convalida da sola le candidate già viste (la 168,
la miscela). Il verificatore dell'audit propone anche, per (b), di tenere in V la famiglia della candidata (così il suo t non le
abbassa la soglia) e di togliere da V anche la 55 C3 (pure bocciata nel calcolo): sono domande per il proprietario, non sono nella
funzione.

**Lo Sharpe che serve oggi per 0,80** (rendimenti normali, `sharpe_minimo`; sul mazzo di oggi dopo le correzioni) su 300 / 150 / 100 / 52 /
22 settimane: in vigore 2,27 / 2,42 / 2,53 / 2,79 / 3,30; con (a) 2,09 / 2,24 / 2,36 / 2,61 / 3,12; con (b) 1,96 / 2,11 / 2,23 / 2,48 /
2,98. Il t da 3 chiede 1,25 / 1,77 / 2,16 / 3,00 / 4,61: sotto un anno di dati decide il t, non la probabilità, e per le idee con una
storia corta resta il giudizio in avanti (`research/programma6/paper/REGOLE.md`, sezione 17). Vale anche per le varianti di G1, che
dal 23 novembre si giudicano con l'N di oggi: a una variante servono 2,27 su 300 settimane, G1 ha 1,97 (esame-3, domanda aperta).

**Quello che il mazzo non conta, scritto qui perché non era scritto (esame-6)**: N parte dalla prova 1 del programma 6, come il conto
del registro (`research/REGISTRO.md`, sezione 1). Restano fuori le circa 60 idee del programma 5 con le loro varianti, il vecchio
sistema automatico e i protocolli per moneta: non hanno serie settimanali nel formato del mazzo, e il conto del registro le tiene in
sezioni separate. Contarle (come le prove 1 e 2B, ognuna una famiglia con il suo Sharpe) abbasserebbe lo 0,945 di G1 a circa 0,92 /
0,90 / 0,87 con 30 / 60 / 100 famiglie in più (stima dell'audit, con la dispersione ferma). La scelta resta al proprietario.

**Gli anni (esame-9)**: «ogni anno positivo» resta la media delle settimane × 52 per anno solare, con gli anni parziali qualunque sia la
loro lunghezza (la prova 165 usava almeno 8 settimane). Una regola sola per gli anni parziali la decide il proprietario; intanto la
funzione scrive accanto il conto composto.
