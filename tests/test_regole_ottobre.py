"""Pacchetto A, 30 set 2026: le regole delle letture del 3, 7 e 14 ottobre,
scritte PRIMA delle letture (si' del proprietario).

Qui si proteggono, su dati finti, i pezzi nuovi del FUORI CAMPIONE del
`portafoglio` e la regola del 3 ott in `trades`:
  * il verdetto «esecuzione» solo sugli stessi segnali e con almeno 30 accoppiati;
  * i doppioni del motore (stessa moneta, candela, direzione) contati una volta;
  * il margine per giornata, con un effetto di giornata comune;
  * i segnali presi dal paper accanto a quelli del portafoglio del motore;
  * la sopravvivenza: coppie uscite dal registro rigiocate fino all'uscita;
  * la regola del 3 ott nei tre esiti;
  * il main con un client finto (coppia rimossa rigiocata, righe «dati da cache»
    contate e non stampate) e la dimensione dell'output.
"""
import datetime as dt
import math
import random
import time

from scripts import portafoglio_backtest as pb
from scripts import trade_stats as ts


def _ts(y, m, d, h=0, mi=0):
    return dt.datetime(y, m, d, h, mi, tzinfo=dt.timezone.utc).timestamp()


PAV = _ts(2026, 9, 16)
V = _ts(2026, 9, 26, 12)


def _m(sym, strat, entry, pnl_pct=0.01, stop_pct=0.01, mfe=1.0, direction="long", bars=4):
    return {"symbol": sym, "strategy": strat, "direction": direction, "entry_ts": entry,
            "bars_held": bars, "pnl_pct": pnl_pct, "stop_pct": stop_pct, "mfe_r": mfe,
            "scale_r_mults": None, "fine_dati": False}


def _p(sym, strat, entry, pnl=-1.0, mfe=0.5, **extra):
    """Trade del paper: entry 100, stop originale 99, size 1 -> R = pnl."""
    t = {"symbol": sym, "strategy": strat, "direction": "long",
         "entry_time": dt.datetime.fromtimestamp(entry, dt.timezone.utc).isoformat(),
         "exit_ts": entry + 3600, "entry_price": 100.0, "orig_stop": 99.0, "size": 1.0,
         "pnl": pnl, "mfe_r": mfe, "exit_reason": "stop_loss"}
    t.update(extra)
    return t


# --------------------------------------------------------------------------- #
# 1. esecuzione solo sugli stessi segnali, con almeno 30 accoppiati            #
# --------------------------------------------------------------------------- #
def _caso_segnali_scelti(n_coppie_segnali: int):
    """Esecuzione PERFETTA sugli stessi segnali, ma il paper prende solo i
    segnali della coppia debole: la media di tutti i trade mostra un divario
    grande, la riga accoppiata zero. Con la regola di prima era «esecuzione»."""
    pairs = {"A|ga": {"validated_at": PAV}, "B|gb": {"validated_at": PAV}}
    motore, paper = [], []
    for i in range(n_coppie_segnali):
        e = PAV + 86400 + i * 7200
        motore.append(_m("A", "ga", e, pnl_pct=0.01 * (1.2 if i % 2 else 0.8)))
        rb = -0.2 if i % 2 else -0.6
        motore.append(_m("B", "gb", e, pnl_pct=0.01 * rb))
        paper.append(_p("B", "gb", e + 905, pnl=rb))
    return pb.fuori_campione(motore, paper, pairs, list(pairs), PAV)


def test_la_media_di_tutti_non_decide_piu_esecuzione():
    fc = _caso_segnali_scelti(100)
    assert fc["differenza"] > 2 * fc["errore_standard"]     # prima: «e' esecuzione»
    ss = fc["stessi_segnali"]
    assert ss["n"] == 100 and math.isclose(ss["differenza"], 0.0, abs_tol=1e-9)
    assert "Esecuzione: non e' esecuzione" in fc["lettura"]
    assert "Esecuzione: e' esecuzione" not in fc["lettura"]


def test_esecuzione_serve_30_accoppiati_nel_confronto():
    """Paper sempre 1R sotto il motore sugli stessi segnali: con 29 accoppiati
    non si decide, con 30 e' esecuzione."""
    def caso(n):
        pairs = {"A|ga": {"validated_at": PAV}}
        motore, paper = [], []
        for i in range(n):
            e = PAV + 86400 + i * 7200          # 12 al giorno: piu' giornate
            r = 0.5 + 0.1 * (i % 3)
            motore.append(_m("A", "ga", e, pnl_pct=0.01 * r))
            paper.append(_p("A", "ga", e + 905, pnl=r - 1.0))
        return pb.fuori_campione(motore, paper, pairs, list(pairs), PAV)

    assert "Esecuzione: non si decide: 29 accoppiati, ne servono 30." in caso(29)["lettura"]
    assert "Esecuzione: e' esecuzione" in caso(30)["lettura"]


