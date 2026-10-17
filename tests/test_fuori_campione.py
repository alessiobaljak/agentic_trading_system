"""H5, 30 set 2026: IL FUORI CAMPIONE — il motore dopo la validazione contro il paper.

Il confronto «PERIODO DEL PAPER» (simulato contro paper dal 16 set) misura
anche la SELEZIONE: sugli stessi giorni 16-24 set il simulato faceva -1.357 con
le coppie del 25 set (ops 0232) e +8.465 con quelle del 30 (ops 0359). La
sezione nuova del `portafoglio` guarda solo i trade del motore entrati DOPO la
validazione di ogni coppia, accanto ai trade del paper sulle stesse coppie e
dagli stessi istanti. Qui si proteggono i conti puri (da quando si conta, cosa
si esclude, R, errore standard, le tre letture della regola, le coppie
rimosse), il main con un client finto e la lunghezza dell'output (l'agente ops
taglia oltre 20.000 caratteri).

Revisione del 30 set 2026 (prima della prima lettura): le coppie senza data
partono dal 25 set 12:00 UTC e non dal 21 (le generate promosse dalla discovery
non avevano la data fino al commit 425d808); nessun verdetto sotto 80 trade del
motore; il paper tagliato alla fine dei dati del motore; «stessi segnali» e
«non aperti» a parte; il bias (b) contato; la riga del periodo del paper che
non conclude piu' nemmeno col simulato in perdita.
"""
import argparse
import datetime as dt
import math
import time

from scripts import portafoglio_backtest as pb


def _ts(y, m, d, h=0):
    return dt.datetime(y, m, d, h, tzinfo=dt.timezone.utc).timestamp()


PAV = _ts(2026, 9, 16)            # inizio del paper
V_A = _ts(2026, 9, 25, 12)        # validazione della coppia A
AZZ = _ts(2026, 9, 27, 3)         # l'azzeramento della sessione (J13)


def _m(sym, strat, entry, pnl_pct=0.01, stop_pct=0.01, mfe=1.0, fine=False, scala=None):
    """Un trade del motore come lo scrive `trade_in_dict`."""
    return {"symbol": sym, "strategy": strat, "direction": "long", "entry_ts": entry,
            "bars_held": 4, "pnl_pct": pnl_pct, "stop_pct": stop_pct, "mfe_r": mfe,
            "scale_r_mults": scala, "fine_dati": fine}


def _p(sym, strat, entry, pnl=-1.0, mfe=0.5, **extra):
    """Un trade del paper come sta su Firestore: entry 100, stop originale 99,
    size 1 -> rischio 1 USDT, quindi R = pnl."""
    t = {"symbol": sym, "strategy": strat, "direction": "long",
         "entry_time": dt.datetime.fromtimestamp(entry, dt.timezone.utc).isoformat(),
         "exit_ts": entry + 3600, "entry_price": 100.0, "orig_stop": 99.0, "size": 1.0,
         "pnl": pnl, "mfe_r": mfe, "exit_reason": "stop_loss"}
    t.update(extra)
    return t


# --------------------------------------------------------------------------- #
# da quando si conta                                                          #
# --------------------------------------------------------------------------- #
def test_inizio_dalla_validazione_o_dal_25_set():
    assert pb.inizio_fuori_campione({"validated_at": V_A}, PAV) == (V_A, "validated_at")
    # senza data -> 25 set 12:00 UTC: fino al commit 425d808 (arrivato sulla
    # macchina il 25 set alle 08:33 UTC) la discovery promuoveva le generate
    # senza scrivere la data, non solo prima del 21 set
    assert pb.inizio_fuori_campione({}, PAV) == (_ts(2026, 9, 25, 12), "senza_data")
    assert pb.VALIDATED_AT_DAL == _ts(2026, 9, 25, 12)
    # mai prima del pavimento (inizio del paper, o del run se parte dopo)
    assert pb.inizio_fuori_campione({"validated_at": _ts(2026, 9, 10)}, PAV)[0] == PAV
    assert pb.inizio_fuori_campione({}, _ts(2026, 9, 28))[0] == _ts(2026, 9, 28)
    # un campo illeggibile vale «senza data», non un errore
    assert pb.inizio_fuori_campione({"validated_at": "boh"}, PAV)[1] == "senza_data"


