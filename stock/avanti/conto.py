"""Il conto demo condiviso fra la prima candela, la miscela (decisione del proprietario, 12 novembre 2026: «per la miscela [...] usa
quello attuale») e la prova 45 (decisione del 23 novembre 2026: «metti la prova 45 sul demo», `GAMMA.md`). Le strategie stanno nello
stesso conto di Alpaca ma non si toccano: si dividono per **titolo** (la miscela compra solo SPY e QQQ, la prova 45 solo VOO, mai fra
le azioni della prima candela) e ognuna ha il suo **capitale virtuale** di 100'000 dollari, su cui calcola le quantità e il
rendimento. Il conto vero ha quindi più esposizione del suo valore: è solo il contenitore; il risultato di ciascuna si legge sul suo
capitale.

La contabilità: alla partenza della miscela si fotografa il valore del conto (`conto_condiviso.json`). Da lì il guadagno della prima
candela è la somma del suo diario (ogni sera è senza posizioni) più il non realizzato dei suoi titoli; quello della prova 45 è la somma
del suo diario (`gamma_diario.csv`, anche lei ogni sera senza posizioni) più, per oggi, le sue esecuzioni e le sue posizioni; tutto il
resto della variazione del conto è della miscela. I valori di fine giornata stanno in `valori.csv` (numeri nostri, non prezzi di borsa).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

QUI = Path(__file__).resolve().parent
STATO = QUI / "conto_condiviso.json"
VALORI = QUI / "valori.csv"
SIMBOLI_MISCELA = ("SPY", "QQQ")
SIMBOLI_GAMMA = ("VOO",)             # la prova 45 sul demo (GAMMA.md, regola 3)
CAPITALE_MISCELA = 100_000.0
CAPITALE_GAMMA = 100_000.0
DIARIO_GAMMA = QUI / "gamma_diario.csv"
COLONNE = ["giorno", "conto", "prima_candela", "miscela", "gamma"]
# Le tasse americane sulle vendite (SEC e FINRA) che il conto demo addebita: circa 20,7 dollari per milione di dollari venduti,
# misurati sul conto (audit del 27 novembre 2026). Si tolgono alla strategia che vende (prima tutte finivano nella miscela).
TASSA_VENDITE = 20.7e-6
# I valori di fine giornata si scrivono con le chiusure ufficiali, quando le barre del giorno sono complete (il piano gratuito di
# Alpaca dà i dati di tutte le borse con 16 minuti di ritardo): 20 minuti dopo la fine della seduta (audit del 27 novembre 2026)
DOPO_LA_CHIUSURA_PER_I_VALORI = pd.Timedelta(minutes=20)


def della_miscela(simbolo: str) -> bool:
    return simbolo in SIMBOLI_MISCELA


def della_gamma(simbolo: str) -> bool:
    return simbolo in SIMBOLI_GAMMA


def della_candela(simbolo: str) -> bool:
    """Tutti i titoli che non sono della miscela né della prova 45: la prima candela chiude e cancella solo questi."""
    return not della_miscela(simbolo) and not della_gamma(simbolo)


def separa(posizioni: list[dict]) -> tuple[list[dict], list[dict]]:
    """(posizioni della prima candela, posizioni della miscela); quelle della prova 45 in nessuna delle due (`di_gamma`)."""
    return ([p for p in posizioni if della_candela(p["symbol"])], [p for p in posizioni if della_miscela(p["symbol"])])


def di_gamma(posizioni: list[dict]) -> list[dict]:
    return [p for p in posizioni if della_gamma(p["symbol"])]


def _flusso(esecuzioni: list[dict], tiene) -> float:
    """I soldi entrati (vendite) meno quelli usciti (acquisti) con le esecuzioni dei titoli scelti da `tiene`."""
    return sum((1 if str(e["side"]).startswith("sell") else -1) * float(e["qty"]) * float(e["price"])
               for e in esecuzioni if tiene(e["symbol"]))


def tasse_vendite(diario: pd.DataFrame) -> float:
    """Le tasse sulle vendite stimate delle operazioni chiuse di un diario: per un acquisto si vende all'uscita, per una vendita allo
    scoperto all'ingresso."""
    if not len(diario) or not {"guadagno", "quantita", "lato", "ingresso", "uscita_prezzo"} <= set(diario.columns):
        return 0.0
    d = diario[pd.to_numeric(diario["guadagno"], errors="coerce").notna()]
    if not len(d):
        return 0.0
    q = pd.to_numeric(d["quantita"], errors="coerce").fillna(0.0)
    prezzo = [float(u) if lt == "buy" else float(i) for lt, u, i in zip(d["lato"], d["uscita_prezzo"], d["ingresso"])]
    return float(TASSA_VENDITE * sum(abs(a) * b for a, b in zip(q, prezzo) if pd.notna(b)))


