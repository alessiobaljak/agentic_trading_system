"""
IL SELETTORE — passo 1: addestramento e confronto offline, fuori dal bot.

DA DOVE VIENE
Il disegno e' in docs/disegno_cervello.md, «Punto 2 — Il selettore»: davanti a un
segnale di una coppia validata, un modello dice la probabilita' `p` che il trade
chiuda in utile netto. Oggi (24 set 2026) il bot apre TUTTI i segnali validi con
confidenza fissa a 60, che la calibrazione giudica «flat». Il selettore e' il
primo tentativo di dare a quel numero un significato — ma qui e' SOLO un
esperimento offline: il bot non lo usa, e non lo usera' senza il verdetto di
questo file (batte «apri tutto» su >= 2 finestre su 3) e poi una settimana di
ombra (passo 2).

DA QUALI DATI
Dalle righe del gate: i trade OOS delle coppie PASSATE, che il giro di
`discover_strategies` scrive in `data/selettore/<data>_<intervallo>.jsonl` con le
condizioni del grafico all'ingresso (rsi, adx, stocastico, volatilita', distanza
dalla media, bande, volume, geometria dello stop, mercato). Il PAPER NON ENTRA:
resta il giudice, come per la calibrazione della confidenza (bot/learning/
calibration.py) — se un giorno `p` andra' in ombra sul paper, sara' per
verificarla, non per addestrarla. Nessuna variabile di identita' (coin,
strategia): il modello deve imparare condizioni, non nomi.

COME IMPARA
Regressione logistica con penalita' L2, scritta su numpy/scipy (niente
scikit-learn: il proprietario ha chiesto zero dipendenze nuove). Le variabili
sono poche e fisse (VARIABILI), standardizzate con media e scala che restano nel
modello, cosi' i coefficienti si possono stampare e leggere: «rsi alto ->
p scende» e' una frase, non un peso opaco. Pesi di recenza con mezza vita 180
giorni: un trade di due anni fa pesa un sedicesimo di uno di oggi. Tutto
deterministico: stessi dati, stesso modello, nessun seme nell'addestramento.

Una logistica e' lineare: da sola non puo' imparare «long va bene con BTC sopra
la media, short con BTC sotto», perche' l'effetto di `market_up` avrebbe un solo
segno per tutti e due i versi. Per questo (audit del 24 set 2026) ci sono due
variabili di INTERAZIONE costruite a mano (`long_x_mercato`, `long_x_banda`:
+1 quando direzione e contesto sono d'accordo, -1 quando sono opposti) e le
dummy del regime di mercato all'ingresso (bull, bear, incerto; sideways e' lo
zero di tutte e tre).

COME SI GIUDICA SENZA BARARE
Walk-forward nel tempo, come il gate: si addestra sui trade fino a un taglio e si
misura su quelli DOPO. La soglia si sceglie sul train e si giudica sul test. Il
metro e' uno solo e include il rendimento assoluto, non il win rate: «apri solo
se p >= soglia, size secondo p» contro «apri tutto», su (pnl - drawdown). Un
selettore che apre un trade al mese perde il confronto anche se lo azzecca.

«Batte» su una finestra non basta che sia un `>` secco: un selettore a caso
vince due finestre su tre con probabilita' vicina al 50%. Quindi, per ogni
finestra, le p del test vengono PERMUTATE 200 volte (seme fisso: stesso dato,
stesso verdetto) e si ricalcola il metro della selezione con la stessa soglia;
la finestra e' vinta solo se il metro osservato supera il 95° percentile dei
permutati E la baseline. `p_perm` nella finestra e' la frazione di permutazioni
che fanno almeno quanto l'osservato (audit del 24 set 2026).

Il dataset dal 24 set 2026 contiene anche i trade OOS delle spec BOCCIATE dal
gate (campo `passed`, False; se manca la riga e' vecchia e vale True). Si
addestra su tutte — le condizioni d'ingresso sono vere anche per una spec che
il gate non ha promosso — ma le misure sono riportate anche separate per
`passed` (solo_passate / solo_bocciate), perche' quello che il bot aprirebbe
sono solo i trade delle passate. Il verdetto resta sull'insieme intero.
"""
from __future__ import annotations

import glob
import json
import math
import os
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
from scipy.optimize import minimize

#: dove il gate scrive il dataset (un file per giro e intervallo). Sovrascrivibile
#: da ambiente per i test e per analisi su una copia locale.
SELETTORE_DIR = os.getenv("SELETTORE_DIR", "data/selettore")