# --------------------------------------------------------------------------- #
# 2. doppioni fusi                                                             #
# --------------------------------------------------------------------------- #
def test_segnali_unici_fonde_stessa_moneta_candela_direzione():
    righe = [
        {"sym": "X", "dir": "long", "ts": 1000.0, "r": 1.0, "mfe": 2.0, "tp": True,
         "giorno": "g", "uscita": False},
        {"sym": "X", "dir": "long", "ts": 1000.0, "r": 0.0, "mfe": 1.0, "tp": False,
         "giorno": "g", "uscita": False},                     # gemella: stesso segnale
        {"sym": "X", "dir": "short", "ts": 1000.0, "r": -1.0, "mfe": None, "tp": None,
         "giorno": "g", "uscita": False},                     # altra direzione
        {"sym": "Y", "dir": "long", "ts": 1000.0, "r": 0.5, "mfe": None, "tp": None,
         "giorno": "g", "uscita": False},                     # altra moneta
        {"sym": "X", "dir": "long", "ts": 1900.0, "r": 0.2, "mfe": None, "tp": None,
         "giorno": "g", "uscita": False},                     # altra candela
    ]
    segnali, doppioni = pb.segnali_unici(righe)
    assert doppioni == 1 and len(segnali) == 4
    gem = next(s for s in segnali if s["sym"] == "X" and s["dir"] == "long" and s["ts"] == 1000.0)
    # R e mfe medi delle gemelle, quota che tocca il primo gradino
    assert gem["r"] == 0.5 and gem["mfe"] == 1.5 and gem["tp"] == 0.5
    assert sorted(gem["membri"]) == [0, 1]


def test_gemelle_contano_una_volta_e_non_finiscono_fra_i_non_aperti():
    """Due strategie gemelle sulla stessa moneta e candela: nel motore un
    segnale solo. Il paper ne apre una: il segnale e' preso, la gemella non e'
    un «non aperto»."""
    pairs = {"A|g1": {"validated_at": PAV}, "A|g2": {"validated_at": PAV}}
    motore, paper = [], []
    for i in range(10):
        e = PAV + 86400 + i * 7200
        motore += [_m("A", "g1", e, pnl_pct=0.005), _m("A", "g2", e, pnl_pct=0.005)]
        if i < 6:
            paper.append(_p("A", "g1", e + 905, pnl=0.5))
    fc = pb.fuori_campione(motore, paper, pairs, list(pairs), PAV)
    assert fc["motore"]["trade"] == 20 and fc["motore"]["n"] == 10
    assert fc["motore"]["doppioni"] == 10
    assert fc["stessi_segnali"]["n"] == 6
    assert fc["motore_non_aperti"]["n"] == 4        # prima sarebbero stati 14
    assert fc["segnali_presi"]["paper"] == 6 and fc["segnali_presi"]["segnali"] == 10


# --------------------------------------------------------------------------- #
# 3. margine per giornata                                                      #
# --------------------------------------------------------------------------- #
def test_margine_per_giornata_uguale_a_quello_per_trade_senza_raggruppamento():
    vals = [0.3, -1.0, 0.8, 0.1, -0.4, 1.2]
    a = [(v, f"g{i}") for i, v in enumerate(vals)]
    s = pb.statistiche_lato([(v, None, None) for v in vals])
    assert math.isclose(pb.errore_standard_per_giorno(a), s["dev_std"] / math.sqrt(len(vals)))
    # meno di 2 giornate o di 2 righe: niente errore
    assert pb.errore_standard_per_giorno([(v, "g") for v in vals]) is None
    assert pb.errore_standard_per_giorno([(1.0, "g1")]) is None
    assert pb.errore_standard_per_giorno(a, [(1.0, "g1")]) is None
    assert pb.errore_regola(0.1, None) is None
    assert pb.errore_regola(0.1, 0.05) == 0.1 and pb.errore_regola(0.1, 0.2) == 0.2


def test_giornate_nere_allargano_il_margine_e_si_cancellano_negli_accoppiati():
    """Effetto di giornata comune: ogni giorno tutti i trade prendono lo stesso
    colpo (le giornate nere del 19, 23 e 26 set). Il margine trade per trade
    resta stretto, quello per giornata si allarga. Negli accoppiati paper e
    motore prendono lo STESSO colpo, che si cancella nella differenza."""
    rnd = random.Random(7)
    motore, paper, coppie, giorni = [], [], [], []
    for g in range(12):
        colpo = rnd.gauss(0, 1.0)
        for _ in range(15):
            rumore_m, rumore_p = rnd.gauss(0, 0.3), rnd.gauss(0, 0.3)
            motore.append((colpo + rumore_m, f"g{g}"))
            paper.append((colpo + rumore_p - 0.1, f"g{g}"))
            coppie.append((colpo + rumore_m, colpo + rumore_p - 0.1))
            giorni.append(f"g{g}")
    m = pb.statistiche_lato([(v, None, None) for v, _ in motore])
    es_trade = m["dev_std"] / math.sqrt(m["n"])
    es_giorno = pb.errore_standard_per_giorno(motore)
    assert es_giorno > 2.5 * es_trade
    # differenza fra due lati NON accoppiati: se i due lati hanno gli stessi
    # giorni nella stessa proporzione il colpo si cancella anche qui (e la regola
    # tiene il piu' largo, quello trade per trade); se il paper opera solo in
    # alcuni giorni (come fa: salta segnali), il colpo non si cancella e il
    # margine per giornata e' piu' largo di quello trade per trade
    p = pb.statistiche_lato([(v, None, None) for v, _ in paper])
    assert pb.errore_standard_per_giorno(motore, paper) < pb.errore_standard_differenza(m, p)
    paper_pochi = [(v, g) for v, g in paper if g in ("g0", "g1", "g2", "g3")]
    p2 = pb.statistiche_lato([(v, None, None) for v, _ in paper_pochi])
    assert (pb.errore_standard_per_giorno(motore, paper_pochi)
            > 1.2 * pb.errore_standard_differenza(m, p2))
    # accoppiati: il colpo si cancella, il margine per giornata resta piccolo
    ss = pb.statistiche_abbinate(coppie, giorni)
    assert ss["errore_giorno"] < es_giorno / 3
    assert ss["errore_regola"] == max(ss["errore_standard"], ss["errore_giorno"])