def valore_gamma(posizioni: list[dict], diario_gamma: pd.DataFrame | None, oggi: str | None = None,
                 esecuzioni_oggi: list[dict] | None = None, escludi: set[str] | None = None,
                 entrata_oggi: bool | None = None) -> float:
    """Il valore della prova 45 (funzione pura): 100'000 più i guadagni del suo diario, meno le tasse sulle vendite stimate; per oggi,
    se il diario non ha ancora la riga del giorno e oggi c'è stato il suo ingresso, i soldi usciti ed entrati con le sue esecuzioni di
    oggi più il valore di mercato delle sue posizioni; altrimenti il non realizzato. `entrata_oggi` e `escludi` (le chiusure di
    posizioni rimaste, «gamma-rim-») vengono dagli ordini di Alpaca (`classifica`); None = come prima del 27 novembre 2026."""
    d = diario_gamma if diario_gamma is not None else pd.DataFrame(columns=["giorno", "guadagno"])
    realizzato = float(pd.to_numeric(d["guadagno"], errors="coerce").dropna().sum()) if len(d) else 0.0
    realizzato -= tasse_vendite(d)
    pos = di_gamma(posizioni)
    if oggi is not None and esecuzioni_oggi is not None and oggi not in set(d["giorno"].astype(str)) and entrata_oggi is not False:
        mie = [e for e in esecuzioni_oggi if e.get("order_id") not in (escludi or set())]
        di_oggi = _flusso(mie, della_gamma) + sum(float(p.get("market_value") or 0.0) for p in pos)
    else:
        di_oggi = sum(float(p.get("unrealized_pl") or 0.0) for p in pos)
    return CAPITALE_GAMMA + realizzato + di_oggi


def leggi_stato() -> dict | None:
    return json.loads(STATO.read_text()) if STATO.exists() else None


def valori(equity: float, posizioni: list[dict], diario: pd.DataFrame, stato: dict | None, oggi: str | None = None,
           esecuzioni_oggi: list[dict] | None = None, diario_gamma: pd.DataFrame | None = None,
           escludi: set[str] | None = None, entrate_oggi: set[str] | None = None,
           entrata_gamma_oggi: bool | None = None) -> tuple[float, float | None]:
    """(valore della prima candela, valore della miscela o None se la miscela non è partita). Funzione pura.

    Il guadagno della prima candela dopo la partenza: il suo diario; per oggi, se il diario non è ancora scritto, i soldi usciti ed
    entrati con le sue esecuzioni di oggi più il valore di mercato delle sue posizioni (parte ogni giorno senza posizioni, quindi è
    il guadagno di oggi, comprese le uscite a stop già avvenute). Il guadagno della prova 45 (`valore_gamma`) si toglie da quello della
    miscela, che prende «tutto il resto». Dal 27 novembre 2026 (audit e revisione separata) le operazioni di oggi si riconoscono dagli
    ordini di Alpaca, mai dai file del repository (un lavoro può vederli vecchi): `entrate_oggi` sono i titoli entrati oggi con il nome
    «candela15-{oggi}-»; solo le loro esecuzioni e il loro valore di mercato fanno il guadagno di oggi, e gli altri titoli (una posizione
    rimasta da un altro giorno, o chiusa) contano con il non realizzato. `escludi`: le chiusure delle posizioni rimaste («candela-rim-»,
    «gamma-rim-»), che vanno nella riga del giorno dell'ingresso. Con `entrate_oggi` None vale il conto di prima. Le tasse sulle
    vendite stimate si tolgono alla strategia che vende."""
    if stato is None:
        return float(equity), None
    candela_pos, _ = separa(posizioni)
    giorni = diario["giorno"].astype(str) if len(diario) else pd.Series(dtype=str)
    dopo = diario[giorni > stato["dal"]] if len(diario) else diario
    realizzato = float(pd.to_numeric(dopo["guadagno"], errors="coerce").dropna().sum()) if len(dopo) else 0.0
    realizzato -= tasse_vendite(dopo)
    if oggi is not None and esecuzioni_oggi is not None and oggi > stato["dal"] and oggi not in set(giorni):
        di_oggi_titolo = (lambda s: True) if entrate_oggi is None else (lambda s: s in entrate_oggi)  # noqa: E731
        mie = [e for e in esecuzioni_oggi if e.get("order_id") not in (escludi or set()) and di_oggi_titolo(e["symbol"])]
        di_oggi = (_flusso(mie, della_candela)
                   + sum(float(p.get("market_value") or 0.0) for p in candela_pos if di_oggi_titolo(p["symbol"]))
                   + sum(float(p.get("unrealized_pl") or 0.0) for p in candela_pos if not di_oggi_titolo(p["symbol"])))
    else:
        di_oggi = sum(float(p.get("unrealized_pl") or 0.0) for p in candela_pos)
    candela = stato["candela_alla_partenza"] + realizzato + di_oggi
    gamma = (valore_gamma(posizioni, diario_gamma, oggi, esecuzioni_oggi, escludi, entrata_gamma_oggi) if diario_gamma is not None
             else CAPITALE_GAMMA)
    miscela = (CAPITALE_MISCELA + (float(equity) - stato["conto_alla_partenza"]) - (candela - stato["candela_alla_partenza"])
               - (gamma - CAPITALE_GAMMA))
    return float(candela), float(miscela)


