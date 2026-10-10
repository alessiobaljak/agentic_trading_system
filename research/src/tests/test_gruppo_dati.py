"""Test degli strumenti di ``research/src/dati.py`` per la campagna di gruppo
(``research/campagne/GRUPPO/regole.md``, sezione 13), tutti SENZA rete.

Si verifica:

1. ``periodi_gruppo`` (sezione 1, punto 3): sulle 80 schede vere il taglio e'
   il 2023-01-16, con i numeri del coordinamento (349 giorni di validazione,
   93.167 giorni-moneta, obiettivo 65.216, 65.247 di costruzione, da 412 a
   1.112 giorni per moneta); casi sintetici calcolati a mano; con una moneta
   sola le date di ``periodi_campagna``; gli errori;
2. ``leggi_scheda_gruppo`` (sezione 1, punto 2, e sezione 2, punto 8): primo
   mese e fascia di slippage come numero, su tutte le 80 schede e su schede
   finte;
3. il filtro di liquidita' (sezione 2, punto 7): file ``1d`` finti, media sui
   giorni presenti, mese senza candele sotto la soglia, soglia letta da
   ``parametri.yaml``, mese della barra dalla sua apertura in UTC;
4. i rifiuti in campagna (sezione 2, punto 4, sezione 12, punto 4, e sezione
   13): con il marcatore GRUPPO ETHUSDT alza, AAVEUSDT e BTCUSDT no; con il
   marcatore di una moneta sola gli altri simboli alzano; la lista dei
   contratti e l'indice dell'archivio alzano in ogni campagna; senza marcatore
   e con il coordinamento tutto come prima.

Il marcatore si cerca in ``dati.RADICE_PROGETTO``, mai sotto l'argomento
``radice``. Una fixture automatica la punta a una cartella temporanea vuota,
cosi' questi test non dipendono da un marcatore vero nel repo; i test che
simulano una sessione scrivono il marcatore li'.
"""

import json
import re
import shutil
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional, Sequence

import pytest
import yaml

from research.src import dati, guardiano
from research.src.dati import VaultChiuso, VietatoInCampagna
from research.src.motore import Candela
from research.src.tests.test_dati import FetchFinto, zip_in_memoria

#: la radice del progetto vera, presa prima che la fixture la cambi
RADICE_PROGETTO_VERA = dati.RADICE_PROGETTO
#: l'elenco vero delle monete del gruppo (lo si copia nei progetti finti: ha l'impronta approvata)
MONETE_CSV_VERO = dati.RADICE_DEFAULT / "campagne" / "GRUPPO" / "monete.csv"
CARTELLA_SCHEDE_VERE = dati.RADICE_DEFAULT / "campagne" / "GRUPPO" / "schede"

ORA = 3_600_000
GIORNO = 24 * ORA
MILIONI = 1_000_000


def ms(anno: int, mese: int, giorno: int, ore: int = 0, minuti: int = 0) -> int:
    """L'istante UTC in ms, calcolato con datetime (indipendente da ``dati.ms_da_data``)."""
    return int(datetime(anno, mese, giorno, ore, minuti, tzinfo=timezone.utc).timestamp()) * 1000


@pytest.fixture(autouse=True)
def progetto(tmp_path_factory, monkeypatch) -> Path:
    """Un progetto finto SENZA marcatore: ``dati.RADICE_PROGETTO`` punta qui per ogni test."""
    cartella = tmp_path_factory.mktemp("progetto")
    monkeypatch.setattr(dati, "RADICE_PROGETTO", cartella)
    return cartella


def metti_marcatore(progetto: Path, contenuto, elenco: Optional[bytes] = None) -> None:
    """Scrive ``<progetto>/research/.sessione`` e l'elenco del gruppo (di norma quello vero, copiato)."""
    (progetto / "research").mkdir(parents=True, exist_ok=True)
    testo = contenuto if isinstance(contenuto, str) else json.dumps(contenuto)
    (progetto / "research" / ".sessione").write_text(testo, encoding="utf-8")
    cartella = progetto / "research" / "campagne" / "GRUPPO"
    cartella.mkdir(parents=True, exist_ok=True)
    if elenco is None:
        shutil.copyfile(MONETE_CSV_VERO, cartella / "monete.csv")
    else:
        (cartella / "monete.csv").write_bytes(elenco)


# ---------------------------------------------------------------------------
# (1) periodi_gruppo
# ---------------------------------------------------------------------------


def _primo_mese_dalla_riga(testo: str) -> date:
    """Il primo mese dalla riga «Primo mese di dati», letto qui con una regex (controllo indipendente)."""
    trovato = re.search(r"^\| Primo mese di dati[^|]*\| (\d{4})-(\d{2})-(\d{2}) \|$", testo, re.MULTILINE)
    assert trovato, "riga «Primo mese di dati» non trovata"
    return date(int(trovato.group(1)), int(trovato.group(2)), int(trovato.group(3)))


def _primi_giorni_veri() -> dict:
    monete = guardiano.leggi_monete_gruppo(str(RADICE_PROGETTO_VERA))
    return {m: dati.leggi_scheda_gruppo(m)["primo_mese"] for m in monete}


