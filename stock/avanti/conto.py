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
                 entrata_oggi: bool | None = None, ordini_oggi: list[dict] | None = None) -> float:
    """Il valore della prova 45 (funzione pura): 100'000 più i guadagni del suo diario, meno le tasse sulle vendite stimate; per oggi,
    se il diario non ha ancora la riga del giorno e oggi c'è stato il suo ingresso, i soldi usciti ed entrati con le sue esecuzioni di
    oggi più il valore di mercato delle sue posizioni; altrimenti il non realizzato. `entrata_oggi` e `escludi` (le chiusure di
    posizioni rimaste, «gamma-rim-») vengono dagli ordini di Alpaca (`classifica`); None = come prima del 27 novembre 2026."""
    d = diario_gamma if diario_gamma is not None else pd.DataFrame(columns=["giorno", "guadagno"])
    realizzato = float(pd.to_numeric(d["guadagno"], errors="coerce").dropna().sum()) if len(d) else 0.0
    realizzato -= tasse_vendite(d)
    realizzato += rim_fuori_dal_diario(d, ordini_oggi or [], "gamma-rim-")
    pos = di_gamma(posizioni)
    # oggi è «scritto» solo con una riga con la quantità: la riga «chiusa la posizione rimasta» non conta (revisione del 27 novembre)
    scritti = (set(d.loc[pd.to_numeric(d["quantita"], errors="coerce").notna(), "giorno"].astype(str)) if "quantita" in d.columns
               else set(d["giorno"].astype(str)))
    if oggi is not None and esecuzioni_oggi is not None and oggi not in scritti and entrata_oggi is not False:
        di_oggi_ordine = _di_oggi(ordini_oggi)
        mie = [e for e in esecuzioni_oggi if e.get("order_id") not in (escludi or set()) and di_oggi_ordine(e)]
        di_oggi = _flusso(mie, della_gamma) + sum(float(p.get("market_value") or 0.0) for p in pos)
    else:
        di_oggi = sum(float(p.get("unrealized_pl") or 0.0) for p in pos)
    return CAPITALE_GAMMA + realizzato + di_oggi


def leggi_stato() -> dict | None:
    return json.loads(STATO.read_text()) if STATO.exists() else None


def valori(equity: float, posizioni: list[dict], diario: pd.DataFrame, stato: dict | None, oggi: str | None = None,
           esecuzioni_oggi: list[dict] | None = None, diario_gamma: pd.DataFrame | None = None,
           escludi: set[str] | None = None, entrate_oggi: set[str] | None = None,
           entrata_gamma_oggi: bool | None = None, ordini_oggi: list[dict] | None = None) -> tuple[float, float | None]:
    """(valore della prima candela, valore della miscela o None se la miscela non è partita). Funzione pura.

    Il guadagno della prima candela dopo la partenza: il suo diario; per oggi, se il diario non è ancora scritto, i soldi usciti ed
    entrati con le sue esecuzioni di oggi più il valore di mercato delle sue posizioni (parte ogni giorno senza posizioni, quindi è
    il guadagno di oggi, comprese le uscite a stop già avvenute). Il guadagno della prova 45 (`valore_gamma`) si toglie da quello della
    miscela, che prende «tutto il resto». Dal 27 novembre 2026 (audit e revisione separata) le operazioni di oggi si riconoscono dagli
    ordini di Alpaca, mai dai file del repository (un lavoro può vederli vecchi): `entrate_oggi` sono i titoli entrati oggi con il nome
    «candela15-{oggi}-»; solo le loro esecuzioni e il loro valore di mercato fanno il guadagno di oggi, e gli altri titoli (una posizione
    rimasta da un altro giorno, o chiusa) contano con il non realizzato. `escludi`: le chiusure delle posizioni rimaste («candela-rim-»,
    «gamma-rim-»), che vanno nella riga del giorno dell'ingresso. Con `entrate_oggi` None vale il conto di prima. Le tasse sulle
    vendite stimate si tolgono alla strategia che vende. `ordini_oggi` (gli ordini di Alpaca di oggi): il guadagno delle chiusure
    «rim» di oggi di righe che nel diario di questo lavoro sono ancora «aperte» (il lavoro che le ha chiuse non ha ancora salvato)."""
    if stato is None:
        return float(equity), None
    candela_pos, _ = separa(posizioni)
    giorni = diario["giorno"].astype(str) if len(diario) else pd.Series(dtype=str)
    dopo = diario[giorni > stato["dal"]] if len(diario) else diario
    realizzato = float(pd.to_numeric(dopo["guadagno"], errors="coerce").dropna().sum()) if len(dopo) else 0.0
    realizzato -= tasse_vendite(dopo)
    realizzato += rim_fuori_dal_diario(dopo, ordini_oggi or [], "candela-rim-")
    if oggi is not None and esecuzioni_oggi is not None and oggi > stato["dal"] and oggi not in set(giorni):
        di_oggi_titolo = (lambda s: True) if entrate_oggi is None else (lambda s: s in entrate_oggi)  # noqa: E731
        di_oggi_ordine = _di_oggi(ordini_oggi)
        mie = [e for e in esecuzioni_oggi if e.get("order_id") not in (escludi or set()) and di_oggi_titolo(e["symbol"])
               and di_oggi_ordine(e)]
        di_oggi = (_flusso(mie, della_candela)
                   + sum(float(p.get("market_value") or 0.0) for p in candela_pos if di_oggi_titolo(p["symbol"]))
                   + sum(float(p.get("unrealized_pl") or 0.0) for p in candela_pos if not di_oggi_titolo(p["symbol"])))
    else:
        di_oggi = sum(float(p.get("unrealized_pl") or 0.0) for p in candela_pos)
    candela = stato["candela_alla_partenza"] + realizzato + di_oggi
    gamma = (valore_gamma(posizioni, diario_gamma, oggi, esecuzioni_oggi, escludi, entrata_gamma_oggi, ordini_oggi)
             if diario_gamma is not None else CAPITALE_GAMMA)
    miscela = (CAPITALE_MISCELA + (float(equity) - stato["conto_alla_partenza"]) - (candela - stato["candela_alla_partenza"])
               - (gamma - CAPITALE_GAMMA))
    return float(candela), float(miscela)