def adesso() -> dict:
    """I valori di adesso letti dal conto: {conto, candela, miscela, gamma, posizioni_candela, posizioni_miscela, posizioni_gamma}."""
    from stock.avanti import avanti as av
    conto = av._richiesta("GET", "/v2/account")
    posizioni = av._richiesta("GET", "/v2/positions")
    f = QUI / "diario.csv"
    diario = pd.read_csv(f) if f.exists() else pd.DataFrame(columns=av.COLONNE)
    equity = float(conto["equity"])
    stato = leggi_stato()
    oggi = av.ny_adesso().date().isoformat()
    esecuzioni = av.esecuzioni_del_giorno(oggi) if stato is not None else None
    dg = pd.read_csv(DIARIO_GAMMA) if DIARIO_GAMMA.exists() else pd.DataFrame(columns=["giorno", "guadagno"])
    if esecuzioni is None:
        esecuzioni = av.esecuzioni_del_giorno(oggi)
    c = classifica(av._ordini_dal(oggi), oggi)
    candela, miscela = valori(equity, posizioni, diario, stato, oggi, esecuzioni, diario_gamma=dg, escludi=c["rimaste"],
                              entrate_oggi=c["entrate_candela"], entrata_gamma_oggi=c["entrata_gamma"])
    gamma = valore_gamma(posizioni, dg, oggi, esecuzioni, c["rimaste"], c["entrata_gamma"])
    pc, pm = separa(posizioni)
    return {"conto": equity, "candela": candela, "miscela": miscela, "gamma": gamma, "posizioni_candela": pc,
            "posizioni_miscela": pm, "posizioni_gamma": di_gamma(posizioni), "entrate_candela": c["entrate_candela"],
            "moltiplicatore": conto.get("multiplier"), "potere_d_acquisto": conto.get("buying_power")}


def classifica(ordini: list[dict], oggi: str) -> dict:
    """Dagli ordini di Alpaca di oggi (funzione pura): i titoli entrati oggi dalla prima candela, se la prova 45 è entrata oggi, e gli
    id delle chiusure di posizioni rimaste da altri giorni («candela-rim-», «gamma-rim-»)."""
    def nome(o):
        return str(o.get("client_order_id", ""))

    def eseguito(o):
        return float(o.get("filled_qty") or 0) > 0
    return {"entrate_candela": {o["symbol"] for o in ordini if nome(o).startswith(f"candela15-{oggi}-") and eseguito(o)},
            "entrata_gamma": any(nome(o) == f"gamma-{oggi}-in" and eseguito(o) for o in ordini),
            "rimaste": {o["id"] for o in ordini if nome(o).startswith(("candela-rim-", "gamma-rim-"))}}


def chiusura_ufficiale(simbolo: str, chiusura: pd.Timestamp) -> float | None:
    """La chiusura dell'ultima barra al minuto della seduta (tutte le borse; per esempio quella delle 15:59), o None se non c'è: solo ore
    di seduta, mai il dopo borsa (la barra giornaliera di Alpaca potrebbe comprenderlo: revisione separata del 27 novembre 2026)."""
    from stock.dati import alpaca
    df = alpaca.barre(simbolo, "1Min", (chiusura - pd.Timedelta(minutes=10)).to_pydatetime(), chiusura.to_pydatetime())
    df = df[df.index < chiusura.tz_convert("UTC")] if not df.empty else df
    return float(df["close"].iloc[-1]) if not df.empty else None


