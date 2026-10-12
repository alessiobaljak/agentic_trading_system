"""Controlla solo che il codice delle varianti giri (prepara, condizione, segnale, uscita) su poche barre.
Non conta segnali ne' trade e non stampa nessun numero dei dati: stampa solo 'ok' o l'errore."""
from comune import motore
import quadro
from registro import VARIANTI

for id_, voce in VARIANTI.items():
    var = voce[1]()
    if var.tf not in ("1h", "1d", "4h", "8h", "30m"):
        continue
    try:
        s = quadro.carica(var.tf, "costruzione")
        ctx = var.prepara(s)
        ctx["serie"] = s
        for i in (len(s.c) - 3, len(s.c) - 2):
            var.condizione(ctx, i)
            sg = var.segnale(ctx, i)
            pos = motore.Posizione(var.direzione, s.c[i], 1.0, None, 1.0, int(s.ts[i - 5]), s.c[i], 1.0, 1.0, 0.0, False, False)
            var.uscita(ctx, i, pos)
        print(id_, "ok")
    except Exception as e:  # noqa: BLE001
        print(id_, "ERRORE", repr(e))
