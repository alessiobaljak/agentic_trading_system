"""Le correzioni dell'audit del 26 novembre 2026 alla raccolta di Hyperliquid (research/trader_copiati/):
* raccolta-6: il foglio del giudice delle balene dice da dove viene il gruppo, scrive che è fatto solo dei conti scelti quando la mappa
  delle liquidazioni ha meno di 10 giorni, e mostra la leva media e massima (regola 5); la misura delle regole 10-11 (i tre conti
  copiati) legge anche `liquidazioni_*.jsonl.gz`;
* raccolta-4: la mappa sceglie i 600 conti con più posizioni aperte fra i primi della classifica; le balene saltano i conti con il conto
  a leva a zero;
* raccolta-7: a ogni giro si salvano interi `metaAndAssetCtxs` e `allMids` in `mercato_AAAA-MM.jsonl.gz`.
Nessuna rete: le chiamate a Hyperliquid sono finte e i file vanno in cartelle temporanee."""
import gzip
import json
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

from research.trader_copiati import conto_hyperliquid as ch
from research.trader_copiati import giudice_balene as gb

UTC = timezone.utc


def _scrivi_gz(f, righe):
    with gzip.open(f, "wt", encoding="utf-8") as g:
        for r in righe:
            g.write(json.dumps(r) + "\n")


def _giri(dal: datetime, al: datetime, passo_ore: int = 4) -> list:
    out, t = [], dal
    while t <= al:
        out.append(t)
        t += timedelta(hours=passo_ore)
    return out


# ------------------------------------------------------------------------------------------------------------------------------
# raccolta-6: il foglio del giudice
# ------------------------------------------------------------------------------------------------------------------------------

MONETE = {"BTC": (2.0, 50_000.0), "ETH": (-50.0, 3_000.0), "SOL": (1_000.0, 150.0), "DOGE": (1e6, 0.2), "XRP": (-1e5, 1.0)}


def _archivio_giudice(tmp_path, primo_giro_mappa: datetime):
    """Un conto scelto («s1», 1 milione, 5 monete, giri dal 12 al 29 novembre) e un conto della mappa («m1») dal giro indicato."""
    righe_pos, righe_liq = [], []
    for k, t in enumerate(_giri(datetime(2026, 11, 12, 0, 17, tzinfo=UTC), datetime(2026, 11, 29, 20, 17, tzinfo=UTC))):
        f = 1 + 0.001 * k * (1 if k % 3 else -1)                 # prezzi che si muovono un poco
        scala = 1.0 if k % 2 else 2.0                              # esposizione lorda che cambia giro per giro
        pos = [{"moneta": m, "quantita": q * scala, "valore": abs(q * scala) * p * f, "entrata": p, "leva": 10}
               for m, (q, p) in MONETE.items()]
        righe_pos.append({"ora": t.strftime("%Y-%m-%d %H:%M"), "letto": 0, "indirizzo": "s1", "conto": 1e6, "posizioni": pos})
        if t >= primo_giro_mappa:
            liq = [[0, m, q, round(abs(q) * p * f, 2), p, None, 5, "cross"] for m, (q, p) in MONETE.items()]
            righe_liq.append({"ora": t.strftime("%Y-%m-%d %H:%M"), "letto_da": "00:00:00", "letto_a": "00:01:00",
                              "conti_della_settimana": "liquidazioni_conti_2026-11-23.json", "conti_letti": 1, "conti": [2e5],
                              "prezzi": {}, "colonne": [], "posizioni": liq})
    _scrivi_gz(tmp_path / "posizioni_2026-11.jsonl.gz", righe_pos)
    _scrivi_gz(tmp_path / "liquidazioni_2026-11.jsonl.gz", righe_liq)
    (tmp_path / "liquidazioni_conti_2026-11-23.json").write_text(json.dumps({"conti": [{"indirizzo": "m1"}]}))
    return righe_pos


@pytest.fixture
def cartelle(tmp_path, monkeypatch):
    arch, usc = tmp_path / "arch", tmp_path / "usc"
    arch.mkdir()
    monkeypatch.setattr(gb, "ARCHIVIO", arch)
    monkeypatch.setattr(gb, "USCITA", usc)
    return arch, usc


