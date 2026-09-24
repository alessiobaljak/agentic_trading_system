"""H5: LA MISURA CHE SEPARA «IL MERCATO E' CAMBIATO» DA «IL PAPER ESEGUE MALE».

24 settembre 2026. Il paper apre ~4,9 trade al giorno contro 8,6 simulati e
perde (PF 0,63) dove il gate prometteva 1,88. Due spiegazioni opposte danno lo
stesso sintomo, e finora nessuno strumento le distingueva. Le due misure:

  (a) `confronto`: i segnali del gate nel periodo del paper, divisi in APERTI
      dal paper (un trade del paper entro due barre) e NON APERTI. Se i non
      aperti rendono e gli aperti no, il difetto e' nel percorso live; se
      perdono tutti e due, il gate ha promesso su un regime che non c'e' piu'.
  (b) `portafoglio`: il PnL simulato giorno per giorno dal 16 set accanto al
      PnL del paper per giorno UTC di uscita.

Qui si proteggono i conti puri: l'abbinamento (tolleranza, un gate-trade usato
una volta sola, insiemi complementari), le metriche dei due gruppi, la lettura
nei tre casi, e il PnL del paper per giorno.
"""
import datetime as dt

from scripts import confronto_gate_paper as cgp
from scripts import portafoglio_backtest as pb


class _G:
    """Un trade del gate come lo produce il motore: oggetto, non dict."""

    def __init__(self, ts, pnl_pct=0.0, direction="long"):
        self.entry_ts = ts
        self.pnl_pct = pnl_pct
        self.direction = direction


def _p(ts):
    return {"entry_time": ts}


TF_15M = 0.25   # due barre = 1800 s


# --------------------------------------------------------------------------- #
# (a) abbina: aperti e non aperti                                             #
# --------------------------------------------------------------------------- #
def test_abbina_divide_aperti_e_non_aperti():
    gate = [_G(1000), _G(1500), _G(999_000)]
    aperti, non_aperti = cgp.abbina([_p(1000), _p(1100)], gate, TF_15M)
    assert aperti == {0, 1}
    assert non_aperti == {2}


def test_abbina_gli_insiemi_sono_disgiunti_e_complementari():
    gate = [_G(1000), _G(50_000), _G(100_000), _G(200_000)]
    aperti, non_aperti = cgp.abbina([_p(1000), _p(100_100)], gate, TF_15M)
    assert aperti & non_aperti == set()
    assert aperti | non_aperti == set(range(len(gate)))
    assert aperti == {0, 2}


def test_abbina_tolleranza_di_due_barre():
    """Il segnale nasce a barra chiusa e il bot esegue dopo: entro due barre
    e' lo stesso ingresso, a un secondo in piu' non lo e'."""
    dentro, _ = cgp.abbina([_p(1000)], [_G(1000 + 1800)], TF_15M)
    assert dentro == {0}
    fuori_ap, fuori_no = cgp.abbina([_p(1000)], [_G(1000 + 1801)], TF_15M)
    assert fuori_ap == set() and fuori_no == {0}


def test_abbina_un_gate_trade_si_usa_una_volta_sola():
    """Due trade del paper vicini a UN solo segnale del gate: uno dei due
    resta senza riscontro, e il segnale non viene contato «aperto» due volte."""
    aperti, non_aperti = cgp.abbina([_p(1000), _p(1100)], [_G(1000)], TF_15M)
    assert aperti == {0}
    assert non_aperti == set()


def test_abbina_sceglie_il_gate_trade_piu_vicino():
    aperti, _ = cgp.abbina([_p(1000)], [_G(1700), _G(1050), _G(400)], TF_15M)
    assert aperti == {1}


def test_abbina_e_pura_e_regge_le_liste_vuote():
    assert cgp.abbina([], [], TF_15M) == (set(), set())
    assert cgp.abbina([_p(1000)], [], TF_15M) == (set(), set())
    assert cgp.abbina([], [_G(1000)], TF_15M) == (set(), {0})
    # un paper senza entry_time leggibile non abbina niente
    assert cgp.abbina([{"entry_time": None}], [_G(1000)], TF_15M) == (set(), {0})


def test_abbina_e_parita_ingressi_contano_uguale():
    """Le due funzioni devono venire dallo stesso cuore: se divergessero, il
    report direbbe «3/4 ingressi combaciano» e «2 aperti» sulla stessa coppia."""
    gate = [_G(1000), _G(1500), _G(999_000)]
    paper = [_p(1000), _p(1100), _p(500_000)]
    aperti, _ = cgp.abbina(paper, gate, TF_15M)
    assert len(aperti) == cgp.parita_ingressi(paper, gate, TF_15M)["trovati"]


