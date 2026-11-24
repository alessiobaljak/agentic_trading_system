# Prova 37b — l'esame «da crisi» della prova 37 (il ribilanciamento dei fondi 60/40) sul periodo chiuso

Scritto il 24 novembre 2026, **prima di guardare qualsiasi dato del periodo chiuso** (gennaio 2025 → settembre 2026) per questa regola,
dopo il FAIL del revisore della prova 37 (`REVISIONE_P037.md`) e dalle idee I44 e I53 di `REGISTRO.md`, come la prova 45b per la 45
(decisione del proprietario del 22 novembre: le idee si provano da sole, con il flusso di sempre). Conta come **1 prova** (ogni apertura
del periodo chiuso conta una prova, decisione del 24 ottobre): 115 nel conto.

## Perché

Il revisore ha confermato il calcolo della prova 37 (si riproduce al centesimo), ma **tutto il guadagno 2016-2024 viene da marzo 2020**
(il 101% in logaritmi); negli altri giorni, dopo i costi, la regola rende zero. Il suo giudizio: «se torna una crisi con giorni da ±10%
che si alternano, la parte guadagna». È un'assicurazione, non una strategia di tutti i giorni, e va giudicata così (idea I53): **paga in
una crisi nuova e indipendente, e quanto costa negli altri mesi?**

Il periodo chiuso è indipendente: (1) nessuna prova della famiglia «ribilanciamento» lo ha mai usato; (2) è dopo la fine del campione
dell'articolo (17 marzo 2023), quindi i numeri della regola non sono stati scelti su questi giorni. **Si sa** che nell'aprile 2025 c'è
stato un crollo con giorni molto agitati (i dazi); **non si sa** come si è mossa la regola in quei giorni, né quanto è costata negli altri
mesi.

**Sospetti scritti prima:** sapere che c'è stata una crisi ha fatto scegliere questo esame (è un esame nato dopo il risultato della 37);
un secondo episodio resta un caso solo; nell'aprile 2025 le obbligazioni del Tesoro sono scese insieme alle azioni in alcuni giorni,
cosa diversa dal marzo 2020.

## La regola, i dati e i costi

**Identici alla prova 37** (`P037_ribilanciamento.md`): SPY contro IEF, segnale a fascia e di calendario dell'articolo, peso limitato a
±1, stessi costi (scarto, slittamento, commissioni, prestito della parte corta), stesse funzioni di `p037.py`. Prezzi di Yahoo (in
locale, mai nel repository) dal 1° ottobre 2024, perché i segnali partano già pronti il 2 gennaio 2025. Solo le date cambiano: **dal 2
gennaio 2025 al 30 settembre 2026**. Nessun parametro si tocca.

## L'esame da crisi (tutte e tre le condizioni)

**Il mese della crisi**, fissato prima e senza guardare la regola: il mese di calendario del periodo chiuso con la **deviazione standard
dei rendimenti giornalieri dello SPY più alta** (è la misura che conta per questa regola: giorni grandi che si alternano).

1. **Paga nella crisi:** con i costi, il rendimento della regola nel mese della crisi è **sopra zero**.
2. **Paga più di quanto costa:** con i costi, la regola chiude l'intero periodo chiuso **in guadagno**, anche **con i costi doppi**.
3. **Serve accanto a chi tiene le azioni:** la correlazione giornaliera con lo SPY è sotto 0,3, e un conto fatto per tre quarti di SPY
   e per un quarto di questa parte ha uno Sharpe più alto del tenere solo lo SPY sugli stessi giorni. (Come la prova 45b: il confronto è
   con lo SPY, perché la miscela non ha le serie del periodo chiuso per tutte le sue parti.)

**Se passa:** la proposta di metterla sul demo come parte d'assicurazione della miscela va al proprietario (la decide lui). **Se non
passa:** la prova 37 è bocciata definitivamente e il periodo chiuso della famiglia «ribilanciamento» è usato.

## Da leggere accanto (non cambiano l'esito)

Il rendimento di ogni mese, della regola e dello SPY; quale mese è quello della crisi e quanto ha fatto lo SPY in quel mese; la regola
con TLT al posto di IEF; con un giorno di ritardo; la quota del guadagno che viene dai 10 giorni migliori.
