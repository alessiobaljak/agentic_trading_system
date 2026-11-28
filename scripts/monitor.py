"""
Monitoring job (GitHub Action ogni 15 min).

Legge da Firebase RTDB il battito del bot e lo stato del demo e del conto vero, e manda un avviso Telegram se il bot e'
offline (battito piu' vecchio di HEARTBEAT_MAX_AGE secondi) o se il demo o il conto vero sono fermi o hanno un allarme acceso.

Dal 27 novembre 2026 (audit del 26 novembre, salute-6): la soglia del battito e' quella di sempre della dashboard e del
controllo, 900 secondi (prima 180); e al posto della perdita del giorno del vecchio sistema (/risk_state, fermo dal 13
ottobre) si guardano il fermo e gli allarmi del demo e del conto vero, gli stessi della riga in cima alla dashboard
(dashboard/app/lib/strategie.ts, `allarmiAccesi`; components/strategie/RigaStato.tsx). Ogni allarme va al telefono una volta
sola finche' resta acceso (un fermo nuovo, con un'altra ora, vale come nuovo): quelli gia' mandati sono in /monitor/avvisati.
Un allarme che il bot ha gia' mandato al telefono da se' (il campo `telefono` nel nodo, scritto da bot/portafoglio/demo_binance.py
dal 27 novembre 2026) non si rimanda: il monitor resta la rete di sicurezza per quelli che il bot non ha mandato (bot fermo o con il
codice di prima). Bastano le chiavi di Firebase e di Telegram che il lavoro ha gia' (.github/workflows/monitoring.yml).

Revisione del 27 novembre 2026 (reviews/reports/2026-11-27-bot.md, problema 212): non si mandano nemmeno gli allarmi che il bot tiene
fuori dal telefono di proposito (bot/portafoglio/demo_binance.py, salute-6):
* `limiti_binance` con `codice` 429: Binance limita le richieste per qualche minuto, l'allarme resta solo su Firebase (il 418, il
  blocco dell'indirizzo, si manda). Non si segna fra gli avvisati: se lo stesso nodo diventa un 418 senza `telefono`, parte
  (salvo il limite di uno all'ora qui sotto);
* un allarme senza `telefono` che si e' acceso meno di un'ora (`STESSO_TIPO_S`, come `AVVISO_STESSO_TIPO_S` del bot) dopo che il bot
  ha mandato al telefono lo stesso allarme: e' il limite di uno all'ora del bot. L'ora dell'ultimo invio del bot si ricorda in
  /monitor/telefono_del_bot (dal campo `telefono` visto acceso a un giro del monitor). Se il monitor non ha visto quell'invio
  (l'allarme si e' acceso e spento fra due suoi giri), non lo sa e l'allarme riacceso parte.

Revisione del 27 novembre 2026, secondo giro (reviews/reports/2026-11-27-bot-bis.md), corretti il 28 novembre:
* problema 219: un 429 che dura oltre `LIMITE_429_S` (30 minuti, come `LIMITE_429_AL_TELEFONO_S` del bot) si manda, una volta finche'
  resta acceso: da quando dura lo dice il nodo (`dal`, scritto dal bot dal 28 novembre) o, se manca, la prima volta che il monitor
  l'ha visto (/monitor/limiti_429_visti);
* problema 220: il limite di uno all'ora si conta per tipo di avviso del bot, come fa il bot (`_tipo_dell_avviso`: il nodo
  `limiti_binance` ha due tipi, il blocco 418 e il 429 che dura), e non vale per il fermo: un fermo nuovo senza `telefono` parte
  sempre (anche il bot lo manda sempre, `SEMPRE_AL_TELEFONO`).
"""
from __future__ import annotations

import html
import time
from datetime import datetime

from bot.core.firebase_client import get_firebase
from bot.execution.notifier import TelegramNotifier

# secondi: la soglia della dashboard (TopVitals.tsx, RigaStato.tsx) e del controllo (bot/learning/controllo.py, SOGLIA_ONLINE_S).
# Il bot scrive il battito a ogni giro; a mezzanotte un giro dura 13-18 minuti (gli scarichi dei paper, audit del 26 novembre
# 2026, salute-2): il lunedi' fra le 00:20 e le 00:23 UTC un avviso puo' partire anche con il bot vivo.
HEARTBEAT_MAX_AGE = 900

