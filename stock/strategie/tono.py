"""Il tono delle notizie del mese (`stock/prove/P028_tono_delle_notizie.md`): il voto di una notizia, il tono di un titolo, la scelta."""
from __future__ import annotations

import re
from datetime import date, datetime

import numpy as np
import pandas as pd

from stock.simulatore.portafoglio import Storia, StatoConto, verso_pesi

BUONE = frozenset("""beat beats tops topped exceeds exceeded raises raised raise upgrade upgrades upgraded outperform overweight buy
record strong stronger growth grows wins win awarded approval approves approved breakthrough positive profit profitable buyback
repurchase expands expansion partnership accelerates boosts boost improves improved better bullish""".split())
CATTIVE = frozenset("""miss misses missed lowers lowered cuts cut downgrade downgrades downgraded underperform underweight sell weak
weaker loss losses decline declines warns warning lawsuit sues sued probe investigation subpoena recall recalls fraud bankruptcy
default layoffs delays delayed halts halted resigns breach fine fined penalty negative bearish disappointing shortfall impairment
restructuring suspends suspended terminates terminated fails failed rejects rejected concerns""".split())
SIMBOLI_MASSIMI, NOTIZIE_MINIME = 3, 3
QUINTO, TITOLI_MASSIMI, TITOLI_MINIMI = 0.2, 50, 25
FONDI = ("ETF", "ETN", "Fund", "Index", "iShares", "ProShares", "SPDR", "Vanguard", "Direxion", "WisdomTree", "VanEck", "Global X",
         "First Trust", "Invesco")
_PAROLE = re.compile(r"[a-z]+")


def voto(testo: str) -> int:
    """+1 se le parole buone sono più delle cattive, −1 se meno, 0 se pari."""
    parole = _PAROLE.findall(testo.lower())
    b = sum(p in BUONE for p in parole)
    c = sum(p in CATTIVE for p in parole)
    return (b > c) - (b < c)


def toni(notizie: pd.DataFrame, confini: list[datetime]) -> list[dict[str, tuple[float, int]]]:
    """`notizie`: colonne creata (istante), simboli (lista), testo. `confini`: gli istanti delle decisioni, in ordine. Per ogni
    intervallo (confine prima, confine] : simbolo -> (tono, numero di notizie), solo con almeno NOTIZIE_MINIME notizie dell'azienda."""
    n = notizie[notizie["simboli"].map(len).between(1, SIMBOLI_MASSIMI)]
    c = np.array([pd.Timestamp(x).tz_convert("UTC").value for x in confini])
    quando = n["creata"].map(lambda t: t.value).to_numpy()
    periodo = np.searchsorted(c, quando, side="left") - 1          # creata in (c[k], c[k+1]] -> k
    df = pd.DataFrame({"periodo": periodo, "simboli": n["simboli"].to_numpy(), "voto": n["testo"].map(voto).to_numpy()})
    df = df[(df["periodo"] >= 0) & (df["periodo"] < len(c) - 1)].explode("simboli")
    out: list[dict[str, tuple[float, int]]] = [{} for _ in range(len(c) - 1)]
    g = df.groupby(["periodo", "simboli"])["voto"].agg(["mean", "size"])
    for (k, s), r in g[g["size"] >= NOTIZIE_MINIME].iterrows():
        out[int(k)][s] = (float(r["mean"]), int(r["size"]))
    return out


def classifica(tono: dict[str, tuple[float, int]], ammessi, piu_bassi: bool = False) -> list[str]:
    """I titoli ammessi con il tono, dal più alto (o dal più basso): a pari tono prima chi ha più notizie, poi in ordine alfabetico."""
    segno = 1 if piu_bassi else -1
    return sorted((s for s in tono if s in ammessi), key=lambda s: (segno * tono[s][0], -tono[s][1], s))


def scegli(tono: dict[str, tuple[float, int]], ammessi, piu_bassi: bool = False) -> list[str]:
    """Il 20% con il tono più alto (o più basso), al massimo 50; nessuno se i titoli con il tono sono meno di 25."""
    ordine = classifica(tono, ammessi, piu_bassi)
    if len(ordine) < TITOLI_MINIMI:
        return []
    return ordine[:min(TITOLI_MASSIMI, int(QUINTO * len(ordine)))]


def e_un_fondo(nome: str) -> bool:
    return any(x.lower() in nome.lower() for x in FONDI)


def strategia(elenchi: dict[date, list[str]], fondo: str, lato: int = 1):
    """`elenchi`: giorno della decisione -> titoli scelti. Metà del conto nei titoli a pesi uguali, metà venduta allo scoperto nel
    `fondo`; elenco vuoto: tutto chiuso. Gli ordini partono all'apertura del giorno di borsa dopo."""
    def decidi(giorno: date, storia: Storia, stato: StatoConto) -> list:
        scelti = elenchi.get(giorno)
        if scelti is None:
            return []
        pesi = {s: lato * 0.5 / len(scelti) for s in scelti}
        if scelti:
            pesi[fondo] = -lato * 0.5
        prezzi = {}
        for s in set(pesi) | set(stato.azioni):
            h = storia(s)
            if h is not None and not h.empty:
                prezzi[s] = float(h["close"].iloc[-1])
        return verso_pesi(stato, pesi, prezzi, etichetta="mese")
    return decidi