def test_periodi_gruppo_sulle_schede_vere():
    monete = guardiano.leggi_monete_gruppo(str(RADICE_PROGETTO_VERA))
    assert len(monete) == 80
    # le schede sono esattamente una per moneta dell'elenco
    assert sorted(p.stem for p in CARTELLA_SCHEDE_VERE.glob("*.md")) == sorted(monete)
    primi = _primi_giorni_veri()
    # la lettura di leggi_scheda_gruppo coincide con una regex scritta qui
    for moneta in monete:
        assert primi[moneta] == _primo_mese_dalla_riga((CARTELLA_SCHEDE_VERE / f"{moneta}.md").read_text("utf-8"))

    periodi = dati.periodi_gruppo(primi)

    assert periodi["fine_costruzione"] == date(2023, 1, 16)
    assert periodi["fine_costruzione_ts"] == ms(2023, 1, 16, 23, 59) + 59_999  # 23:59:59.999 UTC
    assert periodi["inizio_validazione"] == date(2023, 1, 17)
    assert periodi["inizio_validazione_ts"] == ms(2023, 1, 17)
    assert periodi["fine_validazione"] == date(2023, 12, 31)
    assert periodi["giorni_validazione"] == 349
    assert periodi["giorni_moneta"] == 93_167
    assert periodi["giorni_moneta_obiettivo"] == 65_216
    assert periodi["giorni_moneta_costruzione"] == 65_247
    assert periodi["giorni_moneta_validazione"] == 27_920 == 80 * 349
    per_moneta = periodi["monete"]
    assert list(per_moneta) == sorted(monete)
    costruzione = [v["giorni_costruzione"] for v in per_moneta.values()]
    assert min(costruzione) == 412 and max(costruzione) == 1_112
    assert sum(costruzione) == 65_247
    assert all(v["giorni_validazione"] == 349 for v in per_moneta.values())
    assert all(v["giorni"] == v["giorni_costruzione"] + 349 for v in per_moneta.values())
    # il giorno prima del taglio la somma non arrivava all'obiettivo (80 monete attive: 65.247 - 80)
    assert 65_247 - 80 < 65_216 <= 65_247
    # gli stessi numeri della sezione gruppo di parametri.yaml (regole.md, sezione 0, punto 5)
    gruppo = yaml.safe_load(dati.PERCORSO_PARAMETRI.read_text("utf-8"))["gruppo"]
    assert gruppo["taglio_costruzione"] == periodi["fine_costruzione"]
    assert gruppo["inizio_validazione"] == periodi["inizio_validazione"]
    assert gruppo["numero_monete"] == len(per_moneta)


def test_periodi_gruppo_una_moneta_uguale_a_periodi_campagna():
    for primo in (date(2020, 1, 1), date(2021, 3, 1), date(2023, 1, 1), date(2023, 12, 30)):
        periodi = dati.periodi_gruppo({"AAAUSDT": primo})
        moneta = dict(periodi["monete"]["AAAUSDT"])
        assert moneta.pop("giorni_validazione") == (date(2023, 12, 31) - moneta["fine_costruzione"]).days
        assert moneta == dati.periodi_campagna(primo)
        assert periodi["fine_costruzione_ts"] == moneta["fine_costruzione_ts"]


def test_periodi_gruppo_una_moneta_a_mano():
    # 2023-01-01 -> 2023-12-31: 365 giorni; obiettivo (70 x 365) // 100 = 25.550 // 100 = 255;
    # il 255-esimo giorno del 2023 e' il 12 settembre (243 giorni fino al 31 agosto + 12)
    periodi = dati.periodi_gruppo({"AAAUSDT": date(2023, 1, 1)})
    assert periodi["giorni_moneta"] == 365
    assert periodi["giorni_moneta_obiettivo"] == 255
    assert periodi["giorni_moneta_costruzione"] == 255  # raggiunto esattamente
    assert periodi["fine_costruzione"] == date(2023, 9, 12)
    assert periodi["inizio_validazione"] == date(2023, 9, 13)
    assert periodi["giorni_validazione"] == 110  # 18 di settembre + 31 + 30 + 31


def test_periodi_gruppo_due_monete_a_mano():
    # A dal 2023-01-01 (365 giorni), B dal 2023-07-01 (31+31+30+31+30+31 = 184): 549 giorni-moneta;
    # obiettivo (70 x 549) // 100 = 38.430 // 100 = 384.
    # Fino al 30 giugno conta solo A: 181 giorni. Dal 1 luglio 2 al giorno: 181 + 2k >= 384 -> k = 102
    # (181 + 204 = 385; con k = 101, 383 non basta). Il giorno 102 dal 1 luglio e' il 10 ottobre
    # (luglio 31, agosto 31, settembre 30: 92 giorni, poi 10).
    periodi = dati.periodi_gruppo({"BBBUSDT": date(2023, 7, 1), "AAAUSDT": date(2023, 1, 1)})
    assert periodi["giorni_moneta"] == 549
    assert periodi["giorni_moneta_obiettivo"] == 384
    assert periodi["fine_costruzione"] == date(2023, 10, 10)
    assert periodi["giorni_moneta_costruzione"] == 385  # supera l'obiettivo di 1: in quel giorno erano attive 2 monete
    assert periodi["giorni_validazione"] == 82  # 21 di ottobre + 30 + 31
    assert periodi["giorni_moneta_validazione"] == 549 - 385 == 2 * 82
    assert list(periodi["monete"]) == ["AAAUSDT", "BBBUSDT"]  # in ordine dei caratteri, non d'inserimento
    a, b = periodi["monete"]["AAAUSDT"], periodi["monete"]["BBBUSDT"]
    assert a["giorni_costruzione"] == 283  # 273 giorni fino al 30 settembre + 10
    assert b["giorni_costruzione"] == 102
    assert a["fine_costruzione"] == b["fine_costruzione"] == date(2023, 10, 10)
    assert a["inizio_validazione"] == b["inizio_validazione"] == date(2023, 10, 11)
    assert a["inizio_ts"] == ms(2023, 1, 1) and b["inizio_ts"] == ms(2023, 7, 1)
    assert a["fine_costruzione_ts"] == ms(2023, 10, 11) - 1
    # l'ordine del dizionario d'ingresso non cambia nulla
    assert dati.periodi_gruppo({"AAAUSDT": date(2023, 1, 1), "BBBUSDT": date(2023, 7, 1)}) == periodi