#: i conti di cui si guardano il fermo e gli allarmi: (ramo su RTDB, nome nel messaggio)
CONTI = (("demo_binance", "demo"), ("conto_vero", "conto vero"))
#: gli allarmi gia' mandati al telefono: {chiave: firma}
NODO_AVVISATI = "/monitor/avvisati"
#: problema 212: quando il bot ha mandato al telefono ogni allarme, l'ultima volta che il monitor l'ha visto: {chiave: ora}
NODO_TELEFONO_DEL_BOT = "/monitor/telefono_del_bot"
#: il limite del bot, lo stesso allarme al telefono al massimo una volta all'ora (bot/portafoglio/demo_binance.py,
#: AVVISO_STESSO_TIPO_S; un test controlla che siano uguali)
STESSO_TIPO_S = 3600
#: quanto si ricorda l'ora di un invio del bot (basta che superi l'ora del limite anche con i giri del monitor in ritardo)
MEMORIA_TELEFONO_S = 2 * 86400
#: problema 219: un 429 acceso da oltre questo si manda (bot/portafoglio/demo_binance.py, LIMITE_429_AL_TELEFONO_S; un test li confronta)
LIMITE_429_S = 1800
#: problema 219: la prima volta che il monitor ha visto acceso ogni 429 (per i nodi senza `dal`): {chiave: ora}
NODO_429_VISTI = "/monitor/limiti_429_visti"


def _ora(ts) -> str:
    """L'ora di un allarme in ora italiana, come la dashboard."""
    try:
        from bot.core.tempo import fuso
        return datetime.fromtimestamp(float(ts), tz=fuso()).strftime("%d/%m %H:%M")
    except Exception:  # noqa: BLE001
        return "ora sconosciuta"


def _testo(v, n: int = 300) -> str:
    """Un testo scritto dal bot, pronto per un messaggio HTML di Telegram (un «<» non scappato fa rifiutare il messaggio)."""
    return html.escape(str("" if v is None else v)[:n])


def _numero(v) -> float | None:
    """Un'ora scritta dal bot come numero, o None."""
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if x == x and abs(x) != float("inf") else None


def allarmi_accesi(fb) -> dict[str, tuple[str, str, bool]]:
    """Il fermo e gli allarmi accesi del demo e del conto vero: {chiave: (firma, testo del messaggio, gia' mandato dal bot)}.

    La firma dice quando un allarme e' nuovo. Per un fermo e' la sua ora: un fermo dopo un «riparti» e' un altro fermo. Per gli
    altri allarmi basta che sia acceso: la loro ora cambia a ogni riscrittura, e il testo con il numero dei tentativi. Il terzo
    valore e' vero se il nodo ha `telefono`: il bot l'ha gia' mandato al telefono. (I nodi, con `ora`, `telefono` e `codice`, li
    legge `_nodi_accesi`.)"""
    return {chiave: (firma, testo, bool(nodo.get("telefono"))) for chiave, (firma, testo, nodo) in _nodi_accesi(fb).items()}


def _nodi_accesi(fb) -> dict[str, tuple[str, str, dict]]:
    """Come `allarmi_accesi`, con il nodo scritto dal bot al posto del terzo valore."""
    out: dict[str, tuple[str, str, dict]] = {}
    for ramo, nome in CONTI:
        fermo = fb.get_rtdb(f"/{ramo}/fermo")
        if isinstance(fermo, dict) and fermo:
            chiuse = fermo.get("chiuse")
            out[f"{ramo}-fermo"] = (
                str(fermo.get("ora")),
                f"🛑 <b>{nome.capitalize()} FERMO</b> dal {_ora(fermo.get('ora'))}: {_testo(fermo.get('motivo'))}"
                + (f" ({_testo(chiuse)} posizioni chiuse)" if chiuse is not None else "")
                + ". Per farlo ripartire: «Riparti» nella sua scheda, nella pagina Strategie della dashboard.",
                fermo)
        allarme = fb.get_rtdb(f"/{ramo}/allarme")
        if isinstance(allarme, dict) and allarme.get("testo"):
            out[f"{ramo}-allarme"] = (
                "acceso",
                f"⚠️ <b>Allarme del {nome}</b> (conto non vuoto da fermo, {_ora(allarme.get('ora'))}): "
                f"{_testo(allarme.get('testo'))}",
                allarme)
        allarmi = fb.get_rtdb(f"/{ramo}/allarmi")
        if isinstance(allarmi, dict):
            for tipo, a in sorted(allarmi.items(), key=lambda x: str(x[0])):
                if isinstance(a, dict) and a.get("testo"):
                    out[f"{ramo}-allarmi-{tipo}"] = (
                        "acceso",
                        f"⚠️ <b>Allarme del {nome}</b> ({_testo(str(tipo).replace('_', ' '))}, {_ora(a.get('ora'))}): "
                        f"{_testo(a.get('testo'))}",
                        a)
    return out


