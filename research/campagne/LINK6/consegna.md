# Consegna (Passo 4) — campagna LINK6

Scritta il 18 ottobre 2026. Protocollo: `research/PROTOCOLLO_4.md` (versione 6).

## Esito

**Nessuna strategia valida trovata.**

Su LINKUSDT, nel periodo di costruzione (dalla prima candela del 2020-01-17 al 2022-09-30), nessuna delle varianti
provate supera la Fase 2 (sezione 10.3: almeno 150 trade, R medio di almeno 0,2 R dopo i costi, p-value di 0,023 o
meno contro 1.000 entrate casuali). Non ci sono candidati: la validazione (Passo 3) non ha niente da eseguire
(`validazione.md`), e il vault di LINKUSDT resta chiuso e mai aperto.

## I numeri

- **Varianti usate:** 33 su 40 (sezione 8.3): 32 con la Fase 2, piu' una variante nata dalla Fase 3 scartata dal
  controllo sulle monete di controllo.
- **Varianti nate dalla Fase 3 scartate dal controllo sulle monete di controllo:** 1 su 1 (V-019, richiesta R-001,
  risposta «non supera»).
- **Scarti per stima dei trade sotto 150:** nessuna variante registrata; le bozze sotto i minimi sono state escluse
  prima di scriverle (`codice/bozze_stima_*.json`, solo conteggi).
- **Idee:** 16, ognuna con fonte pubblicata prima del 2024 (`ipotesi.md`).
- **Tentativi non usati:** 7, perche' non restavano idee con un perche' e una fonte che non nascessero dai risultati
  (`fase5.md`; condivise dal coordinamento).

Fonti di ogni numero qui sotto: le voci `registrazione` e `risultato` di `log.jsonl` (riassunte da
`codice/riepilogo.py`). R medio dopo i costi; «casuali» e' l'R medio delle 1.000 entrate casuali della variante.

## Le 16 idee provate

| Idea | Varianti | Trade | R medio | Casuali | p-value | Esito e motivo |
|---|---|---|---|---|---|---|
| I-01 Rottura di Donchian a 55 in tendenza (1h, trailing) | V-001 long, V-002 short | 229, 183 | −0,085, −0,061 | −0,030, −0,051 | 0,766, 0,548 | non supera: R negativo |
| I-02 Funding estremo, contrarian (1h) | V-003 short sopra +0,05%, V-004 long sotto 0,00% | 202, 174 | +0,002, +0,128 | −0,038, −0,013 | 0,298, 0,047 | non supera: R sotto 0,2 e p-value sopra 0,023 |
| I-03 Rottura del range asiatico (1h) | V-005 long, V-006 short | 412, 344 | −0,079, +0,005 | −0,051, −0,059 | 0,740, 0,104 | non supera: R vicino a zero o negativo |
| I-04 Volume anomalo con la direzione della candela (2h) | V-007 long, V-008 short | 312, 339 | +0,030, +0,024 | −0,025, −0,035 | 0,119, 0,089 | non supera: R sotto 0,2 |
| I-05 Ritorno nelle bande di Bollinger con ADX basso (30m) | V-009 long, V-010 short | 316, 327 | −0,161, −0,150 | −0,103, −0,061 | 0,835, 0,940 | non supera: R negativo, costi alti a 30m |
| I-06 Rottura delle bande dopo la compressione della volatilita' (1h) | V-011 long, V-012 short | 212, 160 | −0,054, +0,043 | −0,044, −0,008 | 0,554, 0,245 | non supera |
| I-07 Ritorno nelle bande con ordine limit (1h) | V-013 long, V-014 short | 217, 226 | −0,100, −0,130 | −0,015, −0,039 | 0,912, 0,908 | non supera: R negativo |
| I-08 RSI che passa 50 con ADX alto (1h) | V-015 long, V-016 short | 316, 271 | −0,076, −0,008 | −0,019, −0,053 | 0,825, 0,237 | non supera |
| I-09 Incrocio del MACD in tendenza (2h) | V-017 long, V-018 short | 232, 191 | −0,012, +0,017 | +0,016, −0,061 | 0,692, 0,103 | non supera |
| I-10 Prezzo che incrocia la SMA(50) (4h) | V-020 long, V-021 short | 199, 199 | +0,091, +0,010 | +0,084, −0,083 | 0,354, 0,001 | non supera: R sotto 0,2 (V-021 batte il caso, ma di pochi centesimi di R) |
| I-11 RSI(14) agli estremi, ritorno (1h) | V-022 long, V-023 short | 273, 301 | −0,088, −0,197 | −0,009, −0,038 | 0,883, 0,993 | non supera: R negativo |
| I-12 Stocastico agli estremi (2h) | V-024 long, V-025 short | 238, 366 | −0,102, −0,125 | −0,020, −0,042 | 0,886, 0,946 | non supera: R negativo |
| I-13 Rottura a 20 nelle ore degli Stati Uniti con volume (1h) | V-026 long, V-027 short | 222, 197 | −0,018, −0,036 | −0,027, −0,062 | 0,429, 0,343 | non supera |
| I-14 Incrocio EMA 20/50 (1h) | V-028 long, V-029 short | 220, 220 | +0,242, +0,084 | +0,165, −0,076 | 0,130, 0,003 | non supera: V-028 p-value sopra 0,023 (il rialzo del 2020, non il segnale); V-029 R sotto 0,2 |
| I-15 RSI a 50 dalla parte del VWAP (1h) | V-030 long, V-031 short | 777, 768 | −0,034, +0,027 | −0,061, −0,070 | 0,210, 0,003 | non supera: R sotto 0,2 |
| I-16 Ritorno nelle bande nel fine settimana, con la candela di rifiuto (1h) | V-032 long, V-033 short | 159, 167 | −0,085, −0,048 | −0,065, −0,041 | 0,609, 0,538 | non supera: R negativo |