def test_il_foglio_dice_che_il_gruppo_e_dei_soli_conti_scelti_se_la_mappa_ha_meno_di_10_giorni(cartelle):
    arch, usc = cartelle
    _archivio_giudice(arch, datetime(2026, 11, 22, 8, 17, tzinfo=UTC))      # come la mappa vera: 8 giorni al 30 novembre
    md = gb.main(datetime(2026, 11, 30, tzinfo=UTC)).read_text()
    assert "**Il gruppo è fatto solo dei conti scelti**: la mappa delle liquidazioni ha 8 giorni di dati" in md
    assert "giudicabili 1 dai conti scelti" in md and "e 0 dalla sola mappa" in md
    dd = {d["indirizzo"]: d for d in json.loads((usc / "2026-11-30.json").read_text())}
    assert dd["s1"]["fonte"] == "scelti" and not dd["s1"]["fuori"]
    assert dd["m1"]["fonte"] == "mappa" and dd["m1"]["fuori"]                # meno di 10 giorni: fuori


def test_con_10_giorni_di_mappa_la_nota_non_c_e_e_i_conti_della_mappa_entrano(cartelle):
    arch, usc = cartelle
    _archivio_giudice(arch, datetime(2026, 11, 12, 0, 17, tzinfo=UTC))
    md = gb.main(datetime(2026, 11, 30, tzinfo=UTC)).read_text()
    assert "fatto solo dei conti scelti" not in md
    assert "giudicabili 1 dai conti scelti (`scelti_*.json`, con le balene) e 1 dalla sola mappa" in md


def test_leva_media_e_massima_della_regola_5(cartelle):
    arch, usc = cartelle
    righe = _archivio_giudice(arch, datetime(2026, 11, 22, 8, 17, tzinfo=UTC))
    md = gb.main(datetime(2026, 11, 30, tzinfo=UTC)).read_text()
    d = next(x for x in json.loads((usc / "2026-11-30.json").read_text()) if x["indirizzo"] == "s1")
    # la leva di ogni giro con un intervallo dopo (tutti tranne l'ultimo): somma dei valori diviso il valore del conto
    leve = [sum(abs(p["valore"]) for p in r["posizioni"]) / r["conto"] for r in righe[:-1]]
    assert d["leva_media"] == pytest.approx(np.mean(leve)) and d["leva_massima"] == pytest.approx(max(leve))
    assert d["leva_massima"] > d["leva_media"] > 0
    assert "leva media / massima" in md and f"{d['leva_media']:.2f} / {d['leva_massima']:.2f}" in md


# ------------------------------------------------------------------------------------------------------------------------------
# raccolta-6: la misura delle regole 10-11 (i tre conti copiati)
# ------------------------------------------------------------------------------------------------------------------------------

def test_le_posizioni_si_leggono_anche_dalla_mappa(tmp_path):
    _scrivi_gz(tmp_path / "posizioni_2026-11.jsonl.gz", [
        {"ora": "2026-11-30 08:17", "indirizzo": "x", "conto": 100.0, "posizioni": [{"moneta": "BTC", "quantita": 1, "valore": 50.0}]}])
    _scrivi_gz(tmp_path / "liquidazioni_2026-11.jsonl.gz", [
        {"ora": "2026-11-30 08:17", "conti_della_settimana": "liquidazioni_conti_2026-11-30.json", "conti": [200.0, None, 300.0],
         "posizioni": [[0, "ETH", -2.0, 20000.0, 1, None, 5, "cross"], [2, "SOL", 3.0, 30000.0, 1, 1, 5, "cross"],
                       [2, "BTC", 1.0, 99999.0, 1, 1, 5, "cross"]]}])
    (tmp_path / "liquidazioni_conti_2026-11-30.json").write_text(
        json.dumps({"conti": [{"indirizzo": "m"}, {"indirizzo": "n"}, {"indirizzo": "x"}]}))
    giro = ch.posizioni_giri(tmp_path)["2026-11-30 08:17"]
    assert giro["m"] == (200.0, [("ETH", -2.0, 20000.0)])
    assert "n" not in giro                                       # non letto in quel giro
    assert giro["x"] == (100.0, [("BTC", 1.0, 50.0)])            # nei due file: contano le posizioni dei conti scelti


