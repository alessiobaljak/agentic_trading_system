# Prova 28 — il tono delle notizie del mese, coperto con il fondo dell'indice

Regole scritte il 12 novembre 2026 **prima di qualsiasi calcolo** e prima di scaricare l'archivio delle notizie (idea I26 di
`REGISTRO.md`, del proprietario, 30 ottobre 2026: leggere le notizie, comprare, tenere settimane o mesi). Si conoscevano le prove 1-27
e il solo controllo dei dati `P028a_risultati.md` (conteggi delle notizie, nessun rendimento). Contano come **4 prove** (due
strategie, e la miscela con ciascuna): 73 nel conto.

## Perché dovrebbe funzionare

Le parole delle notizie su un'azienda anticipano utili e prezzi nei giorni e nelle settimane dopo, soprattutto dove gli analisti sono
pochi (Tetlock, Saar-Tsechansky, Macskassy, «More than words», *Journal of Finance* 63, 2008); i titoli con notizie continuano nella
stessa direzione per mesi, quelli senza notizie no (Chan, «Stock price reaction to news and no-news», *Journal of Financial Economics*
70, 2003). **Sospetti scritti prima:**

* nelle 500 grandi la notizia entra nel prezzo in poche ore (prove 10, 18, 20, 21): ci si aspetta poco dalla variante A;
* l'archivio è magro: nel campione 2-3 notizie al mese per titolo fino al 2019, 5-9 dopo; il 78% ha solo il titolo
  (`P028a_risultati.md`); un tono misurato su 3 titoli di giornale è rumoroso;
* **l'elenco di parole l'ho scritto io nel 2026**: è fatto di parole generiche, non di nomi o di fatti di quegli anni, ma non è un
  elenco pubblicato prima del 2016 (quello di Loughran e McDonald ha una licenza che non permette di metterlo in un repository
  pubblico);
* l'archivio può essere stato corretto dopo (titoli riscritti, simboli aggiunti): si usa la data di creazione e non si può controllare;
* la lezione della prova 27: una parte che compra soltanto si muove con il mercato e non entra nella miscela. Per questo qui la parte è
  **coperta**: per ogni dollaro comprato, un dollaro del fondo dell'indice venduto allo scoperto.

## I dati

* **Le notizie:** l'archivio di Alpaca (fonte Benzinga), tutte le notizie dal 1° gennaio 2016 al 31 dicembre 2024, scaricate da un
  lavoro di GitHub; restano nella memoria del lavoro (licenza), nel repository vanno solo i risultati. Vale l'istante di creazione.
* **I prezzi:** al giorno di Alpaca, non rettificati, con dividendi e frazionamenti, come le altre prove.
* **La composizione dell'S&P 500** giorno per giorno: `stock/prove/dati/P028_membri.csv.gz` (da github.com/fja05680/sp500, con i cambi
  di simbolo, una riga per fine mese).

## Il tono (uguale per le due varianti)

* **Notizia dell'azienda:** una notizia che cita da 1 a 3 simboli (i riassunti di mercato che ne citano tanti non contano).
* **Il testo:** titolo e riassunto (se c'è), in minuscolo, diviso in parole di sole lettere.
* **Il voto della notizia:** +1 se le parole buone sono più delle cattive, −1 se sono meno, 0 se pari o se non ce ne sono.
  * Buone: beat, beats, tops, topped, exceeds, exceeded, raises, raised, raise, upgrade, upgrades, upgraded, outperform, overweight,
    buy, record, strong, stronger, growth, grows, wins, win, awarded, approval, approves, approved, breakthrough, positive, profit,
    profitable, buyback, repurchase, expands, expansion, partnership, accelerates, boosts, boost, improves, improved, better, bullish.
  * Cattive: miss, misses, missed, lowers, lowered, cuts, cut, downgrade, downgrades, downgraded, underperform, underweight, sell,
    weak, weaker, loss, losses, decline, declines, warns, warning, lawsuit, sues, sued, probe, investigation, subpoena, recall,
    recalls, fraud, bankruptcy, default, layoffs, delays, delayed, halts, halted, resigns, breach, fine, fined, penalty, negative,
    bearish, disappointing, shortfall, impairment, restructuring, suspends, suspended, terminates, terminated, fails, failed, rejects,
    rejected, concerns.
  * Le parole che descrivono solo il movimento del prezzo (sale, scende, balza, crolla) **non** ci sono, di proposito: misurerebbero
    il rendimento del mese, che le prove 3 e 11 hanno già bocciato.
* **Il tono del mese di un titolo:** la media dei voti delle sue notizie create dopo le 16:00 di New York dell'ultimo giorno di borsa
  del mese prima e fino alle 16:00 dell'ultimo giorno di borsa del mese. Serve un minimo di **3 notizie** nel mese.

## Le due varianti

Si decide all'ultima chiusura del mese; ordini a mercato all'apertura del primo giorno di borsa del mese dopo; si tiene un mese.

* **A — le 500 grandi.** Fra i membri dell'S&P 500 di quel giorno con il tono calcolabile e la barra del giorno: il **20% con il tono
  più alto**, al massimo 50 titoli (a pari tono prima chi ha più notizie, poi in ordine alfabetico), pesi uguali, in tutto il **50%**
  del conto; venduto allo scoperto lo **SPY** per il 50% del conto.
* **B — le aziende piccole.** Lo stesso, fra i titoli che quel giorno **non** sono nell'S&P 500, hanno chiusura di almeno 5 dollari e
  mediana dei dollari scambiati nelle 20 sedute prima di almeno 2 milioni (i filtri della prova 27); si escludono i fondi (titoli il
  cui nome nell'elenco di Alpaca contiene ETF, ETN, Fund, Index, iShares, ProShares, SPDR, Vanguard, Direxion, WisdomTree, VanEck,
  Global X, First Trust, Invesco; e i simboli senza nome nell'elenco restano). Venduto allo scoperto l'**IWM** per il 50% del conto.
* Se i titoli con il tono calcolabile sono meno di 25, quel mese si resta fuori (tutto chiuso).

## I costi (fissati prima)

A: come le prove 11 e 24 (metà dello scarto misurato dove c'è, altrimenti 5 punti base più 2 di slittamento). B: metà scarto 15 punti
base e slittamento 5, come la prova 27. Commissioni Interactive Brokers «fisso». Prestito dei fondi venduti allo scoperto: **0,5%
l'anno** lo SPY, **1% l'anno** l'IWM (stime: il dato vero del passato non c'è). Versione con tutti i costi raddoppiati.

## L'esame

**Da sola:** (1) Sharpe annuo con i costi più alto del tenere lo SPY sugli stessi giorni; (2) Sharpe corretto ≥ 0,95 con tutte le
serie del conto; (3) Sharpe sopra zero con i costi doppi; (4) almeno il 60% dei trimestri in guadagno.

**Per entrare nella miscela** (idea I30): Sharpe con i costi sopra zero, anche con i costi doppi; correlazione dei rendimenti
giornalieri con la miscela della prova 25 sotto 0,3; la miscela nuova (tre quarti la miscela, un quarto la parte nuova) con lo Sharpe
più alto della miscela e del tenere lo SPY.

Da leggere accanto (non sono prove): quanti titoli hanno il tono calcolabile ogni mese; il rendimento medio del mese dopo del quinto
con il tono più alto meno quello del quinto con il tono più basso, senza costi, con il suo t; il risultato anno per anno. Se una
variante passa uno dei due esami: revisore separato, poi il periodo chiuso (la famiglia «notizie a settimane o mesi» non l'ha mai
usato), poi la conferma in avanti sul demo.