# --------------------------------------------------------------------------- #
# 4. segnali presi: paper contro portafoglio del motore                        #
# --------------------------------------------------------------------------- #
def test_quota_del_portafoglio_del_motore_una_posizione_per_moneta():
    """Tre segnali sulla stessa moneta a un'ora l'uno dall'altro, ognuno che
    dura 8 barre (2 ore): il portafoglio del motore ne apre solo 2 (il secondo
    trova la moneta gia' aperta), come farebbe il paper."""
    righe = []
    for i in range(3):
        t = _m("A", "g1", PAV + i * 3600, bars=8)
        righe.append({"sym": "A", "dir": "long", "ts": t["entry_ts"], "r": 1.0, "mfe": None,
                      "tp": None, "giorno": "g", "uscita": False, "t": t})
    segnali, _ = pb.segnali_unici(righe)
    assert pb.quota_portafoglio_motore(segnali, righe, 900.0) == 2
    assert pb.quota_portafoglio_motore([], [], 900.0) == 0


def test_segnali_presi_stampati_accanto_al_portafoglio(capsys):
    fc = _caso_segnali_scelti(40)
    pr = fc["segnali_presi"]
    assert pr["segnali"] == 80 and pr["paper"] == 40
    # A e B sono monete diverse, ma dopo 3-4 perdite di B in un giorno il tetto
    # per moneta al giorno (come nel bot) ferma il portafoglio del motore
    assert 40 < pr["portafoglio_motore"] < 80
    pb.stampa_fuori_campione(fc, "2026-09-16", 0, None)
    out = capsys.readouterr().out
    assert "segnali presi: paper 40 su 80 (50%)" in out
    assert (f"il portafoglio del motore, anche lui una posizione per moneta, "
            f"{pr['portafoglio_motore']} su 80") in out
    assert "non e' un verdetto sul bot" in out


# --------------------------------------------------------------------------- #
# 5. sopravvivenza                                                             #
# --------------------------------------------------------------------------- #
ORA = _ts(2026, 10, 9, 8)


def _registro_e_diario():
    pairs = {
        "VIVA|gen_v": {"pass_count": 5, "validated_at": V, "last_seen_at": ORA},
        "SOST|gen_s": {"pass_count": 4, "validated_at": V, "last_seen_at": ORA,
                       "sostituita_da": "gen_figlia", "sostituita_at": _ts(2026, 10, 3),
                       "last_params": {"profit_lock_keep": 0.65}},
        "VECCHIA|gen_n": {"pass_count": 3, "validated_at": V,
                          "last_seen_at": _ts(2026, 10, 2)},             # coin uscita
        "AZZ|gen_z": {"pass_count": 0, "validated_at": _ts(2026, 9, 20),
                      "sessione_azzerata_at": _ts(2026, 9, 27, 3)},
        "MAI|gen_m": {"pass_count": 1},                                   # mai validata
    }
    diario = {"events": [
        {"key": "RIM|gen_r", "tipo": "promossa", "at": _ts(2026, 9, 27, 10)},
        {"key": "RIM|gen_r", "tipo": "rimossa", "at": _ts(2026, 10, 8, 6)},
        {"key": "RIM2|base_rsi", "tipo": "rimossa", "at": _ts(2026, 10, 8, 6)},  # base
        {"key": "PRIMA|gen_p", "tipo": "rimossa", "at": _ts(2026, 9, 10)},       # prima
    ]}
    return pairs, diario


def test_coppie_uscite_motivi_date_e_configurazione():
    pairs, diario = _registro_e_diario()
    paper = [_p("RIM", "gen_r", _ts(2026, 10, 1), scale_r_mults=[1.5, 3.0],
                sl_to_breakeven=False, profit_lock_keep=0.35),
             _p("AZZ", "gen_z", _ts(2026, 9, 22)),
             _p("FANTASMA", "gen_f", _ts(2026, 9, 29))]
    u = pb.coppie_uscite(pairs, diario, ["VIVA|gen_v"], paper, PAV, ORA)
    assert set(u) == {"RIM|gen_r", "RIM2|base_rsi", "SOST|gen_s", "VECCHIA|gen_n",
                      "AZZ|gen_z", "FANTASMA|gen_f"}
    r = u["RIM|gen_r"]
    assert r["motivo"] == "rimossa" and r["rigiocabile"]
    assert r["inizio"] == _ts(2026, 9, 27, 10) and r["fine"] == _ts(2026, 10, 8, 6)
    # il record e' cancellato: la configurazione d'uscita viene dal paper
    assert r["params"] == {"scale_r_mults": [1.5, 3.0], "sl_to_breakeven": False,
                           "profit_lock_keep": 0.35}
    assert u["RIM2|base_rsi"]["rigiocabile"] is False
    assert u["RIM2|base_rsi"]["perche"] == "strategia base"
    s = u["SOST|gen_s"]
    assert s["motivo"] == "sostituita" and s["fine"] == _ts(2026, 10, 3) and s["rigiocabile"]
    assert s["params"] == {"profit_lock_keep": 0.65}
    n = u["VECCHIA|gen_n"]
    assert n["motivo"] == "non piu' vista" and n["fine"] == _ts(2026, 10, 2) + pb.FRESH_DAYS * 86400
    a = u["AZZ|gen_z"]
    assert a["motivo"] == "azzerata" and not a["rigiocabile"]
    assert a["perche"] == "regola della sessione cambiata"
    assert u["FANTASMA|gen_f"]["motivo"] == "ignota" and not u["FANTASMA|gen_f"]["rigiocabile"]
    # senza diario le rimosse non si vedono, il resto si'
    assert "RIM|gen_r" not in pb.coppie_uscite(pairs, None, ["VIVA|gen_v"], [], PAV, ORA)