#: le variabili del modello, POCHE E FISSE per non imparare il rumore. Le prime
#: dieci arrivano da `feats` della riga; le altre sono derivate qui:
#:  - direzione e ora del giorno (seno/coseno, cosi' le 23 e l'1 sono vicine,
#:    come lo sono sul mercato);
#:  - due INTERAZIONI direzione x contesto (audit 24 set 2026): la logistica e'
#:    lineare e senza queste non puo' dire «long bene col mercato su, short bene
#:    col mercato giu'». `long_x_mercato` = (is_long - 0.5) * (market_up - 0.5) * 4
#:    vale +1 se direzione e mercato concordano, -1 se sono opposti, 0 se il
#:    mercato e' ignoto (market_up neutro = 0.5). `long_x_banda` fa lo stesso
#:    con la posizione nelle bande (bb_pos, 0 = banda bassa, 1 = alta);
#:  - le dummy del regime all'ingresso (riga `regime`): bull, bear, incerto;
#:    sideways e regime mancante sono tutte e tre a 0.
VARIABILI = ("rsi", "adx", "stoch_k", "atr_pct", "dist_ema", "bb_pos", "vol_ratio",
             "stop_pct", "r1", "market_up", "is_long", "hour_sin", "hour_cos",
             "long_x_mercato", "long_x_banda",
             "regime_bull", "regime_bear", "regime_incerto")

#: quante variabili di VARIABILI vengono direttamente da `feats`.
_N_FEATS = 10

#: regime -> (regime_bull, regime_bear, regime_incerto). Le chiavi sono i valori
#: di `Regime` in bot/core/models.py; sideways e regime ignoto = tutte a 0.
_REGIMI = {"bull_trending": (1.0, 0.0, 0.0), "bear_trending": (0.0, 1.0, 0.0),
           "high_uncertainty": (0.0, 0.0, 1.0)}

#: variabili di `feats` che, se mancano, rendono la riga inutilizzabile: senza
#: rsi o senza geometria dello stop non c'e' una «condizione» da imparare.
_OBBLIGATORIE = ("rsi", "adx", "stoch_k", "atr_pct", "dist_ema", "stop_pct", "r1")

#: valori neutri per le variabili che possono mancare senza rompere la riga:
#: mercato ignoto = a meta', bande non calcolabili = al centro, volume senza
#: media = «normale».
_NEUTRI = {"market_up": 0.5, "bb_pos": 0.5, "vol_ratio": 1.0}

#: mezza vita dei pesi di recenza, in giorni: un trade vecchio di 180 giorni pesa
#: la meta' di uno di oggi. Dal disegno (docs/disegno_cervello.md).
MEZZA_VITA_GIORNI = 180.0

#: le soglie fra cui scegliere sul train, e i limiti della size in funzione di p
#: (dal disegno: size fra 0.5 e 1.25, il risk manager puo' solo ridurre).
SOGLIE = (0.40, 0.45, 0.50, 0.55, 0.60, 0.65)
SIZE_MIN, SIZE_MAX = 0.5, 1.25

#: quota delle righe (in ordine di tempo) che fa da train alla PRIMA finestra;
#: il resto si divide in parti uguali fra le finestre di test.
QUOTA_TRAIN_INIZIALE = 0.4

BATTE, NON_BATTE, INSUFFICIENTE = "batte", "non batte", "campione insufficiente"

FAMIGLIE = ("reversion", "momentum", "breakout", "altro")


# --------------------------------------------------------------------------- #
# Dalla riga del dataset al vettore                                            #
# --------------------------------------------------------------------------- #
def _float(v) -> float | None:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def _ora(row: dict) -> int | None:
    """Ora del giorno (UTC): dal campo `hour` se c'e', altrimenti da `entry_ts`."""
    h = row.get("hour")
    if h is not None:
        try:
            return int(h) % 24
        except (TypeError, ValueError):
            pass
    ts = _float(row.get("entry_ts"))
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc).hour
    except (OverflowError, OSError, ValueError):
        return None


def _regime(row: dict) -> tuple[float, float, float]:
    """Le tre dummy del regime. Il gate scrive `str(t.regime)`: puo' arrivare
    «bull_trending» o «Regime.BULL_TRENDING», quindi si prende l'ultimo pezzo
    dopo il punto, in minuscolo. Ignoto o sideways -> (0, 0, 0)."""
    reg = row.get("regime")
    if reg is None:
        return (0.0, 0.0, 0.0)
    nome = str(reg).strip().lower().rsplit(".", 1)[-1]
    return _REGIMI.get(nome, (0.0, 0.0, 0.0))