#: i due motivi per cui il bot tiene fuori dal telefono un allarme di proposito (problema 212)
FUORI_429 = "un 429 di Binance da meno di 30 minuti: il bot lo tiene solo su Firebase"
FUORI_UNO_ALL_ORA = "il bot lo ha mandato meno di un'ora prima: il suo limite di uno all'ora"


def _e_un_429(chiave: str, nodo: dict) -> bool:
    return chiave.endswith("-allarmi-limiti_binance") and _numero(nodo.get("codice")) == 429


def _tipo_dell_avviso(chiave: str, nodo: dict) -> str | None:
    """Problema 220: la chiave del limite di uno all'ora, per tipo di avviso come nel bot (bot/portafoglio/demo_binance.py). Per gli
    allarmi in `allarmi/<tipo>` e per `allarme` (il conto non vuoto da fermo) e' il nodo; `limiti_binance` ha due tipi, il blocco
    (418) e il 429 che dura, e il codice li separa; il fermo non ha il limite (None): il bot lo manda sempre."""
    if chiave.endswith("-fermo"):
        return None
    if chiave.endswith("-allarmi-limiti_binance"):
        codice = _numero(nodo.get("codice"))
        return f"{chiave}-{int(codice)}" if codice is not None else chiave
    return chiave


def _dal_429(chiave: str, nodo: dict, visti_429: dict) -> float | None:
    """Problema 219: da quando dura il 429 di questo nodo: il `dal` scritto dal bot o la prima volta che il monitor l'ha visto, il
    piu' vecchio dei due."""
    ore = [x for x in (_numero(nodo.get("dal")), _numero(visti_429.get(chiave))) if x is not None]
    return min(ore) if ore else None


def _tenuto_fuori_dal_bot(chiave: str, nodo: dict, telefono_del_bot: dict, now: float | None = None,
                          visti_429: dict | None = None) -> str | None:
    """Problema 212: perche' il bot ha tenuto fuori dal telefono di proposito questo allarme (acceso e senza `telefono`), o None.
    Un 429 di `limiti_binance` che dura da meno di ``LIMITE_429_S`` (``FUORI_429``; problema 219: oltre si manda); oppure lo stesso
    tipo di avviso mandato dal bot meno di ``STESSO_TIPO_S`` prima (``FUORI_UNO_ALL_ORA``, il limite di uno all'ora; problema 220:
    per tipo, e mai per il fermo). L'ora dell'allarme e' quella dell'ultima riscrittura, quindi non prima dell'accensione: se dice
    meno di un'ora, il bot l'ha di sicuro saltato per il limite."""
    if _e_un_429(chiave, nodo):
        dal = _dal_429(chiave, nodo, visti_429 or {})
        if now is None or dal is None or now - dal < LIMITE_429_S:
            return FUORI_429
    tipo = _tipo_dell_avviso(chiave, nodo)
    if tipo is None:
        return None
    ultimo, ora = _numero(telefono_del_bot.get(tipo)), _numero(nodo.get("ora"))
    if ultimo is not None and ora is not None and 0 <= ora - ultimo < STESSO_TIPO_S:
        return FUORI_UNO_ALL_ORA
    return None