def correzione_alla_chiusura(posizioni: list[dict], chiusure: dict[str, float | None]) -> float | None:
    """Quanto cambia il valore del conto se le posizioni si valutano alla chiusura ufficiale invece che al prezzo di adesso (funzione
    pura); None se manca una chiusura."""
    corr = 0.0
    for p in posizioni:
        c = chiusure.get(p["symbol"])
        if c is None:
            return None
        corr += float(p["qty"]) * (c - float(p.get("current_price") or 0.0))
    return corr


def parti(giorno: str) -> dict:
    """La fotografia della partenza della miscela: si fa una volta, a prima candela senza posizioni."""
    stato = leggi_stato()
    if stato is not None:
        return stato
    v = adesso()
    if v["posizioni_candela"]:
        raise RuntimeError("la miscela non può partire mentre la prima candela ha posizioni aperte")
    stato = {"dal": giorno, "conto_alla_partenza": v["conto"], "candela_alla_partenza": v["conto"],
             "miscela_alla_partenza": CAPITALE_MISCELA}
    STATO.write_text(json.dumps(stato, indent=1))
    return stato


def leggi_valori() -> pd.DataFrame:
    return pd.read_csv(VALORI) if VALORI.exists() else pd.DataFrame(columns=COLONNE)


def registra(giorno: str, chiusura: pd.Timestamp | None = None) -> str:
    """Scrive la riga di fine giornata, una volta sola per giorno e solo a prima candela senza posizioni. Dal 27 novembre 2026
    (audit): le posizioni della miscela e della prova 45 si valutano alla chiusura ufficiale del giorno, non ai prezzi del dopo borsa
    dell'ora in cui parte il lavoro; per questo si aspettano 20 minuti dopo la fine della seduta. Con posizioni rimaste da un altro
    giorno la riga non si scrive."""
    df = leggi_valori()
    if giorno in set(df["giorno"].astype(str)):
        return f"valori del {giorno} già scritti"
    if chiusura is not None:
        from stock.avanti import avanti as av0
        if av0.ny_adesso() < chiusura + DOPO_LA_CHIUSURA_PER_I_VALORI:
            return f"valori del {giorno} non scritti: si aspettano le chiusure ufficiali (20 minuti dopo la fine della seduta)"
    # prima gli ordini aperti della prova 45 (l'asta di chiusura), POI il conto: senza ordini aperti nessuna esecuzione può cadere fra
    # una lettura e l'altra, e i valori scritti una volta sola restano coerenti
    from stock.avanti import avanti as av
    if any(della_gamma(o["symbol"]) for o in av._richiesta("GET", "/v2/orders", params={"status": "open", "limit": 500})):
        return f"valori del {giorno} non scritti: la prova 45 ha ancora ordini aperti"
    v = adesso()
    if v["posizioni_candela"]:
        return f"valori del {giorno} non scritti: la prima candela ha ancora posizioni"
    if v["posizioni_gamma"]:
        return f"valori del {giorno} non scritti: la prova 45 ha ancora posizioni"
    pm = v["posizioni_miscela"]
    if pm and chiusura is None:
        return f"valori del {giorno} non scritti: serve l'ora della chiusura per le chiusure ufficiali"
    corr = correzione_alla_chiusura(pm, {p["symbol"]: chiusura_ufficiale(p["symbol"], chiusura) for p in pm}) if pm else 0.0
    if corr is None:
        return f"valori del {giorno} non scritti: manca la chiusura ufficiale di un titolo della miscela"
    v["conto"] += corr
    if v["miscela"] is not None:
        v["miscela"] += corr                       # le posizioni a fine giornata sono solo della miscela
    riga = {"giorno": giorno, "conto": round(v["conto"], 2), "prima_candela": round(v["candela"], 2),
            "miscela": round(v["miscela"], 2) if v["miscela"] is not None else "",
            "gamma": round(v["gamma"], 2) if DIARIO_GAMMA.exists() else ""}      # vuota finché la prova 45 non è partita
    pd.concat([df, pd.DataFrame([riga], columns=COLONNE)], ignore_index=True).to_csv(VALORI, index=False)
    return (f"valori del {giorno}: prima candela {riga['prima_candela']}, miscela {riga['miscela'] or '—'}, "
            f"prova 45 {riga['gamma'] or '—'}")


def giorni(colonna: str) -> dict[str, float]:
    df = leggi_valori()
    if colonna not in df.columns:
        return {}
    x = pd.to_numeric(df[colonna], errors="coerce")
    return {str(g): float(v) for g, v in zip(df["giorno"], x) if pd.notna(v)}
