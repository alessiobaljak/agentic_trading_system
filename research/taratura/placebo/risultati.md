# Prova a placebo dell'esame — risultati (9 ottobre 2026)

Regole scritte e committate prima del lancio: `regole.md`, commit **8b6abf6b** (branch `research/coordinamento`).
Esiti grezzi: `esiti_k0.jsonl` (3.840 righe, una per placebo e periodo, tutte con la versione del codice 8b6abf6b).
Misure calcolate con `riassunto.py` (uscita completa in fondo). Durata del calcolo: circa 1 ora e mezza su 4
processori.

## Esito, con la regola scritta prima

**L'esame regge sui prezzi veri.** M1 = 0,41% (soglia 3%), M2 = 3,26% (soglia 13%). Nessun esito al limite: le
soglie stanno fuori dagli intervalli per moneta. Per il punto 6 delle regole si procede con la versione 4.5;
nessuna delle tre campagne consegnate va rifatta per questa prova.

| Misura | Valore | Intervallo al 95% per moneta | Dichiarato (sezione 11) | Soglia |
|---|---|---|---|---|
| M1: «netta» contro la (b) in costruzione | 6 su 1.479 = **0,41%** | 0,13-0,74% | 0-2% | 3% |
| M2: p sotto 0,10 in validazione | 44 su 1.348 = **3,26%** | 2,41-4,17% | 6-11% | 13% |
| M1 nella fascia 70-149 trade (la più vicina alla taratura) | 1 su 561 = 0,18% | 0-0,56% | 0-2% | — |
| M2 nella fascia 30-69 trade | 24 su 591 = 4,06% | 2,68-5,69% | 6-11% | — |
| Candidati (netta contro (a) e (b), R medio positivo), informativo | 3 su 1.479 = 0,20% | 0-0,47% | — | — |

Copertura: 160 coppie moneta-timeframe su 160, nessun errore. Placebo: 1.920 in costruzione, 1.484 con almeno 70
trade, 1.479 valutabili (7 non valutabili fra costruzione e validazione: meno di 3 blocchi interi); 1.350 in
validazione con almeno 30 trade, 1.348 valutabili. Trade in costruzione: mediana 192; blocchi interi: mediana 48.

## Cosa vuol dire

* **L'esame non promuove il rumore**, nemmeno sui prezzi veri con la loro persistenza di regime: una strategia
  senza vantaggio risulta «netta» lo 0,41% delle volte, meno del 2% dichiarato.
* **L'esame è più severo di quanto dichiara.** Sotto il caso puro il p-value dell'asticella dovrebbe stare sotto
  0,10 circa il 10% delle volte; qui ci sta il 3,26% (e sotto 0,05 l'1,0%). Il `t` contro la (b) delle placebo ha
  media 0,007 e deviazione standard 0,815 invece di 1: centrato giusto, ma con le code strette. Il motivo
  probabile (non provato qui) è che l'errore del candidato non scende mai sotto il pavimento della (b) e che
  all'errore si somma quello della baseline: un errore un po' sovrastimato. Prezzo: **meno potenza**. Un
  vantaggio vero ma piccolo passa più difficilmente di quanto si pensava: è un'altra ragione per la campagna di
  gruppo, non per allentare l'esame (le regole d'esame non si cambiano guardando questi numeri).
* **Informativo, non decide:** 5 delle 6 placebo «nette» sono incroci delle medie a 1 ora (5 su 154 = 3,25% per
  quella regola, intervallo per moneta 0,65-5,92%), tutte fra 150 e 230 trade. È l'unica regola sopra il 2%: i
  suoi segnali sono rari e a grappoli lunghi, cioè il caso in cui la persistenza di regime pesa di più. Da tenere
  d'occhio se una campagna porta un candidato di questo tipo.
* Per il Passo 6 (versione 4.5): la probabilità per moneta del trasferimento è il più alto fra 0,02, M1 sul
  totale (0,0041) e la quota «netta» in validazione (4 su 1.348 = 0,0030): vale **0,02**, da scrivere in
  `vault/APERTURA.md` all'apertura.

## Limiti

Regole d'ingresso e uscite fisse da manuale, non le idee di una campagna; niente funding; serie dello stop e del
mark uguali al last; nessuna verifica della Fase 4 (che fermerebbe altro rumore); monete idonee del 2023 che non
sono di campagna. La prova misura i falsi positivi dell'esame, non la sua potenza su un vantaggio vero.

## Uscita completa di riassunto.py

