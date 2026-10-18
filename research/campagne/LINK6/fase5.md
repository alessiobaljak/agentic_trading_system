# Fase 5 — Sfida alla conclusione (Passo 2, campagna LINK6)

Scritta il 18 ottobre 2026, sul solo periodo di costruzione (dalla prima candela al 2022-09-30). Fonti dei numeri:
`log.jsonl` (voci `risultato`), `codice/riepilogo.py`, `codice/fase3_analisi.py`, `codice/fase5_pvalue.py`.

## Conclusione che sfido

Nessuna delle varianti provate ha un vantaggio sulla costruzione: 26 varianti con la Fase 2, nessuna la supera; una
variante nata dalla Fase 3 (V-019) scartata dal controllo sulle monete di controllo. Varianti che consumano un
tentativo: 27 su 40. Candidati: nessuno.

## Le domande della Fase 5

**Mi sono fissato sulla prima idea decente?** No (osservato). 13 idee, da famiglie diverse del catalogo: rottura di
canale (E3), funding (E11), range asiatico (E10), volume anomalo (E12), ritorno nelle bande (E5, a mercato e con
limit), rottura delle bande dopo la compressione (E4 con F3), RSI a 50 (E7 con F2), MACD (E9), prezzo e media (E2),
RSI agli estremi (E6), stocastico (E8), rottura nelle ore degli Stati Uniti (E3 con F5 e C1). Una sola idea ha avuto un
seguito (V-004 → V-019), e il seguito e' stato fermato dal controllo.

**Cosa direbbe uno scettico? (risposta con un test)** «Se i segnali non valgono niente, i p-value devono essere
distribuiti come il caso.» Test (`codice/fase5_pvalue.py`, sui 26 p-value gia' calcolati): p-value medio 0,531 (caso:
0,500); 3 sotto 0,10 (caso: 2,6 attesi; probabilita' di almeno 3 per caso 0,489); 1 a 0,023 o meno (caso: 0,60;
probabilita' di almeno 1 per caso 0,454); Kolmogorov-Smirnov contro l'uniforme: statistica 0,171, p 0,387. I p-value
non si distinguono da quelli del caso (osservato). Un secondo scettico direbbe: «allora il metodo non sa vedere i
vantaggi». Risposta: la prova B del collaudo (vantaggio inserito apposta) l'ha verificata il coordinamento al Passo 0;
la sessione di ricerca non ne legge i numeri (sezione 13bis). Inferito: il metodo vede un vantaggio quando c'e', e qui
non c'e'.

**Quali parti dei risultati sono piu' probabilmente fortuna?** (inferito) V-004 (R medio +0,128, p-value 0,047) e
V-021 (p-value 0,001 con R medio +0,010): sono i due p-value piu' bassi su 26, quanti il caso ne da'. V-021 batte le
sue entrate casuali solo perche' gli short casuali perdono nel rialzo di fondo (casuali −0,083 R). La modifica di V-004
(V-019) non e' migliore sulle monete di controllo (R-001): coerente con un risultato di V-004 dovuto al caso o specifico
di LINKUSDT.

**Qualche scelta e' stata guidata da cio' che so del 2024-2026?** Per quanto posso giudicare, no (ipotizzato, non
dimostrabile: sezione 15). Le idee vengono dalla letteratura citata in `ipotesi.md`, tutta precedente al 2024, e i
valori dalla stima dei trade e da motivi scritti prima dei test. Non posso escludere un'influenza che non vedo.

**I candidati vengono da idee diverse o sono ritagli della stessa idea?** Non ci sono candidati. Osservazione utile
per le campagne future: le quattro idee di ritorno alla media (I-05, I-07, I-11, I-12, otto varianti) hanno tutte R
medio negativo e sotto le loro entrate casuali; le idee di tendenza (I-01, I-08, I-09, I-10) sono vicine a zero.

## Perche' non uso i 13 tentativi rimasti

Scelta della sessione (sezione 1: l'agente decide quali idee provare). Le famiglie del catalogo non provate sono poche
(incrocio di medie E1, che a 4h dava 121-122 trade; VWAP F7; fine settimana F6; conferme C2 e C3). Non ho una ragione
nuova, scritta prima, per aspettarmi un vantaggio li', e ogni variante in piu' aumenta la probabilita' di un falso
candidato (sezione 8.3: con 40 varianti il 61% di probabilita' di almeno uno). Il rischio di fermarmi: perdere un
vantaggio in quelle combinazioni; lo giudico basso (ipotizzato). Se il proprietario o il coordinamento allo STOP
chiedono di continuare, si continua con il limite di 40.

## Esito

Passo 2 finito senza candidati. Se lo STOP lo conferma, la validazione (Passo 3) non ha candidati da eseguire, e la
consegna (Passo 4) scrivera' «nessuna strategia valida trovata».
