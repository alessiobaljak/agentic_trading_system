# Regola delle monete di verifica (scritta al Passo 1, si applica al Passo 6)

Scritta il 7 ottobre 2026, prima di qualunque dato del periodo del vault. Non si applica adesso.

**Monete di verifica** = tutti i contratti perpetui in USDT con dati nell'archivio (compresi i delistati) che:
1. non sono monete di campagna (`monete_campagna.csv`);
2. hanno un volume medio giornaliero in USDT (quote volume delle candele giornaliere) **sopra 20 milioni nel
   periodo del vault** (2024-01-01 → 2026-09-30); per un contratto delistato o nato durante il vault, la media
   si calcola sui giorni del vault in cui era negoziato, e il test di trasferimento vale solo su quei giorni;
3. hanno almeno un mese di dati nel periodo del vault.

Non c'è un requisito di storia prima del 2024: una moneta nata nel 2024 o nel 2025 è una moneta di verifica
a pieno titolo, perché il trasferimento usa solo il periodo del vault.

**Fascia di slippage** delle monete di verifica: calcolata sul volume medio del periodo del vault (non del
2023), con le stesse fasce di `config/parametri.yaml`. È un'informazione del vault usata solo per i costi, da
dichiarare nei report (sezione 11 del protocollo).

**Conteggio.** La lista si crea al Passo 6 con `research/src/passo1.py` applicato alla finestra del vault (o
con una funzione gemella), e si riporta: quante monete di verifica, quante delistate, quante nate nel vault.