def avvisa_allarmi(fb, notifier, now: float | None = None) -> int:
    """Manda al telefono gli allarmi nuovi, una volta per allarme finche' resta acceso, e aggiorna /monitor/avvisati (un
    allarme spento ne esce: se si riaccende, si manda di nuovo). Un allarme gia' mandato dal bot (`telefono`) si segna senza
    rimandarlo. Uno che il bot tiene fuori di proposito (`_tenuto_fuori_dal_bot`) non si manda: il 429 resta fuori dagli
    avvisati (se lo stesso nodo diventa un 418 senza `telefono`, si giudica di nuovo), quello del limite di uno all'ora si segna
    come gli altri mandati dal bot. Un invio
    che non riesce non si segna: si riprova al giro dopo. Torna quanti messaggi ha mandato."""
    now = time.time() if now is None else now
    accesi = _nodi_accesi(fb)
    prima = fb.get_rtdb(NODO_AVVISATI)
    prima = dict(prima) if isinstance(prima, dict) else {}
    del_bot_prima = fb.get_rtdb(NODO_TELEFONO_DEL_BOT)
    del_bot_prima = dict(del_bot_prima) if isinstance(del_bot_prima, dict) else {}
    del_bot = {k: v for k, v in del_bot_prima.items()
               if _numero(v) is not None and now - float(v) <= MEMORIA_TELEFONO_S}
    visti_prima = fb.get_rtdb(NODO_429_VISTI)
    visti_prima = dict(visti_prima) if isinstance(visti_prima, dict) else {}
    visti_429 = {k: (visti_prima[k] if _numero(visti_prima.get(k)) is not None else now)        # problema 219
                 for k, (_, _, nodo) in accesi.items() if _e_un_429(k, nodo)}
    dopo: dict[str, str] = {}
    mandati = 0
    for chiave, (firma, testo, nodo) in accesi.items():
        dal_bot = bool(nodo.get("telefono"))
        quando = _numero(nodo.get("telefono"))
        tipo = _tipo_dell_avviso(chiave, nodo)                                                  # problema 220
        gia = _numero(del_bot.get(tipo)) if tipo else None
        if tipo and quando is not None and (gia is None or quando > gia):
            del_bot[tipo] = quando
        perche = None if dal_bot or prima.get(chiave) == firma else _tenuto_fuori_dal_bot(chiave, nodo, del_bot, now, visti_429)
        if prima.get(chiave) == firma or dal_bot:
            dopo[chiave] = firma
        elif perche is not None:
            if perche != FUORI_429:
                dopo[chiave] = firma
            print(f"[monitor] allarme non mandato, il bot lo tiene fuori di proposito ({perche}): {chiave}")
        elif notifier.send(testo):
            dopo[chiave] = firma
            mandati += 1
            print(f"[monitor] allarme mandato al telefono: {chiave}")
        else:
            print(f"[monitor] allarme non mandato, si riprova al giro dopo: {chiave}")
    if dopo != prima:
        fb.set_rtdb(NODO_AVVISATI, dopo or None)
    if del_bot != del_bot_prima:
        fb.set_rtdb(NODO_TELEFONO_DEL_BOT, del_bot or None)
    if visti_429 != visti_prima:
        fb.set_rtdb(NODO_429_VISTI, visti_429 or None)
    print(f"[monitor] allarmi accesi di demo e conto vero: {len(accesi)} ({mandati} mandati ora)")
    return mandati


def main() -> None:
    fb = get_firebase()
    notifier = TelegramNotifier()

    # manutenzione: se il bot e' fermo di proposito (rebuild GATE 1, deploy, ecc.)
    # non sparare l'alert "offline" ogni 15 min. Il bot AZZERA questo flag da solo
    # all'avvio, quindi il monitoraggio torna attivo per il live senza interventi.
    if fb.get_rtdb("/commands/maintenance"):
        print("[monitor] modalita' manutenzione attiva -> nessun alert (bot fermo apposta)")
        return

    status = fb.get_rtdb("/bot_status") or {}
    heartbeat = status.get("heartbeat")
    now = time.time()

    if not heartbeat or (now - float(heartbeat)) > HEARTBEAT_MAX_AGE:
        age = "mai" if not heartbeat else f"{int(now - float(heartbeat))}s fa"
        print(f"[monitor] bot OFFLINE (ultimo heartbeat: {age})")
        notifier.bot_offline()
    else:
        print(f"[monitor] bot ONLINE (heartbeat {int(now - float(heartbeat))}s fa)")

    # il fermo e gli allarmi del demo e del conto vero (al posto della perdita del giorno del vecchio /risk_state)
    avvisa_allarmi(fb, notifier)


if __name__ == "__main__":
    main()