def vettore(row: dict) -> list[float] | None:
    """La riga del dataset come lista di float nell'ordine di VARIABILI.

    None se manca una variabile obbligatoria: meglio scartare la riga che
    inventare una condizione di mercato. Le tre opzionali prendono il valore
    neutro (_NEUTRI); regime mancante = sideways (dummy a 0)."""
    feats = row.get("feats") or {}
    if not isinstance(feats, dict):
        return None
    out: list[float] = []
    for nome in VARIABILI[:_N_FEATS]:
        v = _float(feats.get(nome))
        if v is None:
            if nome in _NEUTRI:
                v = _NEUTRI[nome]
            else:
                return None
        out.append(v)
    direction = str(row.get("direction", "")).lower()
    if direction not in ("long", "short"):
        return None
    is_long = 1.0 if direction == "long" else 0.0
    out.append(is_long)
    h = _ora(row)
    if h is None:
        return None
    ang = 2.0 * math.pi * h / 24.0
    out.append(math.sin(ang))
    out.append(math.cos(ang))
    # interazioni direzione x contesto (vedi VARIABILI): con market_up/bb_pos al
    # neutro 0.5 valgono 0, cioe' «non so», non «concorde».
    market_up = out[VARIABILI.index("market_up")]
    bb_pos = out[VARIABILI.index("bb_pos")]
    out.append((is_long - 0.5) * (market_up - 0.5) * 4.0)
    out.append((is_long - 0.5) * (bb_pos - 0.5) * 4.0)
    out.extend(_regime(row))
    return out


def _passata(row: dict) -> bool:
    """La riga viene da una spec passata dal gate? Se il campo manca la riga e'
    di prima del 24 set 2026, quando si scrivevano SOLO le passate: True."""
    p = row.get("passed")
    return True if p is None else bool(p)


def _esito(row: dict) -> bool | None:
    """Vinto o perso. `is_win` se c'e'; altrimenti dal pnl netto."""
    w = row.get("is_win")
    if w is not None:
        return bool(w)
    p = _float(row.get("pnl_pct"))
    return None if p is None else p > 0


# --------------------------------------------------------------------------- #
# Lettura del dataset                                                          #
# --------------------------------------------------------------------------- #
#: cosa ha visto l'ultima `carica_righe`: quanti file, quante righe rotte
#: saltate, quanti duplicati fusi (stesso trade, stessa strategia, altro giro),
#: quante gemelle fuse (stesso trade, strategia diversa). Serve al report per
#: dire da dove vengono i numeri, senza cambiare la firma della funzione.
ULTIMA_LETTURA: dict[str, int] = {"file": 0, "scartate": 0, "duplicate": 0,
                                  "gemelle_fuse": 0, "righe": 0}


def _chiave(row: dict) -> tuple | None:
    """(symbol, entry_ts, direction): identifica il TRADE, non la coppia.

    Fino al 24 set 2026 la chiave conteneva la strategia, e le coppie gemelle
    (stessa coin, spec diverse che entrano sulla stessa candela nello stesso
    verso) mettevano nel dataset lo stesso trade k volte: il modello lo vedeva
    con peso k e il walk-forward lo contava k volte. Un trade e' un trade."""
    ts = _float(row.get("entry_ts"))
    sym = row.get("symbol")
    direction = str(row.get("direction", "")).lower()
    if ts is None or not sym or direction not in ("long", "short"):
        return None
    return (str(sym), ts, direction)


def carica_righe(cartella: str | None = None, giorni: int | None = None) -> list[dict]:
    """Legge tutti i `.jsonl` della cartella e restituisce le righe DEDUPLICATE.

    Un giro al giorno rivaluta le stesse coppie, quindi lo stesso trade compare in
    piu' file: si tiene l'ULTIMA occorrenza (file in ordine di nome = di data,
    righe in ordine di scrittura), che porta i costi e la geometria piu' recenti.
    Lo stesso vale per le coppie gemelle (stessa coin, strategia diversa, stesso
    ingresso): una riga sola, l'ultima, contata in `gemelle_fuse`; se una qualsiasi
    delle gemelle era di una spec passata, la riga fusa resta `passed` — quel trade
    il bot lo aprirebbe davvero.
    Fail-open sulle righe rotte: una riga illeggibile si salta e si conta, non
    ferma il report. `giorni` tiene solo i trade entrati negli ultimi N giorni
    (rispetto al trade piu' recente presente, non all'orologio: cosi' il
    risultato non cambia da un'ora all'altra)."""
    cartella = cartella or SELETTORE_DIR
    file = sorted(glob.glob(os.path.join(cartella, "*.jsonl")))
    viste: dict[tuple, dict] = {}
    scartate = duplicate = gemelle = 0
    for path in file:
        try:
            with open(path, encoding="utf-8") as f:
                for riga in f:
                    riga = riga.strip()
                    if not riga:
                        continue
                    try:
                        row = json.loads(riga)
                    except ValueError:
                        scartate += 1
                        continue
                    if not isinstance(row, dict):
                        scartate += 1
                        continue
                    k = _chiave(row)
                    if k is None:
                        scartate += 1
                        continue
                    row.setdefault("famiglia", "altro")
                    prima = viste.get(k)
                    if prima is not None:
                        if str(prima.get("strategy")) == str(row.get("strategy")):
                            duplicate += 1
                        else:
                            gemelle += 1
                        if _passata(prima) and not _passata(row):
                            row["passed"] = True
                    viste[k] = row
        except OSError:
            continue
    righe = sorted(viste.values(), key=lambda r: float(r["entry_ts"]))
    if giorni is not None and righe:
        ultimo = float(righe[-1]["entry_ts"])
        limite = ultimo - float(giorni) * 86400.0
        righe = [r for r in righe if float(r["entry_ts"]) >= limite]
    ULTIMA_LETTURA.update({"file": len(file), "scartate": scartate,
                           "duplicate": duplicate, "gemelle_fuse": gemelle,
                           "righe": len(righe)})
    return righe


