# Proposte di lezioni di metodo (solo errori di metodo e trappole dei dati)

Da unire in `lezioni/metodo.md` al Passo 7, se il coordinamento le condivide.

1. **La stima dei trade deve usare un'occupazione definita UNA volta, prima di ogni variante.**
   Qui l'occupazione e' stata dichiarata variante per variante (15 barre per il canale con uscita a
   60, 7 per il momentum con uscita a 7): per V01 la stima (100) non era un limite inferiore (72 trade
   veri), per V03 lo era in eccesso (97 stimati con 7 barre di occupazione, scartata). Proposta:
   occupazione = numero massimo di barre in posizione della variante, sempre; chi vuole un conteggio
   piu' fine lo dichiara nel protocollo, non nella variante.
2. **«Netta» con 100-150 trade e' un'asticella molto alta a 8 ore-1 giorno.** Con R medi dell'ordine
   di 0,05-0,10 e deviazioni standard di 0,5-0,7 R per trade, l'errore standard della differenza e'
   circa 0,06-0,13: servirebbero 300-500 trade per rendere netto un vantaggio vero di 0,08 R. Sulle
   idee giornaliere con 2,8 anni di costruzione la potenza e' quasi nulla. Il protocollo lo dichiara
   gia' (sezione 11, potenza bassa); vale la pena scriverlo come numero: a 1 giorno una campagna su
   una moneta sola puo' quasi solo scartare.
3. **Un risultato al 90-96° percentile del caso ma non netto non ha un posto nel protocollo.** V08
   e' stato chiuso dalla regola della Fase 2 senza toccare la validazione. E' giusto (la regola e'
   scritta prima), ma il coordinamento potrebbe valutare se un candidato «sopra il 90° percentile ma
   non netto» debba andare in validazione come «candidato debole», con il suo p-value nell'asticella:
   la validazione e' il test piu' economico e l'asticella corregge per i tentativi. Da decidere prima
   delle prossime campagne, non guardando V08.
4. **Baseline (a) e (b) misurano cose diverse e vanno riportate entrambe.** La baseline
   incondizionata su timeframe corti e' dominata dai costi (a 1 ora: −0,12 R per trade): un
   candidato la batte «nettamente» solo perche' entra meno spesso (V14). Il confronto con le entrate
   casuali con lo stesso numero di trade e' quello che smaschera.
5. **Lo stop in ATR su candele giornaliere e' incompatibile con il tetto del 6% del bot.** Chi
   disegna idee a 1 giorno deve saperlo prima: o stop in percentuale (e R diversi), o idee non
   eseguibili dal bot.
6. **Il mark price di Binance ha giorni interi mancanti nell'archivio** (per BTCUSDT 770 barre a
   15 minuti in 7 buchi): il caricatore non puo' pretendere l'allineamento; la regola di riempimento
   va decisa al Passo 0 per tutte le monete, non in ogni campagna.
7. **Il numero di simulazioni casuali va fissato per timeframe** (qui 100, ma 50 a 30 minuti per il
   tempo di calcolo): e' una scelta dichiarata nel log, ma meglio nel protocollo.
8. **I file di aiuto delle 1h sono lenti con il motore attuale** (slicing delle candele a ogni barra):
   un esame completo con 100 simulazioni a 1 ora dura circa 5 minuti, a 30 minuti circa 8 con 50
   simulazioni. Per le prossime monete conviene passare al motore l'indice invece della fetta, o
   accettare i tempi.
