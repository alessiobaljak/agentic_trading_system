"""Le notizie dopo l'audit del 26 novembre 2026: «piena» per sito, gli articoli già visti in tutto l'archivio, le ore in UTC, le sigle
che davano abbinamenti falsi e la prova in avanti (research/notizie/REGOLE.md, nota del 27 novembre). Solo dati finti."""
import gzip
import hashlib
import json
import os
import time
from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from research.notizie import prova_avanti as pa
from research.notizie import raccolta
from research.programma6 import seconda as sc
from research.programma6 import terza as te


@pytest.fixture
def zurigo():
    """Il fuso della macchina sull'ora svizzera per la durata del test (poi quello di prima)."""
    prima = os.environ.get("TZ")
    os.environ["TZ"] = "Europe/Zurich"
    time.tzset()
    yield
    if prima is None:
        os.environ.pop("TZ", None)
    else:
        os.environ["TZ"] = prima
    time.tzset()


def _scrivi(archivio, giorno: str, righe: list):
    with gzip.open(archivio / f"{giorno}.jsonl.gz", "at", encoding="utf-8") as g:
        for a in righe:
            g.write(json.dumps(a, ensure_ascii=False) + "\n")


def _art(link: str, titolo: str, visto: str, fonte: str = "coindesk") -> dict:
    return {"fonte": fonte, "titolo": titolo, "sommario": "", "link": link, "pubblicato": visto,
            "id": hashlib.sha1(link.encode()).hexdigest()[:16], "visto": visto}


# --- la raccolta ---------------------------------------------------------------------------------------------------------------------

def test_piena_si_calcola_per_sito_e_non_per_pagina():
    # il 26 novembre alle 16:18: prima pagina di Crypto Briefing tutta nuova, la seconda 16 nuovi su 30: nessuna perdita
    giro = [("coindesk", 25, 3), ("cryptobriefing", 30, 30), ("cryptobriefing2", 30, 16), ("cryptobriefing3", 30, 0),
            ("cryptobriefing4", 30, 0), ("bitcoinist", 8, 8), ("zycrypto", 0, 0)]
    assert raccolta.note_piena(giro) == ["", "", "", "", "", "piena", ""]
    # tutte le pagine tutte nuove: «piena» una volta sola, sulla riga dell'ultima pagina del sito
    giro = [("beincrypto", 12, 12), ("beincrypto2", 12, 12), ("cryptonews", 20, 1)]
    assert raccolta.note_piena(giro) == ["", "piena", ""]
    # l'ultima pagina che non risponde, con le altre tutte nuove: il sito resta pieno (non si sa se manca qualcosa)
    assert raccolta.note_piena([("cryptobriefing", 30, 30), ("cryptobriefing2", 0, 0)]) == ["", "piena"]
    assert raccolta.sito("cryptobriefing4") == "cryptobriefing" and raccolta.sito("cryptonewsdotnet") == "cryptonewsdotnet"


def test_gli_articoli_gia_visti_si_cercano_in_tutto_l_archivio(tmp_path, monkeypatch):
    monkeypatch.setattr(raccolta, "ARCHIVIO", tmp_path)
    oggi = datetime(2026, 11, 27, 4, 17, tzinfo=timezone.utc)
    vecchio = _art("https://cointelegraph.com/news/what-happened-in-crypto-today", "Here's what happened in crypto today",
                   "2026-11-09 08:17:00")
    _scrivi(tmp_path, "2026-11-09", [vecchio])
    assert vecchio["id"] in raccolta.visti_di_recente(oggi)
    assert vecchio["id"] not in raccolta.visti_di_recente(oggi, giorni=10)      # com'era prima: 18 giorni fa era già uscito