# --------------------------------------------------------------------------- #
# (a) metriche dei gruppi e lettura                                           #
# --------------------------------------------------------------------------- #
def test_metriche_gruppo():
    trades = [_G(1, 2.0, "long"), _G(2, -1.0, "short"), _G(3, 3.0, "long"), _G(4, -1.0, "long")]
    m = cgp.metriche_gruppo(trades)
    assert m["n"] == 4
    assert abs(m["pf"] - 2.5) < 1e-9          # 5 / 2
    assert abs(m["wr"] - 0.5) < 1e-9
    assert abs(m["pnl_medio"] - 0.75) < 1e-9
    assert m["long"] == 3 and m["short"] == 1


def test_metriche_gruppo_accetta_anche_dict():
    m = cgp.metriche_gruppo([{"pnl_pct": 1.0, "direction": "short"}, {"pnl_pct": -0.5}])
    assert m["n"] == 2 and abs(m["pf"] - 2.0) < 1e-9
    assert m["short"] == 1 and m["long"] == 1


def test_metriche_gruppo_vuoto_e_soli_vinti():
    """Un gruppo vuoto vale 0, non un errore. Un gruppo di soli vinti ha PF
    infinito: 0 lo farebbe sembrare perdente, che e' il contrario del vero."""
    v = cgp.metriche_gruppo([])
    assert v["n"] == 0 and v["pf"] == 0.0 and v["wr"] == 0.0 and v["pnl_medio"] == 0.0
    assert cgp.metriche_gruppo([_G(1, 1.0), _G(2, 0.5)])["pf"] == float("inf")


def _m(n, pf):
    return {"n": n, "pf": pf, "wr": 0.5, "pnl_medio": 0.0, "long": n, "short": 0}


def test_lettura_h5_i_tre_casi():
    assert cgp.lettura_h5(_m(10, 0.5), _m(20, 1.5)) == \
        "il difetto e' nel percorso live, non nel mercato"
    assert cgp.lettura_h5(_m(10, 0.5), _m(20, 0.6)) == \
        "il gate ha promesso su un regime che non c'e' piu'"
    assert cgp.lettura_h5(_m(10, 1.0), _m(20, 1.0)) == \
        "non distinguibile con questo campione"


def test_lettura_h5_ai_confini_delle_soglie():
    """Le soglie sono 0,8 e 1,2: sotto/sopra e' un giudizio, in mezzo e' rumore."""
    assert cgp.lettura_h5(_m(5, 0.79), _m(5, 1.2)).startswith("il difetto")
    assert cgp.lettura_h5(_m(5, 0.8), _m(5, 1.2)).startswith("non distinguibile")
    assert cgp.lettura_h5(_m(5, 0.79), _m(5, 1.19)).startswith("non distinguibile")
    assert cgp.lettura_h5(_m(5, 0.79), _m(5, 0.79)).startswith("il gate ha promesso")
    # aperti che rendono e non aperti che perdono: non e' nessuno dei due casi
    assert cgp.lettura_h5(_m(5, 1.5), _m(5, 0.5)).startswith("non distinguibile")


def test_lettura_h5_con_un_gruppo_vuoto_non_giudica():
    assert cgp.lettura_h5(_m(0, 0.0), _m(20, 1.5)).startswith("non distinguibile")
    assert cgp.lettura_h5(_m(10, 0.5), _m(0, 0.0)).startswith("non distinguibile")


def test_inizio_paper_prende_il_piu_vecchio_fra_data_e_trade():
    base = dt.datetime(2026, 9, 16, tzinfo=dt.timezone.utc).timestamp()
    assert cgp.inizio_paper([], "2026-09-16") == base
    # un trade del paper PRIMA della data vince
    prima = base - 3600
    assert cgp.inizio_paper([_p(prima), _p(base + 10)], "2026-09-16") == prima
    # un trade dopo la data non la sposta
    assert cgp.inizio_paper([_p(base + 10)], "2026-09-16") == base
    # data illeggibile: si ricade sui trade (fail-open)
    assert cgp.inizio_paper([_p(base + 10)], "boh") == base + 10


# --------------------------------------------------------------------------- #
# (b) il PnL del paper per giorno UTC di uscita                               #
# --------------------------------------------------------------------------- #
def _ts(y, m, d, h=0):
    return dt.datetime(y, m, d, h, tzinfo=dt.timezone.utc).timestamp()


