"""LA SONDA SUI TIMEFRAME: che misuri quello che dice, e che non scriva niente.

Domanda del proprietario: «se ci sono monete non copribili a 15 min, magari dobbiamo
passare a 1 ora o 5 min». Prima di cambiare il motore si misura — e una misura che
puo' essere letta in due modi opposti non e' una misura.

I due rischi che questi test chiudono:

  1. **Scrivere.** Una coppia validata a 1 ora che finisse nel registro verrebbe
     operata dal bot a 15 minuti: la divergenza fra gate e vissuto costruita a mano.
     La sonda deve essere in sola lettura, e questo va verificato, non promesso in
     una docstring.

  2. **Leggere male.** Se a 1 ora passa piu' roba OVUNQUE — anche sulle monete gia'
     coperte — non e' un fatto sulle monete, e' un fatto sul timeframe (costi che
     pesano meno, meno barre quindi piu' rumore). Senza gruppo di controllo le due
     spiegazioni sono indistinguibili, e si riscriverebbe il sistema per inseguire
     un artefatto.
"""
import inspect

from scripts import timeframe_probe as probe


def test_it_never_writes_anything():
    """Sola lettura, verificato sul sorgente. `set_doc` o `merge_into_registry` qui
    dentro vorrebbero dire coppie validate a una scala e operate a un'altra."""
    src = inspect.getsource(probe)
    for vietato in ("set_doc", "merge_into_registry", "update_registry",
                    "persist_specs", "set_rtdb"):
        assert vietato not in src, (
            f"la sonda chiama `{vietato}`: deve solo misurare. Una coppia validata a "
            f"un timeframe diverso, scritta nel registro, verrebbe operata dal bot al "
            f"timeframe globale.")


def test_the_current_timeframe_is_always_measured_as_a_reference():
    """Senza 15m nel confronto, un tasso a 1 ora non si sa se sia alto o basso."""
    assert "15m" in probe.TIMEFRAMES


def test_it_runs_without_arguments():
    """Una voce della lista bianca NON puo' ricevere argomenti: una richiesta ops
    nomina una voce, non compone un comando. Tutti i parametri hanno un default."""
    sig = inspect.signature(probe.main)
    assert not [p for p in sig.parameters.values()
                if p.default is inspect.Parameter.empty]
    src = inspect.getsource(probe.main)
    assert "ap.error(" not in src, "nessun percorso deve morire sull'usage"


def test_covered_means_validated_not_merely_confirmed():
    """Due conferme su tre non rendono una moneta operabile: il bot opera solo le
    validate. Se il gruppo «coperte» le includesse, la sonda misurerebbe il
    guadagno su monete che in realta' non copriamo — cioe' diluirebbe proprio il
    segnale che cerca."""
    from scripts.optimize import MIN_PASSES
    from bot.core.firebase_client import encode_pairs

    class FB:
        def get_doc(self, *a):
            return {"pairs": encode_pairs({
                "COPERTAUSDT|gen_a": {"symbol": "COPERTAUSDT", "generated": True,
                                      "pass_count": MIN_PASSES},
                "QUASIUSDT|gen_b": {"symbol": "QUASIUSDT", "generated": True,
                                    "pass_count": MIN_PASSES - 1},
            })}

    def _universo(_n):
        return ["COPERTAUSDT", "QUASIUSDT", "ALTRAUSDT"]

    originale = probe.top_symbols_by_volume
    probe.top_symbols_by_volume = _universo
    try:
        scoperte, controllo = probe.scegli_monete(FB(), 10, 4)
    finally:
        probe.top_symbols_by_volume = originale

    assert "ALTRAUSDT" in scoperte
    assert controllo == ["COPERTAUSDT"]
    assert "COPERTAUSDT" not in scoperte


def test_the_same_candidates_are_used_on_every_timeframe():
    """Confrontare insiemi di strategie diversi non direbbe niente sul timeframe:
    la variabile dev'essere una sola. Le spec si generano UNA volta, fuori dal ciclo
    sulle scale."""
    src = inspect.getsource(probe.main)
    assert src.index("generate_specs(") < src.index("for tf in tfs:")