def _giudizio(cartella, lunedi: str, voci: dict, scritto_il: str | None = None, correzioni=()):
    cartella.mkdir(parents=True, exist_ok=True)
    x = {"lunedi": lunedi, "giudizi": [{"indirizzo": i, "voce": v, "motivo": "prova"} for i, v in voci.items()],
         "correzioni": list(correzioni)}
    if scritto_il:
        x["scritto_il"] = scritto_il
    (cartella / f"{lunedi}.json").write_text(json.dumps(x))


def test_quale_giudizio_vale_a_ogni_giro(tmp_path):
    _giudizio(tmp_path, "2026-11-30", {"a": "costante"}, "2026-11-30 04:40",
              correzioni=[{"ora": "2026-12-02 10:00", "indirizzo": "a", "voce": "caso", "motivo": "una moneta sola"}])
    _giudizio(tmp_path, "2026-12-07", {"b": "costante"})                     # senza ora: vale dal lunedì alle 08:00
    gg = ch.giudizi(tmp_path)
    t = lambda s: datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=UTC)  # noqa: E731
    assert ch.giudizio_del_giro(gg, t("2026-11-30 04:17")) is None            # scritto dopo il giro
    assert ch.giudizio_del_giro(gg, t("2026-11-30 06:14"))["lunedi"].day == 30
    assert ch.voci_al(ch.giudizio_del_giro(gg, t("2026-12-02 20:17")), t("2026-12-02 20:17")) == {"a": "costante"}
    assert ch.voci_al(ch.giudizio_del_giro(gg, t("2026-12-03 00:17")), t("2026-12-03 00:17")) == {"a": "caso"}  # dal giorno dopo
    assert ch.giudizio_del_giro(gg, t("2026-12-07 04:17"))["lunedi"].day == 30  # fino al giudizio nuovo
    assert ch.giudizio_del_giro(gg, t("2026-12-07 08:17"))["lunedi"].day == 7
    assert ch.giudizio_del_giro(gg, t("2026-12-15 00:17")) is None           # lunedì 14 saltato: niente giudizio


def test_tre_conti_copiati_esposizione_uguale_e_cassa_sotto_i_5_costanti(tmp_path):
    simboli = {"BTCUSDT", "ETHUSDT", "SOLUSDT"}
    giro = {f"c{i}": (100.0, [("BTC", 1.0, 300.0)]) for i in range(4)}        # 4 «costanti» comprati su Bitcoin (leva 3)
    giro["m"] = (1000.0, [("ETH", -1.0, 500.0), ("SOL", 1.0, 500.0)])         # un «mercato»
    voci = {**{f"c{i}": "costante" for i in range(4)}, "m": "mercato"}
    _giudizio(tmp_path, "2026-11-30", voci, "2026-11-30 04:40")
    pos = {"2026-11-30 04:17": giro, "2026-11-30 08:17": giro}
    serie = ch.giri_giudice(simboli, pos, ch.giudizi(tmp_path))
    assert list(serie["a"]["ora"]) == [datetime(2026, 11, 30, 8, 17, tzinfo=UTC)]   # il giro prima del giudizio non conta
    a, b, c = (serie[k].iloc[0] for k in "abc")
    assert a["pesi"] == {} and a["cassa"] == "meno di 5 «costanti»"
    assert c["pesi"] == {"ETHUSDT": pytest.approx(-1.0), "SOLUSDT": pytest.approx(1.0)} and c["conti"] == 1
    # (b): ogni conto a esposizione 2, la media (Bitcoin 2·4/5, Ether −1/5, Solana 1/5), poi il totale a esposizione 2
    lordo = 8 / 5 + 1 / 5 + 1 / 5
    assert b["pesi"] == {"BTCUSDT": pytest.approx(1.6 * 2 / lordo), "ETHUSDT": pytest.approx(-0.2 * 2 / lordo),
                         "SOLUSDT": pytest.approx(0.2 * 2 / lordo)}
    assert b["esposizione"] == pytest.approx(2.0) and b["leva_media_conti"] == pytest.approx((3 * 4 + 1) / 5)
    voci["c4"] = "costante"
    giro["c4"] = (100.0, [("ETH", 1.0, 100.0)])
    _giudizio(tmp_path, "2026-11-30", voci, "2026-11-30 04:40")
    a = ch.giri_giudice(simboli, pos, ch.giudizi(tmp_path))["a"].iloc[0]
    assert a["cassa"] == "" and a["conti"] == 5 and a["esposizione"] == pytest.approx(2.0)


