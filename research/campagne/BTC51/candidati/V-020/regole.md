# Candidato V-020 — regole

Ipotesi: I-09 (da I-04), `research/campagne/BTC51/ipotesi.md`. Registrazione e risultati nel log
(`research/campagne/BTC51/log.jsonl`, id `V-020` e `V-020-F4`).

## Specifica (sezione 7.1 del protocollo)

```json
{"timeframe": "1h", "direzione": "long",
 "filtro": {"codice": "F6", "giorni": "feriali"},
 "ingresso": {"codice": "E11", "soglia": 0.0},
 "conferma": null,
 "tipo_ingresso": {"codice": "M"},
 "stop": {"codice": "S1", "k": 2.0},
 "uscite": [{"codice": "U2", "n": 24}]}
```

In parole: su candele da 1 ora, solo long. Alla chiusura della prima candela che inizia dopo un regolamento del
funding (00:00, 08:00, 16:00 UTC), se l'ultimo funding regolato è **sotto 0,00%** e la candela è di un giorno feriale
(lunedì-venerdì UTC), si compra a mercato all'apertura della candela successiva. Stop a 2 × ATR(14) della candela del
segnale sotto il prezzo d'ingresso. Uscita all'apertura della candela successiva alla 24ª candela chiusa dopo
l'ingresso, se lo stop non è scattato prima. Una posizione alla volta.

## Meccanismo economico (ipotesi, non dimostrato)

Il funding negativo vuol dire che chi è short a leva paga chi è long: c'è una folla di short. Quando la folla è
affollata il prezzo tende a risalire nelle 24 ore seguenti (chiusura degli short, ritorno del funding verso il valore
normale). Nel fine settimana, con meno operatori, il segnale vale meno (idea nata dai dati: vedi ipotesi I-09).

## Metriche di costruzione (dal 2020-01-01 al 2022-09-30)

180 trade (5,46 al mese); R medio +0,223; profit factor 1,46; vincenti 48,3%; drawdown massimo −9,0 R; p-value 0,017 (entrate casuali: R medio −0,004);
senza il 5% dei trade migliori +0,012; costi doppi +0,147. Fase 4: verifiche da 1 a 7 superate (la 8 non si applica).

## Eseguibile dal bot?

No così com'è: al Passo 0 il bot non eseguiva nessuna variante del catalogo (scelta (b) della sezione 7.10, aggiunta
al bot prima del paper).