def test_esegui_non_risalva_un_articolo_vecchio_e_scrive_piena_per_sito(tmp_path, monkeypatch):
    from research.trader_copiati import hyperliquid as th
    from research.trader_copiati import liquidazioni as tl
    monkeypatch.setattr(raccolta, "ARCHIVIO", tmp_path)
    monkeypatch.setattr(raccolta, "nomi", lambda oggi: tmp_path / "nomi.json")
    monkeypatch.setattr(raccolta, "tendenze", lambda ora: 0)
    monkeypatch.setattr(th, "esegui", lambda ora, log: 0)
    monkeypatch.setattr(tl, "esegui", lambda ora, log: 0)
    fisso = "https://cointelegraph.com/news/what-happened-in-crypto-today"
    vecchio = _art(fisso, "Here's what happened in crypto today", (datetime.now(timezone.utc) - timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S"))
    _scrivi(tmp_path, vecchio["visto"][:10], [vecchio])
    gia_visto = _art("https://cryptobriefing.com/vecchio", "Vecchio", "2026-11-26 16:18:00")
    _scrivi(tmp_path, "2026-11-26", [gia_visto])
    pagine = {
        "cointelegraph": [{"fonte": "cointelegraph", "titolo": "Here's what happened in crypto today", "sommario": "", "link": fisso,
                           "pubblicato": None}],
        "cryptobriefing": [{"fonte": "cryptobriefing", "titolo": f"N{k}", "sommario": "", "link": f"https://cryptobriefing.com/n{k}",
                            "pubblicato": None} for k in range(3)],
        "cryptobriefing2": [{"fonte": "cryptobriefing2", "titolo": "Vecchio", "sommario": "", "link": "https://cryptobriefing.com/vecchio",
                             "pubblicato": None}],
        "bitcoinist": [{"fonte": "bitcoinist", "titolo": "B", "sommario": "", "link": "https://bitcoinist.com/b", "pubblicato": None}],
    }
    monkeypatch.setattr(raccolta, "FONTI", {k: "" for k in pagine})
    monkeypatch.setattr(raccolta, "leggi_fonte", lambda nome, url: [dict(a) for a in pagine[nome]])
    log = []
    r = raccolta.esegui(log=log.append)
    assert r["nuovi"] == 4                                         # tre di Crypto Briefing e uno di Bitcoinist; la pagina fissa no
    righe = (tmp_path / "giri.csv").read_text().strip().splitlines()[1:]
    note = {x.split(",")[1]: x.split(",")[4] for x in righe}
    assert note == {"cointelegraph": "", "cryptobriefing": "", "cryptobriefing2": "", "bitcoinist": "piena"}
    assert "piene: bitcoinist;" in log[-1]


def test_le_sigle_del_27_novembre_contano_solo_con_il_dollaro():
    el = {"ARKUSDT": {"sigla": "ARK", "nome": "ARK"}, "HIVEUSDT": {"sigla": "HIVE", "nome": "Hive"},
          "GENIUSUSDT": {"sigla": "GENIUS", "nome": "Genius"}, "1000SATSUSDT": {"sigla": "SATS", "nome": "SATS (Ordinals)"},
          "APRUSDT": {"sigla": "APR", "nome": "Capricorn"}, "ANTUSDT": {"sigla": "ANT", "nome": "Autonomi"}}
    falsi = "ARK Invest buys more; HIVE Digital mines; the GENIUS Act passes; Strive SATS shares; 36% APR on stablecoins"
    assert raccolta.citate(falsi, el) == []
    assert sorted(raccolta.citate(falsi, el, set(raccolta.PAROLE_FINO_AL_26_NOVEMBRE))) == \
        ["1000SATSUSDT", "APRUSDT", "ARKUSDT", "GENIUSUSDT", "HIVEUSDT"]
    assert raccolta.citate("$ARK and $sats pump", el) == ["ARKUSDT", "1000SATSUSDT"]
    # ANT resta fuori dalle parole: dal 17 novembre ANTUSDT è il perpetuo sulle azioni di Anthropic (REGOLE.md, nota del 27 novembre)
    assert raccolta.citate("Anthropic shares trade under the ticker ANT", el) == ["ANTUSDT"]
    assert raccolta.PAROLE == set(raccolta.PAROLE_FINO_AL_26_NOVEMBRE) | raccolta.PAROLE_27_NOVEMBRE
    assert not raccolta.PAROLE_FINO_AL_26_NOVEMBRE & raccolta.PAROLE_27_NOVEMBRE


def test_citatore_da_lo_stesso_risultato_di_citate():
    el = {"BTCUSDT": {"sigla": "BTC", "nome": "Bitcoin"}, "ETHUSDT": {"sigla": "ETH", "nome": "Ethereum"},
          "SOLUSDT": {"sigla": "SOL", "nome": "Solana"}, "ONEUSDT": {"sigla": "ONE", "nome": "Harmony"},
          "ARKUSDT": {"sigla": "ARK", "nome": "ARK"}, "OPUSDT": {"sigla": "OP", "nome": "Optimism"},
          "1000PEPEUSDT": {"sigla": "PEPE", "nome": "Pepe"}, "GENIUSUSDT": {"sigla": "GENIUS", "nome": "Genius"},
          "XUSDT": {"sigla": "X", "nome": "X Empire"}, "PUNTOUSDT": {"sigla": "A.B", "nome": "Dot.Coin"}}
    testi = ["Bitcoin and Ether rally", "ETH/BTC at lows; SOLANA up", "$op airdrop and Optimism grants", "ONE more thing about Harmony",
             "ARK Invest", "$ark", "PEPE-USD and Pepe memes", "Genius move by the GENIUS Act", "X Empire tokens, $x", "A.B and Dot.Coin",
             "solana sol Sol SOL", "the ETHUSDT perpetual", "BTC2 and 2BTC", "Ethereum's upgrade", ""]
    for parole in (None, set(raccolta.PAROLE_FINO_AL_26_NOVEMBRE), set()):
        c = raccolta.citatore(el, parole)
        for t in testi:
            assert c(t) == raccolta.citate(t, el, parole), (t, parole is None)


def test_le_ore_dell_archivio_si_leggono_in_utc_con_qualunque_fuso(zurigo):
    x = "2026-11-25 21:14:30"
    assert datetime.fromisoformat(x).astimezone(timezone.utc).hour == 20       # il modo di prima: l'ora svizzera la spostava
    assert raccolta.ora_utc(x) == datetime(2026, 11, 25, 21, 14, 30, tzinfo=timezone.utc)
    assert raccolta.ora_utc("2026-11-25T21:14:30Z") == datetime(2026, 11, 25, 21, 14, 30, tzinfo=timezone.utc)
    assert raccolta.ora_utc("2026-11-25 22:14:30+01:00") == datetime(2026, 11, 25, 21, 14, 30, tzinfo=timezone.utc)
    assert raccolta.ora_utc("") is None and raccolta.ora_utc(None) is None and raccolta.ora_utc("ieri") is None


# --- la prova in avanti --------------------------------------------------------------------------------------------------------------

def test_ogni_articolo_conta_una_volta_nel_giorno_utc_in_cui_lo_abbiamo_visto(tmp_path, monkeypatch, zurigo):
    monkeypatch.setattr(raccolta, "ARCHIVIO", tmp_path)
    a = _art("https://x.com/a", "A", "2026-11-29 00:30:00")             # dopo la mezzanotte UTC: giorno 29 (l − 1 per il 30 novembre)
    b = _art("https://x.com/b", "B", "2026-11-28 23:59:00")
    _scrivi(tmp_path, "2026-11-28", [b])
    _scrivi(tmp_path, "2026-11-29", [a])
    _scrivi(tmp_path, "2026-12-09", [dict(b, visto="2026-12-09 08:17:00")])   # lo stesso collegamento salvato di nuovo dopo 10 giorni
    arts, n = pa.articoli()
    assert n == {"righe": 3, "doppie": 1, "senza_ora": 0}
    assert sorted(g for g, _ in arts) == [sc.giorno(2026, 11, 28), sc.giorno(2026, 11, 29)]


def test_le_finestre_del_segnale():
    T, lun = 200, 150                                     # il lunedì è il giorno 150: l − 2 = 148, l − 29 = 121
    A = np.zeros((T, 3))
    V = np.full((T, 3), 1e6)
    A[148, 0] += 2                                        # l − 2: dentro
    A[149, 0] += 5                                        # l − 1: fuori
    A[121, 0] += 1                                        # l − 29: dentro
    A[120, 0] += 7                                        # l − 30: fuori dai 28 giorni, dentro i giorni raccolti (filtro dei 3 articoli)
    A[120, 1] += 2                                        # moneta 1: 2 articoli soli in tutto, sotto il minimo di 3
    A[30, 2] += 3                                         # moneta 2: 3 articoli 120 giorni prima di l − 2, oltre i 112
    g = pa.segnale(A, V, np.array([lun]), inizio_idx=0)[0]
    assert g[0] == pytest.approx(np.log((3 + 1) / 28e6))
    assert np.isnan(g[1]) and np.isnan(g[2])
    # con la raccolta iniziata il giorno 121 il filtro non vede gli articoli di prima
    A2 = np.zeros((T, 1))
    A2[120, 0], A2[125, 0] = 5, 2
    assert np.isnan(pa.segnale(A2, V[:, :1], np.array([lun]), inizio_idx=121)[0, 0])
    assert np.isfinite(pa.segnale(A2, V[:, :1], np.array([lun]), inizio_idx=0)[0, 0])


SIGLE = [f"Q{chr(65 + j // 26)}{chr(65 + j % 26)}" for j in range(30)]          # QAA, QAB, ...: sigle finte, mai parole comuni


def _pannello_finto(seme: int = 3, al: tuple = (2026, 12, 13)) -> dict:
    t0 = sc.giorno(2026, 4, 1)
    T = sc.giorno(*al) - t0 + 1                           # di norma fino a domenica 13 dicembre: due settimane finite dal 30 novembre
    simboli = [s + "USDT" for s in SIGLE] + ["ARKUSDT"]
    S = len(simboli)
    rng = np.random.default_rng(seme)
    C = 100 * np.exp(np.cumsum(rng.normal(0, 0.03, (T, S)), axis=0))
    O = np.vstack([C[:1], C[:-1]])
    return {"t0": t0, "simboli": simboli, "close": C, "open": O, "high": np.maximum(O, C) * 1.01, "low": np.minimum(O, C) * 0.99,
            "quote_volume": np.full((T, S), 1e7), "funding": rng.normal(1e-4, 1e-4, (T, S))}


def _archivio_finto(tmp_path, monkeypatch):
    arch = tmp_path / "archivio"
    arch.mkdir()
    monkeypatch.setattr(raccolta, "ARCHIVIO", arch)
    monkeypatch.setattr(raccolta, "QUI", tmp_path)
    elenco = {s + "USDT": {"sigla": s, "nome": ""} for s in SIGLE} | {"ARKUSDT": {"sigla": "ARK", "nome": "ARK"}}
    (tmp_path / "nomi_2026-11.json").write_text(json.dumps({"elenco": elenco}))
    k = 0
    for j, s in enumerate(SIGLE):                         # la moneta j ha 3 + j articoli fra il 1° e il 28 novembre
        for i in range(3 + j):
            giorno = f"2026-11-{1 + (i * 7 + j) % 28:02d}"
            _scrivi(arch, giorno, [_art(f"https://x.com/{k}", f"Notizia su {s} oggi", f"{giorno} 12:00:00")])
            k += 1
    for i in range(40):                                   # ARK Invest: abbinamento falso, conta solo senza le sigle del 27 novembre
        _scrivi(arch, "2026-11-20", [_art(f"https://x.com/ark{i}", "ARK Invest buys more Coinbase", "2026-11-20 08:00:00")])
    _scrivi(arch, "2026-12-02", [_art("https://x.com/0", "Notizia su QAA oggi", "2026-12-02 08:17:00")])   # doppione: non conta


def test_il_conto_senza_le_sigle_nuove_e_quello_di_citatore_con_le_parole_di_prima(tmp_path, monkeypatch):
    _archivio_finto(tmp_path, monkeypatch)
    pan = _pannello_finto()
    arts, _ = pa.articoli()
    A = pa.conteggi(pan, arts)
    j = pan["simboli"].index("ARKUSDT")
    assert A[pa.OGGI][:, j].sum() == 0 and A[pa.SENZA][:, j].sum() == 40
    el = json.loads((tmp_path / "nomi_2026-11.json").read_text())["elenco"]
    diretto = raccolta.citatore(el, set(raccolta.PAROLE) - raccolta.PAROLE_27_NOVEMBRE)
    B = np.zeros_like(A[pa.SENZA])
    for g, t in arts:
        for s in diretto(t):
            B[g - pan["t0"], pan["simboli"].index(s)] += 1
    assert (B == A[pa.SENZA]).all()


def test_prova_avanti_sui_dati_finti(tmp_path, monkeypatch):
    _archivio_finto(tmp_path, monkeypatch)
    pan = _pannello_finto()
    uscita = tmp_path / "avanti"
    log = []
    res = pa.esegui(log=log.append, pan=pan, uscita=uscita, limite=False)
    assert res["settimane_finite"] == 2 and res["articoli"]["doppie"] == 1
    scelte = json.loads((uscita / "scelte.json").read_text())
    oggi, senza = scelte["2026-11-30"][pa.OGGI], scelte["2026-11-30"][pa.SENZA]
    # long il quinto con più articoli per dollaro (qui il volume è uguale per tutte), short il quinto con meno
    assert set(oggi["long"]) == {s + "USDT" for s in SIGLE[24:]} and set(oggi["short"]) == {s + "USDT" for s in SIGLE[:6]}
    assert oggi["monete_con_il_segnale"] == 30 and senza["monete_con_il_segnale"] == 31
    assert "ARKUSDT" in senza["long"] and "ARKUSDT" not in oggi["long"]
    assert sum(oggi["long"].values()) == pytest.approx(1, abs=1e-4) and sum(oggi["short"].values()) == pytest.approx(-1, abs=1e-4)
    righe = (uscita / "settimane.csv").read_text().splitlines()
    assert righe[0].startswith("lunedi,GA2C (parole di oggi),monete con il segnale (parole di oggi)") and [r[:10] for r in righe[1:]] == ["2026-11-30", "2026-12-07"]
    assert "G1 a mercato" in righe[0] and (uscita / "RISULTATI.md").exists() and len(log) <= 20
    assert res["numeri"]["GA2C (parole di oggi)"]["settimane"] == 2


def test_il_30_novembre_non_ci_sono_ancora_settimane_finite(tmp_path, monkeypatch):
    _archivio_finto(tmp_path, monkeypatch)
    res = pa.esegui(log=lambda x: None, pan=_pannello_finto(al=(2026, 11, 29)), uscita=tmp_path / "avanti", limite=False)
    assert res["settimane_finite"] == 0
    assert "lunedì 7 dicembre" in (tmp_path / "avanti" / "RISULTATI.md").read_text()


def test_g1_a_limite_parte_dal_giorno_prima(monkeypatch):
    # con le spese «a limite» uguali a quelle a mercato, G1 a limite deve tornare G1 a mercato: le spese del primo giorno tenuto sono
    # solo le variazioni di quel giorno, non l'entrata da zero
    from research.programma6 import cinquantaseiesima as cs
    from research.programma6 import cinquantunesima as cu
    monkeypatch.setattr(cs, "spese_a_limite",
                        lambda W, R, giorni, simboli, costo: ((np.abs(cu.variazioni(W, R)) * costo).sum(axis=1), 0, 0, 0))
    pan = _pannello_finto()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    g = pa.g1(pan, ps, limite=True)
    assert list(g.index) == [sc.giorno(2026, 11, 30), sc.giorno(2026, 12, 7)]
    assert np.allclose(g["G1 a limite"], g["G1 a mercato"], atol=1e-6)
    assert (g["G1 a mercato"] != 0).all()


def test_sui_dati_veri_non_parte_prima_del_30_novembre(monkeypatch):
    class Finto(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 11, 29, 23, 59, tzinfo=timezone.utc)
    monkeypatch.setattr(pa, "datetime", Finto)
    monkeypatch.setattr(sc, "pannello", lambda: pytest.fail("il pannello vero non si deve leggere"))
    with pytest.raises(SystemExit, match="30 novembre"):
        pa.esegui(log=lambda x: None)


def test_i_fogli_del_mattino_leggono_le_ore_in_utc_con_qualunque_fuso(zurigo):
    """voce14_lettura._quando (usata anche dai fatti gravi) legge le ore dell'archivio in UTC (27 novembre 2026)."""
    from research.programma7.misure_g1 import voce14_lettura as v14
    assert v14._quando({"pubblicato": "2026-11-25 21:14:30"}) == datetime(2026, 11, 25, 21, 14, 30, tzinfo=timezone.utc)
    assert v14._quando({"pubblicato": "", "visto": "2026-11-25 21:14:30"}) == datetime(2026, 11, 25, 21, 14, 30, tzinfo=timezone.utc)
    assert v14._quando({}) is None