def test_periodi_gruppo_numeri_interi():
    # 1.430 giorni: in virgola mobile 0,70 x 1430 = 1000,999..., int() darebbe 1.000; con gli interi e' 1.001
    primo = date(2023, 12, 31) - timedelta(days=1429)
    periodi = dati.periodi_gruppo({"AAAUSDT": primo})
    assert periodi["giorni_moneta"] == 1430
    assert int(0.70 * 1430) == 1000
    assert periodi["giorni_moneta_obiettivo"] == 1001
    assert periodi["monete"]["AAAUSDT"]["giorni_costruzione"] == 1001
    assert periodi["fine_costruzione"] == primo + timedelta(days=1000)


def test_periodi_gruppo_errori():
    with pytest.raises(ValueError, match="nessuna moneta"):
        dati.periodi_gruppo({})
    with pytest.raises(ValueError, match="dopo la fine"):
        dati.periodi_gruppo({"AAAUSDT": date(2024, 1, 1)})
    with pytest.raises(TypeError):
        dati.periodi_gruppo({"AAAUSDT": datetime(2023, 1, 1)})
    with pytest.raises(TypeError):
        dati.periodi_gruppo({"AAAUSDT": "2023-01-01"})
    with pytest.raises(ValueError, match="simbolo"):
        dati.periodi_gruppo({"": date(2023, 1, 1)})
    # A dal 2020-01-01 (1.461 giorni), B dal 2023-12-01 (31): l'obiettivo (70 x 1.492) // 100 = 1.044 lo
    # raggiunge A da sola nel 2022, prima che B cominci: B non avrebbe costruzione
    with pytest.raises(ValueError, match="BBBUSDT"):
        dati.periodi_gruppo({"AAAUSDT": date(2020, 1, 1), "BBBUSDT": date(2023, 12, 1)})
    # un giorno solo: obiettivo 0, taglio il 2023-12-31, nessun giorno di validazione
    with pytest.raises(ValueError, match="validazione"):
        dati.periodi_gruppo({"AAAUSDT": date(2023, 12, 31)})


# ---------------------------------------------------------------------------
# (2) leggi_scheda_gruppo
# ---------------------------------------------------------------------------


def test_scheda_vera_aave_e_una_da_0_1000():
    aave = dati.leggi_scheda_gruppo("AAVEUSDT")
    assert aave == {
        "simbolo": "AAVEUSDT",
        "primo_mese": date(2020, 10, 1),
        "slippage_per_lato": 0.0005,
        "fine_in_sample": date(2023, 12, 31),
    }
    assert "| Fascia di slippage per lato (volume medio 2023) | 0.1000% |" in (
        CARTELLA_SCHEDE_VERE / "1INCHUSDT.md").read_text("utf-8")
    assert dati.leggi_scheda_gruppo("1INCHUSDT")["slippage_per_lato"] == 0.001


def test_tutte_le_80_schede_si_leggono():
    monete = guardiano.leggi_monete_gruppo(str(RADICE_PROGETTO_VERA))
    schede = [dati.leggi_scheda_gruppo(m) for m in monete]
    assert len(schede) == 80
    assert [s["simbolo"] for s in schede] == list(monete)
    slippage = [s["slippage_per_lato"] for s in schede]
    assert set(slippage) == {0.0005, 0.001}
    assert slippage.count(0.0005) == 36 and slippage.count(0.001) == 44
    # tutte con dati prima del 2022-01-01 (storia_minima_anni) e dal primo giorno del mese
    assert all(s["primo_mese"] < date(2022, 1, 1) and s["primo_mese"].day == 1 for s in schede)


SCHEDA_FINTA = """# {simbolo}

Scheda finta per i test.

| Campo | Valore |
|---|---|
| Simbolo (Binance USDS-M, perpetuo in USDT) | `{simbolo}` |
| Primo mese di dati (inizio dell'in-sample) | {primo} |
| Fascia di slippage per lato (volume medio 2023) | {fascia} |
| Fine dell'in-sample | {fine} |
"""


def scrivi_scheda(radice: Path, simbolo: str, testo: Optional[str] = None, **campi) -> None:
    valori = {"simbolo": simbolo, "primo": "2021-03-01", "fascia": "0.0500%", "fine": "2023-12-31"}
    valori.update(campi)
    cartella = radice / "campagne" / "GRUPPO" / "schede"
    cartella.mkdir(parents=True, exist_ok=True)
    (cartella / f"{simbolo}.md").write_text(testo if testo is not None else SCHEDA_FINTA.format(**valori), "utf-8")