# --------------------------------------------------------------------------- #
# Regressione logistica (L2, pesata) su numpy/scipy                            #
# --------------------------------------------------------------------------- #
def _matrice(righe: list[dict]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[dict]]:
    """X (n x d), y (0/1), pnl_pct, entry_ts e le righe USABILI, nell'ordine dato."""
    xs, ys, pnl, ts, usate = [], [], [], [], []
    for r in righe:
        v = vettore(r)
        e = _esito(r)
        p = _float(r.get("pnl_pct"))
        t = _float(r.get("entry_ts"))
        if v is None or e is None or p is None or t is None:
            continue
        xs.append(v)
        ys.append(1.0 if e else 0.0)
        pnl.append(p)
        ts.append(t)
        usate.append(r)
    if not xs:
        d = len(VARIABILI)
        return (np.zeros((0, d)), np.zeros(0), np.zeros(0), np.zeros(0), [])
    return (np.asarray(xs, dtype=float), np.asarray(ys, dtype=float),
            np.asarray(pnl, dtype=float), np.asarray(ts, dtype=float), usate)


def _pesi_recenza(ts: np.ndarray, mezza_vita: float | None, riferimento: float | None) -> np.ndarray:
    """peso = 0.5 ** (eta_giorni / mezza_vita), normalizzato a somma n cosi' la
    forza della regolarizzazione non dipende da quanto sono vecchi i dati."""
    n = len(ts)
    if n == 0:
        return np.zeros(0)
    if not mezza_vita:
        return np.ones(n)
    rif = float(riferimento) if riferimento is not None else float(ts.max())
    eta = np.clip((rif - ts) / 86400.0, 0.0, None)
    w = np.power(0.5, eta / float(mezza_vita))
    s = float(w.sum())
    return w * (n / s) if s > 0 else np.ones(n)


def _logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def addestra(righe: list[dict], lam: float = 1.0,
             mezza_vita_giorni: float | None = MEZZA_VITA_GIORNI,
             riferimento_ts: float | None = None,
             famiglia: str = "tutte") -> dict:
    """Addestra la logistica e restituisce il modello come dict serializzabile.

    Obiettivo: somma pesata delle log-perdite + lam/2 * ||coef||^2 (l'intercetta
    non e' penalizzata). Con i pesi a somma n equivale a C = 1/lam di
    scikit-learn, cosi' `lam` ha un significato noto. Le variabili sono
    standardizzate con media e scala salvate nel modello: `prob` le riapplica.
    Una variabile costante (scala 0) prende scala 1 e coefficiente ~0.
    Con una sola classe presente non c'e' nulla da separare: coefficienti a zero
    e intercetta al tasso di vittoria (con Laplace), cosi' `prob` resta sensata.
    Nessun random: L-BFGS da zero, gradiente analitico."""
    X, y, _, ts, _ = _matrice(righe)
    n, d = X.shape
    media = X.mean(axis=0) if n else np.zeros(d)
    scala = X.std(axis=0) if n else np.ones(d)
    scala = np.where(scala > 1e-12, scala, 1.0)
    base = {"variabili": list(VARIABILI), "media": media.tolist(), "scala": scala.tolist(),
            "n": int(n), "famiglia": famiglia, "lam": float(lam),
            "mezza_vita_giorni": mezza_vita_giorni,
            "riferimento_ts": (float(riferimento_ts) if riferimento_ts is not None
                               else (float(ts.max()) if n else None))}
    vinti = int(y.sum()) if n else 0
    if n == 0 or vinti == 0 or vinti == n:
        return {**base, "coef": [0.0] * d,
                "intercetta": _logit((vinti + 1.0) / (n + 2.0))}

    Z = (X - media) / scala
    w = _pesi_recenza(ts, mezza_vita_giorni, base["riferimento_ts"])

    def obiettivo(theta: np.ndarray):
        b, c = theta[0], theta[1:]
        z = Z @ c + b
        # log(1 + e^-z) e log(1 + e^z) senza overflow
        nll = y * np.logaddexp(0.0, -z) + (1.0 - y) * np.logaddexp(0.0, z)
        p = 1.0 / (1.0 + np.exp(-z))
        r = w * (p - y)
        f = float((w * nll).sum() + 0.5 * lam * float(c @ c))
        g = np.concatenate(([r.sum()], Z.T @ r + lam * c))
        return f, g

    res = minimize(obiettivo, np.zeros(d + 1), jac=True, method="L-BFGS-B",
                   options={"maxiter": 500})
    theta = res.x
    return {**base, "coef": [float(v) for v in theta[1:]], "intercetta": float(theta[0])}