def test_sopravvivenza_due_righe_e_uscite_fino_al_giorno_dell_uscita(capsys):
    """La coppia rimossa perde dopo la validazione: nella riga «ancora validate»
    non c'e', in «tutte le coppie operate» si'. I suoi trade dopo l'uscita e
    prima della validazione restano fuori."""
    pairs, diario = _registro_e_diario()
    uscite = pb.coppie_uscite(pairs, diario, ["VIVA|gen_v"], [], PAV, ORA)
    motore = [_m("VIVA", "gen_v", V + 3600 * (i + 1), pnl_pct=0.005) for i in range(6)]
    rig = [_m("RIM", "gen_r", _ts(2026, 9, 27, 9), pnl_pct=0.05),         # prima: fuori
           _m("RIM", "gen_r", _ts(2026, 10, 2), pnl_pct=-0.01),
           _m("RIM", "gen_r", _ts(2026, 10, 3), pnl_pct=-0.01),
           _m("RIM", "gen_r", _ts(2026, 10, 8, 7), pnl_pct=0.05)]         # dopo: fuori
    fc = pb.fuori_campione(motore, [], pairs, ["VIVA|gen_v"], PAV,
                           uscite=uscite, motore_uscite=rig)
    sv = fc["sopravvivenza"]
    assert sv["validate"]["motore_n"] == 6 and math.isclose(sv["validate"]["motore_r"], 0.5)
    assert sv["tutte"]["motore_n"] == 8
    assert math.isclose(sv["tutte"]["motore_r"], (6 * 0.5 - 2.0) / 8)
    assert sv["rigiocate"] == 3 and sv["rigiocate_con_trade"] == 1
    assert sv["rigiocate_config_globale"] == 2          # RIM e VECCHIA: nessuna config nota
    # le regole leggono «tutte le coppie operate»
    assert fc["motore"]["n"] == 8
    out = pb.sezione_fuori_campione(motore, [], pairs, ["VIVA|gen_v"], ["VIVA|gen_v"],
                                    PAV, PAV, diario, uscite=uscite, motore_uscite=rig)
    testo = capsys.readouterr().out
    assert "coppie ancora validate: motore 6 segnali +0.50R" in testo
    assert f"tutte le coppie operate: motore 8 segnali {pb._fmt_r(1.0 / 8)}R" in testo
    assert "non rigiocate 2 coppie uscite" in testo and "regola della sessione cambiata" in testo
    assert out["non_rigiocate"] == {"regola della sessione cambiata": 1, "strategia base": 1}
    assert not pb.contiene_liste_annidate(out)


# --------------------------------------------------------------------------- #
# 6-8. la regola del 3 ott (trades) e le regole stampate                       #
# --------------------------------------------------------------------------- #
DAL3 = _ts(2026, 9, 27, 19, 40)


def _tr(entry, r, declassata=False):
    return {"symbol": "X", "strategy": "gen_x", "direction": "long", "declassata": declassata,
            "entry_time": dt.datetime.fromtimestamp(entry, dt.timezone.utc).isoformat(),
            "entry_price": 100.0, "orig_stop": 99.0, "size": 1.0, "pnl": r,
            "exit_reason": "stop_loss"}


def _campione(r_decl, r_att, n=40, rumore=0.3):
    rnd = random.Random(3)
    out = []
    for i in range(n):
        e = DAL3 + 600 + i * 4 * 3600                    # ~6 giornate
        out.append(_tr(e, r_decl + rnd.gauss(0, rumore), declassata=True))
        out.append(_tr(e + 60, r_att + rnd.gauss(0, rumore)))
    return out


def test_regola_3_ott_i_tre_esiti():
    assert ts.esito_3_ott(0.30, 0.10) == "diverso"
    assert ts.esito_3_ott(-0.30, 0.10) == "diverso"
    assert ts.esito_3_ott(0.02, 0.10) == "uguale"            # [-0,08; +0,12] dentro ±0,15
    assert ts.esito_3_ott(0.02, 0.29) == "non si decide"     # il margine di oggi, ~±0,29
    assert ts.esito_3_ott(0.10, 0.10) == "non si decide"     # sul bordo: non esclude lo 0
    assert ts.esito_3_ott(None, 0.1) == "non si decide"
    assert ts.UGUALE_ENTRO_R == 0.15


def test_regola_3_ott_sul_confronto_e_taglio_al_27_sera():
    uguali = ts.confronto_3_ott(_campione(0.05, 0.05, n=200, rumore=0.2))
    assert uguali["esito"] == "uguale" and uguali["margine"] < 0.15
    diversi = ts.confronto_3_ott(_campione(-0.5, 0.3))
    assert diversi["esito"] == "diverso" and diversi["differenza"] < 0
    rumorosi = ts.confronto_3_ott(_campione(0.0, 0.05, n=20, rumore=1.0))
    assert rumorosi["esito"] == "non si decide"
    # i trade entrati prima del 27 set 19:40 UTC non contano (difetto della sessione)
    prima = [_tr(DAL3 - 60, -5.0, declassata=True), _tr(DAL3 - 60, 5.0)]
    c = ts.confronto_3_ott(prima + _campione(-0.5, 0.3))
    assert c["declassate_n"] == diversi["declassate_n"] and c["differenza"] == diversi["differenza"]
    assert ts.confronto_3_ott([])["esito"] == "non si decide"