def test_scheda_finta_fasce_esatte(tmp_path):
    scrivi_scheda(tmp_path, "XXXUSDT", fascia="0.0500%")
    scrivi_scheda(tmp_path, "YYYUSDT", fascia="0.1000%", primo="2020-02-01")
    x = dati.leggi_scheda_gruppo("XXXUSDT", tmp_path)
    y = dati.leggi_scheda_gruppo("YYYUSDT", tmp_path)
    assert x["slippage_per_lato"] == 0.0005 and x["primo_mese"] == date(2021, 3, 1)
    assert y["slippage_per_lato"] == 0.001 and y["primo_mese"] == date(2020, 2, 1)
    # sono gli stessi float delle fasce di parametri.yaml
    assert {0.0005, 0.001} <= set(dati.fasce_slippage_per_lato())


@pytest.mark.parametrize(
    "campi, messaggio",
    [
        ({"fascia": "0.0300%"}, "fascia"),          # non e' una fascia di parametri.yaml
        ({"fascia": "0.05"}, "percentuale"),        # manca il %
        ({"primo": "2021-03-15"}, "AAAA-MM-01"),    # non e' il primo del mese
        ({"primo": "2024-01-01"}, "dopo la fine"),
        ({"fine": "2024-12-31"}, "fine dell'in-sample"),
        ({"simbolo": "ALTROUSDT"}, "non di"),       # la scheda e' di un'altra moneta
    ],
)
def test_scheda_finta_errori(tmp_path, campi, messaggio):
    valori = {"simbolo": "XXXUSDT", "primo": "2021-03-01", "fascia": "0.0500%", "fine": "2023-12-31"}
    valori.update(campi)
    scrivi_scheda(tmp_path, "XXXUSDT", testo=SCHEDA_FINTA.format(**valori))
    with pytest.raises(ValueError, match=messaggio):
        dati.leggi_scheda_gruppo("XXXUSDT", tmp_path)


def test_scheda_finta_righe_mancanti_o_doppie(tmp_path):
    testo = SCHEDA_FINTA.format(simbolo="XXXUSDT", primo="2021-03-01", fascia="0.0500%", fine="2023-12-31")
    senza = "\n".join(r for r in testo.splitlines() if not r.startswith("| Primo mese"))
    scrivi_scheda(tmp_path, "XXXUSDT", testo=senza)
    with pytest.raises(ValueError, match="trovate 0"):
        dati.leggi_scheda_gruppo("XXXUSDT", tmp_path)
    doppia = testo + "| Fascia di slippage per lato (bis) | 0.1000% |\n"
    scrivi_scheda(tmp_path, "XXXUSDT", testo=doppia)
    with pytest.raises(ValueError, match="trovate 2"):
        dati.leggi_scheda_gruppo("XXXUSDT", tmp_path)
    with pytest.raises(FileNotFoundError):
        dati.leggi_scheda_gruppo("NESSUNAUSDT", tmp_path)
    for simbolo in ("../AAVEUSDT", "aaveusdt", "", "AAVE/USDT"):
        with pytest.raises(ValueError, match="simbolo"):
            dati.leggi_scheda_gruppo(simbolo, tmp_path)


# ---------------------------------------------------------------------------
# (3) filtro di liquidita'
# ---------------------------------------------------------------------------


def test_soglia_da_parametri_yaml(tmp_path):
    assert dati.liquidita_minima_usdt_giorno() == 20_000_000.0
    assert yaml.safe_load(dati.PERCORSO_PARAMETRI.read_text("utf-8"))["scelte_dati"][
        "liquidita_minima_usdt_giorno"] == 20_000_000
    finto = tmp_path / "parametri.yaml"
    finto.write_text("scelte_dati:\n  liquidita_minima_usdt_giorno: 5\n", "utf-8")
    assert dati.liquidita_minima_usdt_giorno(finto) == 5.0
    for testo in ("scelte_dati: {}\n", "scelte_dati:\n  liquidita_minima_usdt_giorno: venti\n",
                  "scelte_dati:\n  liquidita_minima_usdt_giorno: true\n",
                  "scelte_dati:\n  liquidita_minima_usdt_giorno: -1\n", "- una lista\n"):
        finto.write_text(testo, "utf-8")
        with pytest.raises(ValueError):
            dati.liquidita_minima_usdt_giorno(finto)


SIMBOLO_LIQ = "AAVEUSDT"


def riga_giorno(ts: int, qv: Optional[float]) -> str:
    """Una riga klines giornaliera; ``qv=None`` scrive solo 7 campi (manca la colonna quote_volume)."""
    campi: List[object] = [ts, 10, 11, 9, 10.5, 1000, ts + GIORNO - 1]
    if qv is not None:
        campi += [qv, 50, 500, qv / 2, 0]
    return ",".join(str(c) for c in campi)


def scrivi_mese_1d(radice: Path, anno: int, mese: int, righe: Sequence[str], simbolo: str = SIMBOLO_LIQ) -> None:
    percorso = dati.percorso_mese(simbolo, "klines", "1d", anno, mese, radice)
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.write_bytes(zip_in_memoria(percorso.stem + ".csv", "\n".join(righe) + "\n"))


