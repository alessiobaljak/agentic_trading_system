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

    assert "QUASIUSDT" in scoperte, "due conferme non sono una moneta operabile"
    assert "ALTRAUSDT" in scoperte
    assert controllo == ["COPERTAUSDT"]


def test_the_same_candidates_are_used_on_every_timeframe():
    """Confrontare insiemi di strategie diversi non direbbe niente sul timeframe:
    la variabile dev'essere una sola. Le spec si generano UNA volta, fuori dal ciclo
    sulle scale."""
    src = inspect.getsource(probe.main)
    assert src.index("generate_specs(") < src.index("for tf in tfs:")