def test_regola_3_ott_stampata_nel_blocco_declassate(capsys):
    rep = ts.declassate_report(_campione(-0.5, 0.3))
    ts.print_declassate(rep)
    out = capsys.readouterr().out
    assert "REGOLA DEL 3 OTT (regola scritta il 30 set, prima delle letture)" in out
    assert "dal 27 set 19:40 UTC: declassate 40 trade" in out
    assert "-> DIVERSO (le declassate fanno peggio delle attive)" in out


def test_regole_scritte_prima_nel_testo():
    r = pb.REGOLA_FUORI_CAMPIONE
    assert "regola scritta il 30 set, prima delle letture" in r
    assert "stessi segnali" in r and "30 trade accoppiati" in r and "80 segnali" in r
    assert "stesso segnale e stesso mercato" in r and "per giornata" in r
    assert "3, 7, 14 ott" in pb.TRE_LETTURE and "~7%" in pb.TRE_LETTURE


# --------------------------------------------------------------------------- #
# main con un client finto                                                    #
# --------------------------------------------------------------------------- #
class _FbFinto:
    def __init__(self, docs):
        self.docs, self.is_live, self.scritti, self.letti = docs, True, {}, []

    def get_doc(self, coll, doc):
        self.letti.append((coll, doc))
        return self.docs.get((coll, doc))

    def set_doc(self, coll, doc, data):
        self.scritti[(coll, doc)] = data


def test_main_rigioca_la_coppia_rimossa_e_non_stampa_le_righe_da_cache(monkeypatch, capsys):
    ora = time.time()
    oggi = dt.datetime.fromtimestamp(ora, dt.timezone.utc).date()
    monkeypatch.setattr(pb, "PAPER_START", (oggi - dt.timedelta(days=10)).isoformat())
    v = ora - 6 * 86400
    pairs = {"AAAUSDT|gen_a": {"pass_count": 5, "last_seen_at": ora, "validated_at": v}}
    diario = {"events": [{"key": "RRRUSDT|gen_r", "tipo": "promossa", "at": v},
                         {"key": "RRRUSDT|gen_r", "tipo": "rimossa", "at": ora - 2 * 86400}]}
    specs = {"gen_a": {"id": "gen_a"}, "gen_r": {"id": "gen_r"}}
    fb = _FbFinto({("strategy_registry", "validated"): {"pairs": pairs},
                   ("discovered_strategies", "specs"): {"specs": specs},
                   ("gate_history", "lifecycle"): diario})
    monkeypatch.setattr(pb, "get_firebase", lambda: fb)

    class _Wfo:
        def __init__(self, **kw):
            self.bt = None

    monkeypatch.setattr(pb, "WalkForwardOptimizer", _Wfo)
    chiamate = []

    def _trades(sym, strategie, specs_, args, inizio_ts, bt):
        chiamate.append((sym, [s for s, _ in strategie]))
        print(f"[backtest] dati da cache: 6145 candele ({sym} 15m)")
        print(f"[backtest] ATTENZIONE {sym}: solo serie PARZIALE disponibile")
        out = []
        for strat, rec in strategie:
            for g in (5, 4, 3, 1):
                out.append(_m(sym, strat, ora - g * 86400, pnl_pct=-0.01 if sym == "RRRUSDT"
                              else 0.02))
        return out, [], 6000

    monkeypatch.setattr(pb, "trades_della_coin", _trades)
    paper = [_p("AAAUSDT", "gen_a", ora - 4 * 86400, pnl=-1.0),
             _p("RRRUSDT", "gen_r", ora - 3 * 86400 + 905, pnl=-1.0, profit_lock_keep=0.35)]
    monkeypatch.setattr(pb, "_trade_paper", lambda fb_, dal_ts: paper)

    assert pb.main([]) == 0
    testo = capsys.readouterr().out
    # la coppia rimossa e' rigiocata (con la config del paper), fuori dal portafoglio
    assert ("RRRUSDT", ["gen_r"]) in chiamate
    assert "uscite rigiocate 1" in testo and "rigiocate 1" in testo
    # le righe «dati da cache» si contano, le altre del caricatore restano
    assert "dati da cache:" not in testo and "candele da cache per 2 coin" in testo
    assert "solo serie PARZIALE" in testo
    fc = fb.scritti[("portfolio", "backtest")]["fuori_campione"]
    sv = fc["sopravvivenza"]
    # AAA: 4 trade dopo la validazione (6 giorni fa); RRR: 3 (5, 4, 3 giorni fa, prima
    # della rimozione di 2 giorni fa), e non quello di 1 giorno fa
    assert sv["validate"]["motore_n"] == 4 and sv["tutte"]["motore_n"] == 7
    assert sv["rigiocate"] == 1 and sv["rigiocate_config_globale"] == 0
    assert fb.scritti[("portfolio", "backtest")]["n_trade"] == 4       # solo AAA nel portafoglio
    assert not pb.contiene_liste_annidate(fb.scritti[("portfolio", "backtest")])
    # nessuna lettura in piu': registro, spec, paper (finto) e diario, una volta ciascuno
    assert sorted(set(fb.letti)) == sorted(fb.letti)
    assert "coppie ancora validate" in testo and "tutte le coppie operate" in testo


