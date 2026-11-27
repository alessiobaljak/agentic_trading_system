"""Lo «stato» della macchina dentro i 20.000 caratteri dell'agente (audit del 26 novembre 2026: salute-1, salute-8, salute-9, ordini-2,
ordini-4, ordini-5). La risposta tipica con dati finti della dimensione di oggi (249 coppie validate del vecchio sistema, tabelle di 19
e 22 giorni come nella risposta 0778 del 27 novembre), le tabelle a 14 giorni, il vecchio sistema in fondo, la riga della macchina, il
conto vero con F5 e il suo ultimo ribilancio, demo meno paper senza le monete che il demo non ha. Niente rete e niente comandi veri:
Firebase, Binance, i prezzi pubblici e i comandi della macchina sono finti."""
import calendar
import random
import subprocess

import pytest

from bot.core.firebase_client import encode_pairs
from scripts import ops_agent
from scripts import state_snapshot as ss


def _ms(g, h=0, m=0):
    a, me, d = (int(x) for x in g.split("-"))
    return calendar.timegm((a, me, d, h, m, 0)) * 1000


def _g(d):
    return ss._giorno(d * 86400)


ORA = _ms("2026-11-27", 4, 18) / 1000
OGGI = int(ORA // 86400)

# i 58 pesi di G1 di oggi, paper e demo, in frazione del conto (risposta 0778 del 27 novembre, sezione «G1 oggi, moneta per moneta»)
PESI = {"WLFIUSDT": (-0.1039, -0.1027), "TRXUSDT": (0.0734, 0.0711), "HYPEUSDT": (-0.0636, -0.0691), "AEROUSDT": (-0.0629, -0.0651),
        "XMRUSDT": (-0.0610, -0.0639), "1000SHIBUSDT": (0.0623, 0.0627), "RENDERUSDT": (-0.0577, -0.0614), "BCHUSDT": (0.0553, 0.0594),
        "XLMUSDT": (0.0565, 0.0574), "FARTCOINUSDT": (-0.0535, -0.0568), "ASTERUSDT": (-0.0497, -0.0534), "ADAUSDT": (0.0503, 0.0523),
        "NEARUSDT": (-0.0490, -0.0498), "XPLUSDT": (-0.0489, -0.0496), "SANDUSDT": (0.0459, 0.0490), "ETHFIUSDT": (-0.0469, -0.0461),
        "GRASSUSDT": (-0.0456, -0.0466), "GTCUSDT": (0.0442, 0.0452), "BEATUSDT": (-0.0389, -0.0412), "WLDUSDT": (0.0385, 0.0400),
        "1000BONKUSDT": (0.0376, 0.0395), "APTUSDT": (0.0381, 0.0388), "JUPUSDT": (0.0338, 0.0382), "TIAUSDT": (0.0373, 0.0376),
        "FETUSDT": (0.0363, 0.0374), "1000PEPEUSDT": (0.0365, 0.0363), "SEIUSDT": (0.0358, 0.0363), "ERAUSDT": (0.0347, 0.0324),
        "OPUSDT": (0.0345, 0.0335), "INJUSDT": (0.0337, 0.0344), "VVVUSDT": (-0.0336, -0.0325), "TRUMPUSDT": (0.0327, 0.0321),
        "APRUSDT": (-0.0319, -0.0325), "LITUSDT": (0.0323, 0.0), "USELESSUSDT": (-0.0285, -0.0301), "BEAMXUSDT": (-0.0288, -0.0279),
        "ARIAUSDT": (-0.0240, -0.0262), "BMTUSDT": (0.0251, 0.0212), "LSKUSDT": (0.0243, 0.0213), "QUSDT": (-0.0243, -0.0242),
        "MAGMAUSDT": (-0.0239, -0.0241), "ICNTUSDT": (-0.0228, -0.0208), "IRYSUSDT": (0.0219, 0.0), "HOTUSDT": (0.0212, 0.0196),
        "BIRBUSDT": (0.0205, 0.0164), "PIEVERSEUSDT": (-0.0168, 0.0), "AINUSDT": (-0.0151, -0.0155), "BULLAUSDT": (-0.0121, -0.0147),
        "HUMAUSDT": (0.0139, 0.0119), "UAIUSDT": (-0.0137, 0.0), "ONEUSDT": (0.0116, 0.0134), "IDOLUSDT": (-0.0103, -0.0125),
        "BLESSUSDT": (-0.0110, -0.0121), "EVAAUSDT": (-0.0102, 0.0), "INITUSDT": (0.0091, 0.0089), "AGTUSDT": (-0.0067, -0.0044),
        "JCTUSDT": (-0.0046, 0.0), "AKEUSDT": (0.0027, 0.0004)}
RIFIUTATI = [
    {"simbolo": "EVAAUSDT", "errore": 'margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"Invalid symbol."}'},
    {"simbolo": "LITUSDT", "errore": 'POST /fapi/v1/order: 400 {"code":-4140,"msg":"Invalid symbol status for opening position."}'},
    {"simbolo": "PIEVERSEUSDT", "errore": 'margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"Invalid symbol."}'},
    {"simbolo": "UAIUSDT", "errore": 'margine unico non impostato: POST /fapi/v1/marginType: 400 {"code":-1121,"msg":"Invalid symbol."}'}]
MACCHINA = {
    "df": "Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda1        75G   41G   31G  57% /\n",
    "free": ("               total        used        free      shared  buff/cache   available\n"
             "Mem:           15623        7012        1234         123        7377        8300\n"
             "Swap:              0           0           0\n"),
    "timedatectl": ("               Local time: Fri 2026-11-27 04:18:00 UTC\n           Universal time: Fri 2026-11-27 04:18:00 UTC\n"
                    "                 RTC time: Fri 2026-11-27 04:18:00\n                Time zone: Etc/UTC (UTC, +0000)\n"
                    "System clock synchronized: yes\n              NTP service: active\n          RTC in local TZ: no\n"),
}
# la dimensione di oggi delle sezioni che non cambiano con questa correzione (risposta 0778 del 27 novembre; la sezione delle
# esecuzioni del demo è tagliata dal 16 novembre: 3.001-3.025 caratteri nelle risposte 0736-0744, quando si vedeva intera)
DIMENSIONI_DI_OGGI = {
    "## Paper F5": 801, "## Paper G1 ": 820, "## Paper G11": 816, "## Paper G1N": 866, "## Paper N3 ed E4": 210,
    "## G1 sul conto demo di Binance": 1471, "## G1 sul demo: esecuzioni": 3001, "## G1 oggi, moneta per moneta": 1957,
    "## G1: il funding per regolamento": 1376, "## Ultima decisione": 245, "## Ultimo run di ottimizzazione": 160,
    "## Dove muoiono le candidate": 900,
    "## Supervisore": 631, "## Trade chiusi": 1653, "## Deriva paper vs gate": 92, "## Calibrazione della confidenza": 281,
}


class _Fb:
    """Firebase finto di sola lettura: ogni scrittura si registra (lo stato non deve scrivere niente)."""

    def __init__(self, rtdb, docs=None, trades=None):
        self.rtdb, self.docs, self.trades, self.scritture = rtdb, docs or {}, trades or [], []

    def get_rtdb(self, ramo):
        return self.rtdb.get(ramo)

    def get_doc(self, collezione, doc):
        return self.docs.get((collezione, doc))

    def query_collection(self, collezione, **kw):
        return list(self.trades) if collezione == "trades" else []

    def set_rtdb(self, *a, **k):
        self.scritture.append(("set_rtdb", a))

    def set_doc(self, *a, **k):
        self.scritture.append(("set_doc", a))


class _Demo:
    """Il cliente finto del conto demo: solo GET, righe dall'ora di inizio in ordine, al massimo ``limit`` (come Binance)."""

    def __init__(self, binance):
        self.b, self.chiamate = binance, []

    def chiedi(self, metodo, percorso, parametri=None, firmata=False):
        p = dict(parametri or {})
        assert metodo == "GET" and firmata
        self.chiamate.append(percorso)
        if percorso == "/fapi/v1/commissionRate":
            return {"symbol": "BTCUSDT", "makerCommissionRate": "0.000200", "takerCommissionRate": "0.000400"}
        if percorso == "/fapi/v2/positionRisk":
            return self.b["posizioni"]
        righe = self.b[p["incomeType"]] if percorso == "/fapi/v1/income" else self.b["esecuzioni"].get(p["symbol"], [])
        return sorted((r for r in righe if p["startTime"] <= r["time"] <= p["endTime"]), key=lambda r: r["time"])[: int(p.get("limit") or 500)]


class _Risposta:
    def __init__(self, dati, codice=200, headers=None):
        self.dati, self.status_code, self.headers = dati, codice, headers or {}

    def json(self):
        return self.dati


def _rendimento(simbolo, giorno):
    return ((sum(map(ord, simbolo)) + giorno * 7) % 11 - 5) / 100          # fra −5% e +5%, fisso per moneta e giorno


def _candele(chiamate=None, assenti=()):
    """requests.get finto per le candele giornaliere del prezzo mark (una richiesta per moneta)."""
    def get(url, params=None, timeout=None):
        assert url == ss.PREZZI_MARK_GIORNALIERI and timeout
        if chiamate is not None:
            chiamate.append(params["symbol"])
        if params["symbol"] in assenti:
            return _Risposta({"code": -1121, "msg": "Invalid symbol."}, 400)
        out = []
        for d in range(int(params["startTime"] // 86_400_000), int(params["endTime"] // 86_400_000) + 1):
            apertura = 1.0 + d % 3
            out.append([d * 86_400_000, f"{apertura}", "0", "0", f"{apertura * (1 + _rendimento(params['symbol'], d))}", "0"])
        return _Risposta(out)
    return get


def _dati(giorni_equity=20, giorni_diario=23):
    """Firebase, Binance e i trade del vecchio sistema della dimensione di oggi (27 novembre 2026)."""
    rng = random.Random(26)
    paper = {s: w for s, (w, _) in PESI.items()}
    rtdb = {"/bot_status": {"state": "running", "regime": "high_uncertainty", "dry_run": True, "heartbeat": ORA - 30, "price_stream": False},
            "/account/equity": 817.25,
            "/decision_status": {"outcome": "flat", "ts": ORA - 60, "assets_evaluated": 80, "signals_found": 2,
                                 "best_symbol": "PARTIUSDT", "best_strategy": "gen_7b4a474b", "best_adjusted": 0.41, "threshold": 0.62,
                                 "reason": "gate fermo dal 13 ottobre (ops/gate_fermo): nessun segnale sopra la soglia"}}
    for ramo, eq, n in (("/paper_f5", 10777.72, 59), ("/paper_g1", 10700.73, 58), ("/paper_g11", 10707.28, 53), ("/paper_g1n", 10993.76, 58)):
        rtdb[f"{ramo}/stato"] = {"stato": "acceso", "aggiornato": ORA - 700, "equity": eq, "capitale": 10000, "rendimento": eq / 1e4 - 1,
                                 "costi_totali": 35.36, "funding_totale": -526.43, "long": 29, "short": 29, "ultimo_lunedi": "2026-11-27",
                                 "limite_variazioni": 1921, "limite_eseguite": 1914, "costi_a_mercato_totali": 101.43, "ordini_in_attesa": 0}
        rtdb[f"{ramo}/prova"] = {"eseguita": ORA - 30 * 86400, "lunedi": "2026-10-23", "universo": 100, "long": 20, "short": 20,
                                 "pesi_maggiori": {s: w for s, w in list(paper.items())[:10]}}
        rtdb[f"{ramo}/posizioni"] = dict(list(paper.items())[:n]) if ramo != "/paper_f5" else {**paper, "BTCUSDT": 0.01}
    rtdb["/paper_eventi/stato"] = {"stato": "acceso", "aggiornato": ORA - 1300, "equity": 10313.71, "capitale": 10000, "rendimento": 0.0314,
                                   "aperte_n3": 0, "aperte_e4": 0, "chiuse": 1, "rendimento_medio": 0.6274, "e4_in_attesa": 0}
    rtdb["/demo_binance/stato"] = {"stato": "acceso", "aggiornato": ORA - 1560, "equity": 1000.05, "capitale_iniziale": 1000.0,
                                   "rendimento": 0.00005, "long": 27, "short": 25, "limite_eseguiti": 818, "limite_totali": 867,
                                   "ordini_in_attesa": 0, "conto_ridotto": 1000, "valore_vero_del_conto_demo": 5347.96, "stop_a": 688.73,
                                   "massimo": 1059.59, "dal_massimo": -0.0562, "capitale_in_attesa": None}
    rtdb["/demo_binance/ribilanciamenti"] = {
        _g(d): {"ordini": 10, "equity": 1000.0, "monete_mancanti_sul_demo": ["IRYSUSDT"], "rifiutati": RIFIUTATI, "entrate": 2, "uscite": 1,
                "sotto_il_minimo": {"variazioni": 43, "valore_in_frazione_del_conto": 0.072}, "piazzati": d * 86400 + 900,
                "limite": {"ordini": 10, "eseguiti_a_limite": 10, "a_mercato": 0, "controllato": d * 86400 + 4500}, "solo_eventi": False}
        for d in range(OGGI - 20, OGGI + 1)}
    rtdb["/demo_binance/margine"] = {"controllato": ORA - 1560, "separati_trovati": []}
    rtdb["/demo_binance/confronto"] = {"ora": ORA - 1560, "monete": 57, "scarto_totale": 0.147,
                                       "differenze": [{"simbolo": "LITUSDT", "scarto": -0.034}]}
    rtdb["/demo_binance/errore"] = {"ora": ORA - 2 * 86400, "testo": "HTTPSConnectionPool(host='demo-fapi.binance.com', port=443): "
                                                                     "Read timed out. (read timeout=15)"}
    dg = range(OGGI - giorni_equity + 1, OGGI + 1)
    rtdb["/demo_binance/giorni"] = {_g(d): round(1000 * (1 + rng.uniform(-0.03, 0.03)), 2) for d in dg}
    rtdb["/paper_g1/giorni"] = {_g(d): round(10700 * (1 + rng.uniform(-0.03, 0.03)), 2) for d in range(OGGI - giorni_diario + 1, OGGI + 1)}
    rtdb["/paper_eventi/giorni"] = {_g(d): 10313.71 for d in dg}
    rtdb["/demo_binance/diario"] = {_g(d): {"equity": 1000.0, "long": 27, "short": 25,
                                            "entrate": {"funding_incassato": rng.uniform(0.3, 2.7), "commissioni_pagate": rng.uniform(0, 0.7)}}
                                    for d in range(OGGI - giorni_diario + 3, OGGI + 1)}
    rtdb["/paper_g1/diario"] = {_g(d): {"equity": 10700.0, "long": 29, "short": 29, "costi_totali": 1.6 * i, "funding_totale": -24.1 * i}
                                for i, d in enumerate(range(OGGI - giorni_diario + 1, OGGI + 1))}
    rtdb["/conto_vero/stato"] = {"stato": "spento: manca l'interruttore ops/conto_vero_acceso", "acceso": False, "aggiornato": ORA - 9e5}
    rtdb["/paper_g1/funding"] = {
        _g(d): {**{f"{h:02d}:00": {"incassato": rng.uniform(0.5, 2.5), "monete": 58,
                                   "maggiori": {s: rng.uniform(-0.2, 0.9) for s in list(paper)[3:13]}} for h in (0, 8, 16) if d * 86400 + h * 3600 <= ORA},
                **{f"{h:02d}:00": {"incassato": rng.uniform(0.1, 1.0), "monete": 9} for h in (1, 2, 3, 4, 12, 20) if d * 86400 + h * 3600 <= ORA}}
        for d in range(OGGI - 2, OGGI + 1)}
    # Binance: funding per regolamento (00, 08, 16 per 52 monete; altre ore per 17), commissioni ed esecuzioni (95 su 37 monete)
    demo = [s for s, (_, w) in PESI.items() if w]
    funding, n = [], 0
    for d in range(OGGI - 7, OGGI + 1):
        for h in range(24):
            t = d * 86_400_000 + h * 3_600_000
            for s in (demo if h in (0, 8, 16) else demo[-17:] if h % 4 == 0 else []):
                if t <= ORA * 1000:
                    n += 1
                    funding.append({"symbol": s, "incomeType": "FUNDING_FEE", "income": f"{rng.uniform(-0.002, 0.03):.6f}", "asset": "USDT",
                                    "time": t, "tranId": n})
    commissioni, esecuzioni = [], {}
    for i in range(95):
        s, t = demo[i % 37], (OGGI - 5 + i % 6) * 86_400_000 + 900_000 + i * 1000
        c = rng.uniform(0.0005, 0.005)
        commissioni.append({"symbol": s, "incomeType": "COMMISSION", "income": f"{-c:.6f}", "asset": "USDT", "time": t, "tranId": 10**6 + i})
        esecuzioni.setdefault(s, []).append({"id": i, "symbol": s, "quoteQty": f"{c / 0.0003:.4f}", "commission": f"{c:.6f}",
                                             "commissionAsset": "USDT", "maker": i % 2 == 0, "time": t})
    posizioni = [{"symbol": s, "positionAmt": "1" if w > 0 else "-1", "notional": f"{w * 1000.05:.4f}"} for s, (_, w) in PESI.items() if w]
    binance = {"FUNDING_FEE": funding, "COMMISSION": commissioni, "esecuzioni": esecuzioni, "posizioni": posizioni}
    # il vecchio sistema: 249 coppie validate su 278 nel registro, l'ultimo run, l'autopsia, il supervisore, 784 trade chiusi
    coppie = {f"C{i}USDT|gen_{i:08x}": {"symbol": f"C{i}USDT", "strategy": f"gen_{i:08x}", "generated": True, "pass_count": 3,
                                        "last_pf": 2.213, "last_pnl_pct": 0.004, "last_max_dd": 0.002,
                                        "last_params": {"scale_r_mults": [1.5, 3.0, 5.0], "sl_to_breakeven": True, "profit_lock_keep": 0.65}}
              for i in range(278)}
    docs = {("strategy_registry", "validated"): {"pairs": encode_pairs(coppie), "validated": list(coppie)[:249], "ready": True,
                                                 "coverage": 0.8, "ready_fraction": 0.6, "coins_covered": 64, "universe_size": 80,
                                                 "min_passes": 3, "universe_coins": [f"C{i}USDT" for i in range(80)],
                                                 "updated_at": ORA - 45 * 86400},
            ("strategy_params", "current"): {"entries": encode_pairs({f"C{i}USDT|breakout": {"symbol": f"C{i}USDT"} for i in range(1320)}),
                                             "passed": "[]", "updated_at": ORA - 67 * 86400},
            ("supervisor", "state"): {"updated_at": ORA - 1080, "validated": 278, "ready": True, "pass_rate": 0.0032,
                                      "tuning": {"GATE_WIN_RATE_FLOOR": 0.396614},
                                      "history": [{"kind": "none", "reason": "GATE 1 superato: il paper opera, la taratura si ferma"}] * 5},
            ("calibration", "current"): {"verdict": "insufficiente", "trades": 784, "correlation": 0.031, "trust": 1.0,
                                         "note": "la confidenza non ordina i trade: correlazione sotto 0,1, influenza neutra (x1.0)"}}
    criteri = {"regime": 22, "trades": 6, "consistency": 17, "recovery": 64, "total_return": 1207, "holdout": 1, "pf_ex_top": 3}
    docs[("gate_autopsy", "current")] = {"evaluated": 1320, "passed": 0, "updated_at": ORA - 67 * 86400, "binding": criteri, "near_miss_count": 1}
    docs[("gate_autopsy", "discover")] = {"evaluated": 34048, "passed": 113, "updated_at": ORA - 45 * 86400,
                                          "binding": {k: v * 23 for k, v in criteri.items()}, "near_miss_count": 40}
    uscite = ["stop_loss"] * 344 + ["trailing_stop"] * 339 + ["scale_out"] * 74 + ["time_exit"] * 16 + ["take_profit"] * 7 + ["kill_switch"] * 4
    trades = [{"trade_id": f"t{i}", "symbol": f"C{i % 60}USDT", "pnl": rng.uniform(-1.6, 1.4), "exit_reason": u,
               "exit_ts": ORA - 50 * 86400 - i * 3600, "entry_time": ORA - 50 * 86400 - i * 3600 - 7200, "exit_time": ORA - 50 * 86400 - i * 3600,
               "scale_stage_reached": i % 4 if i % 9 == 0 else 0, "mfe_r": rng.uniform(0, 4), "total_cost_usdt": 0.118,
               "commission_usdt": 0.067, "spread_usdt": 0.051, "funding_paid_usdt": 0.0005, "gross_pnl_usdt": -0.115,
               "costs_are_estimated": True}
              for i, u in enumerate(uscite)]
    return rtdb, docs, trades, binance


def _stato(monkeypatch, dati=None, macchina=MACCHINA, chiamate_prezzi=None):
    rtdb, docs, trades, binance = dati or _dati()
    fb = _Fb(rtdb, docs, trades)
    demo = _Demo(binance)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setattr(ss, "get_firebase", lambda: fb)
    monkeypatch.setattr(ss, "cliente_di_sola_lettura", lambda: demo)
    monkeypatch.setattr(ss, "_benchmark_return", lambda ts: 0.0754)
    monkeypatch.setattr(ss.time, "time", lambda: ORA)
    monkeypatch.setattr(ss, "PAUSA_TRA_RICHIESTE_S", 0.0)                 # le pause fra le richieste a Binance
    monkeypatch.setattr(ss, "_esegui_comando", lambda c: macchina[c[0]])
    monkeypatch.setattr("requests.get", _candele(chiamate_prezzi))
    return ss.build(), fb, demo


def _sezioni(testo):
    out, titolo = {}, None
    for riga in testo.split("\n"):
        if riga.startswith("## "):
            titolo = riga
            out[titolo] = []
        if titolo:
            out[titolo].append(riga)
    return {k: "\n".join(v) for k, v in out.items()}


def _sezione(testo, inizio):
    return next(v for k, v in _sezioni(testo).items() if k.startswith(inizio))


# ---- salute-1: la risposta tipica sta nei 20.000 caratteri, e non perde le righe del demo ----
def test_la_risposta_tipica_sta_nei_20000_caratteri_dell_agente(monkeypatch):
    testo, fb, demo = _stato(monkeypatch)
    uscita = "[firebase] connesso (Firestore + RTDB)\n" + testo + "\n"     # quello che l'agente riceve (print, risposta 0778)
    assert len(uscita) < ops_agent.MAX_OUTPUT == 20_000
    assert ops_agent.truncate(uscita) == uscita                             # niente «caratteri omessi»
    assert len(testo) <= ss.LIMITE_DELLA_RISPOSTA and "restano fuori" not in testo     # il ripiego non è scattato
    # i dati finti sono almeno della dimensione di oggi, sezione per sezione
    for inizio, minimo in DIMENSIONI_DI_OGGI.items():
        assert len(_sezione(testo, inizio)) + 1 >= 0.95 * minimo, (inizio, len(_sezione(testo, inizio)), minimo)
    # le righe del demo che la risposta perdeva (audit: dal 18 e dal 25 novembre) ci sono, con le tabelle del funding
    for riga in ("Le 10 monete con il funding più grande nei 5 giorni chiusi", "- monete del paper G1 che il demo non ha avuto",
                 "- il paper G1 di oggi contro il funding del demo, per nome", "| giorno | totale | 00 | 08 | 16 | altre ore |",
                 "- monete: paper 58, demo 52", "| regolamento | demo | paper | demo meno paper |", "- regolamento 2026-11-27 00"):
        assert riga in testo, riga
    # la tabella delle 249 coppie validate non c'è più: il GATE 1 è una riga
    assert "Strategie VALIDATE" not in testo and "| C1USDT |" not in testo
    assert "- GATE 1: 249 coppie validate (>= 3 pass OOS) su 278 nel registro, copertura 64/80 crypto; aggiornato 2026-10-13" in testo
    assert fb.scritture == []                                               # sola lettura: nessuna scrittura su Firebase
    assert set(demo.chiamate) == {"/fapi/v1/commissionRate", "/fapi/v1/income", "/fapi/v1/userTrades", "/fapi/v2/positionRisk"}


def test_il_vecchio_sistema_e_in_fondo(monkeypatch):
    testo, _, _ = _stato(monkeypatch)
    titoli = [r for r in testo.split("\n") if r.startswith("## ")]
    i = titoli.index("## Vecchio sistema (fermo dal 13 ottobre)")
    assert "## Bot" not in titoli and not any(t.startswith("## GATE 1") for t in titoli)
    assert [t for t in titoli[:i] if t.startswith(("## Ultima decisione", "## Ultimo run", "## Trade chiusi", "## Calibrazione"))] == []
    assert titoli[i - 1].startswith("## G1: il funding per regolamento") and titoli[-1] == "## Calibrazione della confidenza"
    vecchio = _sezione(testo, "## Vecchio sistema")
    assert "- regime: high_uncertainty" in vecchio and "- equity: **$817.25**" in vecchio and "- GATE 1: 249 coppie" in vecchio
    # il battito e il DRY_RUN sono del processo che fa girare demo, paper e conto vero: in cima, non qui (revisione del 27 novembre, 203)
    assert "- stato: " not in vecchio and "DRY_RUN" not in vecchio and "heartbeat" not in vecchio
    assert testo.split("\n")[2].startswith("- macchina: ")                  # salute-8: la riga in cima


def test_le_tabelle_giornaliere_restano_di_14_giorni(monkeypatch):
    oggi, _, _ = _stato(monkeypatch)
    fra_due_mesi, _, _ = _stato(monkeypatch, _dati(giorni_equity=80, giorni_diario=80))
    for testo in (oggi, fra_due_mesi):
        sezione = _sezione(testo, "## G1: il demo contro il paper")
        righe = [r for r in sezione.split("\n") if r.startswith("| 2026-")]
        assert len(righe) == 2 * ss.GIORNI_TABELLE and righe[ss.GIORNI_TABELLE - 1].startswith(f"| {_g(OGGI)} |")
        assert "Gli ultimi 14 giorni: i " in sezione and "; gli ultimi 14 giorni." in sezione
    assert "- dal 2026-11-09 (19 giorni)" in oggi and "(79 giorni)" in fra_due_mesi       # il totale resta su tutti i giorni
    # non cresce più di una riga al giorno: le righe sono le stesse, i caratteri cambiano solo con i numeri casuali dei dati finti
    assert len(fra_due_mesi.split("\n")) == len(oggi.split("\n")) and abs(len(fra_due_mesi) - len(oggi)) < 150


def test_oltre_il_limite_restano_fuori_prima_le_sezioni_del_vecchio_sistema(monkeypatch):
    pieno, _, _ = _stato(monkeypatch)
    monkeypatch.setattr(ss, "LIMITE_DELLA_RISPOSTA", len(pieno) - 1)      # un carattere di troppo
    testo, _, _ = _stato(monkeypatch)
    assert len(testo) < len(pieno) - 3000
    assert "- le altre sezioni del vecchio sistema (" in testo and "sono intere in docs/state.md (lo fa GitHub)" in testo
    assert "## Trade chiusi" not in testo and "## Supervisore" not in testo and "## Ultima decisione" not in testo
    assert "- GATE 1: 249 coppie" in testo                                 # la testa del vecchio sistema resta
    assert "- DRY_RUN: True" in _sezione(testo, "## Il bot (un solo processo")   # il battito e il DRY_RUN in cima, sempre
    prima, dopo = _sezioni(pieno), _sezioni(testo)
    for titolo, righe in prima.items():                                    # le sezioni del sistema di oggi restano intere
        if not titolo.startswith(("## Vecchio", "## Ultima", "## Ultimo", "## Dove", "## Supervisore", "## Trade", "## Deriva", "## Calib")):
            assert dopo[titolo] == righe, titolo


# ---- revisione del 27 novembre 2026, problema 203: il battito e il DRY_RUN del bot in cima, non sotto il vecchio sistema ----
def test_il_battito_e_il_dry_run_del_bot_sono_in_cima(monkeypatch):
    testo, _, _ = _stato(monkeypatch)
    righe = testo.split("\n")
    assert righe[2].startswith("- macchina: ") and righe[4] == "## Il bot (un solo processo: paper, demo e conto vero)"
    tre = ["- stato: **running** (🟢 online)", "- ultimo heartbeat: 2026-11-27 04:17 UTC", "- DRY_RUN: True"]
    assert righe[5:8] == tre
    i_f5, i_vecchio = testo.index("## Paper F5"), testo.index("## Vecchio sistema")
    for riga in tre:
        assert testo.index(riga) < i_f5 and riga not in testo[i_vecchio:]
    assert len(testo) <= ss.LIMITE_DELLA_RISPOSTA and "restano fuori" not in testo


def test_un_bot_bloccato_o_un_dry_run_falso_si_vedono():
    fermo = ss.sezione_del_bot(_FbSemplice({"/bot_status": {"state": "running", "heartbeat": 0, "dry_run": True}}))
    assert fermo[1].startswith("- stato: **running** (🔴 **offline**: nessun battito da ") and fermo[3] == "- DRY_RUN: True"
    falso = ss.sezione_del_bot(_FbSemplice({"/bot_status": {"state": "running", "heartbeat": "rotto", "dry_run": False}}))
    assert falso[1] == "- stato: **running** (🔴 **offline**)" and falso[2] == "- ultimo heartbeat: —"
    assert falso[3] == "- DRY_RUN: False **⚠️ non vero: i soldi veri non sono più bloccati dal DRY_RUN**"
    assert ss.sezione_del_bot(_FbSemplice({}))[1:4] == ["- stato: **—** (🔴 **offline**)", "- ultimo heartbeat: —", "- DRY_RUN: —"]


# ---- problema 205: su GitHub nessuno taglia la risposta, il ripiego non scatta e docs/state.md resta intero ----
def test_su_github_il_ripiego_non_scatta(monkeypatch):
    pieno, _, _ = _stato(monkeypatch)
    monkeypatch.setattr(ss, "LIMITE_DELLA_RISPOSTA", 1000)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    testo = ss.build()
    assert "restano fuori" not in testo and "## Trade chiusi" in testo and "## Calibrazione della confidenza" in testo
    monkeypatch.delenv("GITHUB_ACTIONS")
    assert "restano fuori" in ss.build()                                   # sulla macchina sì


# ---- salute-8: disco, memoria e orologio in una riga, che non rompe mai lo stato ----
def test_la_riga_della_macchina(monkeypatch):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    assert ss.riga_della_macchina(lambda c: MACCHINA[c[0]]) == (
        "- macchina: disco / libero 31G su 75G (usato 57%) · memoria disponibile 8300 MB su 15623, swap usata 0 MB su 0 · "
        "orologio sincronizzato (NTP active)")
    pieno = {**MACCHINA, "df": MACCHINA["df"].replace("57%", "93%"), "timedatectl": MACCHINA["timedatectl"].replace(
        "synchronized: yes", "synchronized: no"), "free": MACCHINA["free"].replace("8300", "900")}
    riga = ss.riga_della_macchina(lambda c: pieno[c[0]])
    assert "**disco / libero 31G su 75G (usato 93%): quasi pieno**" in riga and "**orologio NON sincronizzato** (NTP active)" in riga
    assert "**memoria disponibile 900 MB su 15623, swap usata 0 MB su 0: quasi finita**" in riga
    # il formato di prima di systemd 239 («NTP synchronized», «Network time on») e free senza «available»
    vecchio = {**MACCHINA, "timedatectl": "NTP synchronized: yes\nNetwork time on: yes\n",
               "free": "             total       used       free     shared    buffers     cached\nMem:         15623      12389       3234 0 1 2\n"}
    assert ss.riga_della_macchina(lambda c: vecchio[c[0]]).endswith(
        "memoria disponibile 3234 MB su 15623 · orologio sincronizzato (NTP yes)")


@pytest.mark.parametrize("guasto", [FileNotFoundError("df"), subprocess.TimeoutExpired("timedatectl", 5), RuntimeError("codice 1"),
                                    "uscita strana", ""])
def test_un_comando_che_manca_o_sbaglia_non_rompe_la_riga(monkeypatch, guasto):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)

    def esegui(c):
        if isinstance(guasto, Exception):
            raise guasto
        return guasto
    riga = ss.riga_della_macchina(esegui)
    assert riga.startswith("- macchina: disco non letto (") and " · memoria non letto (" in riga and " · orologio non letto (" in riga


def test_i_comandi_veri_senza_shell_e_con_un_tempo_massimo(monkeypatch):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    visti = []

    def finto(comando, **kw):
        visti.append((comando, kw))
        return subprocess.CompletedProcess(comando, 0, stdout=MACCHINA[comando[0]], stderr="")
    monkeypatch.setattr(subprocess, "run", finto)
    assert "disco / libero 31G" in ss.riga_della_macchina()
    assert [c for c, _ in visti] == [["df", "-hP", "/"], ["free", "-m"], ["timedatectl"]]
    assert all(kw["timeout"] == ss.TEMPO_COMANDO_S and kw["env"]["LC_ALL"] == "C" and "shell" not in kw for _, kw in visti)
    monkeypatch.setattr(subprocess, "run", lambda comando, **kw: subprocess.CompletedProcess(comando, 1, stdout="", stderr="no"))
    with pytest.raises(RuntimeError, match="codice 1"):
        ss._esegui_comando(["df"])


def test_su_github_la_riga_della_macchina_non_si_legge(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    assert ss.riga_della_macchina(lambda c: pytest.fail("su GitHub nessun comando")).startswith("- macchina: non letta qui")


# ---- salute-9 e ordini-2/ordini-4: il conto vero si chiama F5 e mostra l'ultimo ribilancio ----
class _FbSemplice:
    def __init__(self, d):
        self.d = d

    def get_rtdb(self, k):
        return self.d.get(k)


def test_il_conto_vero_si_chiama_con_la_sua_strategia(monkeypatch):
    import bot.portafoglio.conto_vero as cv
    # dal 25 novembre 2026 il conto vero esegue F5 (decisione del proprietario): il titolo lo legge dal codice, non lo scrive a mano
    assert ss.strategia_del_conto_vero() == cv.STRATEGIA
    assert ss.sezione_conto_vero(_FbSemplice({}))[0].startswith(f"## {cv.STRATEGIA} sul conto vero di Binance (soldi veri;")
    monkeypatch.setattr(cv, "STRATEGIA", "G1")
    assert ss.sezione_conto_vero(_FbSemplice({}))[0].startswith("## G1 sul conto vero di Binance")
    monkeypatch.setattr(ss, "strategia_del_conto_vero", lambda: "")
    assert ss.sezione_conto_vero(_FbSemplice({}))[0].startswith("## Il conto vero di Binance")


def test_il_conto_vero_mostra_l_ultimo_ribilancio():
    base = {"/conto_vero/stato": {"stato": "acceso", "equity": 281.0, "capitale_iniziale": 280.0, "long": 20, "short": 21, "aggiornato": ORA}}
    assert not [r for r in ss.sezione_conto_vero(_FbSemplice(base)) if "ribilancio" in r]          # se non c'è, niente riga
    testo = "\n".join(ss.sezione_conto_vero(_FbSemplice({**base,
        "/conto_vero/ribilanciamenti": {
            "2026-11-23": {"ordini": 40, "rifiutati": []},
            "2026-11-30": {"ordini": 36, "monete_mancanti_sul_demo": ["NUOVAUSDT"], "solo_eventi": False,
                           "rifiutati": [{"simbolo": "LITUSDT", "errore": "POST /fapi/v1/order: 400 {\"code\":-4140}"},
                                         {"simbolo": "AUSDT", "errore": "margine"}],
                           "sotto_il_minimo": {"variazioni": 15, "valore_in_frazione_del_conto": 0.203},
                           "limite": {"ordini": 36, "eseguiti_a_limite": 33, "a_mercato": 2},
                           "scaduti_senza_mercato": {"ora": ORA, "monete": ["BUSDT", "CUSDT"], "motivo": "versione non approvata"}}},
        "/paper_f5/posizioni": {"LITUSDT": 0.031, "AUSDT": -0.012},
        "/conto_vero/confronto": {"ora": ORA, "monete": 38, "scarto_totale": 0.11, "differenze": [{"simbolo": "LITUSDT", "scarto": -0.031}]}})))
    assert ("- ultimo ribilancio 2026-11-30: 36 ordini, eseguiti a limite 33, a mercato 2; sotto il minimo 15 variazioni (20.3% del "
            "conto); rifiutati 2: LITUSDT (+3.10% in F5) POST /fapi/v1/order: 400 {\"code\":-4140}; AUSDT (-1.20% in F5) margine; "
            "monete senza i filtri del conto vero: NUOVAUSDT; ordini limite scaduti senza il resto a mercato (2026-11-27 04:18 UTC): "
            "2 monete, versione non approvata") in testo
    assert "- posizioni vere contro volute (2026-11-27 04:18 UTC): 38 monete, scarto totale 11.0% del conto; oltre il 2%: LITUSDT -3.1%" in testo
    assert testo.index("ultimo ribilancio") > testo.index("- equity: **$281.00**")


# ---- ordini-5: demo meno paper senza le monete che il demo non ha, con il loro peso a parte ----
def _fb_confronto(ribilanciamenti, posizioni, demo=None, paper=None):
    giorni = ["2026-11-20", "2026-11-21", "2026-11-22"]
    return _FbSemplice({"/demo_binance/giorni": demo or dict(zip(giorni, (1000.0, 1000.0, 979.1))),
                        "/paper_g1/giorni": paper or dict(zip(giorni, (10000.0, 10000.0, 9867.0))),
                        "/paper_g1/posizioni": posizioni, "/demo_binance/ribilanciamenti": ribilanciamenti})


def test_senza_le_monete_mancanti_il_22_novembre():
    # gate2/reports/2026-11-23-G1.md: il 22 novembre demo −2,09%, paper −1,33%; EVAAUSDT, venduta allo 0,84% nel paper e assente sul
    # demo, scende del 63%: vale da sola −0,53 punti della differenza (−0,76); senza di lei la differenza è circa −0,23
    righe = ss.confronto_giorni({"2026-11-21": 1000.0, "2026-11-22": 979.1}, {"2026-11-21": 10000.0, "2026-11-22": 9867.0})
    senza, senza_peso = ss.senza_le_monete_mancanti(righe, {"2026-11-22": {"EVAAUSDT"}}, {"EVAAUSDT": -0.0084},
                                                    {"EVAAUSDT": {"2026-11-22": -0.63}})
    assert righe[0]["differenza"] == pytest.approx(-0.0076, abs=1e-4)
    assert senza["2026-11-22"] == pytest.approx(-0.0076 + 0.0084 * 0.63, abs=1e-4) and senza_peso == set()
    # senza il prezzo il giorno resta vuoto; una moneta senza un peso di oggi non si conta e si dice
    assert ss.senza_le_monete_mancanti(righe, {"2026-11-22": {"EVAAUSDT"}}, {"EVAAUSDT": -0.0084}, {})[0]["2026-11-22"] is None
    s, p = ss.senza_le_monete_mancanti(righe, {"2026-11-22": {"VECCHIAUSDT"}}, {}, {})
    assert s["2026-11-22"] == pytest.approx(righe[0]["differenza"]) and p == {"VECCHIAUSDT"}


def test_le_monete_mancanti_di_ogni_giorno():
    rib = {"2026-11-20": {"monete_mancanti_sul_demo": ["IRYSUSDT"], "rifiutati": [{"simbolo": "LITUSDT", "errore": "-4140"}]},
           "2026-11-20-eventi-0130": {"solo_eventi": True, "rifiutati": [{"simbolo": "EVENTIUSDT"}]},
           "2026-11-22": {"rifiutati": [{"simbolo": "EVAAUSDT"}]}}
    m = ss.monete_mancanti_per_giorno(rib, ["2026-11-19", "2026-11-20", "2026-11-21", "2026-11-22"])
    # il 21 il demo non ha ribilanciato: tiene le posizioni del 20, senza le stesse monete; gli eventi non contano
    assert m == {"2026-11-19": set(), "2026-11-20": {"IRYSUSDT", "LITUSDT"}, "2026-11-21": {"IRYSUSDT", "LITUSDT"}, "2026-11-22": {"EVAAUSDT"}}


def test_la_colonna_e_la_riga_senza_le_monete_che_il_demo_non_ha():
    chiamate = []
    rib = {"2026-11-21": {"rifiutati": [{"simbolo": "EVAAUSDT", "errore": "-1121"}]},
           "2026-11-22": {"rifiutati": [{"simbolo": "EVAAUSDT", "errore": "-1121"}], "monete_mancanti_sul_demo": ["IRYSUSDT", "SENZAUSDT"]}}
    testo = "\n".join(ss.sezione_demo_contro_paper(_fb_confronto(rib, {"EVAAUSDT": -0.0084, "IRYSUSDT": 0.02, "AUSDT": 0.5}),
                                                   now=ORA, http=_candele(chiamate), dormi=lambda s: None))
    assert "| giorno | demo | paper G1 | demo meno paper | eventi nel paper | senza le monete che il demo non ha |" in testo
    d22 = calendar.timegm((2026, 11, 22, 0, 0, 0)) // 86400
    c21 = -0.0084 * _rendimento("EVAAUSDT", d22 - 1)
    c22 = -0.0084 * _rendimento("EVAAUSDT", d22) + 0.02 * _rendimento("IRYSUSDT", d22)
    assert f"| 2026-11-21 | +0.00% | +0.00% | +0.00% | — | {100 * c21:+.2f}% |" in testo
    assert f"| 2026-11-22 | -2.09% | -1.33% | -0.76% | — | {100 * (-0.0076 + c22):+.2f}% |" in testo
    riga = next(r for r in testo.split("\n") if r.startswith("- demo meno paper senza le monete che il demo non ha"))
    assert "stima: pesi del paper di oggi, prezzi mark giornalieri di Binance, senza funding" in riga and "in 2 giorni" in riga
    assert f"media al giorno {100 * (c21 + (-0.0076 + c22)) / 2:+.3f}% (con quelle monete {100 * -0.0038:+.3f}%)" in riga
    assert "quelle di oggi pesano nel paper G1 il 2.84% lordo del conto (3 monete" in riga      # 0,84 + 2,00; SENZAUSDT senza peso
    assert "senza un peso di oggi, non contate: SENZAUSDT" in riga
    assert sorted(chiamate) == ["EVAAUSDT", "IRYSUSDT"]                     # una richiesta per moneta, solo quelle con un peso


def test_senza_prezzi_o_nella_finestra_la_colonna_resta_vuota():
    rib = {"2026-11-22": {"rifiutati": [{"simbolo": "EVAAUSDT"}]}}
    fb = _fb_confronto(rib, {"EVAAUSDT": -0.0084})
    testo = "\n".join(ss.sezione_demo_contro_paper(fb, now=ORA, http=_candele(assenti={"EVAAUSDT"}), dormi=lambda s: None))
    assert "| 2026-11-22 | -2.09% | -1.33% | -0.76% | — | — |" in testo and "prezzi non letti: EVAAUSDT" in testo
    notte = calendar.timegm((2026, 11, 27, 0, 30, 0))
    testo = "\n".join(ss.sezione_demo_contro_paper(fb, now=notte, http=lambda *a, **k: pytest.fail("nessuna richiesta di notte")))
    assert "prezzi non letti: finestra del ribilancio (23:50-01:45 UTC)" in testo
    # senza monete mancanti nessuna richiesta, e la colonna è la differenza
    testo = "\n".join(ss.sezione_demo_contro_paper(_fb_confronto({}, {"EVAAUSDT": -0.0084}), now=ORA,
                                                   http=lambda *a, **k: pytest.fail("nessuna richiesta senza monete mancanti")))
    assert "| 2026-11-22 | -2.09% | -1.33% | -0.76% | — | -0.76% |" in testo
    assert "- demo meno paper senza le monete che il demo non ha: uguale" in testo


def test_la_riga_nella_risposta_tipica(monkeypatch):
    chiamate = []
    testo, _, _ = _stato(monkeypatch, chiamate_prezzi=chiamate)
    riga = next(r for r in testo.split("\n") if r.startswith("- demo meno paper senza le monete che il demo non ha"))
    assert "in 14 giorni" in riga and "quelle di oggi pesano nel paper G1 il 9.49% lordo del conto (5 monete" in riga
    assert sorted(chiamate) == ["EVAAUSDT", "IRYSUSDT", "LITUSDT", "PIEVERSEUSDT", "UAIUSDT"]


def test_un_dato_rotto_non_ferma_lo_stato():
    # la colonna nuova: un elenco di monete che non è un elenco lascia la colonna vuota e lo dice, il resto della sezione c'è
    rib = {"2026-11-22": {"monete_mancanti_sul_demo": 5}}
    testo = "\n".join(ss.sezione_demo_contro_paper(_fb_confronto(rib, {"EVAAUSDT": -0.0084}), now=ORA,
                                                   http=lambda *a, **k: pytest.fail("nessuna richiesta")))
    assert "| 2026-11-22 | -2.09% | -1.33% | -0.76% | — | — |" in testo
    assert "- demo meno paper senza le monete che il demo non ha: non letto (TypeError)" in testo and "- dal 2026-11-21" in testo
    # il ribilancio del conto vero con un numero rotto: la riga lo dice, la sezione resta
    righe = ss.sezione_conto_vero(_FbSemplice({
        "/conto_vero/stato": {"stato": "acceso", "aggiornato": ORA},
        "/conto_vero/ribilanciamenti": {"2026-11-30": {"ordini": 3, "sotto_il_minimo": {"valore_in_frazione_del_conto": "x"}}}}))
    assert "- ultimo ribilancio: non letto (ValueError)" in righe and righe[-1] == ""


# ---- problema 204: le letture pubbliche dei prezzi si fermano al primo 429 o 418, come le altre letture dello stato ----
@pytest.mark.parametrize("codice", [429, 418])
def test_i_prezzi_si_fermano_al_primo_429_o_418(codice):
    chiamate, normale = [], _candele()

    def get(url, params=None, timeout=None):
        chiamate.append(params["symbol"])
        if len(chiamate) == 2:
            return _Risposta({"code": -1003}, codice, headers={"Retry-After": "7"})
        return normale(url, params=params, timeout=timeout)
    simboli = ["AUSDT", "BUSDT", "CUSDT", "DUSDT"]
    out, non_lette, fermo = ss.rendimenti_mark_giornalieri(simboli, "2026-11-20", ORA, http=get, dormi=lambda s: None)
    assert chiamate == ["AUSDT", "BUSDT"] and list(out) == ["AUSDT"] and non_lette == ["BUSDT", "CUSDT", "DUSDT"]
    assert fermo == f"Binance {codice}: letture fermate (Retry-After 7 s)"
    # nella sezione: la riga lo dice, e le monete rimaste sono non lette
    rib = {"2026-11-22": {"rifiutati": [{"simbolo": "EVAAUSDT"}], "monete_mancanti_sul_demo": ["IRYSUSDT", "LITUSDT"]}}
    chiamate.clear()
    testo = "\n".join(ss.sezione_demo_contro_paper(_fb_confronto(rib, {"EVAAUSDT": -0.0084, "IRYSUSDT": 0.02, "LITUSDT": 0.03}),
                                                   now=ORA, http=get, dormi=lambda s: None))
    assert chiamate == ["EVAAUSDT", "IRYSUSDT"]
    assert f"Binance {codice}: letture fermate (Retry-After 7 s); prezzi non letti: IRYSUSDT, LITUSDT" in testo


# ---- problema 206: l'ultimo ribilancio vero è il giorno più alto; «in_corso» a parte; i resti a mercato rifiutati ----
def test_la_chiave_in_corso_non_nasconde_l_ultimo_ribilancio():
    resti = [{"simbolo": "XUSDT", "errore": "POST /fapi/v1/order: 400 {\"code\":-4164}", "peso": -0.0123}]
    righe = ss.sezione_conto_vero(_FbSemplice({
        "/conto_vero/stato": {"stato": "acceso", "aggiornato": ORA},
        "/conto_vero/ribilanciamenti": {
            "2026-11-23": {"ordini": 40},
            "2026-11-30": {"ordini": 36, "limite": {"ordini": 36, "eseguiti_a_limite": 35, "a_mercato": 1}, "resti_rifiutati": resti},
            "2026-11-30-eventi-0130": {"ordini": 2, "solo_eventi": False},
            "in_corso": {"scaduti_senza_mercato": {"ora": ORA, "monete": ["BUSDT"], "motivo": "blocco del codice"}}}}))
    testo = "\n".join(righe)
    assert ("- ultimo ribilancio 2026-11-30: 36 ordini, eseguiti a limite 35, a mercato 1; rifiutati 0; resti a mercato rifiutati 1: "
            "XUSDT (-1.23% del conto) POST /fapi/v1/order: 400 {\"code\":-4164}") in righe
    assert ("- ribilancio senza la chiave degli ordini («in_corso»): ordini limite scaduti senza il resto a mercato "
            "(2026-11-27 04:18 UTC): 1 monete, blocco del codice") in righe
    assert "ultimo ribilancio in_corso" not in testo and "ultimo ribilancio 2026-11-30-eventi" not in testo


def test_i_resti_a_mercato_rifiutati_anche_sul_demo():
    resti = {"0": {"simbolo": "XUSDT", "errore": "-4164"}}                 # Firebase può rendere un elenco come un dizionario
    righe = ss.sezione_demo_binance(_FbSemplice({"/demo_binance/stato": {"stato": "acceso", "aggiornato": ORA},
                                                 "/demo_binance/ribilanciamenti": {"2026-11-27": {"ordini": 5, "resti_rifiutati": resti}}}))
    assert "- ultima decisione 2026-11-27: 5 ordini; resti a mercato rifiutati 1: XUSDT -4164" in righe


# ---- problema 207: il titolo del conto vero dice la strategia del processo, se il conto vero l'ha scritta al suo avvio ----
def test_il_titolo_del_conto_vero_legge_la_strategia_del_processo(monkeypatch):
    monkeypatch.setattr(ss, "strategia_del_conto_vero", lambda: "F5")
    avvio = {"ora": ORA - 3600, "strategia": "G1", "commit_in_esecuzione": "a" * 40}
    stato = {"/conto_vero/stato": {"stato": "spento: manca l'interruttore ops/conto_vero_acceso", "aggiornato": ORA}}
    # fra il commit che cambia la strategia e il riavvio: il processo esegue ancora G1
    righe = ss.sezione_conto_vero(_FbSemplice({**stato, "/conto_vero/avvio": avvio, "/conto_vero/versione": {"commit": "a" * 40}}))
    assert righe[0].startswith("## G1 sul conto vero di Binance")
    assert righe[1] == "- **strategia: nel codice F5, nel processo G1** (avvio del conto vero del 2026-11-27 03:18 UTC): manca il riavvio"
    assert ss.sezione_conto_vero(_FbSemplice({"/conto_vero/avvio": avvio}))[:2] == [righe[0], righe[1]]    # senza versione e senza stato
    # l'avvio è di un processo di prima (il commit di adesso è un altro): vale il codice, niente nota
    righe = ss.sezione_conto_vero(_FbSemplice({**stato, "/conto_vero/avvio": avvio, "/conto_vero/versione": {"commit": "b" * 40}}))
    assert righe[0].startswith("## F5 sul conto vero") and righe[1].startswith("- stato: ")
    # uguali, o senza avvio: il titolo e nessuna nota
    for fb in ({**stato, "/conto_vero/avvio": {**avvio, "strategia": "F5"}}, stato, {**stato, "/conto_vero/avvio": "rotto"}):
        righe = ss.sezione_conto_vero(_FbSemplice(fb))
        assert righe[0].startswith("## F5 sul conto vero") and righe[1].startswith("- stato: ")