def adesso() -> dict:
    """I valori di adesso letti dal conto: {conto, candela, miscela, gamma, posizioni_candela, posizioni_miscela, posizioni_gamma}."""
    from stock.avanti import avanti as av
    f = QUI / "diario.csv"
    diario = pd.read_csv(f) if f.exists() else pd.DataFrame(columns=av.COLONNE)
    stato = leggi_stato()
    oggi = av.ny_adesso().date().isoformat()
    dg = pd.read_csv(DIARIO_GAMMA) if DIARIO_GAMMA.exists() else pd.DataFrame(columns=["giorno", "guadagno"])
    # una fotografia: le posizioni si rileggono dopo le esecuzioni, e se sono cambiate (uno stop eseguito fra le due letture) si rilegge
    # tutto; senza, la stessa vendita contava due volte (revisione separata del 27 novembre 2026)
    for _ in range(3):
        conto = av._richiesta("GET", "/v2/account")
        posizioni = av._richiesta("GET", "/v2/positions")
        esecuzioni = av.esecuzioni_del_giorno(oggi)
        ordini_oggi = av._ordini_dal(oggi)
        dopo = av._richiesta("GET", "/v2/positions")
        if _quantita(dopo) == _quantita(posizioni):
            break
    equity = float(conto["equity"])
    c = classifica(ordini_oggi, oggi)
    candela, miscela = valori(equity, posizioni, diario, stato, oggi, esecuzioni, diario_gamma=dg, escludi=c["rimaste"],
                              entrate_oggi=c["entrate_candela"], entrata_gamma_oggi=c["entrata_gamma"], ordini_oggi=ordini_oggi)
    gamma = valore_gamma(posizioni, dg, oggi, esecuzioni, c["rimaste"], c["entrata_gamma"], ordini_oggi)
    pc, pm = separa(posizioni)
    return {"conto": equity, "candela": candela, "miscela": miscela, "gamma": gamma, "posizioni_candela": pc,
            "posizioni_miscela": pm, "posizioni_gamma": di_gamma(posizioni), "entrate_candela": c["entrate_candela"],
            "moltiplicatore": conto.get("multiplier"), "potere_d_acquisto": conto.get("buying_power")}


