"""Test della prova a placebo dell'esame di gruppo (regole.md di questa cartella).

Si verifica, su serie sintetiche e su file finti (nessun dato vero, nessun numero della prova):

1. lo sfasamento comune: lo stesso d su tutte le monete, due segnali dello stesso istante su monete diverse restano
   insieme, d fra il margine e L - margine, lo stesso seme da' lo stesso d, il margine di 30 giorni o L // 4;
2. i segnali da manuale: uguali a quelli della prova del 9 ottobre (``taratura/placebo/placebo.py``, caricato per
   percorso), calcolati una barra alla volta come in blocco, causali; l'ATR come quello del 9 ottobre; stop, target
   e uscita a tempo contata in barre;
3. gli ingressi: i salti per finestra, buco e barra vietata, contati;
4. la regola data come ``ingressi_placebo`` e la stessa come variante del contratto danno gli stessi trade;
5. ``esegui_placebo`` intero su due monete sintetiche: la riga, le barre vietate uguali a quelle di ``gruppo.py``, il
   pavimento delle sfasate riletto dall'avanzamento, la sfasata piu' vicina;
6. la lettura dei dati: solo ``gruppo.CaricatoreDisco`` sulla radice di lettura, i file nativi a 4 ore, la
   copertura dei dati prima del lancio;
7. il lancio vero: regole chiuse, committate e pushate, identita' delle righe, cartella di lavoro fuori da git, un
   file cambiato durante il lancio;
8. il riassunto: soglie da ``parametri.yaml``, regole, copertura, fedelta', campione con gli sfasamenti in piu', z
   dal t, M1 e M2 sugli z, M3, misure informative e limiti, stampa completa.

Si lancia dalla radice del branch principale: ``python -m pytest <questa cartella>/test_placebo_gruppo.py -q``.
``esegui.py`` mette nel percorso il branch principale (``research``) e questa cartella (``placebo_gruppo``).
Per la velocita' alcuni test abbassano, solo in questo processo, simulazioni, sfasate e ricampionamenti dell'esame
e i minimi di trade (``regole_veloci``): il percorso del codice e' lo stesso.
"""

from __future__ import annotations

import copy
import dataclasses
import hashlib
import importlib.util
import io
import json
import math
import shutil
import subprocess
import sys
import zipfile
import zlib
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import norm
from scipy.stats import t as student

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))

import esegui as E  # noqa: E402  (mette il branch principale nel percorso)
import placebo_gruppo as PG  # noqa: E402
import riassunto as R  # noqa: E402
from research.src import dati, gruppo, motore, statistica  # noqa: E402
from research.src.motore import Candela, Parametri, StoriaChiusa  # noqa: E402

ORA = 3_600_000
GIORNO = 86_400_000
PROVA_9_OTTOBRE = QUI.parent / "placebo" / "placebo.py"


def ms(giorno: date) -> int:
    return int(datetime(giorno.year, giorno.month, giorno.day, tzinfo=timezone.utc).timestamp()) * 1000


def candele_casuali(n: int = 3000, seme: int = 1, passo: int = ORA, t0: int = 0, volatilita: float = 0.01) -> list:
    rng = np.random.default_rng(seme)
    prezzo = 100 * np.exp(np.cumsum(rng.normal(0, volatilita, n)))
    out = []
    for i, p in enumerate(prezzo):
        o = p * (1 + rng.normal(0, 0.002))
        h = max(o, p) * (1 + abs(rng.normal(0, 0.003)))
        lo = min(o, p) * (1 - abs(rng.normal(0, 0.003)))
        ts = t0 + i * passo
        out.append(Candela(ts, float(o), float(h), float(lo), float(p), 1.0, ts + passo - 1))
    return out


def prova_9_ottobre():
    """Il modulo della prova del 9 ottobre, caricato per percorso (sta in un altro pacchetto ``research``)."""
    if "placebo_9_ottobre" in sys.modules:
        return sys.modules["placebo_9_ottobre"]
    spec = importlib.util.spec_from_file_location("placebo_9_ottobre", PROVA_9_OTTOBRE)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules["placebo_9_ottobre"] = modulo
    spec.loader.exec_module(modulo)
    return modulo


# ---------------------------------------------------------------------------
# Un caricatore sintetico (gli stessi metodi di gruppo.CaricatoreDisco)
# ---------------------------------------------------------------------------

#: due monete sintetiche: (simbolo, primo mese, slippage), un mese sotto la liquidita' e qualche buco
DUE = (("AAAUSDT", "2023-07-01", 0.0005), ("BBBUSDT", "2023-08-01", 0.001))
MESI_SOTTO = (("AAAUSDT", 2023, 9),)
BUCHI = (("BBBUSDT", ms(date(2023, 8, 20)) + 5 * ORA), ("BBBUSDT", ms(date(2023, 8, 20)) + 6 * ORA),
         ("AAAUSDT", ms(date(2023, 11, 25)) + 2 * ORA))