def _prob_matrice(modello: dict, X: np.ndarray) -> np.ndarray:
    Z = (X - np.asarray(modello["media"], dtype=float)) / np.asarray(modello["scala"], dtype=float)
    z = Z @ np.asarray(modello["coef"], dtype=float) + float(modello["intercetta"])
    return 1.0 / (1.0 + np.exp(-z))


def prob(modello: dict | None, row: dict) -> float | None:
    """p di chiudere in utile per questa riga secondo il modello. None se la riga
    non e' vettorizzabile o il modello non c'e': chi chiama fa come oggi
    (fail-open), non inventa un numero."""
    if not modello:
        return None
    v = vettore(row)
    if v is None:
        return None
    try:
        return float(_prob_matrice(modello, np.asarray([v], dtype=float))[0])
    except (KeyError, TypeError, ValueError):
        return None


# --------------------------------------------------------------------------- #
# Il metro: «apri tutto» contro «selettore»                                    #
# --------------------------------------------------------------------------- #
def size_da_p(p: float, soglia: float) -> float:
    """Size fra 0.5 e 1.25 in funzione di quanto p supera la soglia."""
    return float(min(max(SIZE_MIN + (p - soglia) * 2.0, SIZE_MIN), SIZE_MAX))


def _drawdown(pnl: np.ndarray) -> float:
    """Massima discesa dal picco della curva cumulata (somma dei pnl_pct in
    ordine di tempo, senza capitalizzare: e' un confronto, non un rendiconto).
    Restituita POSITIVA."""
    if len(pnl) == 0:
        return 0.0
    cum = np.cumsum(pnl)
    picco = np.maximum.accumulate(np.concatenate(([0.0], cum)))[1:]
    return float(np.max(picco - cum))


def _misura(pnl: np.ndarray) -> dict:
    n = int(len(pnl))
    tot = float(pnl.sum()) if n else 0.0
    dd = _drawdown(pnl)
    wr = float((pnl > 0).mean()) if n else 0.0
    return {"n": n, "pnl": round(tot, 6), "dd": round(dd, 6),
            "win_rate": round(wr, 4), "metro": round(tot - dd, 6)}


def _pnl_selettore(p: np.ndarray, pnl: np.ndarray, soglia: float,
                   con_size: bool = True) -> np.ndarray:
    """I pnl dei trade presi (p >= soglia). Con `con_size` ogni pnl e' moltiplicato
    per la size che il bot userebbe; senza, e' la SOLA selezione a size 1.

    Il verdetto si dà sulla sola selezione, di proposito: in un mercato in
    perdita basta dimezzare la size di tutti i trade per «vincere» su (pnl - dd)
    senza aver scelto niente. Quello che vogliamo sapere e' se il selettore
    distingue i segnali buoni dai cattivi; la size e' un'informazione in piu',
    stampata accanto (rilievo dell'implementatore, 24 set 2026)."""
    presi = p >= soglia
    if not presi.any():
        return np.zeros(0)
    if not con_size:
        return pnl[presi]
    size = np.clip(SIZE_MIN + (p[presi] - soglia) * 2.0, SIZE_MIN, SIZE_MAX)
    return pnl[presi] * size


def _scegli_soglia(p: np.ndarray, pnl: np.ndarray, soglie) -> float:
    """La soglia che sul TRAIN massimizza (pnl - drawdown) dei trade presi. A
    parita' vince la piu' bassa (piu' trade): il confronto e' iterato in ordine
    con `>` stretto, quindi e' deterministico."""
    migliore, valore = None, None
    for s in soglie:
        m = _misura(_pnl_selettore(p, pnl, s, con_size=False))["metro"]
        if valore is None or m > valore:
            migliore, valore = float(s), m
    return migliore if migliore is not None else float(soglie[0])


#: permutazioni per finestra e seme base: deterministico, cosi' due lanci sullo
#: stesso dataset danno lo stesso verdetto (audit 24 set 2026).
N_PERMUTAZIONI = 200
SEME_PERMUTAZIONI = 20260924
PERCENTILE_PERM = 95.0