def test_output_del_main_su_70_coin_sotto_i_17_kb(monkeypatch, capsys):
    """Il caso di ops 0371: 202 coppie su 70 coin, ~2.200 trade. Con le righe
    «dati da cache» contate invece che stampate l'output resta sotto ~17 KB
    anche con la sezione piu' lunga (l'agente ops taglia oltre 20.000)."""
    ora = time.time()
    oggi = dt.datetime.fromtimestamp(ora, dt.timezone.utc).date()
    monkeypatch.setattr(pb, "PAPER_START", (oggi - dt.timedelta(days=14)).isoformat())
    pairs = {}
    for i in range(202):
        pairs[f"C{i % 70:02d}USDTXX|gen_{i:05d}"] = {
            "pass_count": 5, "last_seen_at": ora, "validated_at": ora - (6 + i % 5) * 86400}
    diario = {"events": [{"key": f"R{j}USDT|gen_r{j}", "tipo": "rimossa",
                          "at": ora - 86400} for j in range(10)]}
    fb = _FbFinto({("strategy_registry", "validated"): {"pairs": pairs},
                   ("discovered_strategies", "specs"): {"specs": {}},
                   ("gate_history", "lifecycle"): diario})
    monkeypatch.setattr(pb, "get_firebase", lambda: fb)

    class _Wfo:
        def __init__(self, **kw):
            self.bt = None

    monkeypatch.setattr(pb, "WalkForwardOptimizer", _Wfo)
    rnd = random.Random(1)

    def _trades(sym, strategie, specs_, args, inizio_ts, bt):
        print(f"[backtest] dati da cache: 6145 candele ({sym} 15m)")
        out = []
        for strat, _rec in strategie:
            for g in range(11):
                out.append(_m(sym, strat, ora - (60 - g * 5.3) * 86400 + rnd.randint(0, 90) * 900,
                              pnl_pct=0.01 * rnd.choice([-1.0, 0.5, 1.5])))
        return out, [], 6145

    monkeypatch.setattr(pb, "trades_della_coin", _trades)
    paper = [_p(k.split("|")[0], k.split("|")[1], ora - rnd.uniform(0.5, 5) * 86400,
                pnl=rnd.choice([-1.0, 0.3])) for k in list(pairs)[:80]]
    paper += [_p(f"R{j}USDT", f"gen_r{j}", ora - 3 * 86400) for j in range(10)]
    monkeypatch.setattr(pb, "_trade_paper", lambda fb_, dal_ts: paper)

    assert pb.main([]) == 0
    testo = capsys.readouterr().out
    assert "FUORI CAMPIONE (H5)" in testo and "tutte le coppie operate" in testo
    assert "dati da cache:" not in testo
    assert len(testo) < 17_000, len(testo)


# --------------------------------------------------------------------------- #
# Revisione del 30 set 2026: applicazione fedele delle regole (soglie uguali)  #
# --------------------------------------------------------------------------- #
def _caso_selezione(n=90):
    """Una coppia validata con `n` segnali del motore a +0,1R e 5 trade del paper."""
    pairs = {"A|ga": {"validated_at": PAV}}
    motore = [_m("A", "ga", PAV + 86400 + i * 7200, pnl_pct=0.001) for i in range(n)]
    paper = [_p("A", "ga", PAV + 86400 + i * 7200 + 905, pnl=0.1) for i in range(5)]
    return pairs, motore, paper


def test_selezione_non_si_decide_senza_diario_delle_vite(capsys):
    """Senza diario le coppie rimosse mancano dalla riga «tutte le coppie
    operate»: la selezione non si decide (l'esecuzione si')."""
    pairs, motore, paper = _caso_selezione()
    ok = pb.sezione_fuori_campione(motore, paper, pairs, list(pairs), list(pairs),
                                   PAV, PAV, {"events": []})
    assert ok["lettura"].startswith("Selezione: il motore guadagna ancora")
    assert ok["sopravvivenza_completa"] is True
    no = pb.sezione_fuori_campione(motore, paper, pairs, list(pairs), list(pairs),
                                   PAV, PAV, None)
    assert no["lettura"].startswith(
        "Selezione: non si decide: il diario delle vite non si legge")
    assert "Esecuzione: non si decide: 5 accoppiati" in no["lettura"]
    assert no["sopravvivenza_completa"] is False
    # anche un diario con gli eventi illeggibili, o il flag passato dal main
    assert not pb.diario_leggibile({"events": "non json"}) and pb.diario_leggibile({"events": []})
    fc = pb.fuori_campione(motore, paper, pairs, list(pairs), PAV, sopravvivenza_completa=False)
    assert "Selezione: non si decide: il diario" in fc["lettura"]
    capsys.readouterr()


def test_main_passa_la_sopravvivenza_incompleta(monkeypatch):
    """Il main: diario assente, o coppie uscite non ricostruite -> la sezione
    riceve `sopravvivenza_completa` falso."""
    ora = time.time()
    oggi = dt.datetime.fromtimestamp(ora, dt.timezone.utc).date()
    monkeypatch.setattr(pb, "PAPER_START", (oggi - dt.timedelta(days=10)).isoformat())
    pairs = {"AAAUSDT|gen_a": {"pass_count": 5, "last_seen_at": ora, "validated_at": ora - 6 * 86400}}

    class _Wfo:
        def __init__(self, **kw):
            self.bt = None

    monkeypatch.setattr(pb, "WalkForwardOptimizer", _Wfo)
    monkeypatch.setattr(pb, "trades_della_coin", lambda sym, st, sp, a, i, bt: (
        [_m(sym, s, ora - g * 86400) for s, _ in st for g in (3, 2)], [], 6000))
    monkeypatch.setattr(pb, "_trade_paper", lambda fb_, dal_ts: [])
    visti = []
    monkeypatch.setattr(pb, "sezione_fuori_campione",
                        lambda *a, **k: visti.append(k["sopravvivenza_completa"]) or {})

    def gira(docs):
        fb = _FbFinto(docs)
        monkeypatch.setattr(pb, "get_firebase", lambda: fb)
        assert pb.main([]) == 0

    base = {("strategy_registry", "validated"): {"pairs": pairs},
            ("discovered_strategies", "specs"): {"specs": {}}}
    gira({**base, ("gate_history", "lifecycle"): {"events": []}})
    gira(base)                                                   # diario assente
    monkeypatch.setattr(pb, "coppie_uscite", lambda *a, **k: 1 / 0)
    gira({**base, ("gate_history", "lifecycle"): {"events": []}})  # uscite non ricostruite
    assert visti == [True, False, False]


