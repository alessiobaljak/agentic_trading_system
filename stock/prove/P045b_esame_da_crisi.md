# Prova 45b — l'esame «da crisi» della prova 45 sul periodo chiuso (scritto prima; si apre solo se il proprietario lo decide)

Scritto il 22 novembre 2026, **prima di guardare qualsiasi dato del periodo chiuso** (gennaio 2025 → settembre 2026) per questa regola,
dopo il FAIL del revisore della prova 45 (`REVISIONE_P045.md`) e dall'idea I53 di `REGISTRO.md`. **Non si calcola** finché il
proprietario non decide di aprire il periodo chiuso per questa prova (`METODO.md`, sezione 4: il periodo chiuso si apre solo dopo la
ricerca e il revisore; la prova 15 lo ha aperto per decisione del proprietario dopo la revisione). Conta come **1 prova** (ogni apertura
del periodo chiuso conta una prova, decisione del 24 ottobre).

## Perché

Il revisore ha confermato che il segnale c'è (i numeri si rifanno uguali; la direzione è giusta nel 57% delle operazioni anche senza
marzo 2020; nei giorni con la copertura sopra zero il vantaggio è zero), ma che **il guadagno che fa passare l'esame viene da una crisi
sola** (marzo 2020). La domanda giusta è allora: **in un secondo episodio, indipendente, la regola fa la stessa cosa?** Il periodo chiuso
è indipendente per due motivi: (1) nessuna prova della famiglia «ultima mezz'ora» lo ha mai usato; (2) per il 2025-2026 il dato della
copertura è stato pubblicato in tempo reale (il revisore ha trovato cinque copie pubbliche del file salvate dopo il 2024, identiche a
quella di oggi), quindi non può essere stato rifatto dopo. **Si sa** che nell'aprile 2025 c'è stato un crollo; **non si sa** come si è
mossa l'ultima mezz'ora in quei giorni, né quali giorni avevano la copertura sotto zero.

## La regola, i dati e i costi

**Identici alla prova 45** (`P045_ultima_mezzora_gamma.md`): stesso segnale, stessi giorni (copertura del giorno di borsa prima sotto
zero), ingresso alle 15:30, uscita all'asta di chiusura, stessi costi, stesso programma (`p045.py` con le date del periodo chiuso). Solo
le date cambiano: **dal 2 gennaio 2025 al 30 settembre 2026**. Nessun parametro si tocca.

## L'esame da crisi (tutte e quattro le condizioni)

1. **Il segnale c'è ancora:** il guadagno medio lordo per operazione nei giorni sotto zero è **sopra zero** e **più alto** di quello nei
   giorni con la copertura sopra o uguale a zero.
2. **Il guadagno c'è:** con i costi la strategia chiude il periodo in guadagno, **anche con i costi doppi**.
3. **Non un solo mese:** togliendo il mese di calendario con la somma lorda più alta, la somma lorda delle altre operazioni resta
   **sopra zero**.
4. **Serve accanto a chi tiene le azioni:** la correlazione giornaliera con lo SPY è sotto 0,3, e un conto fatto per tre quarti di
   SPY e per un quarto di questa parte ha uno Sharpe più alto del tenere solo lo SPY sugli stessi giorni. (La miscela della prova 25 non
   ha le serie del periodo chiuso per tutte le sue parti; calcolarle aprirebbe il periodo chiuso di altre famiglie: per questo il
   confronto è con lo SPY.)

**Troppo poco per dire:** se nel periodo chiuso ci sono **meno di 20 operazioni**, l'esito è «non si può dire» (non promuove e non
boccia; la prova resta nel conto).

**Se passa:** la proposta di metterla sul demo come parte della miscela va al proprietario (la decide lui). **Se non passa:** la prova
45 è bocciata definitivamente e il periodo chiuso di questa famiglia è usato.

## Da leggere accanto (non cambiano l'esito)

Il numero di operazioni per mese; il guadagno di aprile 2025 da solo; i giorni sotto zero; lo stesso calcolo con la chiusura ufficiale
di Yahoo al posto di quella di Alpaca (Medio 3 del revisore).