def _permuta(p: np.ndarray, pnl: np.ndarray, soglia: float, osservato: float,
             seme: int, n_perm: int = N_PERMUTAZIONI) -> tuple[float, float]:
    """Il metro della selezione con le p RIMESCOLATE fra i trade del test, n_perm
    volte, stessa soglia. Ritorna (p_perm, soglia_perm): la frazione di
    permutazioni che fanno almeno quanto l'osservato e il 95° percentile dei
    metri permutati. Se le p sono a caso, il selettore osservato e' una di
    queste permutazioni: per dire che ha scelto davvero deve batterle quasi
    tutte."""
    if len(p) == 0:
        return 1.0, 0.0
    rng = np.random.RandomState(seme)
    metri = np.empty(n_perm)
    for i in range(n_perm):
        p_perm = p[rng.permutation(len(p))]
        metri[i] = _misura(_pnl_selettore(p_perm, pnl, soglia, con_size=False))["metro"]
    p_perm = float((metri >= osservato).mean())
    return p_perm, float(np.percentile(metri, PERCENTILE_PERM))


def _misure_sottoinsieme(p: np.ndarray, pnl: np.ndarray, maschera: np.ndarray,
                         soglia: float) -> dict:
    """Baseline e selezione (size 1) sui soli trade con `maschera` vera."""
    return {"n": int(maschera.sum()),
            "baseline": _misura(pnl[maschera]),
            "selezione": _misura(_pnl_selettore(p[maschera], pnl[maschera], soglia,
                                                con_size=False))}


def _data(ts: float | None) -> str | None:
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).strftime("%Y-%m-%d")
    except (OverflowError, OSError, ValueError):
        return None


