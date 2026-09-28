# 0330-controllo-28set-ai-stato.req

_eseguito: 2026-09-28 06:18 UTC_

**richiesta:** `ai-stato`
**eseguito:** `.venv/bin/python -m scripts.ai_status`
**esito:** codice 0 in 4.6s

```
==============================================================
STATO DEL LIVELLO AI
==============================================================
✅ chiave: funziona · modello claude-opus-4-8
[firebase] connesso (Firestore + RTDB)

✅ proposte: 20/20 accettate dal validatore · 28 Sep 03:15 UTC (3h fa)
✅ di origine AI fra quelle che hanno passato il gate: 29 su 605

✅ ombra: 184 decisioni registrate · ultima 28 Sep 05:32 UTC (1h fa)
   il bot aveva un trade aperto nello stesso ciclo in 148 decisioni, in 36 no
   d'accordo col bot 15/148 volte quando aveva aperto (serve piu' campione per dire se conviene ascoltarla)
     shadow_veto ×132: avrebbe evitato il trade aperto
     both_flat ×31: entrambi fermi
     agree ×15: stessa scelta del bot
     shadow_only ×5: avrebbe operato, il bot no
     different_pick ×1: altra scelta

❌ prove: nessuna. L'AI sta proponendo alla cieca.
➖ quasi-passaggi: nessuna analisi AI ancora (arriva col prossimo giro)
[paper] misura mfe non disponibile (429 Quota exceeded.) -> scale fisse
➖ scala dal vissuto: non ancora (servono 10 trade con mfe)
==============================================================
Promemoria: l'AI NON decide i trade. Propone strategie (che il gate valida)
e decide in ombra (che non tocca niente). E' voluto: una sua decisione non e'
riproducibile, quindi non potrebbe mai passare il GATE 1.
```
