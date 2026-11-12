# La misura in avanti (in tempo reale) sul conto demo

Richiesta del proprietario, 7 novembre 2026: «scegli tu cosa provare ma non in back testing [...] fare proprio real time, forward
testing». Regole scritte il 7 novembre 2026 **prima della prima operazione**. Non si cambiano durante la misura: una modifica vuol dire
una misura nuova, con un nome nuovo, e la vecchia si chiude con il suo risultato.

## Cosa si prova, e perché questa

**La prima candela da 15 minuti sulle 10 azioni più scambiate del mese** (le regole della prova 17 a 15 minuti, rifatte sulle azioni
nella prova 23).

* È, fra le regole sulle azioni provate sul passato, quella con il vantaggio **prima dei costi** più alto fra quelle che decidono una
  volta al giorno (prova 23: Sharpe 0,96 senza costi, +133% in 9 anni; la zona di rumore fa 1,31 ma decide 12 volte al giorno, e una
  routine non può girare più di una volta l'ora).
* Sul passato, **con i costi stimati**, perde (Sharpe −0,43, `stock/prove/P023_risultati.md`). La domanda di questa misura è quindi
  precisa: **con gli ordini veri, ai prezzi veri dell'apertura, quanto costa davvero, e il vantaggio resta?** Il passato non lo può
  dire, perché lo scarto all'apertura l'abbiamo solo stimato.
* Fa circa 10 operazioni al giorno: in due mesi sono circa 400, abbastanza per un primo giudizio (una sola azione darebbe 250
  operazioni l'anno).

## Le regole (ogni giorno di borsa a seduta intera; i giorni a chiusura anticipata non si opera)

1. **Le azioni:** le 10 più scambiate per dollari nelle 63 sedute prima del mese, fra i membri attuali dell'S&P 500 (una sola azione per
   azienda, come `stock/universo/costruisci.py`). L'elenco del mese si scrive in `elenco_AAAA-MM.csv` il primo giorno di borsa del mese,
   prima dell'apertura.
2. **La candela:** le barre a 1 minuto dalle 9:30 alle 9:44 di New York (fonte: Alpaca, borsa IEX, l'unica in tempo reale nel piano
   gratuito; sul passato si usavano tutte le borse). Apertura, massimo, minimo, chiusura dei 15 minuti.
3. **La direzione:** chiusura sopra l'apertura si compra; sotto si vende allo scoperto; uguale, niente.
4. **L'ordine:** subito dopo le 9:45 (la routine parte alle 9:46; l'ora vera dell'ingresso si scrive), un ordine a mercato con stop e
   obiettivo attaccati (ordine «bracket» di Alpaca), per un decimo del valore del conto × 0,98, azioni intere.
   * **Stop:** il minimo della candela per gli acquisti, il massimo per le vendite (ordine stop: si esce a mercato appena toccato).
   * **Obiettivo:** 10 volte il rischio, misurato dalla chiusura della candela allo stop (ordine limite).
   * Se il prezzo è già oltre lo stop quando parte l'ordine, Alpaca lo rifiuta: si scrive «saltato, già oltre lo stop» (sul passato
     quel giorno sarebbe uscito subito in perdita: si contano a parte). Un titolo che non si può vendere allo scoperto: «saltato».
5. **Fine giornata:** alle 15:55 si chiude tutto a mercato e si cancellano gli ordini rimasti (sul passato alle 15:59).
6. **Il diario:** ogni giorno, dopo la chiusura, una riga per operazione in `diario.csv`: giorno, titolo, lato, quantità, prezzo e ora
   d'ingresso, prezzo e ora d'uscita, come è uscita (stop, obiettivo, chiusura), guadagno in dollari e in proporzione. Solo i nostri
   ordini e i nostri prezzi eseguiti, mai i prezzi di borsa scaricati (licenza dei dati).

## Il conto

**Conto demo di Alpaca** (paper trading: soldi finti, ordini veri contro le quotazioni vere). È la piattaforma che già usiamo per i
prezzi; il demo di Interactive Brokers, scelto per dopo, richiede un conto aperto e un programma acceso sul computer del proprietario.
Alpaca non fa pagare commissioni: nel riepilogo si mette accanto la commissione che Interactive Brokers avrebbe preso (0,005 dollari per
azione, minimo 1 dollaro), per non illudersi. Il demo di Alpaca esegue al prezzo migliore esposto senza code: è un po' più comodo del
vero, e va detto.

## I numeri, ogni settimana (niente attese fisse)

