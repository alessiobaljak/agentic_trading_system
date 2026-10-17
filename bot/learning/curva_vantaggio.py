"""LA CURVA DEL VANTAGGIO DEL SEGNALE (T2, 2 ott 2026).

Domanda (sì del proprietario il 2 ott: «fai la misura del punto 1… la mia idea
alla fine e' operare piu' come un quant»): i segnali delle strategie hanno un
vantaggio sul caso, e per quanto tempo dura? La REGOLA e' nel diario
(`docs/andremo_live.md`, «2 ottobre, mattina: T2 … REGOLA scritta PRIMA dei
numeri») e qui si applica com'e' scritta, senza ritocchi.

Le scelte che la regola lascia aperte, fissate qui una volta sola e uguali per i
segnali e per il caso:
  * PREZZO D'INGRESSO = la chiusura dell'ultima candela da 15m gia' CHIUSA
    all'ora d'ingresso (open_time + 15m <= ingresso): e' l'ultimo prezzo noto in
    quel momento, di solito la candela del segnale. Non la candela che CONTIENE
    l'ingresso: la sua chiusura arriva dopo l'ingresso (sarebbe guardare avanti).
    La finestra in avanti parte dalla candela successiva; la mossa a h candele e'
    close[i+h] / close[i] - 1, col segno della direzione (+ long, - short). Le
    candele si cercano per ORARIO (ts_i + h*15m), non per posizione: con un buco
    nella serie l'ingresso si salta e si conta, non si misura storto.
  * MOSSA TIPICA DI 24 ORE = la mediana di |close[t+24h] / close[t] - 1| sulle
    mosse di 24 ore che stanno tutte nei 30 giorni prima dell'ingresso (l'ultima
    finisce con close[i], gia' noto). Mediana e non deviazione standard: un solo
    giorno di crollo non la gonfia. Servono almeno 15 giorni di mosse, se no
    l'ingresso si salta.
  * IL CASO = per ogni segnale, 20 ingressi a caso sulla stessa moneta, nella
    stessa direzione, con la candela di riferimento nelle 12 ore DOPO quella del
    segnale (non prima: la direzione del segnale e' decisa coi prezzi fino al
    segnale, e un ingresso a caso PRIMA, con quella direzione, conoscerebbe il
    proprio futuro — revisione del 2 ott: su prezzi a caso con direzione che
    segue le ultime 4 ore, 100 prove su 100 «peggio del caso»), misurati con le
    stesse regole (tutte le durate
    dentro i dati: nessun ingresso il cui futuro non c'e' ancora). Estratti senza
    rimpiazzo, con un seme fisso per segnale (seme, moneta, verso, ora): stesso
    risultato a ogni lancio e indipendente dall'ordine dei trade.
  * VANTAGGIO a ogni durata = media dei segnali - media del caso, dove il caso
    di un segnale e' la media dei suoi ingressi a caso (ogni segnale pesa uno).
  * MARGINE AL 95% = ricampionamento a blocchi di giornate (UTC): si estraggono
    con rimpiazzo le giornate dei segnali, 2000 volte, seme fisso, e si rifa' il
    vantaggio; percentili 2,5 e 97,5.
Tutto puro: niente rete, niente Firebase, niente file.
"""
from __future__ import annotations

import math
import random
import zlib
from datetime import datetime, timezone

import numpy as np

#: le durate in candele da 15m: 1, 4, 12 e 24 ore (regola del 2 ott)
ORIZZONTI = (4, 16, 48, 96)
#: secondi di una candela da 15m
PASSO_S = 900
#: giorni PRIMA dell'ingresso su cui si calcola la mossa tipica di 24 ore
GIORNI_NORMA = 30
#: sotto questi giorni di mosse la mossa tipica non si calcola (ingresso saltato)
MIN_GIORNI_NORMA = 15
#: ingressi a caso per ogni segnale
N_CASO = 20
#: gli ingressi a caso stanno nelle 12 ore DOPO il segnale (vedi «IL CASO» sopra)
FINESTRA_CASO_S = 12 * 3600
#: ricampionamenti delle giornate per il margine
N_BOOT = 2000
#: seme fisso (la data della regola): stesso risultato a ogni lancio
SEME = 20261002