@lru_cache(maxsize=None)
def _serie(simbolo: str, primo: str, ms_barra: int) -> tuple:
    """Candele sintetiche dal primo mese al 2023-12-31, con un fattore comune (le monete si muovono insieme)."""
    t_origine = ms(date(2023, 1, 1))
    t0, t_fine = ms(date.fromisoformat(primo)), ms(date(2024, 1, 1))
    n = (t_fine - t0) // ms_barra
    scarto = (t0 - t_origine) // ms_barra
    comune = np.random.default_rng([7, ms_barra]).normal(size=(t_fine - t_origine) // ms_barra)[scarto:scarto + n]
    rng = np.random.default_rng([zlib.crc32(simbolo.encode()), ms_barra])
    rendimenti = 0.006 * math.sqrt(ms_barra / ORA) * (0.6 * comune + 0.8 * rng.normal(size=n))
    ombre = np.abs(rng.normal(size=(n, 2))) * 0.003
    togli = {ts for s, ts in BUCHI if s == simbolo}
    chiusura = 20.0 + zlib.crc32(simbolo.encode()) % 80
    candele = []
    for k in range(n):
        apertura = chiusura
        chiusura = apertura * math.exp(float(rendimenti[k]))
        ts = t0 + k * ms_barra
        if ts in togli:
            continue
        candele.append(Candela(ts, apertura, max(apertura, chiusura) * (1 + float(ombre[k, 0])),
                               min(apertura, chiusura) * (1 - float(ombre[k, 1])), chiusura, 1.0, ts + ms_barra - 1))
    return tuple(candele)


@dataclasses.dataclass(frozen=True)
class CaricatoreSintetico:
    monete: tuple = DUE
    #: (simbolo, ts): la moneta non ha barre da ``ts`` in poi (per esempio tolta dal listino)
    tronca: tuple = ()
    #: (simbolo, chiave): la serie della moneta senza ``funding`` o senza ``giorni_1d``
    senza: tuple = ()

    def _info(self, simbolo):
        for s, primo, slippage in self.monete:
            if s == simbolo:
                return primo, slippage
        raise KeyError(simbolo)

    def scheda(self, simbolo):
        primo, slippage = self._info(simbolo)
        return {"primo_mese": date.fromisoformat(primo), "slippage_per_lato": slippage}

    def serie(self, simbolo, timeframe, inizio, fine):
        primo, _ = self._info(simbolo)
        da, a = ms(inizio), ms(fine + timedelta(days=1))
        fine_moneta = dict(self.tronca).get(simbolo, a)
        candele = [c for c in _serie(simbolo, primo, dati.durata_intervallo(timeframe))
                   if c.ts >= da and c.close_ts < a and c.ts < fine_moneta]
        funding = [(t, 1e-4) for t in range(ms(date.fromisoformat(primo)), a, 8 * ORA) if t >= da]
        out = {"candele": candele, "candele_mark": list(candele), "funding": funding,
               "mesi_sotto_liquidita": [(an, me) for s, an, me in MESI_SOTTO if s == simbolo],
               "barre_tolte": {"last": 0, "mark": 0},
               "giorni_1d": max(0, (a - max(da, ms(date.fromisoformat(primo)))) // GIORNO)}
        for s, chiave in self.senza:
            if s == simbolo:
                out[chiave] = 0 if chiave == "giorni_1d" else []
        return out

    def btc(self, timeframe, inizio, fine):
        return []


MONETE = {s: j for j, (s, _, _) in enumerate(DUE)}


@pytest.fixture(autouse=True)
def progetto_senza_marcatore(tmp_path_factory, monkeypatch):
    """Come i test di research/src: ``dati.RADICE_PROGETTO`` punta a un progetto vuoto, senza marcatore."""
    monkeypatch.setattr(dati, "RADICE_PROGETTO", tmp_path_factory.mktemp("progetto"))


@pytest.fixture
def regole_veloci(monkeypatch):
    """I numeri dell'esame ridotti, solo in questo processo: 30 simulazioni della (b), 30 sfasate, 300
    ricampionamenti, minimi di trade bassi e nessun tetto di concentrazione (due monete sole)."""
    vere = gruppo.regole_del_gruppo()

    def veloci(percorso=None):
        regole = dict(vere)
        regole.update({"simulazioni_baseline_casuale": 30, "sfasamenti_pavimento": 30,
                       "bootstrap_ricampionamenti": 300, "quota_massima_moneta": 1.0,
                       "trade_minimi": {"costruzione": 20, "validazione": 10, "vault": 10}})
        return regole

    monkeypatch.setattr(gruppo, "regole_del_gruppo", veloci)
    return veloci


# ---------------------------------------------------------------------------
# 1. Lo sfasamento comune
# ---------------------------------------------------------------------------


def test_lo_spostamento_e_lo_stesso_su_tutte_le_monete_e_i_grappoli_restano_insieme():
    inizio, L, d = ms(date(2022, 1, 1)), 5000, 1234
    comuni = [inizio + 100 * ORA, inizio + 4990 * ORA]  # lo stesso istante su tre monete (anche vicino alla fine)
    istanti = {"AUSDT": comuni + [inizio + 7 * ORA], "BUSDT": comuni, "CUSDT": [comuni[0], inizio + 4999 * ORA]}
    spostati = E.sposta_istanti(istanti, inizio, L, ORA, d)
    for simbolo, lista in istanti.items():
        assert spostati[simbolo] == [inizio + (((ts - inizio) // ORA + d) % L) * ORA for ts in lista]
    assert spostati["AUSDT"][:2] == spostati["BUSDT"] and spostati["CUSDT"][0] == spostati["BUSDT"][0]
    assert spostati["BUSDT"][1] == inizio + ((4990 + d) % L) * ORA  # in cerchio
    # le distanze fra istanti (in cerchio) non cambiano, anche fra monete
    tutti_prima = sorted({ts for v in istanti.values() for ts in v})
    tutti_dopo = sorted({ts for v in spostati.values() for ts in v})
    assert len(tutti_prima) == len(tutti_dopo)
    distanze = lambda xs: sorted(((b - a) // ORA) % L for a in xs for b in xs if a != b)  # noqa: E731
    assert distanze(tutti_prima) == distanze(tutti_dopo)
    with pytest.raises(ValueError):
        E.sposta_istanti({"AUSDT": [inizio + L * ORA]}, inizio, L, ORA, d)
    with pytest.raises(ValueError):
        E.sposta_istanti({"AUSDT": [inizio + ORA // 2]}, inizio, L, ORA, d)


def test_d_sta_fra_il_margine_e_L_meno_il_margine_e_usa_quasi_tutto_il_cerchio():
    L, margine = 20_000, 720
    ds = [E.sfasamento(E.etichetta("1h", r, dd, per, k), L, margine)
          for r in PG.REGOLE for dd in PG.DIREZIONI for per in E.PERIODI for k in range(20)]
    assert min(ds) >= margine and max(ds) <= L - margine
    assert min(ds) < 3000 and max(ds) > 17_000  # non solo fra L/4 e 3L/4
    # gli estremi sono ammessi: con L piccolo escono tutti i valori da margine a L - margine
    assert {E.sfasamento(f"x{s}", 12, 3) for s in range(400)} == set(range(3, 10))


def test_il_margine_e_30_giorni_di_barre_al_massimo_L_quarti():
    assert E.barre_e_margine(0, 1000 * GIORNO - 1, ORA) == (24_000, 720)
    assert E.barre_e_margine(0, 1000 * GIORNO - 1, 4 * ORA) == (6000, 180)
    assert E.barre_e_margine(0, 51 * GIORNO - 1, ORA) == (1224, 306)  # finestra corta: L // 4
    with pytest.raises(ValueError):
        E.barre_e_margine(0, 2 * ORA - 1, ORA)


def test_lo_stesso_seme_da_lo_stesso_d():
    testo = E.etichetta("4h", "macd", "short", "validazione", 2)
    assert testo == "GRUPPO|4h|macd|short|validazione|2"
    assert E.seme_di(testo) == zlib.crc32(testo.encode("utf-8"))
    assert E.sfasamento(testo, 9000, 180) == E.sfasamento(testo, 9000, 180)
    altri = {E.sfasamento(E.etichetta("4h", "macd", "short", "validazione", k), 9000, 180) for k in range(10)}
    assert len(altri) >= 9  # sfasamenti diversi per k diversi


# ---------------------------------------------------------------------------
# 2. Segnali, ATR, uscite
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("seme", [1, 2, 3])
def test_i_segnali_da_manuale_coincidono_con_quelli_della_prova_del_9_ottobre(seme):
    P9 = prova_9_ottobre()
    for passo, volatilita in ((ORA, 0.01), (4 * ORA, 0.02)):
        c = candele_casuali(2500, seme, passo, volatilita=volatilita)
        for regola in PG.REGOLE:
            for direzione in PG.DIREZIONI:
                in_blocco = PG.segnali_regola(c, regola, direzione)
                assert (in_blocco == P9.segnali_regola(c, regola, direzione)).all(), (regola, direzione)
                assert in_blocco[PG.RISCALDAMENTO:].sum() > 5, (regola, direzione)  # la prova non e' vuota
                calcolo = PG._Regola(regola, direzione)
                barra_per_barra = np.array([calcolo.aggiungi(x) for x in c])
                assert (barra_per_barra == in_blocco).all(), (regola, direzione)
    assert PG.REGOLE == P9.REGOLE and PG.USCITA_DELLA_REGOLA == P9.USCITA_DELLA_REGOLA
    # il 13 ott 2026 il modulo ha preso anche «1d» (seconda edizione: TIMEFRAME, MS_BARRA, BARRE_USCITA_TEMPO);
    # a 1 ora e a 4 ore le uscite a tempo restano quelle della prova del 9 ottobre
    assert {k: v for k, v in PG.BARRE_USCITA_TEMPO.items() if k in P9.BARRE_USCITA_TEMPO} == P9.BARRE_USCITA_TEMPO
    assert PG.BARRE_USCITA_TEMPO["1d"] == 10 and PG.RISCALDAMENTO == P9.RISCALDAMENTO


def test_segnali_causali():
    c = candele_casuali(1500, 9)
    for regola in PG.REGOLE:
        for direzione in PG.DIREZIONI:
            assert (PG.segnali_regola(c, regola, direzione)[:900] == PG.segnali_regola(c[:900], regola, direzione)).all()


def test_l_atr_e_quello_del_9_ottobre():
    P9 = prova_9_ottobre()
    c = candele_casuali(3000, 4)
    nove = P9.atr_semplice(c)
    mio = np.array([PG.atr_alla_barra(c, i) for i in range(len(c))])
    assert np.isnan(mio[:PG.BARRE_ATR]).all()
    assert np.allclose(mio[PG.BARRE_ATR:], nove[PG.BARRE_ATR:], rtol=1e-10, atol=0)


def test_segnale_stop_target_e_riscaldamento():
    c = candele_casuali(300, 5)
    ctx = type("Ctx", (), {"timeframe": "1h", "ms_per_barra": ORA})()
    for regola in PG.REGOLE:
        for direzione in PG.DIREZIONI:
            segnale = PG.crea_segnale(ctx, {"regola": regola, "direzione": direzione})()
            assert segnale(StoriaChiusa(c, PG.RISCALDAMENTO)) is None  # barra 59: riscaldamento
            s = segnale(StoriaChiusa(c, 101))
            a = PG.atr_alla_barra(c, 100)
            lato = 1 if direzione == "long" else -1
            chiusura = c[100].close
            if PG.USCITA_DELLA_REGOLA[regola] == "atr":
                assert s.stop == pytest.approx(chiusura - lato * 1.5 * a) and s.target == pytest.approx(chiusura + lato * 2.5 * a)
            else:
                assert s.stop == pytest.approx(chiusura - lato * 2.0 * a) and s.target is None
            assert s.direzione == direzione
    piatte = [Candela(i * ORA, 10.0, 10.0, 10.0, 10.0, 1.0, i * ORA + ORA - 1) for i in range(100)]
    assert PG.crea_segnale(ctx, {"regola": "rsi", "direzione": "long"})()(StoriaChiusa(piatte, 80)) is None  # ATR 0


@pytest.mark.parametrize("timeframe,barre", [("1h", 24), ("4h", 12)])
def test_l_uscita_a_tempo_conta_le_barre_anche_con_un_buco(timeframe, barre):
    passo = dati.durata_intervallo(timeframe)
    c = candele_casuali(800, 6, passo, volatilita=0.001)
    c = c[:210] + c[212:]  # un buco di due barre dentro una posizione
    ctx = type("Ctx", (), {"timeframe": timeframe, "ms_per_barra": passo})()
    strategia = PG.crea_casuale(ctx, {"regola": "bollinger", "direzione": "long"})(frozenset({100, 200, 400, 600}))
    ris = motore.esegui(c, None, None, [], strategia, Parametri(slippage_per_lato=0.0005))
    indice = {x.ts: k for k, x in enumerate(c)}
    a_tempo = [t for t in ris.trades if t.esito == "segnale"]
    assert len(a_tempo) >= 3
    for t in a_tempo:
        assert indice[t.ts_uscita] - indice[t.ts_entrata] == barre  # tenuta ``barre`` barre, esce all'apertura dopo
    assert {indice[t.ts_entrata] - 1 for t in ris.trades} <= {100, 200, 400, 600}


def test_il_modulo_rispetta_il_contratto_di_gruppo():
    modulo = gruppo.carica_modulo_variante(E.MODULO)
    for nome in gruppo.FUNZIONI_DEL_CONTRATTO:
        assert callable(getattr(modulo, nome))
    gruppo.controlla_import_della_variante(E.MODULO.read_bytes(), E.MODULO)
    # «1d» e' ammesso dal 13 ott 2026 (seconda edizione); un timeframe fuori dalla prova no
    ctx = type("Ctx", (), {"timeframe": "15m", "ms_per_barra": 900_000})()
    with pytest.raises(ValueError):
        PG.crea_a(ctx, {"regola": "rsi", "direzione": "long"})
    assert callable(PG.crea_a(type("Ctx", (), {"timeframe": "1d", "ms_per_barra": GIORNO})(),
                              {"regola": "rsi", "direzione": "long"}))
    with pytest.raises(ValueError):
        PG.crea_a(type("Ctx", (), {"timeframe": "1h"})(), {"regola": "nessuna", "direzione": "long"})


# ---------------------------------------------------------------------------
# 3. Gli ingressi: salti contati
# ---------------------------------------------------------------------------


def test_gli_ingressi_saltano_e_contano_finestra_buco_e_barra_vietata():
    ts = np.array([10 * ORA + k * ORA for k in range(10) if k != 4], dtype=np.int64)  # manca la barra 14
    maschera = bytearray(len(ts))
    maschera[6] = 1  # la barra 17 (indice 6) e' vietata
    monete = {"AUSDT": {"finestra": (10 * ORA, 20 * ORA - 1), "ts": ts, "vietate": {"long|atr": {"maschera": bytes(maschera)}}}}
    spostati = {"AUSDT": [9 * ORA, 10 * ORA, 14 * ORA, 17 * ORA, 19 * ORA, 20 * ORA, 12 * ORA]}
    ingressi, conteggi = E.ingressi_per_moneta(spostati, monete, "long|atr", ORA)
    assert ingressi == {"AUSDT": [10 * ORA, 12 * ORA, 19 * ORA]}
    assert conteggi["saltati"] == {"fuori_finestra": 2, "buco": 1, "vietata": 1}
    assert conteggi["ingressi"] == 3 and conteggi["monete_con_ingressi"] == 1


# ---------------------------------------------------------------------------
# 4. La regola come ingressi_placebo e come variante: gli stessi trade
# ---------------------------------------------------------------------------


def _segnali_veri(caricatore, timeframe, regola, direzione, periodo="costruzione"):
    """Gli istanti in cui la regola scatta (barre >= 60) sulla serie di costruzione di ogni moneta, senza sfasamento."""
    periodi = dati.periodi_gruppo({s: caricatore.scheda(s)["primo_mese"] for s in MONETE})
    istanti = {}
    for s in MONETE:
        c = caricatore.serie(s, timeframe, periodi["monete"][s]["inizio"], periodi["fine_costruzione"])["candele"]
        scatta = PG.segnali_regola(c, regola, direzione)
        scatta[:PG.RISCALDAMENTO] = False
        istanti[s] = [c[i].ts for i in np.flatnonzero(scatta)]
    return istanti


def test_la_regola_come_ingressi_placebo_e_come_variante_da_gli_stessi_trade():
    caricatore = CaricatoreSintetico()
    for regola in PG.REGOLE:
        for direzione in PG.DIREZIONI:
            p = {"regola": regola, "direzione": direzione}
            come_variante = gruppo.conta_trade_di_gruppo(E.MODULO, p, "1h", processi=1, monete=MONETE,
                                                         caricatore=caricatore)
            come_placebo = gruppo.conta_trade_di_gruppo(E.MODULO, p, "1h", processi=1, monete=MONETE,
                                                        caricatore=caricatore,
                                                        ingressi_placebo=_segnali_veri(caricatore, "1h", regola, direzione))
            assert come_variante["trade_stimati"] > 10, (regola, direzione)
            assert come_variante["trade_stimati_per_moneta"] == come_placebo["trade_stimati_per_moneta"], (regola, direzione)
            for s in MONETE:
                for chiave in ("trade", "long", "short", "segnali_non_validi", "segnali_senza_barra"):
                    assert come_variante["per_moneta"][s][chiave] == come_placebo["per_moneta"][s][chiave]


def _senza_origine(risultato):
    copia = json.loads(json.dumps(risultato))
    for chiave in ("id", "file", "ripresa", "ingressi", "impronte"):
        copia.pop(chiave, None)
    for v in copia["per_moneta"].values():
        v.pop("ingressi_dati", None)
    return json.dumps(copia, sort_keys=True)


def test_l_esame_della_regola_come_ingressi_placebo_e_come_variante_e_lo_stesso(tmp_path, regole_veloci):
    caricatore = CaricatoreSintetico()
    p = {"regola": "rottura_20", "direzione": "long"}
    variante = gruppo.esame_di_gruppo(E.MODULO, p, "1h", "costruzione", "V", processi=1, monete=MONETE,
                                      caricatore=caricatore, cartella_campagna=tmp_path / "v")
    placebo = gruppo.esame_di_gruppo(E.MODULO, p, "1h", "costruzione", "P", processi=1, monete=MONETE,
                                     caricatore=caricatore, cartella_campagna=tmp_path / "p",
                                     ingressi_placebo=_segnali_veri(caricatore, "1h", "rottura_20", "long"))
    assert variante["metriche"]["n_trade"] > 50
    assert _senza_origine(variante) == _senza_origine(placebo)


# ---------------------------------------------------------------------------
# 5. esegui_placebo intero, su dati sintetici
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("periodo", ["costruzione", "validazione"])
def test_esegui_placebo_su_due_monete_sintetiche(tmp_path, regole_veloci, periodo):
    caricatore = CaricatoreSintetico()
    prep = E.prepara("1h", periodo, caricatore, MONETE, processi=1)
    periodi = dati.periodi_gruppo({s: caricatore.scheda(s)["primo_mese"] for s in MONETE})
    inizio, fine = prep["finestra_unione"]
    if periodo == "costruzione":
        assert inizio == ms(date(2023, 7, 1)) and fine == periodi["fine_costruzione_ts"]
    else:
        assert inizio == periodi["inizio_validazione_ts"] and fine == ms(date(2024, 1, 1)) - 1
    assert prep["L"] == (fine + 1 - inizio) // ORA and prep["margine"] == min(720, prep["L"] // 4)
    # in validazione i segnali stanno solo nelle barre di validazione, e mai nelle prime 60
    for s, info in prep["monete"].items():
        for chiave, istanti in info["segnali"].items():
            assert all(ts >= info["ts"][PG.RISCALDAMENTO] for ts in istanti)
            if periodo == "validazione":
                assert all(ts >= periodi["inizio_validazione_ts"] for ts in istanti)
    riga = E.esegui_placebo(prep, "bollinger", "short", 1, caricatore=caricatore, cartella_gruppo=tmp_path / "g",
                            radice=tmp_path, processi=1)
    assert riga["etichetta"] == f"GRUPPO|1h|bollinger|short|{periodo}|1"
    assert prep["margine"] <= riga["d"] <= prep["L"] - prep["margine"]
    assert riga["d"] == E.sfasamento(riga["etichetta"], prep["L"], prep["margine"])
    assert riga["barre_per_moneta"] == {s: info["barre_nel_periodo"] for s, info in prep["monete"].items()}
    assert all(v > 0 for v in riga["barre_per_moneta"].values())
    seg = riga["segnali"]
    assert seg["originali"] == seg["ingressi"] + sum(seg["saltati"].values())
    assert seg["originali"] > 50 and seg["ingressi"] > 20
    if periodo == "costruzione":
        assert seg["saltati"]["fuori_finestra"] > 0  # BBBUSDT comincia un mese dopo la finestra unione
        assert riga["conta"]["esito"] == "registrabile" and riga["conta"]["ingressi_senza_barra"] == 0
    e = riga["esame"]
    assert riga["giudicata"] and e is not None
    assert e["vietate_diverse"] == [] and e["ingressi_senza_barra"] == 0  # le stesse barre vietate di gruppo.py
    assert e["sfasate"]["pavimento_uguale"] and e["sfasate"]["con_trade"] >= 2
    assert 0 <= e["sfasate"]["percentile"] <= 100
    assert e["contro_b"]["p_value"] == e["contro_b"]["p_value"]  # un numero
    if e["contro_b"]["valutabile"]:
        assert R.p_coerente(e["contro_b"])  # il p_value e' la coda della t di Student del t
    assert set(e["senza_pavimento"]) >= {"p_value", "t", "netta", "valutabile", "gradi_liberta"}
    assert e["impronta_variante"] == hashlib.sha256(E.MODULO.read_bytes()).hexdigest()
    assert e["impronte_strumenti"] == dict(sorted(gruppo.impronte_degli_strumenti().items()))
    # la sfasata piu' vicina: il t ricalcolato con il pavimento vero e' quello dell'esame
    vicina = e["sfasate"]["senza_la_piu_vicina"]
    assert vicina is not None and 0 <= vicina["distanza_barre"] <= prep["L"] // 2
    assert vicina["ricalcolo_uguale"] is bool(e["contro_b"]["valutabile"])
    if periodo == "costruzione":
        assert e["trade"] == riga["conta"]["trade_stimati"]
    json.dumps(riga)  # la riga si scrive in JSON
    # gli ingressi dati all'esame sono gli istanti veri spostati di d e filtrati, ricalcolati qui a parte
    ricalcolati = 0
    for s, info in prep["monete"].items():
        posizione = {int(ts): j for j, ts in enumerate(info["ts"].tolist())}
        da, a = info["finestra"]
        for ts in info["segnali"]["bollinger|short"]:
            nuovo = inizio + ((ts - inizio) // ORA + riga["d"]) % prep["L"] * ORA
            if da <= nuovo and nuovo + ORA - 1 <= a and nuovo in posizione:
                ricalcolati += not info["vietate"]["short|tempo"]["maschera"][posizione[nuovo]]
    assert ricalcolati == seg["ingressi"]


def test_il_t_con_un_altro_pavimento_ha_l_aritmetica_di_contro_baseline():
    """Problema 14: il t ricalcolato senza la sfasata piu' vicina usa la stessa aritmetica di ``contro_baseline``."""
    r = np.random.default_rng(3).normal(0.05, 1.0, 600)
    # il pavimento della (b) (0,06) sta sopra l'errore del bootstrap (circa 0,04): decide con un pavimento basso
    base = {"tipo": "b", "media": 0.01, "errore_standard": 0.012, "errore_minimo_candidato": 0.06, "valutabile": True}
    ris = statistica.contro_baseline(r, 4, dict(base), n=300, seme=0, dettagli=True)
    assert ris["errore_candidato_senza_pavimento"] < 0.06 == ris["errore_candidato"]
    for pavimento in (0.0, 0.03, 0.08, 0.2):
        ris = statistica.contro_baseline(r, 4, dict(base), n=300, seme=0, pavimento_minimo=pavimento, dettagli=True)
        assert E.t_con_pavimento(ris, pavimento) == ris["t"]
        for altro in (0.0, 0.02, 0.05, 0.3):
            atteso = statistica.contro_baseline(r, 4, dict(base), n=300, seme=0, pavimento_minimo=altro)["t"]
            assert E.t_con_pavimento(ris, altro) == pytest.approx(atteso, rel=1e-12)
    assert E.t_con_pavimento(dict(ris, valutabile=False), 0.1) is None


def test_la_sfasata_piu_vicina_e_quella_che_rimette_gli_ingressi_al_loro_posto():
    griglia = statistica.griglia_sfasamenti(1000, 30, 50)
    sfasamenti, L, d = griglia["sfasamenti"], 1000, 400
    rng = np.random.default_rng(1)
    m = [float(x) for x in rng.normal(0, 0.05, len(sfasamenti))]
    n = [int(x) for x in rng.integers(500, 900, len(sfasamenti))]
    v = E.sfasata_piu_vicina(sfasamenti, L, d, m, n, 800, None)
    distanze = [abs(s - (L - d)) for s in sfasamenti]
    assert v["indice"] == int(np.argmin(distanze)) and v["distanza_barre"] == min(distanze)
    attesa = statistica.pavimento_sfasamento(m[:v["indice"]] + m[v["indice"] + 1:],
                                             n[:v["indice"]] + n[v["indice"] + 1:], 800)["pavimento"]
    assert v["pavimento"] == attesa and v["t"] is None  # senza confronto niente t
    m[v["indice"]] = 0.5  # la sfasata vicina e' un estremo: senza di lei il pavimento scende
    v2 = E.sfasata_piu_vicina(sfasamenti, L, d, m, n, 800, None)
    assert v2["scarto_in_sd"] > 4 and v2["pavimento"] < statistica.pavimento_sfasamento(m, n, 800)["pavimento"]
    # in cerchio: L - d vicino a 0 e' vicino anche a L
    assert E.sfasata_piu_vicina([10, 990], 1000, 5, [0.0, 0.1], [5, 5], 10, None)["indice"] == 1


# ---------------------------------------------------------------------------
# 6. La lettura dei dati: CaricatoreDisco sulla radice di lettura, 4 ore nativi, copertura
# ---------------------------------------------------------------------------


def _zip_csv(percorso: Path, intestazione: str, righe) -> None:
    percorso.parent.mkdir(parents=True, exist_ok=True)
    testo = intestazione + "\n" + "\n".join(",".join(str(x) for x in r) for r in righe) + "\n"
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archivio:
        archivio.writestr(percorso.with_suffix(".csv").name, testo)
    percorso.write_bytes(buffer.getvalue())


KLINE = "open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore"


def _scrivi_mese(radice: Path, simbolo: str, tipo: str, intervallo: str, anno: int, mese: int, prezzo) -> None:
    passo = dati.durata_intervallo(intervallo)
    t0, t1 = ms(date(anno, mese, 1)), ms(date(anno + (mese == 12), mese % 12 + 1, 1))
    righe = []
    for j, ts in enumerate(range(t0, t1, passo)):
        p = prezzo(j)
        righe.append((ts, p, p + 1, p - 1, p, 10.0, ts + passo - 1, 3e7, 1, 1, 1, 0))
    _zip_csv(dati.percorso_mese(simbolo, tipo, intervallo, anno, mese, radice), KLINE, righe)


def test_la_prova_legge_solo_con_caricatore_disco_e_a_4_ore_i_file_nativi(tmp_path):
    """Regola nuova: a 4 ore niente aggregazione dall'1h; si legge tutto con gruppo.CaricatoreDisco, che ha una sola
    radice: la radice di lettura unisce i dati (fuori da git) e le schede del branch principale."""
    assert not hasattr(E, "CaricatorePlacebo")
    simbolo = "AAVEUSDT"
    radice_dati = tmp_path / "dati"
    for tipo in ("klines", "markPriceKlines"):
        _scrivi_mese(radice_dati, simbolo, tipo, "1h", 2023, 1, lambda j: 100.0 + j * 0.01)
        _scrivi_mese(radice_dati, simbolo, tipo, "4h", 2023, 1, lambda j: 500.0 + j)  # non e' l'aggregato dell'1h
        _scrivi_mese(radice_dati, simbolo, tipo, "1d", 2023, 1, lambda j: 100.0)
    _zip_csv(dati.percorso_mese(simbolo, "fundingRate", None, 2023, 1, radice_dati),
             "calc_time,funding_interval_hours,last_funding_rate",
             [(ms(date(2023, 1, 1)) + k * 8 * ORA, 8, 0.0001) for k in range(93)])
    radice = E.radice_di_lettura(tmp_path / "lavoro", radice_dati)
    assert radice == (tmp_path / "lavoro" / "radice").resolve()
    assert (radice / "data").resolve() == (radice_dati / "data").resolve()
    assert (radice / dati.CARTELLA_SCHEDE_GRUPPO).resolve() == E.SCHEDE_DEL_PRINCIPALE.resolve()
    caricatore = gruppo.CaricatoreDisco(str(radice))
    assert caricatore.scheda(simbolo) == gruppo.CaricatoreDisco(str(E.PRINCIPALE / "research")).scheda(simbolo)
    serie = caricatore.serie(simbolo, "4h", date(2023, 1, 1), date(2023, 1, 31))
    assert [c.close for c in serie["candele"]] == [500.0 + j for j in range(31 * 6)]  # i 4h nativi
    assert len(caricatore.serie(simbolo, "1h", date(2023, 1, 1), date(2023, 1, 31))["candele"]) == 31 * 24
    assert len(serie["funding"]) == 93 and serie["giorni_1d"] == 31 and serie["mesi_sotto_liquidita"] == []
    # la ripresa ritrova la stessa radice; un collegamento che punta altrove si rifiuta
    assert E.radice_di_lettura(tmp_path / "lavoro", radice_dati) == radice
    altri = tmp_path / "altri"
    (altri / "data" / "insample").mkdir(parents=True)
    with pytest.raises(SystemExit, match="punta a"):
        E.radice_di_lettura(tmp_path / "lavoro", altri)
    with pytest.raises(SystemExit, match="data/insample"):
        E.radice_di_lettura(tmp_path / "lavoro2", tmp_path / "vuota")


def test_i_mesi_dei_file_si_contano_dal_primo_mese_della_scheda(tmp_path):
    for mese in (11, 12):
        for tipo, intervallo in E.SERIE_DEI_FILE:
            if (tipo, intervallo, mese) == ("markPriceKlines", "4h", 12):
                continue  # un buco
            percorso = dati.percorso_mese("AAAUSDT", tipo, intervallo, 2023, mese, tmp_path)
            percorso.parent.mkdir(parents=True, exist_ok=True)
            percorso.write_bytes(b"x")
    mesi = E.mesi_dei_file("AAAUSDT", date(2023, 10, 1), tmp_path)
    assert set(mesi) == {"klines/1h", "markPriceKlines/1h", "klines/4h", "markPriceKlines/4h", "klines/1d",
                         "fundingRate"}
    assert mesi["klines/1h"] == {"attesi": 3, "presenti": 2, "mancanti": ["2023-10"]}
    assert mesi["markPriceKlines/4h"] == {"attesi": 3, "presenti": 1, "mancanti": ["2023-10", "2023-12"]}


def test_la_copertura_dei_dati_ferma_il_lancio_se_a_una_moneta_manca_qualcosa():
    righe = []
    esito = E.controlla_copertura(CaricatoreSintetico(), MONETE, 1, stampa=righe.append)
    assert esito["monete"] == 2 and set(esito["tabella"]) == set(MONETE)
    for s in MONETE:  # una riga stampata per moneta
        assert sum(1 for r in righe if r.strip().startswith(s)) == 1
    voce = esito["tabella"]["AAAUSDT"]["periodi"]
    assert all(voce[f"{tf}|{p}"]["barre"] > 0 for tf in PG.TIMEFRAME for p in E.PERIODI)
    periodi = dati.periodi_gruppo({s: CaricatoreSintetico().scheda(s)["primo_mese"] for s in MONETE})
    casi = [(CaricatoreSintetico(tronca=(("BBBUSDT", periodi["inizio_validazione_ts"]),)),
             "BBBUSDT: nessuna barra 1h in validazione"),
            (CaricatoreSintetico(senza=(("AAAUSDT", "funding"),)), "AAAUSDT: nessun regolamento di funding"),
            (CaricatoreSintetico(senza=(("BBBUSDT", "giorni_1d"),)), "BBBUSDT: nessuna candela 1d")]
    for caricatore, messaggio in casi:
        with pytest.raises(SystemExit, match=messaggio):
            E.controlla_copertura(caricatore, MONETE, 1, stampa=lambda _: None)


def test_la_copertura_confronta_i_totali_con_il_punto_2_delle_regole(monkeypatch):
    tabella = {"AAAUSDT": {"file": {"klines/1h": {"attesi": 3, "presenti": 3, "mancanti": []},
                                    "markPriceKlines/1h": {"attesi": 3, "presenti": 2, "mancanti": ["2023-10"]},
                                    "fundingRate": {"attesi": 3, "presenti": 3, "mancanti": []}}},
               "BBBUSDT": {"file": {"klines/1h": {"attesi": 2, "presenti": 2, "mancanti": []}}}}
    assert E.totali_dei_file(tabella) == {"klines/1h": {"attesi": 5, "presenti": 5},
                                          "markPriceKlines/1h": {"attesi": 3, "presenti": 2},
                                          "fundingRate": {"attesi": 3, "presenti": 3}}
    monkeypatch.setattr(E, "totali_dei_file", lambda t: {"klines/1h": {"attesi": 3061, "presenti": 3061},
                                                          "markPriceKlines/1h": {"attesi": 3061, "presenti": 3060},
                                                          "fundingRate": {"attesi": 3061, "presenti": 3044}})
    righe = []
    with pytest.raises(SystemExit, match="markPriceKlines/1h: 3060 mesi"):
        E.controlla_copertura(CaricatoreSintetico(), MONETE, 1, severa=True, stampa=righe.append)
    E.controlla_copertura(CaricatoreSintetico(), MONETE, 1, severa=False, stampa=righe.append)  # solo un avviso
    assert any(r.startswith("ATTENZIONE (solo funzionamento)") for r in righe)


def test_i_mesi_dichiarati_sono_quelli_del_punto_2_delle_regole():
    testo = " ".join(E.REGOLE_DELLA_PROVA.read_text(encoding="utf-8").split())
    assert "3.061 mesi di candele a 1 ora del last e del mark e 3.044 mesi di funding" in testo
    assert E.MESI_DICHIARATI == {"klines/1h": 3061, "markPriceKlines/1h": 3061, "fundingRate": 3044}


# ---------------------------------------------------------------------------
# 7. Il lancio vero: regole, git, identita', cartella di lavoro, file cambiati durante il lancio
# ---------------------------------------------------------------------------

IMPRONTE = {nome: hashlib.sha256(nome.encode()).hexdigest() for nome in gruppo.FILE_DEL_VIA_LIBERA}


def test_il_lancio_vero_vuole_le_regole_chiuse_e_le_impronte_del_punto_7(tmp_path):
    righe = "\n".join(f"{v}  {k}" for k, v in IMPRONTE.items())
    bozza = tmp_path / "bozza.md"
    bozza.write_text("> **BOZZA.** testo\n" + righe + "\n", encoding="utf-8")
    chiuse = tmp_path / "chiuse.md"
    chiuse.write_text("# Regole\nDa scrivere al posto della riga BOZZA prima del lancio.\n" + righe + "\n",
                      encoding="utf-8")
    file = tmp_path / "impronte.txt"
    file.write_text(righe, encoding="utf-8")
    assert E.in_bozza(bozza.read_text()) and not E.in_bozza(chiuse.read_text())
    assert E.in_bozza(E.REGOLE_DELLA_PROVA.read_text(encoding="utf-8")) == ("**BOZZA" in E.REGOLE_DELLA_PROVA.read_text(encoding="utf-8"))
    with pytest.raises(SystemExit, match="BOZZA"):
        E.impronte_attese(None, bozza)
    assert E.impronte_attese(None, chiuse) == (IMPRONTE, str(chiuse), False)
    with pytest.raises(SystemExit, match="--funzionamento"):
        E.impronte_attese(file, chiuse)  # nel lancio vero niente file di impronte
    # funzionamento: bozza ammessa, impronte dal file o da nessuna parte
    assert E.impronte_attese(file, bozza, funzionamento=True) == (IMPRONTE, str(file), True)
    vuota = tmp_path / "vuota.md"
    vuota.write_text("> **BOZZA.** senza impronte\n", encoding="utf-8")
    assert E.impronte_attese(None, vuota, funzionamento=True)[0] is None
    chiuse.write_text(righe.splitlines()[0] + "\n", encoding="utf-8")  # ne manca qualcuna
    with pytest.raises(SystemExit, match="mancano le impronte"):
        E.impronte_attese(None, chiuse)


def test_le_impronte_attese_si_leggono_nel_formato_di_sha256sum(tmp_path):
    righe = [f"{v}  {k}" for k, v in IMPRONTE.items()]
    assert E.leggi_impronte("\n".join(righe)) == IMPRONTE
    tabella = "\n".join(f"| `{k}` | `{v}` |" for k, v in IMPRONTE.items())
    assert E.leggi_impronte("# titolo\n" + tabella + "\naltro testo") == IMPRONTE
    with pytest.raises(ValueError):
        E.leggi_impronte(righe[0] + "\n" + "0" * 64 + "  research/src/gruppo.py")
    regole = tmp_path / "regole.md"
    regole.write_text("\n".join(righe[:-1]) + "\n" + "1" * 64 + "  research/config/parametri.yaml\n", encoding="utf-8")
    file = tmp_path / "impronte.txt"
    file.write_text("\n".join(righe), encoding="utf-8")
    with pytest.raises(SystemExit):
        E.impronte_attese(file, regole, funzionamento=True)  # le due fonti non coincidono


def _repo(cartella: Path):
    cartella.mkdir(parents=True)

    def git(*argomenti):
        return subprocess.run(["git", "-C", str(cartella), "-c", "commit.gpgsign=false", "-c", "user.email=t@t",
                               "-c", "user.name=t", *argomenti], check=True, capture_output=True, text=True).stdout

    git("init", "-q")
    return git


def test_il_lancio_vero_vuole_codice_e_regole_della_prova_committati_e_pushati(tmp_path):
    repo = tmp_path / "repo"
    git = _repo(repo)
    for nome in E.FILE_DELLA_PROVA:
        (repo / nome).write_text("x\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="non committati"):
        E.controlla_prova(repo)
    git("add", ".")
    git("commit", "-q", "-m", "a")
    with pytest.raises(SystemExit, match="pusha il branch"):
        E.controlla_prova(repo)  # il ramo remoto non c'e'
    git("update-ref", "refs/remotes/origin/research/coordinamento", "HEAD")
    assert E.controlla_prova(repo)["commit_prova"] == git("rev-parse", "HEAD").strip()
    (repo / "regole.md").write_text("y\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="non committati"):
        E.controlla_prova(repo)  # regole.md modificato
    git("commit", "-q", "-am", "b")
    with pytest.raises(SystemExit, match="pushalo"):
        E.controlla_prova(repo)  # committato ma non pushato
    git("update-ref", "refs/remotes/origin/research/coordinamento", "HEAD")
    pushato = git("rev-parse", "HEAD").strip()
    (repo / "diario.md").write_text("z\n", encoding="utf-8")
    git("add", "diario.md")
    git("commit", "-q", "-m", "c")  # un commit che non tocca la prova non chiede un push
    assert E.controlla_prova(repo)["commit_file_della_prova"] == pushato
    assert set(E.FILE_DELLA_PROVA) == {"placebo_gruppo.py", "esegui.py", "riassunto.py", "regole.md"}


def test_l_identita_contiene_strumenti_codice_regole_monete_schede_e_dati(tmp_path):
    simboli = ("AAVEUSDT", "1INCHUSDT")
    schede = tmp_path / "schede"
    schede.mkdir()
    for s in simboli:
        shutil.copy(E.SCHEDE_DEL_PRINCIPALE / f"{s}.md", schede / f"{s}.md")
    radice_dati = tmp_path / "dati"
    for s in simboli:
        _scrivi_mese(radice_dati, s, "klines", "1h", 2023, 1, lambda j: 1.0 + j)
    regole = tmp_path / "regole.md"
    regole.write_text("regole\n", encoding="utf-8")
    radice = E.radice_di_lettura(tmp_path / "lavoro", radice_dati, schede)
    posizioni = {"1INCHUSDT": 1, "AAVEUSDT": 0}
    prima = E.identita_corrente(radice, posizioni, False, regole)
    assert set(prima) == {"formato", "strumenti", "codice", "regole.md", "monete", "schede", "dati", "funzionamento"}
    assert prima["strumenti"] == {n: E.sha256_file(E.PRINCIPALE / n) for n in sorted(gruppo.FILE_DEL_VIA_LIBERA)}
    assert prima["codice"] == {"placebo_gruppo.py": E.sha256_file(E.MODULO), "esegui.py": E.sha256_file(QUI / "esegui.py")}
    assert prima["monete"]["monete.csv"] == E.sha256_file(E.MONETE_DEL_PRINCIPALE)
    assert prima == E.identita_corrente(radice, posizioni, False, regole)  # stabile
    assert E.differenze_di_identita(prima, E.identita_corrente(radice, posizioni, True, regole)) == ["funzionamento"]
    assert E.differenze_di_identita(prima, E.identita_corrente(radice, {"1INCHUSDT": 0, "AAVEUSDT": 1}, False,
                                                               regole)) == ["monete"]
    regole.write_text("regole cambiate\n", encoding="utf-8")
    assert E.differenze_di_identita(prima, E.identita_corrente(radice, posizioni, False, regole)) == ["regole.md"]
    regole.write_text("regole\n", encoding="utf-8")
    (schede / "AAVEUSDT.md").write_text((schede / "AAVEUSDT.md").read_text() + "\n", encoding="utf-8")
    assert E.differenze_di_identita(prima, E.identita_corrente(radice, posizioni, False, regole)) == ["schede"]
    shutil.copy(E.SCHEDE_DEL_PRINCIPALE / "AAVEUSDT.md", schede / "AAVEUSDT.md")
    _scrivi_mese(radice_dati, "AAVEUSDT", "klines", "1h", 2023, 1, lambda j: 2.0 + j)  # un file di dati cambiato
    assert E.differenze_di_identita(prima, E.identita_corrente(radice, posizioni, False, regole)) == ["dati"]


def test_la_ripresa_salta_le_righe_fatte_e_rifiuta_un_altra_identita(tmp_path):
    file = tmp_path / "esiti_k0.jsonl"
    identita = {"strumenti": {"a": "1"}, "codice": {"placebo_gruppo.py": "x"}, "regole.md": "r"}
    E.scrivi_riga(file, {"etichetta": "A", "identita": identita, "errore": None})
    E.scrivi_riga(file, {"etichetta": "B", "identita": identita, "errore": "rotto"})
    with open(file, "ab") as f:
        f.write(b'{"etichetta": "C", "identi')  # una riga interrotta a meta'
    E.scrivi_riga(file, {"etichetta": "D", "identita": identita, "errore": None})
    assert E.righe_fatte(file, identita) == {"A", "D"}
    assert all(json.loads(r) for r in file.read_text().splitlines()[3:])  # la riga dopo quella rotta e' intera
    compiti = E.compiti_da_fare([0], ["4h"], ["costruzione"], {0: {E.etichetta("4h", "rsi", "long", "costruzione", 0)}})
    assert len(compiti) == 11 and ("4h", "costruzione", "rsi", "long", 0) not in compiti
    with pytest.raises(SystemExit):
        E.righe_fatte(file, dict(identita, **{"regole.md": "s"}))


def test_la_cartella_di_lavoro_sta_fuori_dai_worktree_e_gli_esiti_definitivi_qui(tmp_path):
    assert E.ESITI_DEFINITIVI == QUI
    worktree = QUI.parents[2]
    with pytest.raises(SystemExit, match="fuori da git"):
        E.controlla_lavoro(QUI / "esiti", [worktree, E.PRINCIPALE])
    with pytest.raises(SystemExit, match="fuori da git"):
        E.controlla_lavoro(E.PRINCIPALE / "research" / "lavoro", [worktree, E.PRINCIPALE])
    assert E.controlla_lavoro(tmp_path / "lavoro", [worktree, E.PRINCIPALE]) == (tmp_path / "lavoro").resolve()
    predefinita = E.LAVORO_PREDEFINITO.resolve()
    for vietata in (worktree, E.PRINCIPALE):
        assert predefinita != vietata and vietata not in predefinita.parents


@pytest.fixture
def lancio_finto(tmp_path, monkeypatch):
    """``esegui.main`` con controlli, copertura, preparazione ed esame finti: cosa scrive e quando si ferma."""
    radice_dati = tmp_path / "dati"
    (radice_dati / "data" / "insample").mkdir(parents=True)
    monkeypatch.setattr(E, "ESITI_DEFINITIVI", tmp_path / "definitivi")
    stato = {"identita": {"codice": {"placebo_gruppo.py": "p" * 64}, "strumenti": {"s": "1"}, "regole.md": "r"},
             "chiamate": [], "preparati": [], "guasto": False, "coperture": [], "variante": "p" * 64,
             "identita_chiamate": 0, "cambia_alla": None}
    monkeypatch.setattr(E, "impronte_attese", lambda file, funzionamento=False: ({}, "finto", funzionamento))
    monkeypatch.setattr(E, "controlla_prova", lambda: {"commit_prova": "b" * 40, "commit_file_della_prova": "c" * 40})
    monkeypatch.setattr(E, "controlla_principale", lambda attese, pulito=True: {"commit_principale": "a" * 40,
                                                                                "ramo_principale": "x"})
    monkeypatch.setattr(E, "radice_di_lettura", lambda lavoro, radice: tmp_path / "radice")
    monkeypatch.setattr(E, "controlla_copertura", lambda car, monete, processi, severa=True:
                        stato["coperture"].append(severa) or {})

    def identita(radice, posizioni, funzionamento):
        stato["identita_chiamate"] += 1
        valore = dict(stato["identita"], funzionamento=funzionamento)
        if stato["cambia_alla"] is not None and stato["identita_chiamate"] >= stato["cambia_alla"]:
            valore["regole.md"] = "cambiato"
        return valore

    monkeypatch.setattr(E, "identita_corrente", identita)
    monkeypatch.setattr(E, "prepara", lambda tf, periodo, car, monete, processi:
                        stato["preparati"].append((tf, periodo)) or {"timeframe": tf, "periodo": periodo, "monete": {},
                                                                     "L": 1})

    def finto(prep, regola, direzione, k, **altro):
        stato["chiamate"].append((prep["timeframe"], prep["periodo"], regola, direzione, k))
        assert isinstance(altro["caricatore"], gruppo.CaricatoreDisco)  # si legge solo con CaricatoreDisco
        assert Path(altro["caricatore"].radice) == tmp_path / "radice" == Path(altro["radice"])
        if stato["guasto"]:
            raise RuntimeError("guasto simulato")
        return {"formato": E.FORMATO, "etichetta": E.etichetta(prep["timeframe"], regola, direzione, prep["periodo"], k),
                "periodo": prep["periodo"], "errore": None, "conta": None,
                "esame": {"trade": 1, "impronta_variante": stato["variante"], "impronte_strumenti": {"s": "1"}}}

    monkeypatch.setattr(E, "esegui_placebo", finto)
    stato["argomenti"] = ["--radice-dati", str(radice_dati), "--lavoro", str(tmp_path / "lavoro"), "--timeframe", "4h"]
    stato["cartella"] = tmp_path
    return stato


def test_main_scrive_le_righe_riprende_e_si_ferma(lancio_finto):
    s = lancio_finto
    esiti = s["cartella"] / "definitivi"
    assert E.main(s["argomenti"] + ["--k", "0"]) == 0
    assert len(s["chiamate"]) == 24 and s["preparati"] == [("4h", "costruzione"), ("4h", "validazione")]
    assert s["coperture"] == [True]  # la copertura si controlla a ogni lancio, severa nel lancio vero
    righe = [json.loads(r) for r in (esiti / "esiti_k0.jsonl").read_text().splitlines()]
    assert len(righe) == 24 and all(r["identita"]["regole.md"] == "r" and r["commit_prova"] == "b" * 40
                                    and r["funzionamento"] is False for r in righe)
    s["chiamate"].clear()
    assert E.main(s["argomenti"] + ["--k", "0"]) == 0 and s["chiamate"] == []  # tutto gia' fatto
    assert E.main(s["argomenti"] + ["--k", "1", "--massimo-minuti", "0"]) == 3 and s["chiamate"] == []
    s["guasto"] = True
    assert E.main(s["argomenti"] + ["--k", "1"]) == 2 and len(s["chiamate"]) == 3  # tre errori di fila: fermo
    errori = [json.loads(r) for r in (esiti / "esiti_k1.jsonl").read_text().splitlines()]
    assert len(errori) == 3 and all("guasto simulato" in r["errore"] for r in errori)
    s["guasto"] = False
    s["chiamate"].clear()
    assert E.main(s["argomenti"] + ["--k", "1"]) == 0 and len(s["chiamate"]) == 24  # le righe con errore si rifanno
    assert E.main(s["argomenti"] + ["--k", "2", "--solo-copertura"]) == 0 and not (esiti / "esiti_k2.jsonl").exists()


def test_un_file_cambiato_durante_il_lancio_ferma_senza_scrivere_la_riga(lancio_finto):
    s = lancio_finto
    esiti = s["cartella"] / "definitivi" / "esiti_k0.jsonl"
    s["cambia_alla"] = 3  # 1: al lancio; 2: prima della prima riga; 3: prima della seconda
    assert E.main(s["argomenti"] + ["--k", "0"]) == 4
    assert len(esiti.read_text().splitlines()) == 1
    # l'esame ha usato un altro modulo della variante (cambiato sul disco durante l'esame): fermo, nessuna riga
    s["cambia_alla"] = None
    s["variante"] = "q" * 64
    assert E.main(s["argomenti"] + ["--k", "1"]) == 4
    assert not (s["cartella"] / "definitivi" / "esiti_k1.jsonl").exists()


def test_il_funzionamento_scrive_fuori_da_questa_cartella_e_segna_le_righe(lancio_finto):
    s = lancio_finto
    assert E.main(s["argomenti"] + ["--k", "0", "--funzionamento"]) == 0
    assert s["coperture"] == [False]
    assert not (s["cartella"] / "definitivi").exists()
    righe = [json.loads(r) for r in (s["cartella"] / "lavoro" / "esiti_funzionamento" / "esiti_k0.jsonl")
             .read_text().splitlines()]
    assert len(righe) == 24 and all(r["funzionamento"] and r["identita"]["funzionamento"] for r in righe)


# ---------------------------------------------------------------------------
# 8. Il riassunto
# ---------------------------------------------------------------------------

SOGLIE = copy.deepcopy(R.SOGLIE_DELLE_REGOLE)
IDENTITA = {"regole.md": "r" * 64, "strumenti": IMPRONTE, "codice": {"placebo_gruppo.py": "p" * 64},
            "funzionamento": False}
REGOLE_OK = {"sha256": "r" * 64, "bozza": False, "impronte": IMPRONTE}
GRADI = 200
SOGLIA_NETTA = float(student.ppf(0.97725, GRADI))


def confronto_da_p(p):
    t = float(student.isf(p, GRADI))
    return {"valutabile": True, "p_value": float(student.sf(t, GRADI)), "t": t, "gradi_liberta": GRADI,
            "netta": t > SOGLIA_NETTA}


def confronto(z):
    return confronto_da_p(float(norm.sf(z)))


def righe_finte(z_costruzione, z_validazione, ks=(0, 1, 2, 3), scarti=0, pochi_trade=0):
    """Esiti finti completi: una riga per combinazione, sfasamento e periodo, con gli z dati (in ordine)."""
    righe = {}
    i = {"costruzione": 0, "validazione": 0}
    for k in ks:
        for (tf, regola, direzione) in R.COMBINAZIONI:
            for periodo in R.PERIODI:
                z = (z_costruzione if periodo == "costruzione" else z_validazione)[i[periodo]]
                n = i[periodo]
                i[periodo] += 1
                trade = 900 if periodo == "costruzione" else 400
                if periodo == "validazione" and n < pochi_trade:
                    trade = 250
                esito = "scarto" if (periodo == "costruzione" and n < scarti) else "registrabile"
                riga = {"etichetta": R.etichetta(tf, regola, direzione, periodo, k), "timeframe": tf, "regola": regola,
                        "direzione": direzione, "periodo": periodo, "k": k, "identita": IDENTITA,
                        "funzionamento": False, "regole_bozza": False, "margine": 720,
                        "finestra_unione": [0, 1000], "commit_principale": "a" * 40, "commit_prova": "b" * 40,
                        "minimi": {"costruzione": 700, "validazione": 300, "quota_massima_moneta": 0.1},
                        "conta": {"esito": esito, "motivi": ["trade stimati 10 sotto 700"] if esito == "scarto" else [],
                                  "trade_stimati": trade, "ingressi_senza_barra": 0} if periodo == "costruzione" else None,
                        "esame": None if esito == "scarto" else {
                            "trade": trade, "r_medio": 0.01 * z, "B": 0.0, "effetto_grappolo": 2.0,
                            "quota_moneta_piu_presente": 0.05, "pavimento_decide": n % 2 == 0,
                            "durata_massima_barre": 30, "vietate_diverse": [], "ingressi_senza_barra": 0,
                            "impronta_variante": "p" * 64, "impronte_strumenti": IMPRONTE,
                            "pavimento_sfasate": {"pavimento": 0.01, "finestra_unione": [0, 1000]},
                            "sfasate": {"sopra_p90": z > 1.2816, "pavimento_uguale": True,
                                        "senza_la_piu_vicina": None},
                            "contro_b": confronto(z), "senza_pavimento": confronto(z)}}
                righe[riga["etichetta"]] = riga
    return righe


def per_k(righe):
    out = {}
    for r in righe.values():
        out.setdefault(r["k"], []).append(r)
    return out


def riassumi(righe, errori=(), soglie=SOGLIE, regole=REGOLE_OK):
    tabella = per_k(righe)
    for e in errori:
        tabella.setdefault(e["k"], []).append(e)
    return R.riassumi(tabella, soglie=soglie, regole=regole)


def _coda_a_mano(soglia, mu, sigma):
    return 0.5 * math.erfc((soglia - mu) / sigma / math.sqrt(2.0))


def _z_con(n, alti, valore_alto, base=None):
    z = list(base) if base is not None else [(-1.0 if j % 2 else 1.0) * 0.5 for j in range(n)]
    for j in range(alti):
        z[j] = valore_alto
    return z


def test_le_soglie_del_riassunto_calcolate_a_mano():
    n = 96  # 24 combinazioni x 4 sfasamenti in ogni periodo
    assert R.limite(0.03, n) == 2 and R.limite(0.13, n) == 12
    zc = _z_con(n, 2, 2.5)    # 2 nette: M1 regge (limite 2)
    zv = _z_con(n, 12, 1.5)   # 12 con p < 0,10: M2 regge (limite 12)
    out = riassumi(righe_finte(zc, zv))
    assert out["fase"] == "misure" and out["k"] == [0, 1, 2, 3] and out["k_ignorati"] == []
    m = out["misure"]
    for periodo, z, soglia in (("costruzione", zc, 2.0), ("validazione", zv, 1.2816)):
        mu = sum(z) / n
        sigma = math.sqrt(sum((x - mu) ** 2 for x in z) / (n - 1))
        assert m[periodo]["n"] == n
        assert m[periodo]["mu"] == pytest.approx(mu, abs=1e-9)
        assert m[periodo]["sigma"] == pytest.approx(sigma, abs=1e-9)
        assert m[periodo]["coda_m3"] == pytest.approx(_coda_a_mano(soglia, mu, sigma), rel=1e-7)
    assert m["costruzione"]["conteggio"] == 2 and m["costruzione"]["limite"] == 2
    assert m["validazione"]["conteggio"] == 12 and m["validazione"]["limite"] == 12
    assert out["condizioni"]["M1"] and out["condizioni"]["M2"]
    assert out["condizioni"]["M3_costruzione"] == (_coda_a_mano(2.0, sum(zc) / n, np.std(zc, ddof=1)) <= 0.03)
    assert out["condizioni"]["M3_validazione"] == (_coda_a_mano(1.2816, sum(zv) / n, np.std(zv, ddof=1)) <= 0.13)
    assert out["regge"] == all(out["condizioni"].values())
    # una netta in piu': M1 cade; un p < 0,10 in piu': M2 cade
    out = riassumi(righe_finte(_z_con(n, 3, 2.5), _z_con(n, 13, 1.5)))
    assert not out["condizioni"]["M1"] and not out["condizioni"]["M2"] and not out["regge"]


def test_m1_e_m2_contano_gli_z_come_scritto_nel_testo_di_gruppo():
    """Problema 2: «netta» vuol dire z > 2,00 e «p sotto 0,10» z > 1,2816 (GRUPPO §11.3), non ``netta`` del confronto
    ne' p < 0,10: le due letture differiscono in due strisce strette di p."""
    n = 96
    righe = righe_finte(_z_con(n, 2, 2.5), _z_con(n, 12, 1.5))
    # costruzione: p = 0,02275005 non e' «netta» per contro_baseline (t sotto il quantile 0,97725) ma ha z > 2
    striscia_c = confronto_da_p(0.02275005)
    assert not striscia_c["netta"] and R.z_di(striscia_c) > 2.0
    # validazione: p = 0,099995 e' sotto 0,10 ma ha z <= 1,2816
    striscia_v = confronto_da_p(0.099995)
    assert striscia_v["p_value"] < 0.10 and R.z_di(striscia_v) <= 1.2816
    righe[R.etichetta("4h", "macd", "short", "costruzione", 3)]["esame"]["contro_b"] = striscia_c
    righe[R.etichetta("4h", "macd", "short", "validazione", 3)]["esame"]["contro_b"] = striscia_v
    out = riassumi(righe)
    m = out["misure"]
    assert m["costruzione"]["conteggio"] == 3 and not out["condizioni"]["M1"]  # con «netta» sarebbero 2: reggeva
    assert m["validazione"]["conteggio"] == 12 and out["condizioni"]["M2"]  # con p < 0,10 sarebbero 13: cadeva
    assert m["costruzione"]["letture_diverse_da_netta_o_p"] == 1
    assert m["validazione"]["letture_diverse_da_netta_o_p"] == 1


def test_z_viene_dal_t_senza_limiti_messi_a_mano():
    """Problema 3: con t molto negativo 1 - p_value si arrotonda a 0; lo z della formula viene dalla t di Student,
    senza il limite 1 - 2^-53 (che dava circa -8,2)."""
    c = {"t": -15.0, "gradi_liberta": GRADI, "p_value": float(student.sf(-15.0, GRADI)), "valutabile": True}
    assert c["p_value"] == 1.0 and R.p_coerente(c)
    assert R.z_di(c) == pytest.approx(float(norm.ppf(student.cdf(-15.0, GRADI))), rel=1e-12) and R.z_di(c) < -12
    assert R.z_di(confronto(2.0)) == pytest.approx(2.0, abs=1e-9)
    assert R.z_di(confronto(-1.3)) == pytest.approx(-1.3, abs=1e-9)
    # z non finito: il riassunto si ferma, nessun esito
    n = 96
    righe = righe_finte(_z_con(n, 0, 0), _z_con(n, 0, 0))
    enorme = {"valutabile": True, "t": 1e4, "gradi_liberta": GRADI, "p_value": float(student.sf(1e4, GRADI)),
              "netta": True}
    assert enorme["p_value"] == 0.0 and math.isinf(R.z_di(enorme))
    righe[R.etichetta("1h", "rsi", "long", "costruzione", 0)]["esame"]["contro_b"] = enorme
    out = riassumi(righe)
    assert out["fase"] == "z" and out["z_non_finiti"] == [R.etichetta("1h", "rsi", "long", "costruzione", 0)]
    assert "misure" not in out and "regge" not in out


def test_m3_cade_con_z_troppo_larghi_anche_senza_nette():
    n = 96
    # nessuna netta e nessun p < 0,10, ma z larghi: σ grande sposta la coda oltre le soglie
    zc = [(-1.9 if j % 2 else 1.9) for j in range(n)]
    zv = [(-1.25 if j % 2 else 1.25) for j in range(n)]
    out = riassumi(righe_finte(zc, zv))
    sig_c, sig_v = float(np.std(zc, ddof=1)), float(np.std(zv, ddof=1))
    assert out["misure"]["costruzione"]["conteggio"] == 0 and out["misure"]["validazione"]["conteggio"] == 0
    assert out["misure"]["costruzione"]["coda_m3"] == pytest.approx(_coda_a_mano(2.0, 0.0, sig_c), rel=1e-7)
    assert _coda_a_mano(2.0, 0.0, sig_c) > 0.03 and _coda_a_mano(1.2816, 0.0, sig_v) > 0.13
    assert out["condizioni"]["M1"] and out["condizioni"]["M2"]
    assert not out["condizioni"]["M3_costruzione"] and not out["condizioni"]["M3_validazione"]
    assert not out["regge"]


def test_il_riassunto_si_ferma_se_manca_una_placebo_o_il_campione_e_piccolo():
    n = 96
    righe = righe_finte(_z_con(n, 0, 0), _z_con(n, 0, 0))
    mancante = R.etichetta("1h", "rsi", "long", "validazione", 3)
    righe.pop(mancante)
    out = riassumi(righe, [{"etichetta": mancante, "k": 3, "errore": "X: rotto", "identita": IDENTITA}])
    assert out["fase"] == "copertura" and "misure" not in out
    assert out["copertura"]["errori_senza_riga_buona"] == [mancante]
    # 20 scarti in costruzione: 76 valutabili, sotto 80: si chiedono altri sfasamenti
    out = riassumi(righe_finte(_z_con(n, 0, 0), _z_con(n, 0, 0), scarti=20))
    assert out["fase"] == "campione" and "misure" not in out
    assert out["campione"]["valutabili"] == {"costruzione": 76, "validazione": 96}
    assert out["campione"]["prossimi_k"] == [4]  # 76 / 4 = 19 a sfasamento: 5 sfasamenti in tutto
    # in validazione sotto 300 trade non entra in n
    out = riassumi(righe_finte(_z_con(n, 0, 0), _z_con(n, 0, 0), pochi_trade=40))
    assert out["fase"] == "campione" and out["campione"]["valutabili"]["validazione"] == 56
    assert out["campione"]["prossimi_k"] == [4, 5]  # 56 / 4 = 14 a sfasamento: 6 sfasamenti in tutto
    # righe di due identita' diverse: nessuna misura
    righe = righe_finte(_z_con(n, 0, 0), _z_con(n, 0, 0))
    next(iter(righe.values()))["identita"] = dict(IDENTITA, dati="altri")
    assert riassumi(righe)["fase"] == "identita'"


def test_gli_sfasamenti_in_piu_entrano_solo_se_il_conteggio_lo_chiede():
    """Problema 17: k da 0 a 3; un file di k in piu' entra solo se il campione non basta, in ordine, fino al primo k
    con cui basta; gli altri si ignorano e si dicono."""
    z = _z_con(24 * 6, 0, 0)
    # il campione basta con k 0..3: k 4 e 5 ci sono ma non entrano
    out = riassumi(righe_finte(z, z, ks=range(6)))
    assert out["fase"] == "misure" and out["k"] == [0, 1, 2, 3] and out["k_ignorati"] == [4, 5]
    assert out["misure"]["costruzione"]["n"] == 96
    # 20 scarti (tutti in k 0): con k 0..3 sono 76, con k 4 sono 100: entra solo k 4
    out = riassumi(righe_finte(z, z, ks=range(6), scarti=20))
    assert out["fase"] == "misure" and out["k"] == [0, 1, 2, 3, 4] and out["k_ignorati"] == [5]
    assert out["misure"]["costruzione"]["n"] == 100 and out["misure"]["validazione"]["n"] == 120
    # serve k 4 ma il suo file e' incompleto: copertura
    righe = righe_finte(z, z, ks=range(5), scarti=20)
    righe.pop(R.etichetta("1h", "macd", "long", "costruzione", 4))
    out = riassumi(righe)
    assert out["fase"] == "copertura" and out["k"] == [0, 1, 2, 3, 4]


def test_il_riassunto_si_ferma_con_regole_in_bozza_funzionamento_o_impronte_diverse():
    """Problemi 0, 1 e 13: nessun esito da righe di funzionamento o scritte in bozza, con regole.md ancora in bozza o
    cambiato dopo il lancio, o con impronte che non sono quelle del punto 7."""
    n = 96
    base = righe_finte(_z_con(n, 0, 0), _z_con(n, 0, 0))
    assert riassumi(base)["fase"] == "misure"
    casi = []
    righe = copy.deepcopy(base)
    next(iter(righe.values()))["regole_bozza"] = True
    casi.append((righe, REGOLE_OK, "bozza"))
    righe = copy.deepcopy(base)
    next(iter(righe.values()))["funzionamento"] = True
    casi.append((righe, REGOLE_OK, "funzionamento"))
    casi.append((base, dict(REGOLE_OK, bozza=True), "BOZZA"))
    casi.append((base, dict(REGOLE_OK, sha256="s" * 64), "cambiato"))
    casi.append((base, dict(REGOLE_OK, impronte=dict(IMPRONTE, **{"research/src/gruppo.py": "0" * 64})), "punto 7"))
    for righe, regole, parola in casi:
        out = riassumi(righe, regole=regole)
        assert out["fase"] == "regole" and "misure" not in out, parola
        assert any(parola in p for p in out["problemi"]), (parola, out["problemi"])


def test_soglie_e_minimi_vengono_da_parametri_yaml_e_devono_essere_quelli_delle_regole():
    """Problema 8."""
    assert R.soglie_da_parametri(E.PRINCIPALE / "research" / "config" / "parametri.yaml") == R.SOGLIE_DELLE_REGOLE
    n = 96
    base = righe_finte(_z_con(n, 0, 0), _z_con(n, 0, 0))
    out = riassumi(base, soglie=dict(SOGLIE, campione_minimo=70))
    assert out["fase"] == "soglie" and "campione_minimo" in out["problemi"][0]
    out = riassumi(base, soglie=dict(SOGLIE, trade_minimi={"costruzione": 700, "validazione": 250}))
    assert out["fase"] == "soglie"
    righe = copy.deepcopy(base)
    next(iter(righe.values()))["minimi"]["validazione"] = 200  # una riga calcolata con altri minimi
    out = riassumi(righe)
    assert out["fase"] == "soglie" and "minimi diversi" in out["problemi"][0]
    # ⌊quota · n⌋ esatto: 0,29 · 100 in virgola mobile e' 28,999...
    assert R.limite(0.29, 100) == 29 and math.floor(0.29 * 100) == 28
    assert R.limite(0.03, 100) == 3 and R.limite(0.13, 300) == 39


def test_i_controlli_di_fedelta_fermano_il_riassunto_prima_delle_misure():
    """Problema 4."""
    n = 96
    base = righe_finte(_z_con(n, 0, 0), _z_con(n, 0, 0))
    etichetta_c = R.etichetta("1h", "rsi", "long", "costruzione", 2)
    etichetta_v = R.etichetta("4h", "bollinger", "short", "validazione", 1)
    modifiche = {
        "vietate_diverse": lambda r: r["esame"].update(vietate_diverse=["AAVEUSDT"]),
        "pavimento_ricalcolato_diverso": lambda r: r["esame"]["sfasate"].update(pavimento_uguale=False),
        "ingressi_senza_barra": lambda r: r["esame"].update(ingressi_senza_barra=2),
        "p_value_incoerente": lambda r: r["esame"]["contro_b"].update(p_value=r["esame"]["contro_b"]["p_value"] * 1.01),
        "esame_con_altro_codice": lambda r: r["esame"].update(impronta_variante="q" * 64),
    }
    for nome, modifica in modifiche.items():
        for etichetta_ in (etichetta_c, etichetta_v):
            righe = copy.deepcopy(base)
            modifica(righe[etichetta_])
            out = riassumi(righe)
            assert out["fase"] == "fedelta'" and "misure" not in out, nome
            assert any(etichetta_ in x for x in out["fedelta"][nome]), nome
    righe = copy.deepcopy(base)
    righe[etichetta_c]["conta"]["trade_stimati"] = 899
    out = riassumi(righe)
    assert out["fase"] == "fedelta'" and out["fedelta"]["conta_diversa_dall_esame"] == [etichetta_c]


def test_le_misure_informative_del_riassunto():
    n = 96
    zc, zv = _z_con(n, 2, 2.5), _z_con(n, 12, 1.5)
    out = riassumi(righe_finte(zc, zv))
    # dove decide il pavimento (meta' delle placebo): sd((R - B)/pavimento) = sd(z) sulle placebo pari
    pari = [zc[j] for j in range(n) if j % 2 == 0]
    assert out["dove_decide_il_pavimento"]["costruzione"]["placebo"] == len(pari)
    assert out["dove_decide_il_pavimento"]["costruzione"]["deviazione_standard"] == pytest.approx(np.std(pari, ddof=1))
    assert out["sopra_p90_sfasate_validazione"]["sopra"] == 12
    assert set(out["intervalli_95_per_combinazione"]) == set(R.PERIODI)
    iv = out["intervalli_95_per_combinazione"]["costruzione"]["quota"]
    assert iv[0] <= out["misure"]["costruzione"]["quota"] <= iv[1]
    assert set(out["per_timeframe"]) == {"1h", "4h"} and set(out["per_regola"]) == set(R.REGOLE)
    assert out["senza_pavimento_sfasate"]["costruzione"]["conteggio"] == 2


def test_i_limiti_della_prova_si_contano_senza_decidere():
    """Problemi 5, 14 e 16: finestra unione diversa da quella del pavimento, durata dei trade vicina al margine,
    lettura che cambia senza la sfasata che rimette gli ingressi al loro posto."""
    n = 96
    righe = righe_finte(_z_con(n, 0, 0), _z_con(n, 0, 0))
    a = R.etichetta("1h", "rsi", "long", "costruzione", 0)
    b = R.etichetta("4h", "macd", "short", "validazione", 2)
    c = R.etichetta("1h", "macd", "long", "costruzione", 1)
    righe[a]["esame"]["pavimento_sfasate"]["finestra_unione"] = [100, 1000]
    righe[b]["esame"]["durata_massima_barre"] = 700  # margine 720: a meno di 60 barre
    righe[c]["esame"]["contro_b"] = confronto(1.9)  # non netta; senza la sfasata vicina il pavimento scende
    righe[c]["esame"]["sfasate"]["senza_la_piu_vicina"] = {"distanza_barre": 0, "scarto_in_sd": 3.0,
                                                          "t": confronto(2.3)["t"], "ricalcolo_uguale": True}
    righe[a]["esame"]["sfasate"]["senza_la_piu_vicina"] = {"distanza_barre": 4, "scarto_in_sd": 0.1,
                                                          "t": righe[a]["esame"]["contro_b"]["t"],
                                                          "ricalcolo_uguale": True}
    out = riassumi(righe)
    assert out["fase"] == "misure"
    lim = out["limiti"]
    assert lim["finestra_diversa_dal_pavimento"] == [a] and lim["durata_vicina_al_margine"] == [b]
    v = lim["senza_la_sfasata_piu_vicina"]["costruzione"]
    assert v == {"con_la_misura": 2, "cambiano_lettura": 1, "distanza_esatta_0": 1,
                 "distanza_barre": R.distribuzione([0, 4]), "scarto_in_sd": R.distribuzione([3.0, 0.1])}
    assert lim["senza_la_sfasata_piu_vicina"]["validazione"]["con_la_misura"] == 0


def test_la_stampa_elenca_tutti_gli_errori_e_tutte_le_placebo_mancanti():
    """Problema 10."""
    n = 96
    righe = righe_finte(_z_con(n, 0, 0), _z_con(n, 0, 0))
    tolte = [e for e in list(righe) if e.endswith("|3")][:40]
    errori = []
    for e in tolte:
        righe.pop(e)
        errori.append({"etichetta": e, "k": 3, "errore": f"X: rotto {e}", "identita": IDENTITA})
    out = riassumi(righe, errori)
    assert out["fase"] == "copertura"
    stampate = []
    R.stampa(out, stampate.append)
    testo = "\n".join(stampate)
    assert all(f"  {e}" in testo for e in tolte)  # tutte le mancanti
    assert all(f"rotto {e}" in testo for e in tolte)  # tutti gli errori
    out_fedelta = riassumi({**righe_finte(_z_con(n, 0, 0), _z_con(n, 0, 0))})
    assert out_fedelta["fase"] == "misure"
    stampate.clear()
    R.stampa(out_fedelta, stampate.append)
    assert any(r.startswith("ESITO:") for r in stampate) and any(r.startswith("limiti:") for r in stampate)