def giorni_del_mese(anno: int, mese: int) -> List[int]:
    primo = date(anno, mese, 1)
    dopo = date(anno + (mese == 12), mese % 12 + 1, 1)
    return [ms(g.year, g.month, g.day) for g in (primo + timedelta(days=k) for k in range((dopo - primo).days))]


def prepara_mesi(radice: Path) -> None:
    """Gennaio-agosto 2023 di AAVEUSDT, con il volume scelto a mano (vedi il test)."""
    scrivi_mese_1d(radice, 2023, 1, [riga_giorno(ts, 25 * MILIONI) for ts in giorni_del_mese(2023, 1)])
    scrivi_mese_1d(radice, 2023, 2, [riga_giorno(ts, 15 * MILIONI) for ts in giorni_del_mese(2023, 2)])
    # marzo: nessun file
    aprile = giorni_del_mese(2023, 4)
    scrivi_mese_1d(radice, 2023, 4, [riga_giorno(ts, 30 * MILIONI) for ts in aprile[:5]]
                   + [riga_giorno(ts, 12 * MILIONI) for ts in aprile[5:10]])
    scrivi_mese_1d(radice, 2023, 5, [riga_giorno(ts, 20 * MILIONI) for ts in giorni_del_mese(2023, 5)])
    giugno = giorni_del_mese(2023, 6)
    scrivi_mese_1d(radice, 2023, 6, [riga_giorno(ts, 30 * MILIONI) for ts in giugno[:10]]
                   + [riga_giorno(ts, None) for ts in giugno[10:15]])
    scrivi_mese_1d(radice, 2023, 7, [riga_giorno(ts, None) for ts in giorni_del_mese(2023, 7)])
    scrivi_mese_1d(radice, 2023, 8, [riga_giorno(ts, 19_999_999.99) for ts in giorni_del_mese(2023, 8)])


def test_liquidita_mensile_media_sui_giorni_presenti(tmp_path):
    prepara_mesi(tmp_path)
    liq = dati.liquidita_mensile(SIMBOLO_LIQ, date(2023, 1, 1), date(2023, 8, 31), tmp_path)
    assert list(liq) == [(2023, m) for m in range(1, 9)]
    assert liq[(2023, 1)] == {"giorni": 31, "volume_medio_usdt": 25 * MILIONI, "sotto_soglia": False}
    assert liq[(2023, 2)] == {"giorni": 28, "volume_medio_usdt": 15 * MILIONI, "sotto_soglia": True}
    # nessuna candela giornaliera: sotto la soglia
    assert liq[(2023, 3)] == {"giorni": 0, "volume_medio_usdt": None, "sotto_soglia": True}
    # 10 giorni presenti: (5 x 30 + 5 x 12) / 10 = 21 milioni (diviso 30 giorni sarebbe 7: sotto)
    assert liq[(2023, 4)] == {"giorni": 10, "volume_medio_usdt": 21 * MILIONI, "sotto_soglia": False}
    # esattamente la soglia: non e' «sotto»
    assert liq[(2023, 5)] == {"giorni": 31, "volume_medio_usdt": 20 * MILIONI, "sotto_soglia": False}
    # i 5 giorni senza la colonna del volume non contano (ne' come zero ne' nel numero dei giorni)
    assert liq[(2023, 6)] == {"giorni": 10, "volume_medio_usdt": 30 * MILIONI, "sotto_soglia": False}
    # candele senza nessun volume: come un mese senza candele
    assert liq[(2023, 7)] == {"giorni": 0, "volume_medio_usdt": None, "sotto_soglia": True}
    assert liq[(2023, 8)]["giorni"] == 31 and liq[(2023, 8)]["sotto_soglia"] is True

    sotto = dati.mesi_sotto_liquidita(SIMBOLO_LIQ, date(2023, 1, 1), date(2023, 8, 31), tmp_path)
    assert sotto == [(2023, 2), (2023, 3), (2023, 7), (2023, 8)]


def test_liquidita_mesi_interi_qualunque_giorno(tmp_path):
    prepara_mesi(tmp_path)
    # il taglio del gruppo divide gennaio: dal 17 gennaio il mese si giudica comunque intero
    parziale = dati.liquidita_mensile(SIMBOLO_LIQ, date(2023, 1, 17), date(2023, 2, 3), tmp_path)
    intero = dati.liquidita_mensile(SIMBOLO_LIQ, date(2023, 1, 1), date(2023, 2, 28), tmp_path)
    assert parziale == intero
    assert parziale[(2023, 1)]["giorni"] == 31
    assert dati.mesi_sotto_liquidita(SIMBOLO_LIQ, date(2023, 1, 1), date(2023, 1, 16), tmp_path) == []


def test_liquidita_riga_nel_file_sbagliato_e_doppioni(tmp_path):
    gennaio = giorni_del_mese(2023, 1)
    scrivi_mese_1d(tmp_path, 2023, 1, [riga_giorno(ts, 30 * MILIONI) for ts in gennaio])
    # il file di febbraio ripete il 31 gennaio con un altro volume: vale il primo letto (gennaio),
    # e la riga va a gennaio, non a febbraio
    scrivi_mese_1d(tmp_path, 2023, 2, [riga_giorno(gennaio[-1], 1.0)]
                   + [riga_giorno(ts, 10 * MILIONI) for ts in giorni_del_mese(2023, 2)])
    liq = dati.liquidita_mensile(SIMBOLO_LIQ, date(2023, 1, 1), date(2023, 2, 28), tmp_path)
    assert liq[(2023, 1)] == {"giorni": 31, "volume_medio_usdt": 30 * MILIONI, "sotto_soglia": False}
    assert liq[(2023, 2)] == {"giorni": 28, "volume_medio_usdt": 10 * MILIONI, "sotto_soglia": True}


