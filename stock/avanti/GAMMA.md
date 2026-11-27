# La prova 45 sul conto demo (misura in avanti): l'ultima mezz'ora nei giorni con la copertura delle opzioni sotto zero

Decisione del proprietario, 23 novembre 2026: «metti la prova 45 sul demo». Regole scritte il 23 novembre 2026 **prima della prima
operazione**; una modifica vuol dire una misura nuova, con un nome nuovo, e la vecchia si chiude con il suo risultato.

## Perché, e cosa si chiede

La prova 45 (`stock/prove/P045_ultima_mezzora_gamma.md`) passava l'esame per entrare nella miscela, ma il revisore l'ha bocciata
(`stock/prove/REVISIONE_P045.md`): metà del guadagno prima dei costi viene dalle 18 operazioni di marzo 2020. L'esame da crisi sul
periodo chiuso (prova 45b) dice «non si può dire»: 18 operazioni, sotto il minimo di 20, con la direzione giusta. Sul passato non c'è
altro da guardare: **solo il tempo in avanti può dire di più.** La domanda: nei giorni in cui la copertura delle opzioni del giorno
prima è sotto zero, l'ultima mezz'ora segue ancora la giornata, con gli ordini veri, e l'uscita all'asta di chiusura costa quanto si è
supposto?

**Da sapere prima:** nel 2025-2026 la copertura è stata sotto zero solo nel 4% dei giorni (circa 10 l'anno; 11% nel 2016-2024). La
misura può restare ferma per settimane: un giudizio richiede anni, salvo un periodo agitato. Sul passato il guadagno medio era di
+7,58 punti base a operazione prima dei costi (t 1,91), +5,95 dopo (`stock/prove/P045_risultati.md`).

## Le regole (quelle della prova 45; le differenze sono scritte qui, prima)

1. **Il giorno:** si opera solo se la copertura (colonna `gex` di `squeezemetrics.com/monitor/static/DIX.csv`) con la data del giorno di
   borsa prima è **sotto zero**. Il file si scarica al momento della decisione; se quel giorno manca, il giorno si salta e si scrive
   («manca la copertura»). Il valore non si scrive mai nel repository: solo «sotto zero» o «sopra zero».
2. **Il segnale, sullo SPY come nella prova:** r = chiusura della barra al minuto che finisce mezz'ora prima della chiusura (di solito
   quella delle 15:29) / chiusura dell'ultima barra della seduta di ieri − 1. Se r > 0 si compra, se r < 0 si vende allo scoperto, se
   r = 0 niente. La barra di oggi viene dalla borsa IEX, l'unica in tempo reale nel piano gratuito di Alpaca (nella prova: tutte le
   borse); quella di ieri da tutte le borse, come nella prova. Se la barra di oggi non arriva entro un minuto, il giorno si salta e si
   scrive.
3. **Il titolo comprato o venduto è VOO**, non lo SPY. È un fondo sullo stesso indice (l'S&P 500). Il motivo: lo SPY lo usa la miscela
   nello stesso conto demo, e Alpaca somma le posizioni dello stesso titolo. Le tre strategie del conto si dividono per titolo
   (`stock/avanti/conto.py`). Prima del primo giorno si controlla con il comando `controlla` che Alpaca dia VOO vendibile allo scoperto.
   Se non lo dà, si usa IVV, e la scelta si scrive qui prima della prima operazione.
4. **L'ingresso:** a mercato, appena chiusa la barra del segnale (di solito alle 15:30:0x). Se il programma arriva più di **5 minuti**
   dopo, il giorno si salta e si scrive («avvio in ritardo»). Mai un ingresso più tardi.
5. **L'uscita:** un ordine **alla chiusura** (asta di chiusura), mandato subito dopo l'ingresso (Alpaca li accetta fino alle 15:50).
   * Fino a 2 minuti dalla fine il programma ricontrolla l'ordine ogni 30 secondi. Se Alpaca lo rifiuta, lo cancella o lo fa scadere,
     lo rimanda finché lo accetta (al massimo 3 volte, fino alle 15:50); se non si può, **chiusura a mercato 2 minuti prima della
     fine**, scritta come «mercato».
   * Dopo la chiusura si aspetta che l'ordine alla chiusura sia finito (fino a 7 minuti). Se la posizione è ancora aperta: chiusura
     fuori orario con un ordine limite, come fa la prima candela, scritta come «fuori orario». Prima si cancellano gli ordini su VOO
     ancora aperti; se uno resta, nessun ordine nuovo (due uscite insieme raddoppierebbero) e il lavoro si ferma con un errore.
   * Nessuna posizione resta aperta di notte. **Da sapere:** sul conto demo gli ordini all'asta d'apertura della miscela del 12
     novembre sono scaduti senza esecuzione (`MISCELA.md`). Se anche quelli alla chiusura non si eseguono, lo dirà la prima
     operazione: l'uscita sarà allora fuori orario, si scriverà qui, e l'uscita si cambierà (con una misura nuova).
6. **Quanto:** un **capitale virtuale suo di 100'000 dollari**, come la miscela. La quantità è il 98% del capitale virtuale (100'000 più
   i guadagni fin lì) diviso per l'ultimo prezzo di VOO alla decisione; azioni intere, niente leva sul capitale virtuale.