def test_generata_promossa_il_24_sera_senza_data_non_conta_i_giorni_del_gate():
    """Il caso della revisione: promossa la sera del 24 set dalla discovery,
    quindi senza data. Col pavimento al 21 set tre trade del motore del 22-24 set
    (dentro i dati che l'hanno promossa, quando il paper non poteva ancora
    operarla) entravano come fuori campione: con un'esecuzione perfetta la
    differenza veniva +0,41R. Dal 25 set 12:00 e' zero."""
    rec = {"pass_count": 3, "generated": True}
    motore = [_m("X", "gen_a", _ts(2026, 9, d, 10), pnl_pct=0.011) for d in (22, 23, 24)]
    rs = [0.3, -1.0, 0.5, -1.0, 0.4, -0.2]
    ingressi = [_ts(2026, 9, 26 + i // 2, 6 + i) for i in range(len(rs))]
    motore += [_m("X", "gen_a", e, pnl_pct=0.01 * r) for e, r in zip(ingressi, rs)]
    paper = [_p("X", "gen_a", e + 905, pnl=r) for e, r in zip(ingressi, rs)]
    fc = pb.fuori_campione(motore, paper, {"X|gen_a": rec}, ["X|gen_a"], PAV)
    assert fc["senza_data"] == 1 and fc["motore"]["n"] == 6
    assert math.isclose(fc["differenza"], 0.0, abs_tol=1e-9)


def test_inizio_delle_azzerate_dal_ritorno_fra_le_validate():
    """Azzerata il 27 e rivalidata dopo: si conta dalla nuova validazione.
    Con `validated_at` vecchio (o assente) non si sa quando e' tornata: fuori."""
    rivalidata = {"validated_at": AZZ + 86400, "sessione_azzerata_at": AZZ}
    assert pb.inizio_fuori_campione(rivalidata, PAV) == (AZZ + 86400, "validated_at")
    vecchia = {"validated_at": _ts(2026, 9, 22), "sessione_azzerata_at": AZZ}
    assert pb.inizio_fuori_campione(vecchia, PAV) == (None, "azzerata_senza_data")
    assert pb.inizio_fuori_campione({"sessione_azzerata_at": AZZ}, PAV)[0] is None


def test_filtro_per_data_di_validazione_sui_due_lati():
    pairs = {"A|g1": {"validated_at": V_A}, "B|g2": {}}
    motore = [_m("A", "g1", V_A - 60),                 # prima della validazione: fuori
              _m("A", "g1", V_A + 60, pnl_pct=0.02),   # +2R
              _m("B", "g2", _ts(2026, 9, 22)),         # senza data, prima del 25 12:00: fuori
              _m("B", "g2", _ts(2026, 9, 26), pnl_pct=-0.01)]   # -1R
    paper = [_p("A", "g1", V_A - 60, pnl=5.0),         # prima: fuori
             _p("A", "g1", V_A + 120, pnl=-1.0),
             _p("B", "g2", _ts(2026, 9, 25, 11), pnl=9.0),   # prima del 25 12:00: fuori
             _p("B", "g2", _ts(2026, 9, 25, 13), pnl=0.5)]
    fc = pb.fuori_campione(motore, paper, pairs, ["A|g1", "B|g2"], PAV)
    assert fc["motore"]["n"] == 2 and math.isclose(fc["motore"]["r_medio"], 0.5)
    assert fc["paper"]["n"] == 2 and math.isclose(fc["paper"]["r_medio"], -0.25)
    assert math.isclose(fc["differenza"], 0.75)
    assert fc["coppie_con_motore"] == 2 and fc["coppie_con_paper"] == 2
    assert fc["senza_data"] == 1 and fc["con_data"] == 1


def test_solo_le_coppie_confrontate():
    """Una coppia non validata-e-simulata non ha un lato di fronte: fuori da
    tutti e due, anche se ha trade."""
    pairs = {"A|g1": {"validated_at": V_A}, "Z|gz": {"validated_at": V_A}}
    fc = pb.fuori_campione([_m("Z", "gz", V_A + 60)], [_p("Z", "gz", V_A + 60)],
                           pairs, ["A|g1"], PAV)
    assert fc["motore"]["n"] == 0 and fc["paper"]["n"] == 0


# --------------------------------------------------------------------------- #
# cosa si esclude, e si conta                                                  #
# --------------------------------------------------------------------------- #
def test_esclusioni_del_paper_contate():
    pairs = {"A|g1": {"validated_at": V_A}}
    t = V_A + 600
    paper = [_p("A", "g1", t, esplorativa=True),
             _p("A", "g1", t, exit_reason="manual"),
             _p("A", "g1", t, exit_reason="kill_switch"),
             _p("A", "g1", t, exit_reason="circuit_breaker"),
             _p("A", "g1", t, orig_stop=None),            # senza stop: niente R
             _p("A", "g1", t, pnl=2.0, exit_reason="take_profit"),
             {"symbol": "A", "strategy": "g1", "pnl": 3.0}]   # senza ingresso: fuori
    fc = pb.fuori_campione([], paper, pairs, ["A|g1"], PAV)
    assert fc["paper_esplorativi"] == 1
    assert fc["paper_uscite_esterne"] == 3
    assert fc["paper_senza_r"] == 1
    assert fc["paper"]["n"] == 1 and math.isclose(fc["paper"]["r_medio"], 2.0)


def test_esclusioni_del_motore_contate():
    pairs = {"A|g1": {"validated_at": V_A}}
    t = V_A + 600
    motore = [_m("A", "g1", t, fine=True),                # ancora aperto a fine dati
              _m("A", "g1", t, stop_pct=None),             # senza stop
              _m("A", "g1", t, pnl_pct=-0.005, stop_pct=0.01)]
    fc = pb.fuori_campione(motore, None, pairs, ["A|g1"], PAV)
    assert fc["motore_fine_dati"] == 1 and fc["motore_senza_stop"] == 1
    assert fc["motore"]["n"] == 1 and math.isclose(fc["motore"]["r_medio"], -0.5)
    # paper non leggibile: nessun lato, nessuna differenza, nessun giudizio
    assert fc["paper"] is None and fc["differenza"] is None
    assert fc["lettura"].startswith("non si decide: il paper non e' leggibile")


def test_azzerate_contate_ed_escluse():
    pairs = {"A|g1": {"validated_at": AZZ + 3600, "sessione_azzerata_at": AZZ},
             "B|g2": {"validated_at": _ts(2026, 9, 22), "sessione_azzerata_at": AZZ}}
    motore = [_m("A", "g1", AZZ + 7200), _m("B", "g2", AZZ + 7200)]
    paper = [_p("A", "g1", AZZ + 7200), _p("B", "g2", AZZ + 7200)]
    fc = pb.fuori_campione(motore, paper, pairs, list(pairs), PAV)
    assert fc["azzerate_contate"] == 1 and fc["azzerate_escluse"] == 1
    assert fc["motore"]["n"] == 1 and fc["paper"]["n"] == 1


# --------------------------------------------------------------------------- #
# R, mfe, primo gradino, errore standard                                      #
# --------------------------------------------------------------------------- #
def test_statistiche_lato_e_primo_gradino_con_la_stessa_regola():
    """mfe mediana e «tocca TP1» con `drift.tocca_tp1` su tutti e due i lati:
    la scala del trade se c'e', altrimenti quella globale."""
    pairs = {"A|g1": {"validated_at": V_A}}
    t = V_A + 600
    # tre candele diverse: sulla stessa candela sarebbero UN segnale (pacchetto A)
    motore = [_m("A", "g1", t, pnl_pct=0.02, mfe=2.5, scala=[2.0, 4.0]),
              _m("A", "g1", t + 900, pnl_pct=-0.01, mfe=1.5, scala=[2.0, 4.0]),
              _m("A", "g1", t + 1800, pnl_pct=0.01, mfe=0.2, scala=[2.0, 4.0])]
    paper = [_p("A", "g1", t, pnl=1.0, mfe=2.1, scale_r_mults=[2.0]),
             _p("A", "g1", t, pnl=-1.0, mfe=0.4, scale_r_mults=[2.0])]
    fc = pb.fuori_campione(motore, paper, pairs, ["A|g1"], PAV)
    m, p = fc["motore"], fc["paper"]
    assert math.isclose(m["vinti"], 2 / 3) and math.isclose(m["mfe_mediana"], 1.5)
    assert math.isclose(m["tocca_tp1"], 1 / 3)
    assert math.isclose(p["vinti"], 0.5) and math.isclose(p["tocca_tp1"], 0.5)
    assert math.isclose(p["mfe_mediana"], 1.25)


def test_errore_standard_della_differenza():
    a = pb.statistiche_lato([(1.0, None, None), (-1.0, None, None)])        # sd = sqrt(2)
    b = pb.statistiche_lato([(0.0, None, None), (2.0, None, None),
                             (4.0, None, None), (6.0, None, None)])         # sd^2 = 20/3
    es = pb.errore_standard_differenza(a, b)
    assert math.isclose(es, math.sqrt(2 / 2 + (20 / 3) / 4))
    # meno di 2 trade su un lato: nessun errore (non si inventa)
    uno = pb.statistiche_lato([(1.0, None, None)])
    assert pb.errore_standard_differenza(uno, b) is None
    assert pb.errore_standard_differenza(a, None) is None
    assert pb.statistiche_lato([])["r_medio"] is None


def test_trade_che_servono():
    # differenza 0,2 con 2 e.s. = 0,4: serve 4 volte il campione
    assert pb.trade_che_servono(100, 0.2, 0.2) == 400
    assert pb.trade_che_servono(100, 0.0, 0.2) is None
    assert pb.trade_che_servono(100, -0.1, 0.2) is None
    assert pb.trade_che_servono(100, 0.2, None) is None


# --------------------------------------------------------------------------- #
# le letture della regola (30 set, riviste prima della prima lettura; pacchetto  #
# A dello stesso giorno: selezione sul motore, esecuzione sugli stessi segnali)  #
# --------------------------------------------------------------------------- #
def _lato(valori, giorni=10):
    """Un lato con il margine per giornata: i valori sparsi su `giorni` giornate
    a rotazione (nessun effetto di giornata: margine per giornata ~ trade per trade)."""
    s = pb.statistiche_lato([(v, None, None) for v in valori])
    es = s["dev_std"] / math.sqrt(s["n"]) if s["dev_std"] is not None else None
    s["errore_giorno"] = pb.errore_standard_per_giorno(
        [(v, f"g{i % giorni}") for i, v in enumerate(valori)])
    s["errore_regola"] = pb.errore_regola(es, s["errore_giorno"])
    return s


def _accoppiati(motore, paper, giorni=10):
    coppie = list(zip(motore, paper))
    return pb.statistiche_abbinate(coppie, [f"g{i % giorni}" for i in range(len(coppie))])


def test_lettura_selezione_nessun_verdetto_sotto_80_segnali():
    """Il caso della revisione: con 2 trade a -0,01R la riga scriveva come un
    fatto «il divario e' la selezione del gate». Sotto 80 segnali non si decide."""
    assert pb.MIN_TRADE_MOTORE == 80
    testo = pb.lettura_selezione(_lato([-0.01, 0.0]))
    assert testo.startswith("non si decide: il motore ha solo 2 segnali")
    assert "almeno 80" in testo
    assert pb.lettura_selezione(_lato([-1.0, -1.1] * 39)).startswith(
        "non si decide: il motore ha solo 78 segnali")


def test_lettura_selezione_se_il_motore_non_guadagna():
    testo = pb.lettura_selezione(_lato([0.5, -0.5, -0.2, 0.1] * 20))
    assert testo.startswith("la promessa non regge dopo la validazione")
    # l'azione della regola, e il limite detto: gate o mercato, da qui non si separano
    assert "va nel gate" in testo and "il mercato e' cambiato" in testo
    assert "per giornata" in testo and "su 80 segnali" in testo
    # R medio esattamente 0 e' selezione (<= 0)
    assert pb.lettura_selezione(_lato([1.0, -1.0] * 40)).startswith("la promessa non regge")
    assert "nessun verdetto contro il gate" in pb.lettura_selezione(_lato([1.0, -0.5] * 40))


def test_lettura_esecuzione_solo_con_30_accoppiati():
    """Pacchetto A: il verdetto «esecuzione» esce solo dalla riga «stessi
    segnali» e solo con almeno 30 accoppiati. Con 29, anche un divario enorme
    non decide; con 30 si'."""
    assert pb.MIN_ACCOPPIATI == 30
    m29, p29 = [1.0, 0.8, 1.2] * 9 + [1.0, 0.9], [-1.0, -0.8, -1.2] * 9 + [-1.0, -0.9]
    testo = pb.lettura_esecuzione(_accoppiati(m29, p29))
    assert testo == "non si decide: 29 accoppiati, ne servono 30."
    testo = pb.lettura_esecuzione(_accoppiati(m29 + [1.1], p29 + [-1.1]))
    assert testo.startswith("e' esecuzione: sugli stessi segnali il paper rende meno")
    assert "ingressi e uscite" in testo and "per giornata" in testo
    assert pb.lettura_esecuzione(None).startswith("non si decide: 0 accoppiati")


def test_lettura_esecuzione_gli_altri_esiti():
    # il paper non fa peggio del motore sugli stessi segnali
    assert pb.lettura_esecuzione(_accoppiati([0.5] * 40, [0.6] * 40)).startswith(
        "non e' esecuzione")
    # dispersione zero e differenza nulla: 0 >= 2 x 0, ma non c'e' nessun divario
    assert pb.lettura_esecuzione(_accoppiati([1.0] * 40, [1.0] * 40)).startswith(
        "non e' esecuzione")
    # dentro il margine: quanti accoppiati servirebbero
    m = [2.0, -1.0, 1.5, 0.3] * 10
    p = [1.0, -1.2, 0.2, 1.3] * 10
    testo = pb.lettura_esecuzione(_accoppiati(m, p))
    assert testo.startswith("non si decide: la differenza sta dentro il margine")
    assert "servono circa" in testo
    # quasi uguale: niente numeri assurdi («serve ~6588812 trade»)
    testo = pb.lettura_esecuzione(_accoppiati([0.9, -0.9, 0.004] * 12, [0.0, 0.9, -0.9] * 12))
    assert "quasi uguale" in testo and "servono circa" not in testo
    # tutti in una giornata: il margine per giornata non esiste, niente verdetto
    ss = _accoppiati([1.0, 0.8] * 20, [-1.0, -0.8] * 20, giorni=1)
    assert ss["errore_giorno"] is None and ss["errore_regola"] is None
    assert "2 giornate" in pb.lettura_esecuzione(ss)


def test_lettura_completa_dice_tutte_e_due_e_la_media_di_tutti_non_decide():
    """Il caso della revisione: la media di tutti i trade mostra un divario
    oltre il margine (il paper ha preso i segnali peggiori), ma sugli stessi
    segnali il paper esegue come il motore: prima era «esecuzione», ora no."""
    m = _lato([1.0, 0.8, 1.2, 0.9, 1.1] * 16)
    p = _lato([-1.0, -0.8, -1.2, -0.9, -1.1] * 8)
    ss = _accoppiati([0.1, -0.2, 0.3] * 12, [0.1, -0.2, 0.3] * 12)
    testo = pb.lettura_fuori_campione(m, p, ss)
    assert testo.startswith("Selezione: il motore guadagna ancora")
    assert "Esecuzione: non e' esecuzione" in testo and "14 ott" in testo
    # motore <= 0 E paper peggio sugli stessi segnali: tutte e due
    testo = pb.lettura_fuori_campione(_lato([0.5, -0.5] * 50), p,
                                      _accoppiati([1.0, 0.8] * 20, [-1.0, -0.8] * 20))
    assert "la promessa non regge" in testo and "e' esecuzione" in testo
    assert pb.lettura_fuori_campione(m, None, ss).startswith(
        "non si decide: il paper non e' leggibile")


def test_r_vicino_a_zero_con_tre_decimali():
    """Un motore a +0,001R si stampava «+0.00» e sembrava «<= 0» per la regola."""
    assert pb._fmt_r(0.00133) == "+0.001" and pb._fmt_r(-0.004) == "-0.004"
    assert pb._fmt_r(0.0) == "+0.00" and pb._fmt_r(0.25) == "+0.25"
    assert pb._fmt_r(None) == "n.d."


# --------------------------------------------------------------------------- #
# la fine dei dati, gli stessi segnali, il bias (b) contato                    #
# --------------------------------------------------------------------------- #
def test_paper_tagliato_alla_fine_dei_dati_del_motore():
    """Le candele del motore arrivano alla mezzanotte UTC del run; il paper
    contava anche le ore dopo. Ora si ferma li', e lo conta."""
    fine = _ts(2026, 10, 1)
    pairs = {"C|g3": {"validated_at": _ts(2026, 9, 28)}}
    motore = [_m("C", "g3", _ts(2026, 9, 30, 20)),
              _m("C", "g3", _ts(2026, 9, 30, 23), fine=True)]          # ancora aperto
    esce_dopo = _p("C", "g3", _ts(2026, 9, 30, 22), pnl=-1.0)
    esce_dopo["exit_ts"] = _ts(2026, 10, 1, 1)
    paper = [_p("C", "g3", _ts(2026, 9, 30, 20) + 905, pnl=1.0),      # dentro
             esce_dopo,                                               # uscito dopo
             _p("C", "g3", _ts(2026, 10, 1, 2), pnl=-1.0)]            # entrato dopo
    fc = pb.fuori_campione(motore, paper, pairs, list(pairs), PAV, fine=fine)
    assert fc["paper"]["n"] == 1 and fc["paper_oltre_fine"] == 2
    assert fc["motore"]["n"] == 1 and fc["motore_fine_dati"] == 1
    # senza `fine` (chi chiama alla vecchia maniera) nessun taglio
    assert pb.fuori_campione(motore, paper, pairs, list(pairs), PAV)["paper"]["n"] == 3


def test_stessi_segnali_separano_esecuzione_e_segnali_scelti():
    """Il caso della revisione: esecuzione PERFETTA (ogni trade del paper e' il
    trade del motore sullo stesso segnale), ma il paper prende pochi segnali
    della coppia buona e quasi tutti della debole. La differenza non accoppiata
    c'e'; sugli stessi segnali e' zero, e cio' che manca sta nei «non aperti»."""
    pairs = {"A|ga": {"validated_at": PAV}, "B|gb": {"validated_at": PAV}}
    motore, paper = [], []
    for i in range(100):
        e = PAV + 86400 + i * 7200
        for sym, strat, r, prende in (("A", "ga", 0.5 if i % 2 else 0.3, i % 5 == 0),
                                      ("B", "gb", -0.1 if i % 2 else -0.3, i % 5 != 0)):
            motore.append(_m(sym, strat, e, pnl_pct=0.01 * r))
            if prende:
                paper.append(_p(sym, strat, e + 905, pnl=r))   # entra alla barra dopo
    fc = pb.fuori_campione(motore, paper, pairs, list(pairs), PAV)
    ss, na = fc["stessi_segnali"], fc["motore_non_aperti"]
    assert fc["differenza"] > 0.15                      # non accoppiato: sembra esecuzione
    assert ss["n"] == len(paper) == 100 and fc["paper_senza_segnale"] == 0
    assert math.isclose(ss["differenza"], 0.0, abs_tol=1e-9)
    assert na["n"] == 100 and math.isclose(na["r_medio"], 0.28)
    # un trade del paper senza un segnale del motore vicino si conta a parte
    paper.append(_p("A", "ga", PAV + 86400 + 3600 * 3 + 905, pnl=-1.0))
    fc = pb.fuori_campione(motore, paper, pairs, list(pairs), PAV)
    assert fc["paper_senza_segnale"] == 1 and fc["stessi_segnali"]["n"] == 100


def test_abbina_segnali_un_trade_del_motore_una_volta_sola():
    righe = {"A|g": [[1000.0, 1.0, False], [1900.0, 2.0, False]]}
    abbinati, senza = pb.abbina_segnali(righe, [("A|g", 1905.0, 0.5), ("A|g", 1910.0, 0.4),
                                               ("A|g", 1915.0, 0.3)], tol=1800.0)
    # il primo prende il piu' vicino (1900), il secondo quello rimasto, il terzo niente
    assert abbinati == [(2.0, 0.5), (1.0, 0.4)] and senza == 1
    assert all(r[2] for r in righe["A|g"])
    assert pb.statistiche_abbinate([])["differenza"] is None
    s = pb.statistiche_abbinate([(1.0, 0.0), (2.0, 0.0)])
    assert math.isclose(s["differenza"], 1.5) and math.isclose(s["errore_standard"], 0.5)


def test_bias_b_config_diversa(monkeypatch):
    monkeypatch.setattr(pb.settings, "SCALE_OUT_ENABLED", True)
    oggi = {"scale_r_mults": [2.0, 4.0, 6.0], "sl_to_breakeven": False, "profit_lock_keep": 0.6}
    uguale = {"scale_r_mults": [2.0, 4.0, 6.0], "sl_to_breakeven": False, "profit_lock_keep": 0.6}
    assert pb.config_diversa(uguale, oggi) is False
    assert pb.config_diversa({"scale_r_mults": [1.5, 3.0, 5.0]}, oggi) is True   # scala riscelta
    assert pb.config_diversa({"sl_to_breakeven": True}, oggi) is True
    assert pb.config_diversa({"profit_lock_keep": 0.5}, oggi) is True
    # None = la globale, sui due lati
    assert pb.config_diversa({"scale_r_mults": None, "sl_to_breakeven": None}, {}) is False
    # trade vecchio senza i campi: «non lo so», non «uguale»
    assert pb.config_diversa({"pnl": 1.0}, oggi) is None
    # scale-out spento: scala e break-even non cambiano niente
    monkeypatch.setattr(pb.settings, "SCALE_OUT_ENABLED", False)
    assert pb.config_diversa({"scale_r_mults": [1.5, 3.0, 5.0]}, oggi) is None


def test_bias_b_contato_nel_confronto(monkeypatch):
    monkeypatch.setattr(pb.settings, "SCALE_OUT_ENABLED", False)
    pairs = {"A|g1": {"validated_at": V_A, "last_params": {"profit_lock_keep": 0.6}}}
    t = V_A + 600
    paper = [_p("A", "g1", t, pnl=-1.0, profit_lock_keep=0.5),     # keep diverso da oggi
             _p("A", "g1", t, pnl=1.0, profit_lock_keep=0.6),
             _p("A", "g1", t, pnl=0.5)]                             # senza il campo
    fc = pb.fuori_campione([], paper, pairs, ["A|g1"], PAV)
    assert fc["paper_config_note"] == 2 and fc["paper_config_diverse"] == 1
    assert math.isclose(fc["paper_r_senza_config_diverse"], 0.75)


# --------------------------------------------------------------------------- #
# bias (a): le rimosse e il paper che il motore non vede                      #
# --------------------------------------------------------------------------- #
def test_rimosse_dal_diario():
    diario = {"events": [{"tipo": "rimossa", "at": PAV + 10},
                         {"tipo": "rimossa", "at": PAV - 10},       # prima del paper
                         {"tipo": "promossa", "at": PAV + 10},
                         "rotto"]}
    assert pb.rimosse_dal(diario, PAV) == 1
    # la lista puo' arrivare come stringa JSON: si legge lo stesso
    import json
    assert pb.rimosse_dal({"events": json.dumps(diario["events"][:2])}, PAV) == 1
    # diario assente o illeggibile: «non lo so», non zero
    assert pb.rimosse_dal(None, PAV) is None
    assert pb.rimosse_dal({"events": "{non json"}, PAV) is None
    assert pb.rimosse_dal({}, PAV) is None


def test_paper_fuori_registro():
    t = _ts(2026, 9, 20)
    paper = [_p("OLD", "g9", t, pnl=-1.0), _p("OLD", "g9", t, pnl=-0.5),
             _p("OLD2", "g8", t, pnl=1.0),
             _p("OLD", "g9", t, esplorativa=True),                # esplorativo: fuori
             _p("OLD", "g9", t, exit_reason="manual"),            # esterna: fuori
             _p("OLD", "g9", PAV - 3600),                          # prima del paper
             _p("OLD", "g9", t, orig_stop=None),                  # senza R: contato
             _p("A", "g1", t, pnl=5.0)]                            # validata oggi
    out = pb.paper_fuori_registro(paper, ["A|g1"], PAV)
    assert out["n"] == 3 and out["coppie"] == 2 and out["senza_r"] == 1
    assert math.isclose(out["r_medio"], -0.5 / 3)
    assert pb.paper_fuori_registro(None, [], PAV) is None


def test_diario_vite_una_lettura_fail_open():
    class _Fb:
        def __init__(self):
            self.chiamate = []

        def get_doc(self, coll, doc):
            self.chiamate.append((coll, doc))
            return {"events": []}

    fb = _Fb()
    assert pb._diario_vite(fb) == {"events": []}
    assert fb.chiamate == [("gate_history", "lifecycle")]

    class _Rotto:
        def get_doc(self, *a):
            raise RuntimeError("firestore giu'")

    assert pb._diario_vite(_Rotto()) is None
    assert pb._diario_vite(object()) is None      # client finto senza get_doc


# --------------------------------------------------------------------------- #
# trade_in_dict e trades_della_coin portano cio' che serve                     #
# --------------------------------------------------------------------------- #
class _Sim:
    def __init__(self, entry_ts, bars=4, pnl_pct=0.01, mfe_r=1.2):
        self.entry_ts, self.bars_held, self.pnl_pct, self.mfe_r = entry_ts, bars, pnl_pct, mfe_r
        self.direction = "long"
        self.feats = {"stop_pct": 0.01}


def test_trade_in_dict_campi_nuovi():
    d = pb.trade_in_dict(_Sim(1000.0, bars=4), "A", "g1", scala=(2.0, 4.0),
                         fine_ts=1000.0 + 4 * 900, secondi_barra=900.0)
    assert d["mfe_r"] == 1.2 and d["scale_r_mults"] == [2.0, 4.0] and d["fine_dati"] is True
    d = pb.trade_in_dict(_Sim(1000.0, bars=3), "A", "g1", fine_ts=1000.0 + 4 * 900,
                         secondi_barra=900.0)
    assert d["fine_dati"] is False and d["scale_r_mults"] is None
    # la firma vecchia regge: senza fine dati nessun trade e' «aperto»
    assert pb.trade_in_dict(_Sim(1000.0), "A", "g1")["fine_dati"] is False


def test_trades_della_coin_passa_scala_e_fine_dati(monkeypatch):
    class _C:
        def __init__(self, ts):
            self.open_time = dt.datetime.fromtimestamp(ts, dt.timezone.utc)

    t0 = 1_700_000_000.0
    candele = [_C(t0 + i * 900) for i in range(pb.MIN_CANDELE + 10)]
    ultimo = t0 + (len(candele) - 1) * 900

    class _G:
        def __init__(self, spec):
            self.params = {}

    class _Bt:
        def run_strategy(self, g, symbol, candles, frame=None):
            class _St:
                trades = [_Sim(ultimo - 10 * 900, bars=3), _Sim(ultimo - 2 * 900, bars=2)]
            return _St()

    monkeypatch.setattr(pb, "load_candles", lambda *a, **k: candele)
    monkeypatch.setattr(pb, "compute_indicator_frame", lambda c: None)
    monkeypatch.setattr(pb, "GeneratedStrategy", _G)
    args = argparse.Namespace(interval="15m", giorni=60, source="auto")
    rec = {"last_params": {"scale_r_mults": [2.0, 4.0, 6.0]}}
    tr, saltate, n = pb.trades_della_coin("A", [("gen_a", rec)], {"gen_a": {"timeframe": "15m"}},
                                          args, 0.0, _Bt())
    assert saltate == [] and n == len(candele)
    assert [t["fine_dati"] for t in tr] == [False, True]
    assert all(t["scale_r_mults"] == [2.0, 4.0, 6.0] for t in tr)


# --------------------------------------------------------------------------- #
# l'output: sotto ~3,8 KB (pacchetto A: +~0,7 KB), e il riepilogo per Firebase  #
# senza liste annidate                                                         #
# --------------------------------------------------------------------------- #
def _dati_grandi():
    """202 coppie, ~1.600 trade del motore e ~600 del paper, date di
    validazione su tre mesi: il caso piu' lungo da stampare."""
    pairs, motore, paper = {}, [], []
    for i in range(202):
        k = f"COIN{i:03d}USDT|gen_{i:05d}_abcdef"
        sym, strat = k.split("|")
        rec = {"pass_count": 5}
        if i % 3:
            rec["validated_at"] = _ts(2026, 9, 21) + (i % 90) * 86400
        if i % 17 == 0:
            rec["sessione_azzerata_at"] = AZZ
        pairs[k] = rec
        for j in range(8):
            motore.append(_m(sym, strat, _ts(2026, 12, 20) + j * 3600,
                             pnl_pct=0.01 * ((j % 3) - 1), fine=(j == 0 and i % 50 == 0)))
        for j in range(3):
            paper.append(_p(sym, strat, _ts(2026, 12, 20) + j * 3600, pnl=-0.3 * j,
                            esplorativa=(j == 2 and i % 10 == 0)))
    for j in range(40):
        paper.append(_p("VECCHIAUSDT", f"gen_old{j % 9}", _ts(2026, 9, 18)))
    diario = {"events": [{"tipo": "rimossa", "at": _ts(2026, 9, 20)}] * 15}
    return pairs, motore, paper, diario


def test_sezione_sotto_3800_caratteri_e_riepilogo_pubblicabile(capsys):
    """Prima del pacchetto A la sezione faceva ~2,9 KB su questi dati; ora ~3,7
    KB (+~0,7 KB: righe in segnali, margini per giornata, segnali presi, due
    righe di sopravvivenza, regole e tre letture). Il main compensa togliendo le
    righe «dati da cache» (~3,6 KB, ops 0371)."""
    pairs, motore, paper, diario = _dati_grandi()
    out = pb.sezione_fuori_campione(motore, paper, pairs, list(pairs), list(pairs),
                                    PAV, PAV, diario)
    testo = capsys.readouterr().out
    assert "FUORI CAMPIONE (H5)" in testo and "Lettura:" in testo
    assert pb.REGOLA_FUORI_CAMPIONE in testo
    assert "regola scritta il 30 set, prima delle letture" in testo
    assert pb.TRE_LETTURE in testo and "~7%" in testo
    assert "Domanda:" in testo and "stessi segnali" in testo and "segnali presi:" in testo
    assert "doppioni fusi" in testo and "per giornata" in testo
    assert "coppie ancora validate" in testo and "tutte le coppie operate" in testo
    assert "bias (b)" in testo
    assert "rimosse dal 2026-09-16: 15" in testo and "non piu' validate" in testo
    # niente nomi di campi o collezioni per chi legge dal telefono
    assert "validated_at" not in testo and "gate_history" not in testo
    assert "r_multiplo" not in testo and "e.s." not in testo
    # +0,5 KB il 30 set 2026 (H1-misura): la regola del voto t e la divisione
    # per t, approvate col tetto di mezzo KB in piu' sulla sezione
    assert len(testo) < 3800 + 800, len(testo)  # +300: la regola H1 decisa (30 set sera)
    # la distribuzione delle date non cresce coi mesi
    riga = next(r for r in testo.splitlines() if "senza data di validazione" in r)
    assert len(riga) < 200 and "fino al" in riga
    assert not pb.contiene_liste_annidate(out)
    assert out["rimosse_dal_inizio_paper"] == 15
    assert out["paper_fuori_registro"]["n"] == 40
    assert out["regola"] == pb.REGOLA_FUORI_CAMPIONE


# --------------------------------------------------------------------------- #
# main con un client finto                                                    #
# --------------------------------------------------------------------------- #
class _FbFinto:
    """Solo cio' che main usa: get_doc posizionale, is_live, set_doc."""

    def __init__(self, docs):
        self.docs = docs
        self.is_live = True
        self.scritti = {}

    def get_doc(self, coll, doc):
        return self.docs.get((coll, doc))

    def set_doc(self, coll, doc, data):
        self.scritti[(coll, doc)] = data


def doc_periodo(fb):
    return fb.scritti[("portfolio", "backtest")]["periodo_paper"]


def test_main_stampa_la_sezione_e_la_vecchia_lettura_non_conclude_piu(monkeypatch, capsys):
    ora = time.time()
    oggi = dt.datetime.fromtimestamp(ora, dt.timezone.utc).date()
    inizio_paper = oggi - dt.timedelta(days=10)
    monkeypatch.setattr(pb, "PAPER_START", inizio_paper.isoformat())
    v_a = ora - 5 * 86400
    pairs = {"AAAUSDT|gen_a": {"pass_count": 5, "last_seen_at": ora, "validated_at": v_a},
             "BBBUSDT|gen_b": {"pass_count": 5, "last_seen_at": ora}}
    diario = {"events": [{"tipo": "rimossa", "at": ora - 86400, "key": "X|y"}]}
    fb = _FbFinto({("strategy_registry", "validated"): {"pairs": pairs},
                   ("discovered_strategies", "specs"): {"specs": {}},
                   ("gate_history", "lifecycle"): diario})
    monkeypatch.setattr(pb, "get_firebase", lambda: fb)

    class _Wfo:
        def __init__(self, **kw):
            self.bt = None

    monkeypatch.setattr(pb, "WalkForwardOptimizer", _Wfo)

    def _trades(sym, strategie, specs, args, inizio_ts, bt):
        out = []
        for strat, _rec in strategie:
            for g in (7, 3, 2, 1):   # giorni fa: il simulato vince nel periodo del paper
                out.append(_m(sym, strat, ora - g * 86400, pnl_pct=0.02))
        return out, [], 6000

    monkeypatch.setattr(pb, "trades_della_coin", _trades)
    paper = [_p("AAAUSDT", "gen_a", ora - 3 * 86400, pnl=-1.0),
             _p("AAAUSDT", "gen_a", ora - 2 * 86400, pnl=-1.0),
             _p("AAAUSDT", "gen_a", ora - 7 * 86400, pnl=0.5),   # prima della validazione
             _p("BBBUSDT", "gen_b", ora - 1 * 86400, pnl=-0.5, esplorativa=True)]
    monkeypatch.setattr(pb, "_trade_paper", lambda fb_, dal_ts: paper)

    assert pb.main([]) == 0
    testo = capsys.readouterr().out
    assert "FUORI CAMPIONE (H5)" in testo
    # la sezione sta DOPO il periodo del paper e PRIMA della parte finale
    assert testo.index("PERIODO DEL PAPER") < testo.index("FUORI CAMPIONE (H5)") \
        < testo.index("win rate dopo k perdite")
    # simulato in utile e paper in perdita (-2,00): il caso in cui la riga
    # vecchia concludeva «esecuzione/parita', non il mercato»
    riga = next(r for r in testo.splitlines() if "Lettura: dal " in r)
    assert "non si sa se il divario e' esecuzione o selezione" in riga
    assert "non il mercato" not in riga and "FUORI CAMPIONE" in riga
    assert doc_periodo(fb)["paper_totale"] < 0 < doc_periodo(fb)["simulato_totale"]

    doc = fb.scritti[("portfolio", "backtest")]
    fc = doc["fuori_campione"]
    assert not pb.contiene_liste_annidate(doc)
    # motore: A dopo la validazione (3, 2, 1 giorni fa) + B dopo il 21 set /
    # l'inizio del paper (tutti e quattro se il paper e' iniziato dopo il 21 set)
    assert fc["motore"]["n"] >= 6 and math.isclose(fc["motore"]["r_medio"], 2.0)
    assert fc["paper"]["n"] == 2 and math.isclose(fc["paper"]["r_medio"], -1.0)
    assert fc["paper_esplorativi"] == 1
    assert fc["rimosse_dal_inizio_paper"] == 1
    assert fc["lettura"] and "periodo_paper" in doc