def test_pnl_paper_per_giorno_somma_per_giorno_utc_di_uscita():
    trades = [
        {"exit_ts": _ts(2026, 9, 16, 10), "pnl": 1.5},
        {"exit_ts": _ts(2026, 9, 16, 23), "pnl": -2.0},
        {"exit_ts": _ts(2026, 9, 17, 0), "pnl": 3.25},
        # l'ingresso e' il 16 ma l'uscita il 18: conta il 18, come in `simula`
        {"entry_time": "2026-09-16T08:00:00+00:00", "exit_ts": _ts(2026, 9, 18, 1), "pnl": -1.0},
    ]
    assert pb.pnl_paper_per_giorno(trades) == {
        "2026-09-16": -0.5, "2026-09-17": 3.25, "2026-09-18": -1.0}


def test_pnl_paper_per_giorno_ricade_su_exit_time_iso_e_salta_i_trade_senza_data():
    trades = [
        {"exit_time": "2026-09-20T02:00:00+02:00", "pnl": 4.0},   # 00:00 UTC del 20
        {"exit_time": "2026-09-19T23:30:00", "pnl": 1.0},          # naive = UTC
        {"pnl": 99.0},                                             # senza data: fuori
        {"exit_ts": _ts(2026, 9, 19), "pnl": "non un numero"},     # pnl rotto: fuori
        {"exit_ts": _ts(2026, 9, 19), "pnl": None},                # None = 0
    ]
    assert pb.pnl_paper_per_giorno(trades) == {"2026-09-19": 1.0, "2026-09-20": 4.0}
    assert pb.pnl_paper_per_giorno([]) == {}


def test_lettura_periodo_paper_i_casi():
    assert "esecuzione/parita'" in pb.lettura_periodo_paper(50.0, -30.0, "2026-09-16")
    assert "e' il mercato" in pb.lettura_periodo_paper(-20.0, -30.0, "2026-09-16")
    assert "nessun divario" in pb.lettura_periodo_paper(50.0, 10.0, "2026-09-16")
    assert "non e' leggibile" in pb.lettura_periodo_paper(50.0, None, "2026-09-16")
    # l'avvertimento sulla selezione (holdout = ultimi 45 giorni) c'e' sempre
    for testo in (pb.lettura_periodo_paper(50.0, -30.0, "x"),
                  pb.lettura_periodo_paper(-1.0, -1.0, "x"),
                  pb.lettura_periodo_paper(5.0, 5.0, "x"),
                  pb.lettura_periodo_paper(5.0, None, "x")):
        assert "selezione" in testo


def test_sezione_periodo_paper_stampa_e_riassume(capsys):
    sim = {"pnl_per_giorno": {"2026-09-15": 9.0, "2026-09-16": 10.0,
                              "2026-09-17": -4.0, "2026-09-18": 0.0}}
    paper = [{"exit_ts": _ts(2026, 9, 16, 5), "pnl": -3.0},
             {"exit_ts": _ts(2026, 9, 18, 5), "pnl": -1.0}]
    out = pb.sezione_periodo_paper(sim, paper, dt.date(2026, 9, 16), dt.date(2026, 9, 18),
                                   dt.date(2026, 7, 1))
    assert out["giorni"] == 3
    assert out["simulato_totale"] == 6.0          # il 15 non conta
    assert out["paper_totale"] == -4.0
    assert out["giorni_utile"] == 1 and out["giorni_perdita"] == 1
    assert "esecuzione/parita'" in out["lettura"]
    assert not pb.contiene_liste_annidate(out)
    testo = capsys.readouterr().out
    assert "PERIODO DEL PAPER" in testo and "2026-09-17" in testo and "-4.00" in testo


def test_sezione_periodo_paper_senza_paper_e_con_run_corto(capsys):
    """Firebase assente: colonna «n.d.» e nessun giudizio. Run che parte dopo
    PAPER_START: si contano solo i giorni simulati, e lo si dice."""
    sim = {"pnl_per_giorno": {"2026-09-20": -2.0}}
    out = pb.sezione_periodo_paper(sim, None, dt.date(2026, 9, 16), dt.date(2026, 9, 21),
                                   dt.date(2026, 9, 20))
    assert out["dal"] == "2026-09-20" and out["giorni"] == 2
    assert out["paper_totale"] is None
    testo = capsys.readouterr().out
    assert "n.d." in testo and "dopo PAPER_START" in testo


def test_help_dei_due_script_funziona():
    """Le due voci sono in lista bianca: se argparse esce con 2, sono morte."""
    import subprocess
    import sys

    for mod in ("scripts.confronto_gate_paper", "scripts.portafoglio_backtest"):
        r = subprocess.run([sys.executable, "-m", mod, "--help"],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr[-500:]