```
sfasamenti [0]; versioni del codice: ['8b6abf6b']
coppie moneta-timeframe: 160 su 160; monete con errore: 0; placebo con errore: 0
placebo in costruzione 1920: con >= 70 trade 1484, valutabili contro la (b) 1479; in validazione con >= 30 trade 1350, valutabili 1348
non valutabili (a parte, fuori dal denominatore): {'meno di 3 blocchi interi o errore infinito': 7}
M1 netta contro la (b), costruzione: 6 su 1479 = 0.41% (per moneta 95%: 0.13-0.74%; Wilson 0.19-0.88%; monete con almeno una: 6; quota della moneta piu' presente: 17%) | soglia 3%
M2 p < 0,10 in validazione: 44 su 1348 = 3.26% (per moneta 95%: 2.41-4.17%; Wilson 2.44-4.35%; monete con almeno una: 35; quota della moneta piu' presente: 7%) | soglia 13%
per fascia di trade (il confronto con il dichiarato 0-2% e 6-11% si fa sulla fascia piu' bassa):
  M1 70-149 trade: 1 su 561 = 0.18% (per moneta 95%: 0.00-0.56%; Wilson 0.03-1.00%; monete con almeno una: 1; quota della moneta piu' presente: 100%)
      1h: 0 su 153 = 0.00% (per moneta 95%: 0.00-0.00%; Wilson -0.00-2.45%; monete con almeno una: 0; quota della moneta piu' presente: 0%)
      4h: 1 su 408 = 0.25% (per moneta 95%: 0.00-0.75%; Wilson 0.04-1.38%; monete con almeno una: 1; quota della moneta piu' presente: 100%)
  M1 150-299 trade: 5 su 411 = 1.22% (per moneta 95%: 0.25-2.32%; Wilson 0.52-2.82%; monete con almeno una: 5; quota della moneta piu' presente: 20%)
      1h: 5 su 282 = 1.77% (per moneta 95%: 0.36-3.39%; Wilson 0.76-4.08%; monete con almeno una: 5; quota della moneta piu' presente: 20%)
      4h: 0 su 129 = 0.00% (per moneta 95%: 0.00-0.00%; Wilson -0.00-2.89%; monete con almeno una: 0; quota della moneta piu' presente: 0%)
  M1 300-... trade: 0 su 507 = 0.00% (per moneta 95%: 0.00-0.00%; Wilson 0.00-0.75%; monete con almeno una: 0; quota della moneta piu' presente: 0%)
      1h: 0 su 507 = 0.00% (per moneta 95%: 0.00-0.00%; Wilson 0.00-0.75%; monete con almeno una: 0; quota della moneta piu' presente: 0%)
      4h: nessuna
  M2 30-69 trade: 24 su 591 = 4.06% (per moneta 95%: 2.68-5.69%; Wilson 2.74-5.97%; monete con almeno una: 22; quota della moneta piu' presente: 8%)
      1h: 7 su 234 = 2.99% (per moneta 95%: 1.14-5.45%; Wilson 1.46-6.04%; monete con almeno una: 7; quota della moneta piu' presente: 14%)
      4h: 17 su 357 = 4.76% (per moneta 95%: 2.75-7.00%; Wilson 2.99-7.49%; monete con almeno una: 15; quota della moneta piu' presente: 12%)
  M2 70-149 trade: 8 su 419 = 1.91% (per moneta 95%: 0.72-3.28%; Wilson 0.97-3.72%; monete con almeno una: 8; quota della moneta piu' presente: 12%)
      1h: 8 su 322 = 2.48% (per moneta 95%: 0.94-4.32%; Wilson 1.26-4.83%; monete con almeno una: 8; quota della moneta piu' presente: 12%)
      4h: 0 su 97 = 0.00% (per moneta 95%: 0.00-0.00%; Wilson -0.00-3.81%; monete con almeno una: 0; quota della moneta piu' presente: 0%)
  M2 150-... trade: 12 su 338 = 3.55% (per moneta 95%: 1.85-5.62%; Wilson 2.04-6.10%; monete con almeno una: 11; quota della moneta piu' presente: 17%)
      1h: 12 su 338 = 3.55% (per moneta 95%: 1.85-5.62%; Wilson 2.04-6.10%; monete con almeno una: 11; quota della moneta piu' presente: 17%)
      4h: nessuna
informativo: candidati (netta (a) e (b), R medio > 0, nessuna violazione): 3 su 1479 = 0.20% (per moneta 95%: 0.00-0.47%; Wilson 0.07-0.59%; monete con almeno una: 3; quota della moneta piu' presente: 33%)
informativo: p < 0,10 in costruzione: 71 su 1479 = 4.80% (per moneta 95%: 3.67-5.97%; Wilson 3.82-6.01%; monete con almeno una: 46; quota della moneta piu' presente: 6%)
informativo: netta in validazione (p < 0,02275): 4 su 1348 = 0.30% (per moneta 95%: 0.07-0.60%; Wilson 0.12-0.76%; monete con almeno una: 4; quota della moneta piu' presente: 25%)
informativo: M1 contando le non valutabili come non nette: 6 su 1484 = 0.40% (per moneta 95%: 0.13-0.74%; Wilson 0.19-0.88%; monete con almeno una: 6; quota della moneta piu' presente: 17%)
per timeframe:
  1h: M1 5 su 942 = 0.53% (per moneta 95%: 0.11-1.05%; Wilson 0.23-1.24%; monete con almeno una: 5; quota della moneta piu' presente: 20%)
      M2 27 su 894 = 3.02% (per moneta 95%: 2.13-3.98%; Wilson 2.08-4.36%; monete con almeno una: 26; quota della moneta piu' presente: 7%)
  4h: M1 1 su 537 = 0.19% (per moneta 95%: 0.00-0.58%; Wilson 0.03-1.05%; monete con almeno una: 1; quota della moneta piu' presente: 100%)
      M2 17 su 454 = 3.74% (per moneta 95%: 2.19-5.49%; Wilson 2.35-5.91%; monete con almeno una: 15; quota della moneta piu' presente: 12%)
per direzione:
  long: M1 3 su 739 = 0.41% (per moneta 95%: 0.00-0.93%; Wilson 0.14-1.19%; monete con almeno una: 3; quota della moneta piu' presente: 33%)
        M2 30 su 674 = 4.45% (per moneta 95%: 2.90-5.98%; Wilson 3.14-6.28%; monete con almeno una: 25; quota della moneta piu' presente: 7%)
  short: M1 3 su 740 = 0.41% (per moneta 95%: 0.00-0.94%; Wilson 0.14-1.19%; monete con almeno una: 3; quota della moneta piu' presente: 33%)
         M2 14 su 674 = 2.08% (per moneta 95%: 1.17-3.07%; Wilson 1.24-3.46%; monete con almeno una: 14; quota della moneta piu' presente: 7%)
per regola:
  bollinger: M1 0 su 283 = 0.00% (per moneta 95%: 0.00-0.00%; Wilson 0.00-1.34%; monete con almeno una: 0; quota della moneta piu' presente: 0%)
             M2 9 su 261 = 3.45% (per moneta 95%: 1.55-5.66%; Wilson 1.82-6.42%; monete con almeno una: 9; quota della moneta piu' presente: 11%)
  incrocio_medie: M1 5 su 154 = 3.25% (per moneta 95%: 0.65-5.92%; Wilson 1.39-7.37%; monete con almeno una: 5; quota della moneta piu' presente: 20%)
                  M2 5 su 138 = 3.62% (per moneta 95%: 0.72-6.72%; Wilson 1.56-8.20%; monete con almeno una: 5; quota della moneta piu' presente: 20%)
  macd: M1 0 su 307 = 0.00% (per moneta 95%: 0.00-0.00%; Wilson -0.00-1.24%; monete con almeno una: 0; quota della moneta piu' presente: 0%)
        M2 13 su 275 = 4.73% (per moneta 95%: 2.54-7.07%; Wilson 2.78-7.92%; monete con almeno una: 13; quota della moneta piu' presente: 8%)
  momento_10: M1 0 su 314 = 0.00% (per moneta 95%: 0.00-0.00%; Wilson 0.00-1.21%; monete con almeno una: 0; quota della moneta piu' presente: 0%)
              M2 3 su 297 = 1.01% (per moneta 95%: 0.00-2.33%; Wilson 0.34-2.93%; monete con almeno una: 3; quota della moneta piu' presente: 33%)
  rottura_20: M1 1 su 271 = 0.37% (per moneta 95%: 0.00-1.14%; Wilson 0.07-2.06%; monete con almeno una: 1; quota della moneta piu' presente: 100%)
              M2 8 su 243 = 3.29% (per moneta 95%: 1.22-6.02%; Wilson 1.68-6.36%; monete con almeno una: 7; quota della moneta piu' presente: 25%)
  rsi: M1 0 su 150 = 0.00% (per moneta 95%: 0.00-0.00%; Wilson 0.00-2.50%; monete con almeno una: 0; quota della moneta piu' presente: 0%)
       M2 6 su 134 = 4.48% (per moneta 95%: 1.46-8.33%; Wilson 2.07-9.42%; monete con almeno una: 6; quota della moneta piu' presente: 17%)
per uscita:
  atr: M1 6 su 732 = 0.82% (per moneta 95%: 0.27-1.50%; Wilson 0.38-1.78%; monete con almeno una: 6; quota della moneta piu' presente: 17%)
       M2 26 su 656 = 3.96% (per moneta 95%: 2.62-5.44%; Wilson 2.72-5.74%; monete con almeno una: 23; quota della moneta piu' presente: 8%)
  tempo: M1 0 su 747 = 0.00% (per moneta 95%: 0.00-0.00%; Wilson -0.00-0.51%; monete con almeno una: 0; quota della moneta piu' presente: 0%)
         M2 18 su 692 = 2.60% (per moneta 95%: 1.45-3.95%; Wilson 1.65-4.07%; monete con almeno una: 15; quota della moneta piu' presente: 11%)
blocchi interi in costruzione: mediana 48, minimo 3; trade: mediana 192
ESITO: l'esame regge sui prezzi veri (M1 <= 3% e M2 <= 13%)
```
