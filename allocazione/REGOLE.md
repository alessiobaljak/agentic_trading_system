# Regole di scelta delle strategie in produzione

**Stato: PROPOSTA del 9 novembre 2026, approvata IN PARTE dal proprietario il 9 novembre** («va bene sharpe [...] sotto i 500 una
strategia solo va bene»): approvati lo Sharpe corretto minimo 0,80 (sezione 1) e una strategia sola sotto i 500 USDT (sezione 3). Da
chiarire con lui: la regola della sostituzione (+0,10) e la miscela sopra i 500 USDT («il sistema deve poter avere più strategie
insieme»). Il resto resta proposta. Finché qui non c'è scritto «approvate dal proprietario il ...»
l'agente riporta solo le misure. Queste regole sono scritte PRIMA di confrontare chi vince; dopo l'approvazione si cambiano solo con
un nuovo ok scritto.

Vincoli del proprietario che valgono sempre: nessuna strategia del paper o del demo si spegne (8 nov); conta il profitto, sul passato e
in avanti, e lo Sharpe corretto 0,90 non è un muro (8 nov); eventi spenti per i soldi veri; capitale 250 euro (280 USDT, tetto del
codice 300).

## 1. Chi può entrare (porte; tutte e quattro)
1. Esame sul passato (registro): ogni anno positivo, t almeno 3, Sharpe corretto almeno 0,80 (0,90 non è un muro; il 0,80 è una
   proposta da far approvare: vedi domanda 1 del rapporto).
2. Revisione di backtest-auditor sulla configurazione finale (la revisione separata già nel registro conta finché la configurazione non cambia).
3. Parità di gate2-reconciler dimostrata (con le soglie approvate dal proprietario; senza soglie approvate la parità è «non dimostrata»).
4. Il codice del conto vero la sa già eseguire, oppure il costo del cambio (punto 5) è dichiarato.
Chi non passa le porte non si propone; resta in corso nel paper (nessuno si spegne).

## 2. Come si confrontano due strategie che passano le porte
Si parte dalla strategia già scelta (oggi G1, l'unica che il codice del conto vero sa eseguire). Una sfidante la sostituisce solo se
valgono tutte e tre:
- Passato: Sharpe corretto non più basso di 0,05 rispetto a quella attuale E almeno uno fra (a) Sharpe corretto più alto di 0,10,
  (b) discesa massima più bassa di almeno 5 punti. Il vantaggio deve reggere: con un'esecuzione appena più difficile (spese e scarto
  doppi), dal 2023 in poi, e non deve venire da un solo episodio (nel ricampionamento della revisione separata, un solo episodio
  non può spiegare più del 50% del vantaggio).
- In avanti: almeno 28 giorni interi dalla stessa data di partenza per le due strategie. Prima, il peso dei giorni in avanti è zero:
  non favorisce né sfavorisce nessuno. Dopo, la sfidante non deve essere sotto di più di 1 punto di rendimento cumulato.
- Rumore: se la correlazione dei rendimenti giornalieri è sopra 0,85 le due strategie sono «quasi la stessa»; la differenza in avanti
  conta solo se supera 2 volte il suo errore (deviazione standard delle differenze giornaliere x radice dei giorni). Sotto, è rumore e
  non muove la scelta, in nessuno dei due sensi.

## 3. Capitale
- Capitale minimo di una strategia: 250 USDT (prova 148: da 225 in su lo Sharpe sta al 92-97% di G1, sotto 220 cala in fretta).
- Una strategia sola finché il conto è sotto 2 x 250 = 500 USDT. Una miscela solo se ogni quota resta almeno 250 USDT e la
  correlazione fra le due è sotto 0,70 (sopra, dividere il capitale non diversifica).
- La discesa massima va letta in USDT: con 280 USDT la peggiore discesa del passato di G1 (-27%) porta a circa 205, sotto la zona sicura.

## 4. Rischio
- Discesa massima sul passato non oltre -32% (F5 e G1 sono nel limite) e stop sul conto a -35% dal massimo; in avanti, una discesa
  oltre -15% in meno di 28 giorni fa tornare la strategia in revisione (si riporta, non si spegne).

## 5. Costo del cambio
- Cambiare strategia sul conto vero vuol dire cambiare codice del percorso ordini: live-path-reviewer, ok del proprietario, riavvio.
  La sfidante deve quindi superare il punto 2 con i numeri, non solo di poco. Il costo del cambio si scrive sempre nella proposta.

## 6. Verdetto
TIENI se nessuna sfidante supera il punto 2; PROPONI CAMBIO altrimenti, con numeri e fonte. Senza approvazione: SOLO MISURE.
Ogni lunedì dopo gate2-reconciler; non si cambia per un lunedì buono.