**Variante nata dalla Fase 3.** V-019 (idea I-02): V-004 con l'uscita a tempo dopo 48 candele invece di 24, scelta
guardando le uscite a tempo di V-004 (+0,449 R in media). Il controllo sulle monete di controllo (Fase 3, punto 4,
richiesta R-001) non e' passato: la media dell'R medio sulle monete di controllo non migliora di almeno 0,05 R. Scarto
che consuma il tentativo; nessuna Fase 2 su LINKUSDT.

## Cosa resta (osservato e inferito, `fase5.md`)

- Osservato: i 32 p-value sono compatibili con il caso (medio 0,478; Kolmogorov-Smirnov contro l'uniforme p 0,416).
- Osservato: i costi non spiegano i fallimenti (0,03-0,05 R a trade a 1h e 2h, 0,085 R a 30m); anche prima dei costi
  l'R medio resta vicino a zero.
- Osservato: le otto varianti di ritorno alla media (I-05, I-07, I-11, I-12) e le due del fine settimana (I-16) hanno
  R medio negativo.
- Inferito: i tre p-value a 0,023 o meno (V-021, V-029, V-031) sono la stessa idea, short di tendenza, che batte
  short casuali in perdita nel rialzo della costruzione (buy and hold +184%), ma con R medio fra +0,010 e +0,084,
  molto sotto la soglia: un tempismo vero ma troppo piccolo per pagare.

## Limiti (sezione 15)

- Una sola moneta, e solo il periodo di costruzione: l'esito dice che queste regole del catalogo non avevano un
  vantaggio su LINKUSDT fino a settembre 2022, non che nessuna strategia possa averlo.
- Il catalogo e' chiuso: strategie fuori catalogo non sono state provate.
- La costruzione di LINKUSDT era gia' stata esplorata da un protocollo precedente, di cui questa sessione non conosce
  le varianti.
- Il modello conosce il mercato del 2024-2026: per quanto posso giudicare non ha guidato le scelte, ma non lo posso
  dimostrare.

## Cio' che il Passo 4 chiede per ogni candidato

Non ci sono candidati: specifiche complete, metriche di costruzione e di validazione, verifiche della Fase 4,
previsione per il vault, eseguibilita' dal bot e trade attesi in paper non si applicano. Per il protocollo la ricerca si
chiude al Passo 9, che fa il coordinamento.