ESITO_NESSUNO = "nessun vantaggio misurabile"
ESITO_VANTAGGIO = "c'è un vantaggio"
ESITO_PEGGIO = "i segnali fanno peggio del caso"
ESITO_NON_MISURABILE = "misura non possibile"

_GIORNO_S = 86400


def _epoca(v) -> float | None:
    """Secondi dall'epoca da un datetime (senza fuso = UTC) o da un numero (s o
    ms). None se non leggibile."""
    if isinstance(v, datetime):
        return (v if v.tzinfo else v.replace(tzinfo=timezone.utc)).timestamp()
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(f):
        return None
    return f / 1000.0 if f > 1e11 else f


def durata_testo(h: int, passo_s: int = PASSO_S) -> str:
    ore = h * passo_s / 3600.0
    return "1 ora" if ore == 1 else f"{ore:g} ore"


class Serie:
    """Le chiusure di UNA moneta, ordinate per orario, con le mosse di 24 ore gia'
    pronte per la mossa tipica. `candele`: oggetti con `.open_time` e `.close`
    (le Candle della cache) oppure coppie (open_time, close); open_time datetime
    o epoca (s o ms). Candele doppie: vale l'ultima."""

    def __init__(self, candele, passo_s: int = PASSO_S):
        righe: dict[int, float] = {}
        for c in candele or []:
            if hasattr(c, "close"):
                t, cl = _epoca(getattr(c, "open_time", None)), c.close
            else:
                t, cl = _epoca(c[0]), c[1]
            try:
                cl = float(cl)
            except (TypeError, ValueError):
                continue
            if t is None or not math.isfinite(cl) or cl <= 0:
                continue
            righe[int(round(t))] = cl
        self.passo = int(passo_s)
        chiavi = sorted(righe)
        self.ts = np.array(chiavi, dtype=np.int64)
        self.close = np.array([righe[t] for t in chiavi], dtype=float)
        self._pos = {t: k for k, t in enumerate(chiavi)}
        n = len(chiavi)
        # la mossa di 24 ore che PARTE da ogni candela; NaN se 24 ore dopo manca
        self.mossa24 = np.full(n, np.nan)
        if n:
            j = np.searchsorted(self.ts, self.ts + _GIORNO_S)
            ok = j < n
            ok[ok] = self.ts[j[ok]] == self.ts[ok] + _GIORNO_S
            self.mossa24[ok] = np.abs(self.close[j[ok]] / self.close[ok] - 1.0)
        self._norma: dict[tuple, float | None] = {}

    def __len__(self) -> int:
        return len(self.ts)

    def indice(self, entry_ts: float) -> int | None:
        """L'ultima candela CHIUSA all'ora d'ingresso (open_time + passo <=
        entry_ts). None se non c'e', o se e' piu' vecchia di una candela (buco
        nella serie o dati finiti prima dell'ingresso: il prezzo non sarebbe
        quello dell'ingresso)."""
        k = int(np.searchsorted(self.ts, entry_ts - self.passo, side="right")) - 1
        if k < 0 or entry_ts - (int(self.ts[k]) + self.passo) >= self.passo:
            return None
        return k

    def avanti(self, i: int, orizzonti=ORIZZONTI) -> list[float] | None:
        """Le mosse SENZA segno a ogni durata: close(ts_i + h*passo)/close[i] - 1.
        None se una delle candele manca (dati finiti o buco)."""
        t0, c0 = int(self.ts[i]), float(self.close[i])
        out = []
        for h in orizzonti:
            j = self._pos.get(t0 + h * self.passo)
            if j is None:
                return None
            out.append(float(self.close[j]) / c0 - 1.0)
        return out

    def mossa_tipica(self, i: int, giorni: int = GIORNI_NORMA,
                     min_giorni: int = MIN_GIORNI_NORMA) -> float | None:
        """Mediana di |mossa di 24 ore| sulle mosse che iniziano da `giorni`
        giorni prima della candela i e finiscono entro la sua chiusura (inizio <=
        ts_i - 24h): niente dopo l'ingresso. None con meno di `min_giorni` giorni
        di mosse o mediana nulla."""
        chiave = (i, giorni, min_giorni)
        if chiave in self._norma:
            return self._norma[chiave]
        t_i = int(self.ts[i])
        a = int(np.searchsorted(self.ts, t_i - giorni * _GIORNO_S, side="left"))
        b = int(np.searchsorted(self.ts, t_i - _GIORNO_S, side="right"))
        v = self.mossa24[a:b]
        v = v[~np.isnan(v)]
        r = None
        if len(v) >= min_giorni * (_GIORNO_S // self.passo):
            m = float(np.median(v))
            r = m if m > 0 else None
        self._norma[chiave] = r
        return r


def misura(serie: Serie, i: int, lato: str, orizzonti=ORIZZONTI):
    """(mosse col segno in frazione, stesse mosse in mosse tipiche) per un
    ingresso alla candela i; altrimenti il motivo (stringa) per cui si salta."""
    mosse = serie.avanti(i, orizzonti)
    if mosse is None:
        return "orizzonte oltre i dati (o buco nella serie)"
    norma = serie.mossa_tipica(i)
    if norma is None:
        return f"meno di {MIN_GIORNI_NORMA} giorni di storia per la mossa tipica"
    segno = 1.0 if lato == "long" else -1.0
    r = [segno * m for m in mosse]
    return r, [x / norma for x in r]


def _tf_bot() -> str:
    from bot.config import settings
    return str(settings.ORCHESTRATOR_TIMEFRAME)


def seme_segnale(seme: int, symbol: str, lato: str, ts: float) -> int:
    """Seme del caso per un segnale: dipende solo dal segnale, non dall'ordine.
    crc32 e non hash(): hash() delle stringhe cambia a ogni processo."""
    return zlib.crc32(f"{seme}|{symbol}|{lato}|{int(ts)}".encode())


def ingressi_a_caso(serie: Serie, i: int, lato: str, n: int, seme: int,
                    finestra_s: int = FINESTRA_CASO_S, orizzonti=ORIZZONTI) -> list:
    """Fino a `n` ingressi a caso (senza rimpiazzo) con la candela di riferimento
    nei `finestra_s` secondi DOPO la candela i, nella stessa direzione, misurati come il
    segnale; quelli il cui futuro non c'e' nei dati (o senza mossa tipica) si
    scartano. Lista di (mosse, mosse in mosse tipiche)."""
    t_i = int(serie.ts[i])
    # solo DOPO la candela del segnale (2 ott 2026): la direzione del segnale e'
    # decisa coi prezzi fino a t_i; un ingresso a caso PRIMA, con quella
    # direzione, conoscerebbe il proprio futuro
    a = int(np.searchsorted(serie.ts, t_i, side="right"))
    b = int(np.searchsorted(serie.ts, t_i + finestra_s, side="right"))
    candidati = list(range(a, b))
    random.Random(seme).shuffle(candidati)
    presi = []
    for k in candidati:
        m = misura(serie, k, lato, orizzonti)
        if isinstance(m, str):
            continue
        presi.append(m)
        if len(presi) >= n:
            break
    return presi


def _giorno(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def misura_segnali(segnali: list[dict], serie_per_moneta: dict, orizzonti=ORIZZONTI,
                   n_caso: int = N_CASO, finestra_s: int = FINESTRA_CASO_S,
                   seme: int = SEME, passo_s: int = PASSO_S) -> tuple[list[dict], dict]:
    """Misura ogni segnale e il suo caso. `segnali`: dict con `symbol`, `lato`
    («long»/«short»), `ts` (epoca dell'ingresso), facoltativo `esplorativa`.
    `serie_per_moneta`: {symbol: Serie o lista di candele o None}. Ritorna
    (righe misurate, {motivo: quanti saltati}). Un segnale saltato si CONTA, mai
    si stima."""
    pronte: dict[str, Serie | None] = {}
    righe: list[dict] = []
    saltati: dict[str, int] = {}

    def salta(motivo: str) -> None:
        saltati[motivo] = saltati.get(motivo, 0) + 1

    for s in segnali:
        sym, lato, ts = s.get("symbol"), s.get("lato"), s.get("ts")
        if sym not in pronte:
            grezze = serie_per_moneta.get(sym)
            if isinstance(grezze, Serie):
                pronte[sym] = grezze if len(grezze) else None
            else:
                se = Serie(grezze, passo_s) if grezze else None
                pronte[sym] = se if se is not None and len(se) else None
        serie = pronte[sym]
        if serie is None:
            salta("moneta non in cache")
            continue
        i = serie.indice(float(ts))
        if i is None:
            salta("nessuna candela chiusa subito prima dell'ingresso")
            continue
        m = misura(serie, i, lato, orizzonti)
        if isinstance(m, str):
            salta(m)
            continue
        caso = ingressi_a_caso(serie, i, lato, n_caso, seme_segnale(seme, sym, lato, ts),
                               finestra_s, orizzonti)
        if not caso:
            salta("nessun ingresso a caso utilizzabile")
            continue
        k = len(caso)
        righe.append({
            "symbol": sym, "lato": lato, "ts": float(ts), "giorno": _giorno(float(ts)),
            "esplorativa": bool(s.get("esplorativa")),
            "s_r": m[0], "s_z": m[1],
            "c_r": [sum(c[0][h] for c in caso) / k for h in range(len(orizzonti))],
            "c_z": [sum(c[1][h] for c in caso) / k for h in range(len(orizzonti))],
            "n_caso": k,
        })
    return righe, saltati


def curva(righe: list[dict], orizzonti=ORIZZONTI, n_boot: int = N_BOOT,
          seme: int = SEME, passo_s: int = PASSO_S) -> dict:
    """La curva: a ogni durata n, media dei segnali, media del caso, vantaggio e
    margine al 95% (blocchi di giornate), in mosse tipiche e in % (per farsi
    un'idea). Margine None con meno di 2 giornate (non c'e' niente da
    ricampionare)."""
    n = len(righe)
    giorni = sorted({r["giorno"] for r in righe})
    H = len(orizzonti)
    out = {"n": n, "giorni": len(giorni), "per_durata": []}
    if not n:
        return out
    idx = {g: k for k, g in enumerate(giorni)}
    D = len(giorni)
    conta = np.zeros(D)
    somme = {u: np.zeros((D, H)) for u in ("s_z", "c_z", "s_r", "c_r")}
    for r in righe:
        d = idx[r["giorno"]]
        conta[d] += 1
        for u in somme:
            somme[u][d] += np.asarray(r[u], dtype=float)
    medie = {u: somme[u].sum(axis=0) / n for u in somme}
    ic = {"z": None, "r": None}
    # «la curva sale ancora dopo la durata k?» (revisione del 2 ott): il gradino
    # k -> k+1 col margine tutto sopra lo 0, sugli STESSI ricampionamenti
    sale = None
    if D >= 2:
        scelte = np.random.default_rng(seme).integers(0, D, size=(n_boot, D))
        quanti = conta[scelte].sum(axis=1)[:, None]
        for u in ("z", "r"):
            diff = somme[f"s_{u}"] - somme[f"c_{u}"]
            boot = diff[scelte].sum(axis=1) / quanti
            ic[u] = np.percentile(boot, [2.5, 97.5], axis=0)
            if u == "z" and H > 1:
                sale = np.percentile(np.diff(boot, axis=1), 2.5, axis=0) > 0
    for k, h in enumerate(orizzonti):
        out["per_durata"].append({
            "h": h, "durata": durata_testo(h, passo_s), "n": n,
            "segnali": float(medie["s_z"][k]), "caso": float(medie["c_z"][k]),
            "vantaggio": float(medie["s_z"][k] - medie["c_z"][k]),
            "ic": None if ic["z"] is None else (float(ic["z"][0][k]), float(ic["z"][1][k])),
            "sale_dopo": None if sale is None or k == H - 1 else bool(sale[k]),
            "segnali_pct": float(medie["s_r"][k]) * 100, "caso_pct": float(medie["c_r"][k]) * 100,
            "vantaggio_pct": float(medie["s_r"][k] - medie["c_r"][k]) * 100,
            "ic_pct": None if ic["r"] is None
            else (float(ic["r"][0][k]) * 100, float(ic["r"][1][k]) * 100),
        })
    return out


def per_verso(righe: list[dict], **kw) -> dict:
    """La stessa curva per i soli long e i soli short (solo informativo)."""
    return {v: curva([r for r in righe if r["lato"] == v], **kw) for v in ("long", "short")}


def _elenco(durate: list[str]) -> str:
    return durate[0] if len(durate) == 1 else ", ".join(durate[:-1]) + " e " + durate[-1]


def verdetto(cv: dict) -> dict:
    """L'esito ESATTAMENTE come la regola del 2 ott:
      * a tutte le durate il margine contiene lo 0 -> «nessun vantaggio misurabile»;
      * a qualche durata il margine sta tutto sopra lo 0 -> «c'è un vantaggio», col
        punto dove la curva smette di salire: dalla prima durata col margine sopra
        lo 0, la prima dopo la quale il gradino successivo NON sale oltre il
        margine (revisione del 2 ott: «il punto piu' alto» lo sceglieva il rumore
        su una curva piatta);
      * a qualche durata tutto sotto lo 0 e a nessuna sopra -> «i segnali fanno
        peggio del caso». Se capitano insieme sopra e sotto, l'esito e' «c'è un
        vantaggio» ma il «peggio del caso» si dice per primo (la regola: «lo si
        dice per primo»).
    Senza segnali misurati o senza margine (meno di 2 giornate): «misura non
    possibile»."""
    per_d = cv.get("per_durata") or []
    if not cv.get("n") or not per_d or any(r["ic"] is None for r in per_d):
        return {"esito": ESITO_NON_MISURABILE, "picco": None, "sopra": [], "sotto": [],
                "testo": ESITO_NON_MISURABILE + ": " + (
                    "nessun trade misurato" if not cv.get("n")
                    else "una sola giornata di trade, il margine non si calcola") + "."}
    sopra = [r for r in per_d if r["ic"][0] > 0]
    sotto = [r for r in per_d if r["ic"][1] < 0]
    if sopra:
        da = per_d.index(sopra[0])
        picco = next((r for r in per_d[da:] if not r.get("sale_dopo")), per_d[-1])
        testo = ""
        if sotto:
            testo = (f"prima cosa: a {_elenco([r['durata'] for r in sotto])} i segnali fanno "
                     f"peggio del caso (margine tutto sotto lo 0). Poi: ")
        testo += (f"{ESITO_VANTAGGIO} a {_elenco([r['durata'] for r in sopra])} (margine tutto "
                  f"sopra lo 0). La curva smette di salire a {picco['durata']}: vantaggio medio "
                  f"{picco['vantaggio']:+.3f} mosse tipiche ({picco['vantaggio_pct']:+.2f}%)")
        if picco is per_d[-1]:
            testo += (f"; a {picco['durata']} sale ancora, il punto dove smette potrebbe essere "
                      f"oltre (non misurato)")
        testo += (". Per la regola il TP va dove la curva smette di salire, e si passa a T1 "
                  "dopo le letture del 7-14 ott.")
        return {"esito": ESITO_VANTAGGIO, "picco": picco["h"], "sopra": [r["h"] for r in sopra],
                "sotto": [r["h"] for r in sotto], "testo": testo}
    if sotto:
        return {"esito": ESITO_PEGGIO, "picco": None, "sopra": [],
                "sotto": [r["h"] for r in sotto],
                "testo": (f"{ESITO_PEGGIO} a {_elenco([r['durata'] for r in sotto])} (margine "
                          f"tutto sotto lo 0, e a nessuna durata sopra). Per la regola e' la "
                          f"prima cosa da dire.")}
    return {"esito": ESITO_NESSUNO, "picco": None, "sopra": [], "sotto": [],
            "testo": (f"{ESITO_NESSUNO}: a tutte le durate ({_elenco([r['durata'] for r in per_d])}) "
                      f"il vantaggio sta dentro il margine. Per la regola il lavoro sui TP si "
                      f"ferma: il problema e' l'ingresso (o il gate: R1).")}


def segnali_dai_trade(trades, timeframe: str = "15m") -> tuple[list[dict], dict]:
    """Dai trade chiusi del paper i segnali da misurare: TUTTI i trade veri del
    `timeframe` (esplorativi compresi, contati a parte; uscite manuali o da kill
    switch comprese: qui si guarda il prezzo, non il trade). Gli altri timeframe
    (o senza timeframe registrato) si contano e restano fuori. Ritorna (segnali,
    conti)."""
    from bot.learning.report import ingresso_ts

    conti = {"letti": 0, "del_timeframe": 0, "altri_timeframe": {}, "senza_dati": 0,
             "esplorativi": 0}
    segnali: list[dict] = []
    for t in trades or []:
        if not isinstance(t, dict):
            continue
        conti["letti"] += 1
        # senza timeframe registrato vale quello del bot, come in bot/main.py
        # (revisione del 2 ott)
        tf = str(t.get("timeframe") or _tf_bot())
        if tf != timeframe:
            chiave = tf
            conti["altri_timeframe"][chiave] = conti["altri_timeframe"].get(chiave, 0) + 1
            continue
        conti["del_timeframe"] += 1
        ts = ingresso_ts(t)
        lato = str(getattr(t.get("direction"), "value", t.get("direction")) or "")
        lato = lato.lower().split(".")[-1]
        if not ts or lato not in ("long", "short") or not t.get("symbol"):
            conti["senza_dati"] += 1
            continue
        esp = bool(t.get("esplorativa"))
        conti["esplorativi"] += int(esp)
        segnali.append({"symbol": t["symbol"], "lato": lato, "ts": float(ts),
                        "esplorativa": esp, "strategy": t.get("strategy")})
    segnali.sort(key=lambda s: (s["ts"], s["symbol"]))
    return segnali, conti


def _num(x: float, cifre: int = 3) -> str:
    return f"{x:+.{cifre}f}"


def _ic(ic, cifre: int = 3) -> str:
    return "      —       " if ic is None else f"[{ic[0]:+.{cifre}f}, {ic[1]:+.{cifre}f}]"


def righe_tabella(cv: dict) -> list[str]:
    """La tabella della curva in righe di testo: in mosse tipiche (decide) e in %
    (solo per farsi un'idea, non normalizzata)."""
    righe = [f"  {'durata':<7}{'n':>5}  {'segnali':>8}{'caso':>8}{'vantaggio':>10}  "
             f"{'margine 95%':<18}| in %: {'segn.':>6}{'caso':>7}{'vant.':>7}  margine 95%"]
    for r in cv.get("per_durata") or []:
        righe.append(
            f"  {r['durata']:<7}{r['n']:>5}  {_num(r['segnali']):>8}{_num(r['caso']):>8}"
            f"{_num(r['vantaggio']):>10}  {_ic(r['ic']):<18}| "
            f"      {_num(r['segnali_pct'], 2):>6}{_num(r['caso_pct'], 2):>7}"
            f"{_num(r['vantaggio_pct'], 2):>7}  {_ic(r['ic_pct'], 2)}")
    return righe


def riga_verso(nome: str, cv: dict) -> str:
    """Una riga per verso (long/short): vantaggio e margine a ogni durata."""
    if not cv.get("n"):
        return f"  {nome}: nessun trade misurato"
    parti = [f"{r['durata']} {_num(r['vantaggio'])} {_ic(r['ic'])}"
             for r in cv["per_durata"]]
    return f"  {nome} ({cv['n']} trade, {cv['giorni']} giornate): " + " · ".join(parti)