def walk_forward(righe: list[dict], n_finestre: int = 3, soglie=SOGLIE,
                 min_train: int = 500, lam: float = 1.0,
                 mezza_vita_giorni: float | None = MEZZA_VITA_GIORNI,
                 famiglia: str = "tutte") -> dict:
    """Confronto walk-forward «apri tutto» contro «selettore».

    Le righe si ordinano per entry_ts; la prima quota (QUOTA_TRAIN_INIZIALE) e'
    il train della finestra 1, il resto si divide in `n_finestre` fette di test
    consecutive. Per la finestra k il train e' TUTTO cio' che precede la fetta k
    (finestra espansiva): mai lo stesso periodo da tutte e due le parti.
    In ogni finestra: si addestra sul train, si sceglie la soglia sul train, si
    misura sul test. Il selettore batte la baseline su una finestra se (pnl - dd)
    della SOLA selezione (stessi trade a size 1) e' maggiore della baseline E
    maggiore del 95° percentile di N_PERMUTAZIONI selezioni con le p rimescolate
    (seme SEME_PERMUTAZIONI + indice finestra, quindi deterministico): senza
    questo margine un selettore a caso vinceva 2 finestre su 3 una volta su due
    (audit 24 set 2026). La versione con la size e' riportata accanto ma non
    decide.
    Le righe delle spec bocciate dal gate (`passed` False) entrano nel train e
    nel test come le altre; ogni finestra riporta pero' anche le misure sulle
    sole passate e sulle sole bocciate (`solo_passate`, `solo_bocciate`).
    Verdetto: BATTE se vince su almeno 2 finestre su 3 (in generale: piu' della
    meta'); CAMPIONE INSUFFICIENTE se anche una sola finestra ha train < min_train
    — con meno di 500 trade la logistica impara i nomi dei giorni, non le
    condizioni, ed e' proprio il sovradattamento che il disegno vuole evitare.
    Il modello su TUTTE le righe e' incluso per la pubblicazione futura; il bot
    oggi non lo legge."""
    X, y, pnl, ts, usate = _matrice(righe)
    ordine = np.argsort(ts, kind="stable")
    X, y, pnl, ts = X[ordine], y[ordine], pnl[ordine], ts[ordine]
    usate = [usate[i] for i in ordine]
    passate = np.asarray([_passata(r) for r in usate], dtype=bool)
    n = len(usate)
    scartate = len(righe) - n

    out = {"famiglia": famiglia, "n_righe": n, "n_scartate": int(scartate),
           "n_passate": int(passate.sum()), "n_bocciate": int(n - passate.sum()),
           "n_finestre": int(n_finestre), "n_permutazioni": int(N_PERMUTAZIONI),
           "min_train": int(min_train), "soglie": [float(s) for s in soglie],
           "da": _data(float(ts[0])) if n else None,
           "a": _data(float(ts[-1])) if n else None,
           "finestre": [], "vittorie": 0, "verdetto": INSUFFICIENTE,
           "modello": None, "soglia_consigliata": None}

    # tagli: [0, t0) train iniziale, poi n_finestre fette uguali fino a n
    t0 = int(round(n * QUOTA_TRAIN_INIZIALE))
    tagli = [t0]
    resto = n - t0
    for k in range(1, n_finestre + 1):
        tagli.append(t0 + int(round(resto * k / n_finestre)))

    insufficiente = False
    for k in range(n_finestre):
        a, b = tagli[k], tagli[k + 1]
        fin = {"finestra": k + 1, "train_n": int(a), "test_n": int(b - a),
               "train_da": _data(float(ts[0])) if a else None,
               "train_a": _data(float(ts[a - 1])) if a else None,
               "test_da": _data(float(ts[a])) if b > a else None,
               "test_a": _data(float(ts[b - 1])) if b > a else None,
               "soglia": None, "baseline": None, "selettore": None,
               "batte": False, "margine": None, "insufficiente": False,
               "p_perm": None, "soglia_perm": None,
               "solo_passate": None, "solo_bocciate": None}
        if a < min_train or b <= a:
            fin["insufficiente"] = True
            insufficiente = True
            out["finestre"].append(fin)
            continue
        train = usate[:a]
        modello = addestra(train, lam=lam, mezza_vita_giorni=mezza_vita_giorni,
                           riferimento_ts=float(ts[a - 1]), famiglia=famiglia)
        p_train = _prob_matrice(modello, X[:a])
        soglia = _scegli_soglia(p_train, pnl[:a], soglie)
        p_test = _prob_matrice(modello, X[a:b])
        pnl_test = pnl[a:b]
        base = _misura(pnl_test)
        selez = _misura(_pnl_selettore(p_test, pnl_test, soglia, con_size=False))
        sel = _misura(_pnl_selettore(p_test, pnl_test, soglia))
        # il verdetto e' sulla SELEZIONE a size uguale (vedi _pnl_selettore), e
        # solo se batte anche le p rimescolate (vedi _permuta)
        p_perm, soglia_perm = _permuta(p_test, pnl_test, soglia, selez["metro"],
                                       seme=SEME_PERMUTAZIONI + k)
        pass_test = passate[a:b]
        fin.update({"soglia": soglia, "baseline": base, "selezione": selez,
                    "selettore": sel,
                    "batte": bool(selez["metro"] > base["metro"]
                                  and selez["metro"] > soglia_perm),
                    "margine": round(selez["metro"] - base["metro"], 6),
                    "p_perm": round(p_perm, 4), "soglia_perm": round(soglia_perm, 6),
                    "solo_passate": _misure_sottoinsieme(p_test, pnl_test, pass_test, soglia),
                    "solo_bocciate": _misure_sottoinsieme(p_test, pnl_test, ~pass_test, soglia),
                    "p_media_test": round(float(p_test.mean()), 4) if b > a else None})
        out["finestre"].append(fin)

    vittorie = sum(1 for f in out["finestre"] if f["batte"])
    out["vittorie"] = int(vittorie)
    if insufficiente:
        out["verdetto"] = INSUFFICIENTE
    else:
        out["verdetto"] = BATTE if vittorie * 2 > n_finestre else NON_BATTE

    # il modello su tutto, per la pubblicazione futura (passo 2/3): serve almeno
    # qualche riga per avere coefficienti da stampare, ma sotto min_train non e'
    # un modello da usare — il verdetto lo dice.
    if n >= max(len(VARIABILI) + 1, 20):
        modello = addestra(usate, lam=lam, mezza_vita_giorni=mezza_vita_giorni,
                           famiglia=famiglia)
        out["modello"] = modello
        out["soglia_consigliata"] = _scegli_soglia(_prob_matrice(modello, X), pnl, soglie)
    return out


def report_per_famiglia(righe: list[dict], **kw) -> dict:
    """walk_forward per ogni famiglia di strategie, piu' «tutte». Un modello per
    famiglia (dal disegno): per strategia i trade sono troppo pochi, e famiglie
    diverse cercano condizioni diverse (la reversion vuole rsi estremo, il
    momentum lo teme). Le righe delle spec bocciate NON si filtrano qui: si
    addestra su tutte e ogni finestra riporta le misure separate (24 set 2026)."""
    gruppi: dict[str, list[dict]] = defaultdict(list)
    for r in righe:
        fam = str(r.get("famiglia") or "altro")
        gruppi[fam if fam in FAMIGLIE else "altro"].append(r)
    out = {"tutte": walk_forward(righe, famiglia="tutte", **kw)}
    for fam in FAMIGLIE:
        if gruppi.get(fam):
            out[fam] = walk_forward(gruppi[fam], famiglia=fam, **kw)
    return out