def test_it_prints_as_it_goes_and_stops_before_the_guillotine():
    """IL PRIMO TENTATIVO NON HA LASCIATO NIENTE. Il canale ops uccide a 900s e
    restituisce l'output parziale — ma l'output parziale di un processo Python
    ucciso e' VUOTO: stdout su pipe e' bufferizzato a blocchi. Risultato: codice
    124, zero righe, e nessuna idea di quanto fosse arrivata lontano.

    Due difese, e servono entrambe: ogni riga esce SUBITO (`di`, che fa flush), e la
    sonda ha una deadline PROPRIA piu' corta di quella del canale, cosi' si ferma da
    sola e stampa cio' che ha invece di essere ammazzata a meta'.
    """
    src = inspect.getsource(probe)
    assert "flush=True" in inspect.getsource(probe.di)
    assert "args.budget" in inspect.getsource(probe.main), "manca la deadline propria"
    assert probe.BUDGET_S < 900, "la deadline deve stare DENTRO quella del canale ops"
    # nessun print non flushato nel percorso lungo
    assert "print(" not in inspect.getsource(probe.main), (
        "usa `di()`: un print bufferizzato sparisce se il processo viene ucciso")


def test_the_cheapest_scale_goes_first():
    """A 5 minuti la serie ha dodici volte le candele di un'ora e non e' in cache.
    Misurandola per prima si consuma tutto il budget e non si risponde a NIENTE —
    e' quello che e' successo. Dalla piu' economica alla piu' cara: se il tempo
    finisce si perde solo l'ultima."""
    assert probe.TIMEFRAMES.index("1h") < probe.TIMEFRAMES.index("15m") \
        < probe.TIMEFRAMES.index("5m")


def test_without_the_reference_scale_it_refuses_to_conclude():
    """Se 15m non e' stata misurata, un tasso a 1 ora non si sa se sia alto o basso.
    Meglio dire «niente conclusioni» che produrre un confronto contro il vuoto."""
    src = inspect.getsource(probe.main)
    assert 'rif = risultati.get("15m")' in src
    assert "Niente conclusioni" in src


def test_the_two_groups_never_overlap():
    """AL PRIMO GIRO XRPUSDT ERA IN ENTRAMBI. «scoperte» escludeva solo le monete
    VALIDATE; il controllo di ripiego prende quelle a MIN_PASSES-1, che validate non
    sono — quindi finivano in tutti e due i gruppi.

    Un controllo che contiene le stesse monete del gruppo misurato non controlla
    niente: l'esperimento diventa inutile e nessun numero nel rapporto lo dice."""
    from scripts.optimize import MIN_PASSES
    from bot.core.firebase_client import encode_pairs

    class FB:
        def get_doc(self, *a):
            # nessuna moneta VALIDATA: scatta il controllo di ripiego
            return {"pairs": encode_pairs({
                "QUASIUSDT|gen_a": {"symbol": "QUASIUSDT", "generated": True,
                                    "pass_count": MIN_PASSES - 1}})}

    originale = probe.top_symbols_by_volume
    probe.top_symbols_by_volume = lambda _n: ["QUASIUSDT", "AUSDT", "BUSDT"]
    try:
        scoperte, controllo = probe.scegli_monete(FB(), 10, 4)
    finally:
        probe.top_symbols_by_volume = originale

    assert controllo == ["QUASIUSDT"]
    assert not set(scoperte) & set(controllo), (
        f"gruppi sovrapposti: {set(scoperte) & set(controllo)}")


def test_it_measures_a_distribution_not_a_rare_event():
    """IL PRIMO GIRO UTILE HA DATO 0 PASSAGGI SU TUTTE E SEI LE CASELLE, e non era
    una risposta: era un esperimento senza potenza. Col tasso di passaggio misurato
    (0,19%, una candidata su ~500) una casella da 120 valutazioni produce in media
    0,2 passaggi — zero ovunque e' l'esito piu' probabile ANCHE SE una scala fosse
    nettamente migliore.

    Il profit factor invece esiste per ogni candidata: se una scala e' migliore la
    distribuzione si sposta, e con 120 misure lo si vede."""
    st = probe._statistiche([0.5, 1.2, 0.9, 1.4, 1.0], passate=0, quasi=1)
    assert st["n"] == 5
    assert st["pf_mediano"] == 1.0
    assert st["quota_pf1"] == 0.6
    src = inspect.getsource(probe.main)
    assert "pf_mediano" in src, "la lettura deve basarsi sulla distribuzione"


def test_zero_passes_everywhere_does_not_become_a_conclusion():
    """La conclusione si trae dal PF mediano. Se si guardassero i passaggi, «0 contro
    0» diventerebbe «cambiare timeframe non serve» — una sentenza tratta dal nulla,
    che e' esattamente l'errore che questa sonda esiste per non fare."""
    src = inspect.getsource(probe.main)
    i = src.index("COME SI LEGGE")
    coda = src[i:]
    assert "d_sco = sco[\"pf_mediano\"]" in coda
    assert "Zero non sarebbe una risposta" in src