def _ids(ordini: list[dict]) -> set[str]:
    """Gli id degli ordini e delle loro gambe (gli ordini di Alpaca letti con «nested»)."""
    out: set[str] = set()
    for o in ordini:
        out.add(o.get("id"))
        out |= _ids(o.get("legs") or [])
    return out


def _di_oggi(ordini_oggi: list[dict] | None):
    """Chi decide se un'esecuzione è del flusso di oggi: solo se il suo ordine (o la sua gamba) è stato mandato oggi. Se Alpaca data le
    esecuzioni in UTC, una vendita fuori orario delle 19:30 di ieri cade fra le esecuzioni di oggi (revisione separata del 27
    novembre 2026). Senza gli ordini di oggi (None) vale il conto di prima."""
    if ordini_oggi is None:
        return lambda e: True
    ids = _ids(ordini_oggi)
    return lambda e: e.get("order_id") in ids


def _quantita(posizioni: list[dict]) -> dict[str, str]:
    return {p["symbol"]: str(p["qty"]) for p in posizioni}


def rim_fuori_dal_diario(diario: pd.DataFrame, ordini: list[dict], prefisso: str) -> float:
    """Il guadagno delle chiusure «rim» di oggi (funzione pura) delle operazioni che nel diario di QUESTO lavoro sono ancora «aperte»:
    il lavoro che le ha chiuse non ha ancora salvato il diario, e senza questo il guadagno finiva per qualche ora nella miscela
    (revisione separata del 27 novembre 2026). Prezzo medio eseguito della chiusura meno il prezzo d'ingresso del diario, per la
    quantità eseguita. Le righe «parziali» non si toccano (caso raro)."""
    if not len(diario) or not ordini or not {"uscita", "ingresso", "lato", "simbolo", "giorno"} <= set(diario.columns):
        return 0.0
    aperte = diario[diario["uscita"].astype(str) == "aperta"]
    out = 0.0
    for g, s, lato, ingresso in zip(aperte["giorno"].astype(str), aperte["simbolo"].astype(str), aperte["lato"], aperte["ingresso"]):
        if pd.isna(pd.to_numeric(ingresso, errors="coerce")):
            continue
        testa = f"{prefisso}{g}-{s}-" if prefisso == "candela-rim-" else f"{prefisso}{g}-"
        segno = 1 if lato == "buy" else -1
        for o in ordini:
            q = float(o.get("filled_qty") or 0)
            if str(o.get("client_order_id", "")).startswith(testa) and q > 0 and o.get("filled_avg_price"):
                out += segno * (float(o["filled_avg_price"]) - float(ingresso)) * q
    return out


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


def registra(giorno: str, chiusura: pd.Timestamp | None = None, prima: str | None = None) -> str:
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
    # con una riga «aperta» o «parziale» del giorno (o di quello prima) nei diari di questo lavoro la riga sarebbe sbagliata per sempre:
    # si aspetta che il lavoro che l'ha chiusa salvi (revisione separata del 27 novembre 2026); una riga ferma da più giorni non blocca
    # la seduta prima dal calendario di Alpaca (`prima`), che conosce le feste; senza, il giorno feriale prima
    prima = prima or (pd.Timestamp(giorno) - pd.offsets.BDay(1)).date().isoformat()
    for f, chi in ((QUI / "diario.csv", "della prima candela"), (DIARIO_GAMMA, "della prova 45")):
        d = pd.read_csv(f) if f.exists() else pd.DataFrame(columns=["giorno", "uscita"])
        if len(d) and "uscita" in d.columns:
            g = d["giorno"].astype(str)
            if ((g >= prima) & (g <= giorno) & d["uscita"].astype(str).isin({"aperta", "parziale"})).any():
                return f"valori del {giorno} non scritti: il diario {chi} ha righe aperte"
    # e con un giorno che ha gli ordini ma non ha ancora le sue righe nel diario (il diario della sera non è riuscito: lo riscrive il
    # giro, dopo; revisione separata del 27 novembre 2026)
    from stock.avanti import gamma as ga
    dopo = (pd.Timestamp(giorno) + pd.Timedelta(days=1)).date().isoformat()
    mancanti = {g for g in av.giorni_senza_righe(dopo) if prima <= g <= giorno} | {g for g in (prima, giorno) if ga.riga_mancante(g)}
    if mancanti:
        return f"valori del {giorno} non scritti: il diario non ha ancora le righe del {', '.join(sorted(mancanti))}"
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