def test_rimossa_senza_promossa_parte_da_vissuta_giorni():
    """Il diario tiene gli ultimi 500 eventi: se la «promossa» e' caduta,
    l'inizio viene da `vissuta_giorni` della «rimossa» (mai prima della
    promozione vera), non dal 25 set."""
    rimossa_at = _ts(2026, 10, 8, 6)
    vera = rimossa_at - 5.2537 * 86400                  # promozione vera
    diario = {"events": [{"key": "RIM|gen_r", "tipo": "rimossa", "at": rimossa_at,
                          "vissuta_giorni": round((rimossa_at - vera) / 86400, 2)}]}
    u = pb.coppie_uscite({}, diario, [], [], PAV, ORA)["RIM|gen_r"]
    atteso = rimossa_at - (5.25 - 0.005) * 86400
    assert math.isclose(u["inizio"], atteso) and u["inizio"] >= vera
    assert u["inizio"] > pb.VALIDATED_AT_DAL
    # senza nemmeno `vissuta_giorni` si resta al 25 set 12:00
    diario["events"][0]["vissuta_giorni"] = None
    assert pb.coppie_uscite({}, diario, [], [], PAV, ORA)["RIM|gen_r"]["inizio"] == \
        pb.VALIDATED_AT_DAL


def test_segnale_preso_da_un_altra_strategia_conta_come_preso():
    """Il paper entra su A long con g1, nel motore su A alla stessa candela
    scatta solo la gemella g2: il segnale e' preso (non «non aperto»), ma non
    finisce negli stessi segnali. In direzione opposta resta non preso."""
    pairs = {"A|g1": {"validated_at": PAV}, "A|g2": {"validated_at": PAV}}
    e = PAV + 86400
    fc = pb.fuori_campione([_m("A", "g2", e)], [_p("A", "g1", e + 905)], pairs, list(pairs), PAV)
    assert fc["segnali_presi"]["paper"] == 1 and fc["motore_non_aperti"]["n"] == 0
    assert fc["stessi_segnali"]["n"] == 0
    assert fc["paper_senza_segnale"] == 0 and fc["paper_su_altra_strategia"] == 1
    corto = pb.fuori_campione([_m("A", "g2", e)], [_p("A", "g1", e + 905, direction="short")],
                              pairs, list(pairs), PAV)
    assert corto["segnali_presi"]["paper"] == 0 and corto["motore_non_aperti"]["n"] == 1
    assert corto["paper_senza_segnale"] == 1 and corto["paper_su_altra_strategia"] == 0


def test_esecuzione_sul_bordo_del_margine_non_si_decide():
    """«Oltre il margine» e' strettamente maggiore, come nella regola del 3 ott."""
    assert pb.lettura_esecuzione({"n": 30, "differenza": 0.2, "errore_regola": 0.1}
                                 ).startswith("non si decide")
    assert pb.lettura_esecuzione({"n": 30, "differenza": 0.2001, "errore_regola": 0.1}
                                 ).startswith("e' esecuzione")
    assert ts.esito_3_ott(0.2, 0.2) == "non si decide"


def test_regola_3_ott_caso_limite_e_trade_senza_r(capsys):
    """Il calcolo resta quello della regola (nessun minimo di trade aggiunto):
    2 contro 2 a -1R su 2 giornate da' margine 0 ed esito «uguale». I trade
    senza R si contano e si stampano."""
    rows = [_tr(DAL3 + 600, -1.0, declassata=True), _tr(DAL3 + 600 + 86400, -1.0, declassata=True),
            _tr(DAL3 + 700, -1.0), _tr(DAL3 + 700 + 86400, -1.0)]
    c = ts.confronto_3_ott(rows)
    assert c["margine"] == 0 and c["esito"] == "uguale"
    senza = dict(_tr(DAL3 + 800, 0.5, declassata=True), size=0.0)       # senza R
    prima = dict(_tr(DAL3 - 800, 0.5), size=0.0)                        # prima del 27 sera
    c = ts.confronto_3_ott(rows + [senza, prima])
    assert c["declassate_senza_r"] == 1 and c["attive_senza_r"] == 0 and c["declassate_n"] == 2
    ts.print_declassate(ts.declassate_report(rows + [senza]))
    out = capsys.readouterr().out
    assert "esclusi perche' senza R: declassate 1, attive 0" in out
    assert ("il piu' largo fra quello per giornata e quello trade per trade; almeno 2 "
            "giornate") in out