def _ore_finte(h0: int, n: int, crescita: dict) -> dict:
    idx = np.arange(h0, h0 + n)
    return {s: pd.DataFrame({"open": 100.0 * (1 + g) ** np.arange(n)}, index=idx) for s, g in crescita.items()}


def test_misura_settimana_per_settimana_con_paniere_netta_zero_e_g1(tmp_path, monkeypatch):
    arch, giud, usc, g1 = tmp_path / "arch", tmp_path / "giudizi", tmp_path / "usc", tmp_path / "g1"
    arch.mkdir()
    g1.mkdir()
    giri = _giri(datetime(2026, 11, 30, 8, 17, tzinfo=UTC), datetime(2026, 12, 9, 0, 17, tzinfo=UTC))
    righe = []
    for t in giri:
        for i in range(5):
            righe.append({"ora": t.strftime("%Y-%m-%d %H:%M"), "indirizzo": f"c{i}", "conto": 100.0,
                          "posizioni": [{"moneta": "BTC", "quantita": 1, "valore": 100.0}]})
    _scrivi_gz(arch / "posizioni_2026-11.jsonl.gz", [r for r in righe if r["ora"] < "2026-12"])
    _scrivi_gz(arch / "posizioni_2026-12.jsonl.gz", [r for r in righe if r["ora"] >= "2026-12"])
    _giudizio(giud, "2026-11-30", {f"c{i}": "costante" for i in range(5)}, "2026-11-30 04:40")
    h0 = int(giri[0].timestamp() // 3600) - 2
    ore = _ore_finte(h0, 24 * 12, {"BTCUSDT": 0.001, "ETHUSDT": 0.0, "SOLUSDT": 0.0})
    simboli = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    t0 = h0 // 24 - 1
    pan = {"simboli": simboli, "funding": np.zeros((20, 3)), "t0": t0}
    # G1 della settimana dal 30 novembre: 7 giorni a +0,1% netto
    (g1 / "ricalcolo_g1_ricerca_2026-12-07.json").write_text(json.dumps(
        {(datetime(2026, 11, 30) + timedelta(days=d)).strftime("%Y-%m-%d"): {"lordo": 0.0015, "sp_mercato": 0.0003, "funding": 0.0002}
         for d in range(7)}))
    monkeypatch.setattr(ch, "G1_SETTIMANE", g1)
    monkeypatch.setattr(ch, "scarica_giorni", lambda *a, **k: pytest.fail("niente scarico: i prezzi ci sono"))
    r = ch.misura_giudice(log=lambda x: None, uscita=usc, pan=pan, ore=ore, cartella_giudizi=giud, archivio=arch)
    s = r["a"]["settimane"]["2026-11-30"]
    assert s["completa"] and not s["in_cassa"] and s["conti_del_giudizio"] == 5
    # (a) = Bitcoin a esposizione 2 per tutta la settimana, tratto per tratto dall'entrata delle 09:00 del 30 novembre; il paniere
    # (Bitcoin, Ether e Solana in parti uguali) si ribilancia a ogni tratto; spese solo all'entrata (0,06% sul peso 2)
    entrate = [int(t.timestamp() // 3600) + 1 for t in giri]
    fine = int(datetime(2026, 12, 7, tzinfo=UTC).timestamp() // 3600)
    rr = [1.001 ** (h2 - h1) - 1 for h1, h2 in zip(entrate, entrate[1:]) if h1 < fine]
    netti = [2 * r - (2 * 0.0006 if k == 0 else 0.0) for k, r in enumerate(rr)]
    assert s["paniere"] == pytest.approx(np.prod([1 + r / 3 for r in rr]) - 1)
    assert s["netto"] == pytest.approx(np.prod([1 + x for x in netti]) - 1)
    assert s["solo_netta"] == pytest.approx(np.prod([1 + 2 * r / 3 for r in rr]) - 1)
    assert s["netta_zero"] == pytest.approx(np.prod([1 + x - 2 * r / 3 for x, r in zip(netti, rr)]) - 1)
    assert r["b"]["settimane"]["2026-11-30"]["netto"] == pytest.approx(s["netto"])   # stessi conti: tutti «costanti»
    assert r["c"]["settimane"]["2026-11-30"]["in_cassa"]                            # nessun «mercato» o «caso»
    # dopo 8 giorni dal lunedì senza un giudizio nuovo: in cassa
    assert r["a"]["settimane"]["2026-12-07"]["perche_in_cassa"] == ["nessun giudizio valido"]
    md = (usc / "MISURA.md").read_text()
    riga = next(x for x in md.splitlines() if x.startswith("| 2026-11-30 |"))
    assert riga.startswith("| 2026-11-30 | 5 / 5 / 0 |") and "(c) in cassa: nessun conto nel giudizio" in riga
    assert f"| {100 * (1.001 ** 7 - 1):+.2f}% |" in riga                     # G1: lordo − spese − funding = +0,1% al giorno
    assert json.loads((usc / "misura.json").read_text())["giudizi"] == ["2026-11-30"]


def test_senza_giudizi_la_misura_non_fa_niente(tmp_path):
    assert ch.misura_giudice(log=lambda x: None, uscita=tmp_path / "usc", pan={}, cartella_giudizi=tmp_path / "nessuno") == {}
    assert not (tmp_path / "usc").exists()


# ------------------------------------------------------------------------------------------------------------------------------
# raccolta-4 e raccolta-7: la mappa delle liquidazioni (liquidazioni.py)
# ------------------------------------------------------------------------------------------------------------------------------

from research.trader_copiati import hyperliquid as th  # noqa: E402
from research.trader_copiati import liquidazioni as tl  # noqa: E402

META = [{"universe": [{"name": "BTC", "szDecimals": 5, "maxLeverage": 40}, {"name": "ETH", "szDecimals": 4, "maxLeverage": 25}]},
        [{"funding": "0.0000125", "openInterest": "33922.7", "premium": "-0.0002", "dayNtlVlm": "1821636278.7", "markPx": "61500.0"},
         {"funding": "0.00001", "openInterest": "500000.1", "premium": "0.0001", "dayNtlVlm": "900000000.0", "markPx": "2000.0"}]]
MEDI = {"BTC": "61500.5", "ETH": "2000.1", "@107": "35.2"}


def _stato(posizioni: list, valore: float = 1e6) -> dict:
    return {"marginSummary": {"accountValue": str(valore)},
            "assetPositions": [{"position": {"coin": m, "szi": str(q), "positionValue": str(v), "entryPx": "1", "liquidationPx": None,
                                             "leverage": {"value": 5, "type": "cross"}}} for m, q, v in posizioni]}


def _classifica(n: int) -> dict:
    return {"leaderboardRows": [{"ethAddress": f"0x{k:03d}", "accountValue": str(1e7 - k * 1e4),
                                 "windowPerformances": [["month", {"vlm": "2e6", "pnl": "1", "roi": "0.1"}]]} for k in range(n)]}


@pytest.fixture
def rete(tmp_path, monkeypatch):
    """Hyperliquid finto: la classifica, le posizioni dei conti (0x000 il più grande, con posizioni che crescono con il numero del conto,
    zero per i conti pari), allMids e metaAndAssetCtxs; conta le chiamate."""
    chiamate = []
    stati = {f"0x{k:03d}": _stato([] if k % 2 == 0 else [("BTC", 1, 1e4 * k), ("ETH", -1, 2e3)], 0 if k % 2 == 0 else 1e6)
             for k in range(10)}

    def get(url, dati=None, timeout=90, tentativi=3):
        chiamate.append((dati or {}).get("type", url))
        if url == th.CLASSIFICA:
            return _classifica(10)
        if dati["type"] == "clearinghouseState":
            return stati.get(dati["user"])
        return {"allMids": dict(MEDI), "metaAndAssetCtxs": META}[dati["type"]]

    monkeypatch.setattr(th, "_get", get)
    monkeypatch.setattr(tl, "ARCHIVIO", tmp_path)
    monkeypatch.setattr(tl, "QUANTI", 3)
    monkeypatch.setattr(tl, "CANDIDATI", 8)
    monkeypatch.setattr(tl, "PASSO", 0.0)
    monkeypatch.setattr(tl, "RITMO_SCELTA", 1000.0)
    return tmp_path, chiamate, stati


def _righe(f):
    return [json.loads(x) for x in gzip.open(f, "rt", encoding="utf-8") if x.strip()]


def test_la_scelta_del_lunedi_tiene_i_conti_con_piu_posizioni_aperte(rete):
    arch, chiamate, _ = rete
    lunedi = datetime(2026, 11, 30, 0, 17, tzinfo=UTC)
    assert tl.esegui(lunedi, log=lambda x: None) == 3
    scelta = json.loads((arch / "liquidazioni_conti_2026-11-30.json").read_text())
    # candidati: i primi 8 della classifica (0x000-0x007); i dispari hanno posizioni, più grandi per i numeri più alti
    assert [c["indirizzo"] for c in scelta["conti"]] == ["0x007", "0x005", "0x003"]
    assert scelta["candidati"] == 8 and scelta["candidati_tentati"] == 8 and scelta["candidati_letti"] == 8
    assert scelta["regola"].startswith("dal 30 novembre 2026")
    assert scelta["conti"][0]["posizioni_aperte"] == 7e4 + 2e3 and scelta["conti"][0]["conto_a_leva"] == 1e6
    # la lettura della scelta fa da giro: ogni conto si legge una volta sola
    assert chiamate.count("clearinghouseState") == 8
    riga = _righe(arch / "liquidazioni_2026-11.jsonl.gz")[-1]
    assert riga["letto_nella_scelta"] == 3 and riga["conti_letti"] == 3 and riga["conti"] == [1e6, 1e6, 1e6]
    assert {p[1] for p in riga["posizioni"]} == {"BTC"}                   # la posizione da 2.000 dollari non si salva


def test_il_giro_dopo_la_scelta_rilegge_i_600_e_salva_il_mercato_intero(rete):
    arch, chiamate, _ = rete
    tl.esegui(datetime(2026, 11, 30, 0, 17, tzinfo=UTC), log=lambda x: None)
    chiamate.clear()
    assert tl.esegui(datetime(2026, 11, 30, 4, 17, tzinfo=UTC), log=lambda x: None) == 3
    assert chiamate.count("clearinghouseState") == 3 and th.CLASSIFICA not in chiamate
    assert "letto_nella_scelta" not in _righe(arch / "liquidazioni_2026-11.jsonl.gz")[-1]
    mercato = _righe(arch / "mercato_2026-11.jsonl.gz")
    assert [m["ora"] for m in mercato] == ["2026-11-30 00:17", "2026-11-30 04:17"]
    assert mercato[-1]["metaAndAssetCtxs"] == META and mercato[-1]["allMids"] == MEDI      # risposte intere, anche le coppie a pronti
    assert mercato[-1]["allMids_letto"].startswith("20") and mercato[-1]["metaAndAssetCtxs_letto"].startswith("20")


def test_scaduto_il_tempo_si_completa_con_l_ordine_della_classifica(rete, monkeypatch):
    arch, chiamate, _ = rete
    monkeypatch.setattr(tl, "TEMPO_SCELTA", -1)                           # nessun candidato letto in tempo
    assert tl.esegui(datetime(2026, 11, 30, 0, 17, tzinfo=UTC), log=lambda x: None) == 3
    scelta = json.loads((arch / "liquidazioni_conti_2026-11-30.json").read_text())
    assert scelta["candidati_tentati"] == 0 and scelta["candidati_letti"] == 0
    assert [c["indirizzo"] for c in scelta["conti"]] == ["0x000", "0x001", "0x002"]
    assert all(c["posizioni_aperte"] is None for c in scelta["conti"])
    assert chiamate.count("clearinghouseState") == 3                       # letti nel giro come gli altri giorni


def test_il_mercato_si_salva_anche_senza_conti_e_un_suo_errore_non_ferma_la_mappa(rete, monkeypatch):
    arch, chiamate, _ = rete
    vero = th._get

    def senza_classifica(url, dati=None, timeout=90, tentativi=3):
        return None if url == th.CLASSIFICA else vero(url, dati, timeout, tentativi)

    monkeypatch.setattr(th, "_get", senza_classifica)
    assert tl.esegui(datetime(2026, 11, 30, 0, 17, tzinfo=UTC), log=lambda x: None) == 0
    assert _righe(arch / "mercato_2026-11.jsonl.gz")[-1]["metaAndAssetCtxs"] == META

    def rotto(url, dati=None, timeout=90, tentativi=3):
        if (dati or {}).get("type") == "metaAndAssetCtxs":
            raise RuntimeError("risposta strana")
        return vero(url, dati, timeout, tentativi)

    monkeypatch.setattr(th, "_get", rotto)
    log = []
    assert tl.esegui(datetime(2026, 11, 30, 4, 17, tzinfo=UTC), log=log.append) == 3
    assert _righe(arch / "liquidazioni_2026-11.jsonl.gz")[-1]["ora"] == "2026-11-30 04:17"
    assert any("mercato di Hyperliquid non salvato" in x for x in log)


def test_la_settimana_in_corso_resta_con_l_elenco_gia_scelto(rete):
    arch, chiamate, _ = rete
    (arch / "liquidazioni_conti_2026-11-23.json").write_text(json.dumps({"conti": [{"indirizzo": "0x000"}, {"indirizzo": "0x009"}]}))
    assert tl.esegui(datetime(2026, 11, 27, 4, 17, tzinfo=UTC), log=lambda x: None) == 2
    assert th.CLASSIFICA not in chiamate and chiamate.count("clearinghouseState") == 2
    assert _righe(arch / "liquidazioni_2026-11.jsonl.gz")[-1]["conti"] == [0, 1e6]          # 0x000 ha il conto a leva a zero


# ------------------------------------------------------------------------------------------------------------------------------
# raccolta-4: le balene copiate saltano i conti con il conto a leva a zero (hyperliquid.py)
# ------------------------------------------------------------------------------------------------------------------------------

def _riga_balena(indirizzo, conto, vol=2e7, pnl=1.0):
    return {"ethAddress": indirizzo, "accountValue": str(conto),
            "windowPerformances": [["month", {"vlm": str(vol), "pnl": str(pnl), "roi": "0.1"}]]}


def test_le_balene_saltano_i_conti_a_leva_zero(tmp_path, monkeypatch):
    classifica = [_riga_balena(f"b{k}", 1e8 - k * 1e6) for k in range(6)]
    a_leva = {"b0": 1.64e6, "b1": 0.0, "b2": 0.13e6, "b3": 566.0, "b5": 5e5}     # b4: lettura fallita
    monkeypatch.setattr(th, "QUANTI", 3)
    stato = lambda i: None if i == "b4" else {"marginSummary": {"accountValue": str(a_leva[i])}}  # noqa: E731
    note = {}
    s = th.scegli_balene(classifica, stato, note)
    assert [c["indirizzo"] for c in s] == ["b0", "b2", "b4"]                     # b1 e b3 (sotto 10.000 dollari) saltati, b4 come prima
    assert note["esclusi_conto_a_leva_zero"] == ["b1", "b3"] and note["non_letti"] == 1
    assert s[0]["conto_a_leva"] == 1.64e6 and s[2]["conto_a_leva"] is None
    assert [c["indirizzo"] for c in th.scegli_balene(classifica)] == ["b0", "b1", "b2"]   # senza letture: la regola di prima


def test_la_scelta_delle_balene_scrive_gli_esclusi_e_il_giro_resta_uguale(tmp_path, monkeypatch):
    righe = [_riga_balena(f"b{k}", 1e8 - k * 1e6) for k in range(4)]
    stati = {"b0": _stato([("BTC", 1, 5e4)], 2e5), "b1": _stato([], 0), "b2": _stato([("ETH", -2, 4e3)], 1e5), "b3": _stato([], 3e4)}
    chiamate = []

    def get(url, dati=None, timeout=90, tentativi=3):
        chiamate.append((dati or {}).get("user", url))
        return {"leaderboardRows": righe} if url == th.CLASSIFICA else stati.get(dati["user"])

    monkeypatch.setattr(th, "_get", get)
    monkeypatch.setattr(th, "ARCHIVIO", tmp_path)
    monkeypatch.setattr(th, "QUANTI", 2)
    assert th.esegui(datetime(2026, 11, 30, 0, 17, tzinfo=UTC), log=lambda x: None) == 3      # b0, b2 (balene) e b1 (migliori del mese)
    bal = json.loads((tmp_path / "scelti_balene_2026-11-30.json").read_text())
    assert [c["indirizzo"] for c in bal["conti"]] == ["b0", "b2"] and bal["esclusi_conto_a_leva_zero"] == ["b1"]
    assert "esclusi_conto_a_leva_zero" not in json.loads((tmp_path / "scelti_2026-11-30.json").read_text())
    righe_pos = _righe(tmp_path / "posizioni_2026-11.jsonl.gz")
    assert {r["indirizzo"]: r["conto"] for r in righe_pos} == {"b0": 2e5, "b1": 0.0, "b2": 1e5}
    assert righe_pos[0]["posizioni"][0] == {"moneta": "BTC", "quantita": 1.0, "valore": 5e4, "entrata": 1.0, "leva": 5}


def test_il_ritmo_della_scelta_non_supera_le_letture_al_secondo():
    import time
    r = tl._Ritmo(200.0)
    t = time.monotonic()
    for _ in range(21):
        r.aspetta()
    assert time.monotonic() - t >= 20 / 200 - 1e-3                          # 21 chiamate: almeno 20 intervalli da 5 ms


def test_le_letture_della_scelta_hanno_un_tentativo_solo(monkeypatch):
    """Una risposta 429 (troppe richieste) nella scelta non si riprova e non fa aspettare: il conto si salta (prova del 27 novembre: a
    7 letture al secondo 199 risposte 429 su 1.500, e con le attese di 3, 6 e 9 secondi la scelta leggeva 5 conti al secondo)."""
    import urllib.error
    chiamate, attese = [], []

    def rifiuta(req, timeout=None):
        chiamate.append(1)
        raise urllib.error.HTTPError(th.INFO, 429, "Too Many Requests", {}, None)

    monkeypatch.setattr(th.urllib.request, "urlopen", rifiuta)
    monkeypatch.setattr(th.time, "sleep", attese.append)
    assert th._get(th.INFO, {"type": "clearinghouseState", "user": "x"}, timeout=10, tentativi=1) is None
    assert len(chiamate) == 1 and attese == []
    assert th._get(th.INFO, {"type": "allMids"}) is None                     # il giro di sempre: tre tentativi, due attese
    assert len(chiamate) == 4 and attese == [3, 6]


def test_una_lettura_rifiutata_ferma_tutti_e_si_riprova_una_volta(monkeypatch):
    import time
    volte = {}

    def get(url, dati=None, timeout=90, tentativi=3):
        a = dati["user"]
        volte[a] = volte.get(a, 0) + 1
        if a == "rifiuta_sempre" or (a == "rifiuta_una_volta" and volte[a] == 1):
            return None                                                      # come una risposta 429
        return _stato([("BTC", 1, 2e4)])

    monkeypatch.setattr(th, "_get", get)
    monkeypatch.setattr(tl, "RITMO_SCELTA", 1000.0)
    monkeypatch.setattr(tl, "PAUSA_SCELTA", 0.05)
    tentati = []
    t = time.monotonic()
    st = tl.leggi_candidati(["a", "rifiuta_una_volta", "rifiuta_sempre", "b"], time.monotonic() + 30, tentati)
    assert st["rifiuta_una_volta"] and st["a"] and st["b"] and st["rifiuta_sempre"] is None
    assert volte == {"a": 1, "rifiuta_una_volta": 2, "rifiuta_sempre": 2, "b": 1}
    assert sorted(tentati) == ["a", "b", "rifiuta_sempre", "rifiuta_una_volta"]
    assert time.monotonic() - t >= 0.05                                      # almeno una pausa per tutti