def test_liquidita_soglia_letta_da_parametri(tmp_path, monkeypatch):
    prepara_mesi(tmp_path)
    finto = tmp_path / "parametri.yaml"
    finto.write_text("scelte_dati:\n  liquidita_minima_usdt_giorno: 10000000\n", "utf-8")
    monkeypatch.setattr(dati, "PERCORSO_PARAMETRI", finto)
    # con 10 milioni febbraio (15) e agosto (quasi 20) non sono piu' sotto; marzo e luglio si'
    assert dati.mesi_sotto_liquidita(SIMBOLO_LIQ, date(2023, 1, 1), date(2023, 8, 31), tmp_path) == [
        (2023, 3), (2023, 7)]


def test_liquidita_vault_chiuso_prima_del_disco(tmp_path):
    with pytest.raises(VaultChiuso):
        dati.mesi_sotto_liquidita(SIMBOLO_LIQ, date(2023, 12, 1), date(2024, 1, 31), tmp_path)
    # un giorno di dicembre basta per giudicare dicembre intero, senza toccare il vault
    assert dati.mesi_sotto_liquidita(SIMBOLO_LIQ, date(2023, 12, 1), date(2023, 12, 15), tmp_path) == [(2023, 12)]
    assert not (tmp_path / "data").exists()


def test_mese_della_barra_dalla_sua_apertura_in_utc():
    sotto = [(2023, 2)]
    assert dati.barra_vietata_liquidita(ms(2023, 1, 31, 23), sotto) is False      # 1h che chiude a mezzanotte
    assert dati.barra_vietata_liquidita(ms(2023, 1, 31, 20), sotto) is False      # 4h, ultima di gennaio
    assert dati.barra_vietata_liquidita(ms(2023, 1, 31), sotto) is False          # una 3d aperta il 31 gennaio chiude a febbraio: e' di gennaio
    assert dati.barra_vietata_liquidita(ms(2023, 2, 1), sotto) is True
    assert dati.barra_vietata_liquidita(ms(2023, 2, 28, 23, 45), sotto) is True   # 15m, ultima di febbraio
    assert dati.barra_vietata_liquidita(ms(2023, 3, 1), sotto) is False
    assert dati.barra_vietata_liquidita(ms(2023, 2, 1) - 1, sotto) is False       # l'ultimo ms di gennaio
    assert dati.barra_vietata_liquidita(ms(2023, 2, 15), [[2023, 2]]) is True     # mesi come tornano da un JSON
    assert dati.barra_vietata_liquidita(ms(2023, 2, 15), []) is False
    assert dati.mese_utc(0) == (1970, 1)
    assert dati.mese_utc(-1) == (1969, 12)
    assert dati.mese_utc(ms(2024, 2, 29, 12)) == (2024, 2)
    with pytest.raises(TypeError):
        dati.mese_utc(1.5)


def test_barre_vietate_liquidita_intervalli():
    ts = [ms(2023, 1, 31, h) for h in (21, 22, 23)] + [ms(2023, 2, 1, h) for h in (0, 1, 2)] + [ms(2023, 3, 1)]
    candele = [Candela(t, 1.0, 1.0, 1.0, 1.0, 1.0, t + ORA - 1) for t in ts]
    assert dati.barre_vietate_liquidita(candele, [(2023, 2)]) == [(3, 6)]
    assert dati.barre_vietate_liquidita(ts, [(2023, 2)]) == [(3, 6)]
    assert dati.barre_vietate_liquidita(candele, [(2023, 1), (2023, 3)]) == [(0, 3), (6, 7)]
    assert dati.barre_vietate_liquidita(candele, []) == []
    assert dati.barre_vietate_liquidita([], [(2023, 2)]) == []
    # ogni indice negli intervalli e' una barra vietata, e viceversa
    vietati = {i for a, b in dati.barre_vietate_liquidita(candele, [(2023, 1)]) for i in range(a, b)}
    assert vietati == {i for i, c in enumerate(candele) if dati.barra_vietata_liquidita(c.ts, [(2023, 1)])}


# ---------------------------------------------------------------------------
# (4) rifiuti in campagna
# ---------------------------------------------------------------------------


def riga_1d(ts: int) -> str:
    return riga_giorno(ts, 30 * MILIONI)


def fetch_di_gennaio(simbolo: str) -> FetchFinto:
    """Serve gennaio 2023 in 1d (last e mark) e il funding di gennaio di ``simbolo``."""
    righe = "\n".join(riga_1d(ts) for ts in giorni_del_mese(2023, 1)) + "\n"
    risposte = {}
    for tipo in ("klines", "markPriceKlines"):
        url = dati.url_mese(simbolo, tipo, "1d", 2023, 1)
        risposte[url] = zip_in_memoria(f"{simbolo}-1d-2023-01.csv", righe)
    url_funding = dati.url_mese(simbolo, "fundingRate", None, 2023, 1)
    risposte[url_funding] = zip_in_memoria(f"{simbolo}-fundingRate-2023-01.csv", f"{ms(2023, 1, 1)},8,0.0001\n")
    return FetchFinto(risposte)