def test_riga_delle_coppie_rigiocate_accanto_al_totale(capsys):
    pairs, diario = _registro_e_diario()
    uscite = pb.coppie_uscite(pairs, diario, ["VIVA|gen_v"], [], PAV, ORA)
    motore = [_m("VIVA", "gen_v", V + 3600 * (i + 1)) for i in range(3)]
    rig = [_m("RIM", "gen_r", _ts(2026, 10, 2))]
    pb.stampa_fuori_campione(pb.fuori_campione(motore, [], pairs, ["VIVA|gen_v"], PAV,
                                               uscite=uscite, motore_uscite=rig),
                             "2026-09-16", 1, None)
    out = capsys.readouterr().out
    assert ("coppie confrontate 4 (di cui 3 uscite dal registro e rigiocate) · con trade del "
            "motore 2 (rigiocate 1) · con trade del paper 0 (rigiocate 0)") in out
    # col paper su una coppia rigiocata, fra le coppie del paper ne conta una
    paper = [_p("RIM", "gen_r", _ts(2026, 10, 2) + 905), _p("VIVA", "gen_v", V + 3600 + 905)]
    fc = pb.fuori_campione(motore, paper, pairs, ["VIVA|gen_v"], PAV, uscite=uscite,
                           motore_uscite=rig)
    assert fc["coppie_con_paper"] == 2 and fc["sopravvivenza"]["rigiocate_con_paper"] == 1


def _righe_segnali(trades):
    righe = [{"sym": t["symbol"], "dir": t["direction"], "ts": t["entry_ts"], "r": 1.0,
              "mfe": None, "tp": None, "giorno": "g", "uscita": False, "t": t} for t in trades]
    return pb.segnali_unici(righe)[0], righe


def test_portafoglio_del_motore_in_parita_senza_tetto_di_posizioni(monkeypatch):
    """Sei segnali nella stessa candela su sei monete: in parita' (come il bot)
    il massimo di posizioni non si applica e li apre tutti; fuori parita' 5."""
    segnali, righe = _righe_segnali([_m(f"C{i}", "g", PAV + 3600) for i in range(6)])
    monkeypatch.setattr(pb.settings, "BACKTEST_PARITY", True)
    assert pb.quota_portafoglio_motore(segnali, righe, 900.0) == 6
    monkeypatch.setattr(pb.settings, "BACKTEST_PARITY", False)
    monkeypatch.setattr(pb.settings, "MAX_OPEN_POSITIONS", 5)
    assert pb.quota_portafoglio_motore(segnali, righe, 900.0) == 5


def test_segnali_in_comune_fra_paper_e_portafoglio_del_motore(capsys):
    """Stessi conteggi non vuol dire stessi segnali. Due segnali su A a un'ora
    l'uno dall'altro, lunghi 2 ore nel motore: il portafoglio del motore apre
    solo il primo. Caso B: il paper li prende tutti e due. Caso C: il paper
    prende solo il secondo (1 su 2 contro 1 su 2, nessuno in comune)."""
    pairs = {"A|g": {"validated_at": PAV}}
    t0 = PAV + 86400
    motore = [_m("A", "g", t0, bars=8), _m("A", "g", t0 + 3600, bars=8)]
    b = pb.fuori_campione(motore, [_p("A", "g", t0 + 905), _p("A", "g", t0 + 3600 + 905)],
                          pairs, list(pairs), PAV)["segnali_presi"]
    assert (b["paper"], b["portafoglio_motore"]) == (2, 1)
    assert (b["in_comune"], b["solo_paper"], b["solo_motore"]) == (1, 1, 0)
    fc = pb.fuori_campione(motore, [_p("A", "g", t0 + 3600 + 905)], pairs, list(pairs), PAV)
    c = fc["segnali_presi"]
    assert (c["paper"], c["portafoglio_motore"]) == (1, 1)
    assert (c["in_comune"], c["solo_paper"], c["solo_motore"]) == (0, 1, 1)
    pb.stampa_fuori_campione(fc, "2026-09-16", 0, None)
    assert "(in comune 0, solo paper 1, solo motore 1)" in capsys.readouterr().out


def test_stessi_segnali_solo_nello_stesso_verso():
    """Caso E: un long del motore e uno short del paper sulla stessa coppia e
    candela non sono lo stesso segnale. Caso F: long e short del motore alla
    stessa candela, il paper short si abbina allo short e il long resta fra i
    non aperti."""
    pairs = {"A|g": {"validated_at": PAV}}
    e = PAV + 86400
    fc = pb.fuori_campione([_m("A", "g", e)], [_p("A", "g", e + 905, direction="short")],
                           pairs, list(pairs), PAV)
    assert fc["stessi_segnali"]["n"] == 0 and fc["paper_senza_segnale"] == 1
    motore = [_m("A", "g", e, pnl_pct=0.01), _m("A", "g", e, pnl_pct=-0.01, direction="short")]
    fc = pb.fuori_campione(motore, [_p("A", "g", e + 905, pnl=-0.5, direction="short")],
                           pairs, list(pairs), PAV)
    ss = fc["stessi_segnali"]
    assert ss["n"] == 1 and math.isclose(ss["motore_r"], -1.0) and math.isclose(ss["paper_r"], -0.5)
    assert fc["motore_non_aperti"]["n"] == 1 and math.isclose(fc["motore_non_aperti"]["r_medio"], 1.0)
    # abbina_segnali: con la direzione solo lo stesso verso, senza come prima
    righe = {"A|g": [[1000.0, 1.0, False, 0, "long"], [1000.0, 2.0, False, 1, "short"]]}
    senza: list = []
    abb, n_senza = pb.abbina_segnali(righe, [("A|g", 1100.0, 0.5, "short"),
                                             ("A|g", 1200.0, 0.4, "short")], 1800.0,
                                     senza_segnale=senza)
    assert abb == [(2.0, 0.5)] and n_senza == 1 and senza == [("A|g", 1200.0, 0.4, "short")]
    abb, _ = pb.abbina_segnali({"A|g": [[1000.0, 1.0, False]]}, [("A|g", 1100.0, 0.5)], 1800.0)
    assert abb == [(1.0, 0.5)]
