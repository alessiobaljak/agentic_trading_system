# Prova 29 — vendere allo scoperto le aziende piccole con le notizie peggiori del mese, decide il periodo chiuso

Regole scritte il 13 novembre 2026 **prima di qualsiasi calcolo sul periodo chiuso** (gennaio 2025 → settembre 2026, mai guardato da
nessuna prova sulle notizie) e prima di scaricare le notizie e i prezzi di quel periodo. Idea I31 di `REGISTRO.md`.

## Da dove viene, e perché si giudica solo sul periodo chiuso

Nella prova 28 (variante B, aziende piccole) il quinto con il tono delle notizie più basso ha fatto peggio del quinto più alto di
+0,94% al mese (t 3,04, 2016-2024), ma il quinto alto non ha battuto l'IWM: l'effetto stava tutto dal lato delle notizie cattive. È
coerente con gli studi: le parole negative anticipano i prezzi più delle positive (Tetlock, «Giving content to investor sentiment»,
*Journal of Finance* 62, 2007; Tetlock, Saar-Tsechansky, Macskassy, *Journal of Finance* 63, 2008), e le cattive notizie entrano nei
prezzi lentamente dove vendere allo scoperto è difficile e costoso (Hong, Lim, Stein, *Journal of Finance* 55, 2000).

**L'idea è nata guardando i risultati del 2016-2024**: quel periodo non la può giudicare. La giudica il periodo chiuso, **una volta
sola**, come la prova 19. Il risultato sul 2016-2024 si stampa accanto, con la scritta «già visto», e non conta.

**Sospetti scritti prima:**

* **il costo del prestito**: le aziende piccole con notizie cattive sono spesso care da prendere a prestito (diversi punti l'anno, a
  volte non si possono vendere allo scoperto). Il dato vero del passato non c'è: si usa una stima e si stampa il costo del prestito che
  azzererebbe il guadagno;
* **il periodo chiuso è corto** (21 mesi, circa 20 decisioni): anche un effetto vero può non vedersi, e un risultato buono può essere
  fortuna. Per questo l'esame chiede poco (guadagnare dopo i costi, anche doppi) e il passo dopo, se passa, è la misura **in avanti**
  sul demo, non i soldi veri;
* **il t di 3 è uscito dopo 73 tentativi** e una regola scelta guardando: ci si aspetta che sul periodo chiuso l'effetto sia più piccolo;
* aprire il periodo chiuso **consuma** quel periodo per tutta la famiglia «notizie»: una prova sulle notizie dopo questa potrà essere
  giudicata solo in avanti.

## I dati (gli stessi della prova 28, sul periodo nuovo)

* Le notizie dell'archivio di Alpaca, scaricate da un lavoro di GitHub da dicembre 2024 a settembre 2026; solo i conteggi e i risultati
  entrano nel repository.
* I prezzi al giorno di Alpaca, non rettificati, con il simbolo di allora (`asof` «-»), con dividendi e frazionamenti; un titolo in
  mano che resta 5 giorni di borsa senza prezzi si chiude all'ultima chiusura (come la prova 28).
* La composizione dell'S&P 500 giorno per giorno (stessa fonte), con i simboli di allora.

## Il tono (identico alla prova 28, nessun numero cambiato)

Notizie che citano da 1 a 3 simboli; titolo e riassunto; voto +1 / −1 / 0 con le stesse due liste di parole di
`stock/strategie/tono.py` (`BUONE`, `CATTIVE`); il tono del mese è la media dei voti delle notizie create dopo le 16:00 di New York
dell'ultimo giorno di borsa del mese prima e fino alle 16:00 dell'ultimo giorno di borsa del mese; almeno 3 notizie.

## La regola

* **Quali titoli:** gli stessi filtri della variante B della prova 28: il giorno della decisione **non** nell'S&P 500, chiusura di
  almeno 5 dollari, mediana dei dollari scambiati nelle 20 sedute prima di almeno 2 milioni, esclusi i fondi (stesso elenco di parole).
* **Ogni fine mese** (ultima chiusura del mese), fra quelli con il tono calcolabile: il **20% con il tono più basso**, al massimo 50
  (a pari tono prima chi ha più notizie, poi in ordine alfabetico); se i titoli con il tono calcolabile sono meno di 25, quel mese si
  resta fuori.
* **Posizioni:** vendute allo scoperto a pesi uguali per il **50%** del conto, e comprato l'**IWM** per il **50%**; ordini a mercato
  all'apertura del primo giorno di borsa del mese dopo; si tiene un mese.
* **Periodo giudicato:** decisioni dalla fine di dicembre 2024 alla fine di agosto 2026; rendimenti dal 2 gennaio 2025 al 30 settembre
  2026.

## I costi (fissati prima)

Metà scarto 15 punti base e slittamento 5 (come le prove 27 e 28 sulle piccole); commissioni Interactive Brokers «fisso»; **prestito
dei titoli venduti allo scoperto 3% l'anno** (stima prudente per titoli «facili» ma piccoli; i «difficili» costano di più) e nessun
prestito sull'IWM comprato. Versione con tutti i costi raddoppiati (prestito 6%).

## L'esame, solo sul periodo chiuso

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) con i costi doppi lo Sharpe resta sopra
zero; (3) almeno 4 trimestri su 7 in guadagno.

**Per entrare nella miscela** (idea I30, adattata perché la miscela sul periodo chiuso non si calcola, per non consumarlo anche per lei):
Sharpe con i costi sopra zero, anche con i costi doppi; correlazione dei rendimenti giornalieri **con lo SPY** sotto 0,3 sul periodo
chiuso, e con la miscela della prova 25 sotto 0,3 sul 2016-2024 (già visto: serve solo a sapere se si muove con lei).

Da leggere accanto: il costo del prestito annuo che porterebbe lo Sharpe a zero; il quinto più basso meno l'IWM, mese per mese, senza
costi, e il suo t; quanti titoli scelti ogni mese; i titoli chiusi perché spariti dal listino. **Se passa uno dei due esami:** revisore
separato, poi la proposta al proprietario di misurarla in avanti sul demo (con il controllo che Alpaca permetta di venderli allo
scoperto). Nel conto: **1 prova più 1 apertura del periodo chiuso = 2** (75).
