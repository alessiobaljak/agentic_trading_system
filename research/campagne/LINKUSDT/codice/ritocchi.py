"""I ritocchi (regola 6), ognuno scritto dopo aver visto i risultati di costruzione e prima del suo test.

Ogni ritocco: stessa idea, timeframe, direzione e meccanismo della variante di partenza; cambia soglie,
parametri, uscita, stop o target, o aggiunge un filtro nato dalla Fase 3.
"""
import varianti as VV

RITOCCHI = {
    # Scritto dopo la nota N014, primo dell'ordine della regola 6 (V24, t contro la (b) 2,233).
    "R01": dict(idea="I-14", famiglia="LINKUSDT-V24", ritocco_di="LINKUSDT-V24", tf="1d", direzione="long",
                meccanismo="inversione giornaliera dopo un giorno negativo",
                parametri={"rendimento_barre": 1, "soglia": "< 0", "uscita_barre": 2, "stop_atr": 2},
                cosa_cambia=("uscita dopo 2 barre invece di 1. Perche': la Fase 3 (N013) non mostra un filtro sui dati della "
                             "moneta (ne' ampiezza della discesa ne' volatilita' ordinano l'R), e la fonte trova inversione anche "
                             "a frequenza settimanale: si prova se il rimbalzo dura oltre il primo giorno. Lo stop non conta "
                             "(3 stop su 324)."),
                prepara=VV.costruttore("long", 2, 2, VV.cond_rend_k(1, -1)),
                previsione="R medio fra -0,02 e +0,08, t contro la (b) fra -0,5 e +2,5: probabilmente piu' debole di V24 (il rimbalzo e' di un giorno)"),
    # Scritto dopo il risultato di R01; ordine ricalcolato: primo ancora V24 (t 2,233), famiglia con 1 ritocco.
    "R02": dict(idea="I-14", famiglia="LINKUSDT-V24", ritocco_di="LINKUSDT-V24", tf="1d", direzione="long",
                meccanismo="inversione giornaliera dopo un giorno negativo",
                parametri={"rendimento_barre": 1, "soglia": "< 0", "uscita_barre": 1, "stop_atr": 1},
                cosa_cambia=("stop a 1 ATR(14) invece di 2, uscita dopo 1 barra come V24. Perche': la Fase 3 (N013) mostra che le "
                             "perdite di V24 vengono dai giorni in cui la discesa continua (quartile peggiore del mercato nel giorno "
                             "del trade: R medio -0,229); uno stop piu' stretto taglia quelle perdite. Si sa che cambia anche la "
                             "scala dell'R (rischio misurato su uno stop piu' vicino), uguale per la (a) e la (b)."),
                prepara=VV.costruttore("long", 1, 1, VV.cond_rend_k(1, -1)),
                previsione="R medio fra -0,02 e +0,10, t contro la (b) fra 0 e +2,5"),
    # Scritto dopo il risultato di R02; ordine ricalcolato: primo ancora V24 (t 2,233), famiglia con 2 ritocchi.
    "R03": dict(idea="I-14", famiglia="LINKUSDT-V24", ritocco_di="LINKUSDT-V24", tf="1d", direzione="long",
                meccanismo="inversione giornaliera dopo un giorno negativo",
                parametri={"rendimento_barre": 1, "soglia": "< 0", "uscita_barre": 1, "stop_atr": 2, "target_atr": 1},
                cosa_cambia=("aggiunto un target a 1 ATR(14) sopra la chiusura del giorno di segnale; stop 2 ATR e uscita dopo 1 "
                             "barra come V24. Perche': se il rimbalzo e' compenso a chi offre liquidita' (la fonte), arriva "
                             "dentro il giorno e una parte si perde entro la chiusura; il target lo incassa quando c'e'. Con "
                             "stop prima del target nella stessa barra (regola fissa)."),
                prepara=None,
                previsione="R medio fra -0,03 e +0,08, t contro la (b) fra -0,5 e +2,5"),
}


def _prepara_r03(candele, extra):
    import comune as C
    import indicatori as I
    from research.src.motore import Segnale
    c = I.arr(candele, "close")
    a = I.atr(candele, 14)
    entra = VV.cond_rend_k(1, -1)(candele, extra)

    def segnale(i):
        if not I.ok(a[i]) or a[i] <= 0:
            return None
        return Segnale("long", c[i] - 2 * a[i], c[i] + 1 * a[i])
    return C.Prep(entra, segnale, lambda i, ie: i - ie + 1 >= 1)


RITOCCHI["R03"]["prepara"] = _prepara_r03