7. **Le chiusure anticipate:** si opera come nella prova, con il calendario di Alpaca: l'ingresso è mezz'ora prima della chiusura.

## Il diario e i numeri

* **`gamma_diario.csv`:** una riga per giorno di borsa in cui il programma ha deciso. Contiene il giorno, la data della copertura
  usata, la copertura (sotto zero / sopra zero / mancante), r, il lato, la quantità, il prezzo e l'ora d'ingresso, lo scarto
  dell'ingresso in punti base (il prezzo eseguito contro l'ultimo prezzo di VOO alla decisione; quel prezzo non si scrive), il prezzo e
  l'ora d'uscita, come è uscita (asta / mercato / fuori orario), il guadagno in dollari e in proporzione, la commissione stimata di
  Interactive Brokers e una nota. Lo stato di ogni giorno (ordini, decisione) sta in `gamma_giorni/AAAA-MM-GG.json`.
* Nel diario vanno solo i nostri ordini e i nostri prezzi eseguiti, mai i prezzi di borsa scaricati.
* **Ogni lunedì** al proprietario, nel riepilogo del demo:
  * i giorni sotto zero e le operazioni;
  * il guadagno medio a operazione, prima e dopo la commissione stimata di Interactive Brokers, con il t;
  * il costo dell'ingresso misurato: il prezzo eseguito contro l'ultimo prezzo di VOO alla decisione.
  * Il giudizio si dà quando c'è, come per la prima candela: il t e quante operazioni servirebbero per arrivare a 3. Nessuna attesa
    fissa (decisione del 1° novembre).
* Soldi veri mai, se non su richiesta esplicita, ripetuta e consapevole del proprietario.

**Cosa il demo può dire (audit del 27 novembre 2026):** si opera solo nei giorni con la copertura sotto zero (sul passato il 4-11%
dei giorni), cioè poche operazioni l'anno: il demo dice se ordini, aste e uscite funzionano come sul passato, non se la regola guadagna.

## Come gira

`python -m stock.avanti.gamma auto` (lavoro di GitHub `.github/workflows/azioni_gamma.yml`, acceso solo se esiste
`stock/avanti/gamma_accesa`). Chi avvia non deve essere puntuale: il programma guarda l'orologio di New York e aspetta l'ora
dell'ingresso fino a 4 ore e 30 minuti prima (un lavoro di GitHub dura al massimo 350 minuti). Un avvio in ritardo non entra mai fuori regola. Gli avvii vengono dagli orari di GitHub
e dalla routine della sessione «trading stock» delle 13:30 di New York.

## Le deviazioni dalle regole (scritte quando succedono)

* **27 novembre 2026 — le correzioni del programma** dopo l'audit (`stock/AUDIT_2026-11-27.md`, sezione 3), con l'ok del proprietario del 27 novembre («sì, fai le 19 correzioni») e la revisione separata del codice (`avanti/REVISIONE_AUDIT.md`). Le regole non cambiano. L'ordine fuori orario ha un nome unico; le
  uscite che un altro giorno ha segnato come sue (la chiusura di una posizione rimasta) non contano nella riga di oggi; con uscite
  parziali il guadagno è quello della parte chiusa; a ogni avvio le righe con un'uscita del giorno dopo arrivata tardi si completano;
  l'allarme delle posizioni rimaste esce prima del diario e si ripubblica dopo; la Plancia si aggiorna anche nei giorni senza
  operazione. Una posizione VOO rimasta si chiude con un ordine dal nome `gamma-rim-<giorno dell'ingresso>-<ora>`; nei giorni senza
  ingresso della prova la posizione conta con il guadagno non realizzato (`REGOLE.md`, la stessa regola della prima candela). Nei giorni a
  chiusura anticipata la prova parte anche dalla routine delle 9:10 (prima nessun avvio arrivava in tempo per le 12:30).