GENNAIO = (date(2023, 1, 1), date(2023, 1, 31))


def scarica_e_carica(simbolo: str, radice: Path) -> None:
    """Scarica e carica gennaio 2023 di ``simbolo`` con ogni funzione controllata: nessun rifiuto atteso."""
    fetch = fetch_di_gennaio(simbolo)
    assert dati.scarica_mese(simbolo, "klines", "1d", 2023, 1, radice, fetch) is not None
    assert len(dati.scarica_periodo(simbolo, "markPriceKlines", "1d", *GENNAIO, radice, fetch)) == 1
    assert len(dati.scarica_periodo(simbolo, "fundingRate", None, *GENNAIO, radice, fetch)) == 1
    serie = dati.carica_serie_allineate(simbolo, "1d", *GENNAIO, radice)
    assert len(serie["candele"]) == 31 and serie["n_volume_mancante"] == 0
    assert len(dati.carica_candele(simbolo, "1d", *GENNAIO, radice)) == 31
    assert dati.carica_funding(simbolo, *GENNAIO, radice) == [(ms(2023, 1, 1), 0.0001)]
    assert len(dati.carica_funding_dettaglio(simbolo, *GENNAIO, radice)) == 1
    assert dati.mesi_sotto_liquidita(simbolo, *GENNAIO, radice) == []
    impronte = dati.calcola_impronte(simbolo, radice)
    assert len(impronte) == 3
    assert dati.verifica_impronte(simbolo, radice, impronte) == []


def rifiuta_tutto(simbolo: str, radice: Path) -> None:
    """Ogni funzione controllata rifiuta ``simbolo`` prima di toccare rete o dati."""
    fetch = fetch_di_gennaio(simbolo)
    chiamate = [
        lambda: dati.scarica_mese(simbolo, "klines", "1d", 2023, 1, radice, fetch),
        lambda: dati.scarica_periodo(simbolo, "klines", "1d", *GENNAIO, radice, fetch),
        lambda: dati.carica_serie_allineate(simbolo, "1d", *GENNAIO, radice),
        lambda: dati.carica_candele(simbolo, "1d", *GENNAIO, radice),
        lambda: dati.carica_candele(simbolo, "1d", *GENNAIO, radice, tipo="markPriceKlines"),
        lambda: dati.carica_funding(simbolo, *GENNAIO, radice),
        lambda: dati.carica_funding_dettaglio(simbolo, *GENNAIO, radice),
        lambda: dati.liquidita_mensile(simbolo, *GENNAIO, radice),
        lambda: dati.mesi_sotto_liquidita(simbolo, *GENNAIO, radice),
        lambda: dati.calcola_impronte(simbolo, radice),
        lambda: dati.registra_impronte(simbolo, radice),
        lambda: dati.verifica_impronte(simbolo, radice, {}),
    ]
    for chiamata in chiamate:
        with pytest.raises(VietatoInCampagna, match=re.escape(repr(simbolo))):
            chiamata()
    assert fetch.chiamate == []
    assert not (radice / "data" / "insample" / simbolo).exists()


def rifiuta_lista_e_indice() -> None:
    fetch = FetchFinto()
    with pytest.raises(VietatoInCampagna, match="lista_contratti"):
        dati.lista_contratti(fetch)
    with pytest.raises(VietatoInCampagna, match="elenca_simboli_archivio"):
        dati.elenca_simboli_archivio(fetch)
    assert fetch.chiamate == []


def test_marcatore_gruppo_eth_alza_aave_e_btc_no(tmp_path, progetto):
    metti_marcatore(progetto, {"tipo": "campagna", "simbolo": "GRUPPO"})
    radice = tmp_path / "dati"
    rifiuta_tutto("ETHUSDT", radice)
    rifiuta_tutto("GRUPPO", radice)  # il nome della campagna non e' una moneta
    rifiuta_tutto("aaveusdt", radice)  # insieme ESATTO: niente minuscole
    scarica_e_carica("AAVEUSDT", radice)
    scarica_e_carica("BTCUSDT", radice)
    rifiuta_lista_e_indice()
    assert dati.simboli_ammessi_in_campagna() == frozenset(guardiano.leggi_monete_gruppo(str(progetto))) | {"BTCUSDT"}
    assert len(dati.simboli_ammessi_in_campagna()) == 81


def test_marcatore_gruppo_elenco_non_approvato_rifiuta_tutto(tmp_path, progetto):
    radice = tmp_path / "dati"
    alterato = MONETE_CSV_VERO.read_bytes().replace(b"AAVEUSDT", b"ETHUSDT")
    metti_marcatore(progetto, {"tipo": "campagna", "simbolo": "GRUPPO"}, elenco=alterato)
    for simbolo in ("AAVEUSDT", "BTCUSDT", "ETHUSDT"):
        with pytest.raises(VietatoInCampagna, match="non e' quello approvato"):
            dati.scarica_mese(simbolo, "klines", "1d", 2023, 1, radice, FetchFinto())
    (progetto / "research" / "campagne" / "GRUPPO" / "monete.csv").unlink()
    with pytest.raises(VietatoInCampagna, match="non e' quello approvato"):
        dati.carica_candele("BTCUSDT", "1d", *GENNAIO, radice)
    rifiuta_lista_e_indice()


