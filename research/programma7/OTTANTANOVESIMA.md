# Prova 151 — il weekend dei perpetui su azioni: il rimbalzo del lunedì (idea 138)

Regole scritte l'11 novembre 2026 (secondo giro), **prima di ogni calcolo**, dallo strategy-scout; la prova la esegue
strategy-researcher, il giudizio lo dà backtest-auditor. Nessun risultato è stato guardato (solo un controllo di esistenza dei dati:
il volume del sabato e della domenica del contratto TSLAUSDT di settembre-ottobre è circa un decimo di quello dei giorni feriali).

## Il perché forte
* **Dato mai usato**: Binance quota circa 150 perpetui su azioni, fondi e materie prime (elenco in `programma6/SECONDA.md`, sezione 9).
  Sono stati messi fuori da ogni universo (`programma6/esclusi.py`) e nessuna prova li ha mai usati come segnale
  (`--cerca azioni`, `--cerca TSLA`, `--cerca XAU`, `--cerca TradFi`: nessuna prova). Quasi tutti sono nati nel 2026.
* **Fatto visto in avanti**: i perpetui crypto nuovi sono 2-3 al mese (erano circa 30), mentre i contratti su azioni sono tanti e in
  aumento: è l'unica materia prima che cresce. Sono ancora un mondo a parte (vedi anche `stock/`, che non tocco).
* **Ragione economica** (non un indicatore sul prezzo): nel weekend la Borsa americana è chiusa, quindi nessuno può comprare o
  vendere l'azione vera per coprirsi; il prezzo del perpetuo lo fanno pochi acquirenti al dettaglio in un mercato sottile. Quando la
  Borsa riapre, il prezzo vero si riallinea. Se nel weekend il perpetuo ha spinto troppo (in su o in giù), il lunedì dovrebbe
  rimbalzare. Fonte per l'idea di fondo: l'ordine sbilanciato in un mercato sottile sposta il prezzo e poi rientra (Kyle 1985 sul
  prezzo e la liquidità; per i titoli quotati poco scambiati, Jegadeesh 1990, *Journal of Finance*, inversione di breve periodo).
  **Avviso**: sono fonti generali, non uno studio sui perpetui su azioni (non ne conosco uno); la storia è corta (da gennaio 2026 per
  i più vecchi, aprile per molti); il verso (rimbalzo, non continuazione) è una scommessa, non un fatto.

## Dati e universo
Candele da 1 ora dei perpetui su azioni e fondi di Binance: **da scaricare** dall'archivio pubblico, come `programma6/scarico_ore.py`
(oggi nei dati ci sono le candele di 1 giorno, il premio a 1 ora solo dal 1° novembre e il funding). Universo: i contratti su azioni e
fondi dell'elenco `esclusi.py` (sezione azioni e fondi, più i nati dopo, elencati in `SECONDA.md`), **tolti** i contratti a leva 2x
(nome con «2L»), quelli su titoli non americani (BYD, ASML, i due CSOP, EWJ, EWY, EWZ, ecc.: li decide chi esegue con una lista
scritta in un file prima del calcolo), le materie prime, i metalli, le valute. Ogni lunedì: i 30 contratti con più volume in dollari
delle 4 settimane prima, con almeno 40 giorni di storia. Meno di 20 contratti: la settimana non si fa.

## Il segnale (fissato qui)
Ogni lunedì alle 00:00 UTC, per ogni contratto: R = log(prezzo alle 00:00 del lunedì / prezzo di apertura della candela delle 22:00 UTC
del venerdì) (le 22:00 sono dopo la chiusura di Wall Street sia con l'ora legale sia senza). Si toglie la mediana di R fra i 30
contratti (il weekend di tutto il mercato non conta, conta chi si è mosso di più degli altri). **Long il quinto con R più basso, short
il quinto con R più alto**, 6 contratti per lato, pesi uguali, ogni lato al 100% (neutro al dollaro). Nessuna banda.

## Esecuzione e costi
Ordine all'apertura della barra dopo il segnale: candela delle 01:00 UTC del lunedì. Si tiene fino all'apertura della candela delle
22:00 UTC dello stesso lunedì (21 ore: dentro ci sono la notte asiatica e tutta la sessione americana). Ordine limite 0,02% per un'ora
(entrata), poi a mercato 0,05%; uscita a mercato 0,05%. Scarto di prezzo 0,02% (come le altre monete); come controllo obbligatorio si
riporta anche con scarto 0,05% (i contratti su azioni potrebbero avere un divario più largo: **da confermare dal proprietario**).
Funding vero dei regolamenti nella finestra. Lunedì festivi americani: si fa lo stesso (il contratto quota), ma si segna.

## Periodo e varianti
Dal primo lunedì con almeno 20 contratti ammessi (previsto: primavera 2026) al 2 novembre 2026. **Una sola variante**, scelta prima:
quella sopra. Conta **1 prova** nel conto (da 308 a 309; con le sue 2 della 150 già contate). Nessuna variante dopo aver visto i
risultati. Il controllo descrittivo, che non è una variante e non entra nel giudizio: il rendimento della stessa posizione diviso in
01:00-13:00 UTC (prima della Borsa) e 13:00-22:00 (dentro la Borsa), per capire dove nasce.

## L'esame (regole approvate dal proprietario il 9 novembre)
Passa se: netto dopo i costi positivo; ogni anno positivo (qui solo il 2026: in più, non più di un trimestre negativo); t almeno 3; Sharpe
corretto almeno 0,80 (conto aggiornato, `programma6/asticella.py`). **Limite onesto**: sono al massimo circa 30 lunedì; con questo
conto lo Sharpe corretto richiede un rendimento molto alto. Se il numero di lunedì non basta per un giudizio (t sotto 3 con meno di 40
settimane), il verdetto è «dati troppo corti», non «no»: la regola resta com'è e si misura **in avanti** a ogni lunedì dal 16 novembre
(senza attese fisse: si giudica quando l'esame è decidibile, e i numeri vanno al proprietario ogni lunedì). Non passa se il lato long
o il lato short da soli fanno meno di zero nelle settimane senza i 3 lunedì migliori.

## Cosa si consegna
`RISULTATI_OTTANTANOVESIMA.md` (settimane usate, contratti per settimana, rendimento netto l'anno, Sharpe, t, Sharpe corretto, lato
long e short separati, scarto 0,02% e 0,05%, divisione prima/dentro la Borsa, giro e spese), codice `ottantanovesima.py`, la
variante in `research/trials/`, la lista scritta dei contratti esclusi. Se mancano le candele da 1 ora: lo si scrive, e non si calcola
con quelle da 1 giorno.