# --------------------------------------------------------------------------- #
# Passo 2 — l'ombra nel bot (25 set 2026)                                      #
# --------------------------------------------------------------------------- #
# Il verdetto del passo 1 e' NON BATTE (1 finestra su 3, ops 0231). Il disegno
# vorrebbe l'ombra solo dopo un «batte», ma il proprietario vuole imparare da
# ogni trade del paper: se il bot annota su OGNI apertura la p del selettore,
# fra qualche settimana si potra' misurare SUL PAPER se p predice l'esito
# (calibrazione), senza che il selettore abbia mai deciso nulla. Il paper resta
# giudice, non maestro: qui non si addestra, si legge un modello pubblicato.
#
# `scripts/selettore_report.py` pubblica `selector/current`; il bot lo rilegge
# ogni ora (`TradingBot._load_selettore`) e, subito prima di aprire, calcola p
# con la STESSA funzione delle variabili del gate (`feats_ingresso`) e la stessa
# `prob` di qui. Nessuna decisione cambia: p e soglia viaggiano sulla posizione
# e sul trade chiuso (`selector_p`, `selector_soglia`) e basta.

#: la soglia da usare se il documento pubblicato non ne porta una leggibile.
SOGLIA_DEFAULT = 0.5


def valida_pubblicato(doc) -> dict | None:
    """`selector/current` letto da Firestore -> {modello, soglia, ...} usabile,
    o None se il documento manca o non e' un modello di QUESTA versione.

    Il controllo sulle variabili e' il punto: un modello pubblicato con un altro
    elenco di VARIABILI (una versione vecchia o futura del codice) darebbe una p
    calcolata su colonne sbagliate, cioe' un numero che sembra vero e non lo e'.
    Meglio nessuna ombra che un'ombra che mente."""
    if not isinstance(doc, dict):
        return None
    m = doc.get("modello")
    if not isinstance(m, dict):
        return None
    try:
        if [str(v) for v in (m.get("variabili") or [])] != list(VARIABILI):
            return None
        d = len(VARIABILI)
        coef = [float(x) for x in m["coef"]]
        media = [float(x) for x in m["media"]]
        scala = [float(x) for x in m["scala"]]
        intercetta = float(m["intercetta"])
    except (KeyError, TypeError, ValueError):
        return None
    if len(coef) != d or len(media) != d or len(scala) != d:
        return None
    if not all(math.isfinite(x) for x in coef + media + scala + [intercetta]):
        return None
    soglia = _float(doc.get("soglia"))
    if soglia is None or not 0.0 < soglia < 1.0:
        soglia = SOGLIA_DEFAULT
    return {"modello": {**m, "coef": coef, "media": media, "scala": scala,
                        "intercetta": intercetta},
            "soglia": float(soglia),
            "verdetto": doc.get("verdetto"), "stato": doc.get("stato"),
            "righe": doc.get("righe"), "generato_at": doc.get("generato_at")}


def riga_dal_vivo(symbol: str, strategy: str, direction: str, regime,
                  hour: int | None, feats: dict | None,
                  entry_ts: float | None = None) -> dict:
    """La riga del selettore per un trade che il bot sta per aprire, nello STESSO
    formato delle righe del gate (`righe_selettore` in scripts/discover_strategies.py)
    per la parte che `vettore` legge: symbol, strategy, direction, regime, hour,
    entry_ts, feats. Mancano solo le chiavi dell'ESITO (pnl, is_win, mfe_r,
    bars_held, passed...), che dal vivo non esistono ancora: l'ombra e' proprio
    il modo di scoprirlo dopo. `regime` puo' essere l'enum o la stringa: si
    salva `value` se c'e', come fa il gate con `str(t.regime)`."""
    reg = getattr(regime, "value", regime)
    return {"symbol": str(symbol), "strategy": str(strategy),
            "direction": str(getattr(direction, "value", direction)).lower(),
            "regime": (str(reg) if reg is not None else None),
            "entry_ts": (float(entry_ts) if entry_ts is not None else None),
            "hour": (int(hour) if hour is not None else None),
            "feats": dict(feats or {})}


def variabili_mancanti(row: dict) -> list[str]:
    """Quali variabili OBBLIGATORIE mancano alla riga (perche' `vettore` dira'
    None): serve al log dell'ombra per dire cosa non si e' potuto misurare dal
    vivo, invece di un muto «p non calcolabile»."""
    feats = row.get("feats") or {}
    out = [n for n in _OBBLIGATORIE if _float(feats.get(n) if isinstance(feats, dict) else None) is None]
    if str(row.get("direction", "")).lower() not in ("long", "short"):
        out.append("direction")
    if _ora(row) is None:
        out.append("hour")
    return out