Ogni lunedì al proprietario, in `riepilogo.md`: operazioni, quante in guadagno, guadagno medio a operazione e il suo t, guadagno
totale con e senza la commissione stimata di Interactive Brokers, il confronto con il tenere lo SPY negli stessi giorni, e il costo
vero misurato (la differenza fra il prezzo eseguito e la chiusura della candela). **Il giudizio** si dà quando c'è: la stessa asticella
delle prove sul passato non si può calcolare su poche settimane, quindi si dice il t e quante operazioni servirebbero per arrivare a 3
con il guadagno medio misurato fin lì. Soldi veri mai, se non su richiesta esplicita, ripetuta e consapevole del proprietario.

## Le deviazioni dalle regole (scritte quando succedono)

* **9 novembre 2026:** la routine delle 9:46 è arrivata con 10 minuti di ritardo; gli ordini sono partiti alle **9:57** di New York
  invece che subito dopo le 9:45. Da qui la routine d'apertura parte alle 9:38 e il programma aspetta le 9:45 (lo faceva già); quella di
  chiusura parte alle 15:38 e il programma aspetta le 15:55. Un ingresso dopo le 9:50 si segnala nel riepilogo.
* **9 novembre 2026, chiusura:** il comando che doveva chiudere tutto (cancellare gli ordini e chiudere le posizioni in un colpo solo)
  ha cancellato stop e obiettivi ma **non ha chiuso 8 posizioni su 10**. Le ho chiuse a mano, titolo per titolo, alle 15:56:20-29 di
  New York, prima della fine della seduta: nessuna posizione è passata la notte. Il programma ora cancella prima gli ordini, aspetta,
  chiude titolo per titolo e controlla che non resti niente; se resta qualcosa, si ferma con un errore.
* **10 novembre 2026:** la routine è arrivata di nuovo con 10 minuti di ritardo (partita alle 9:38, arrivata alle 9:48): ordini alle
  **9:49**. Da qui la routine d'apertura parte alle 9:33.
* **11 novembre 2026:** primo giorno su GitHub, **nessun ordine**: l'orario programmato delle 13:05 UTC non è partito (GitHub fa partire
  i lavori programmati quando può, e quel giorno non li faceva partire da ore). Alle 10:11 di New York non si è entrati in ritardo:
  il giorno si salta (un ingresso di mezz'ora dopo non è la regola). Da qui il lavoro lo avvia anche una routine della sessione alle 9:30
  e alle 15:30 di New York (avvio manuale del lavoro di GitHub); l'orario programmato resta come riserva, e la coda dei lavori di GitHub
  impedisce gli ordini doppi.
* **11 novembre 2026, sera:** l'orario delle 13:05 UTC è partito alle 20:07 UTC (7 ore dopo) e il programma, che non aveva un limite
  d'orario, ha mandato gli ordini alle **15:08** di New York (8 eseguiti, 2 rifiutati); la chiusura avviata alle 15:47 non è partita
  (GitHub senza computer libero). Le 7 posizioni rimaste sono state chiuse **fuori orario** alle 16:04 di New York con ordini limite
  (chiusura d'emergenza): nessuna è passata la notte. Giornata **fuori regola**: resta nel diario (−94,49 dollari) ma non conta nel
  giudizio. Da qui l'apertura **non entra mai dopo le 10:00** di New York.
* **12 novembre 2026 — chi avvia non deve essere puntuale** (il proprietario: «il lavoro non deve partire tardi, risolvi
  immediatamente»). Guardando i registri: l'11 novembre i due orari programmati di GitHub sono partiti 7 ore e 6 ore e 22 minuti dopo
  (13:05 → 20:07 UTC, 19:05 → 01:27 UTC). Un orario che può arrivare con ore di ritardo non si può «far partire puntuale»: si è
  cambiato il disegno. Tutti gli avvii lanciano il comando `auto` (`stock/avanti/avanti.py`, funzione `cosa_fare`), che guarda
  l'orologio di New York e il conto: fino a 5 ore e 20 minuti prima delle 9:45 **aspetta acceso** le 9:45; dopo le 10:00 non entra
  mai; dalle 10:35 aspetta acceso le 15:55 e chiude; a seduta finita chiude fuori orario ciò che resta (mai un ordine a mercato a
  borsa chiusa); posizioni rimaste da un altro giorno si chiudono subito. Gli avvii: GitHub ogni mezz'ora, più quattro routine della
  sessione (8:15, 9:10, 13:30 e 15:20 di New York) che avviano il lavoro a mano. Ordini con un nome unico per giorno e titolo: niente
  doppioni. Le regole della strategia non cambiano.