def test_marcatore_btc_eth_alza(tmp_path, progetto):
    metti_marcatore(progetto, {"tipo": "campagna", "simbolo": "BTCUSDT"})
    radice = tmp_path / "dati"
    rifiuta_tutto("ETHUSDT", radice)
    rifiuta_tutto("AAVEUSDT", radice)  # le monete del gruppo valgono solo per GRUPPO
    scarica_e_carica("BTCUSDT", radice)
    rifiuta_lista_e_indice()
    assert dati.simboli_ammessi_in_campagna() == frozenset({"BTCUSDT"})


def test_marcatore_di_una_moneta_ammette_lei_e_btc(tmp_path, progetto):
    metti_marcatore(progetto, {"tipo": "campagna", "simbolo": "ETHUSDT"})
    radice = tmp_path / "dati"
    scarica_e_carica("ETHUSDT", radice)
    scarica_e_carica("BTCUSDT", radice)
    rifiuta_tutto("SOLUSDT", radice)
    rifiuta_tutto("AAVEUSDT", radice)
    rifiuta_lista_e_indice()


EXCHANGE_INFO = json.dumps({"symbols": [{
    "symbol": "ETHUSDT", "status": "TRADING", "contractType": "PERPETUAL",
    "onboardDate": 1, "deliveryDate": 2, "quoteAsset": "USDT",
}]}).encode()

INDICE = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
    "<Prefix>data/futures/um/monthly/klines/</Prefix><IsTruncated>false</IsTruncated>"
    "<CommonPrefixes><Prefix>data/futures/um/monthly/klines/ETHUSDT/</Prefix></CommonPrefixes>"
    "</ListBucketResult>"
).encode()


def tutto_come_prima(radice: Path) -> None:
    """Senza campagna: ogni simbolo passa, lista dei contratti e indice dell'archivio si leggono."""
    scarica_e_carica("ETHUSDT", radice)
    scarica_e_carica("BTCUSDT", radice)
    fetch = FetchFinto({dati.URL_EXCHANGE_INFO: EXCHANGE_INFO,
                        dati.url_indice_archivio(dati.PREFISSO_KLINES_ARCHIVIO): INDICE})
    assert [c["symbol"] for c in dati.lista_contratti(fetch)] == ["ETHUSDT"]
    assert dati.elenca_simboli_archivio(fetch) == ["ETHUSDT"]
    assert dati.marcatore_di_campagna() is None
    assert dati.simboli_ammessi_in_campagna() is None


def test_senza_marcatore_tutto_come_prima(tmp_path, progetto):
    assert not (progetto / "research" / ".sessione").exists()
    tutto_come_prima(tmp_path / "dati")


def test_marcatore_vuoto_o_coordinamento_tutto_come_prima(tmp_path, progetto):
    metti_marcatore(progetto, "   \n")
    tutto_come_prima(tmp_path / "vuoto")
    metti_marcatore(progetto, {"tipo": "coordinamento"})
    tutto_come_prima(tmp_path / "coordinamento")


@pytest.mark.parametrize("contenuto", ["{rotto", '{"tipo": "campagna"}', '{"tipo": "sconosciuto"}',
                                       '{"tipo": "campagna", "simbolo": "../X"}', "[1, 2]"])
def test_marcatore_rotto_rifiuta_tutto(tmp_path, progetto, contenuto):
    metti_marcatore(progetto, contenuto)
    with pytest.raises(VietatoInCampagna, match="rotto"):
        dati.scarica_mese("BTCUSDT", "klines", "1d", 2023, 1, tmp_path, FetchFinto())
    with pytest.raises(VietatoInCampagna, match="rotto"):
        dati.lista_contratti(FetchFinto())


def test_il_marcatore_si_cerca_nel_progetto_non_sotto_radice(tmp_path, progetto):
    # un marcatore accanto ai dati (dove lo troverebbe chi lo cercasse partendo da ``radice``) non conta:
    # il progetto (``RADICE_PROGETTO``) non ne ha, quindi tutto come prima
    radice = tmp_path / "research"
    radice.mkdir()
    (radice / ".sessione").write_text(json.dumps({"tipo": "campagna", "simbolo": "BTCUSDT"}), "utf-8")
    tutto_come_prima(radice)
    # e viceversa: con il marcatore nel progetto il rifiuto vale qualunque sia ``radice``
    metti_marcatore(progetto, {"tipo": "campagna", "simbolo": "BTCUSDT"})
    rifiuta_tutto("ETHUSDT", tmp_path / "altrove")


def test_radice_del_progetto_vera_e_percorso_del_marcatore():
    # la radice vera e' la cartella che contiene research/, calcolata dal file di dati.py
    assert RADICE_PROGETTO_VERA == Path(dati.__file__).resolve().parents[2]
    assert RADICE_PROGETTO_VERA / "research" == dati.RADICE_DEFAULT
    # stesso percorso del marcatore del guardiano
    assert Path(guardiano.percorso_marcatore(str(RADICE_PROGETTO_VERA))) == dati.RADICE_DEFAULT / ".sessione"


def test_il_rifiuto_non_e_un_errore_di_rete_ne_di_dati():
    # _scarica_exchange_info passa all'URL successivo su OSError: un rifiuto non deve essere inghiottito
    assert not issubclass(VietatoInCampagna, OSError)
    assert not issubclass(VietatoInCampagna, ValueError)
