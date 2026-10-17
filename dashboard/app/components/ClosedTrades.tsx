'use client';

import { Fragment, useEffect, useMemo, useState } from 'react';
import { collection, limit, onSnapshot, orderBy, query } from 'firebase/firestore';
import { getDb } from '../lib/firebase';

/**
 * Trade chiusi (Firestore `trades`), RAGGRUPPATI per giorno (header cliccabile che
 * espande/collassa la lista di quel giorno). Per le uscite `trailing_stop` calcola
 * un VERDETTO controfattuale (TP vs SL, vedi evalTrailing) usando le klines Binance
 * lato browser; i verdetti si calcolano SOLO per i giorni espansi (niente raffica
 * di fetch su tutti i trade). Se Binance non è raggiungibile -> "n/d".
 */
export type Trade = {
  trade_id?: string;
  entry_price?: number;
  symbol: string;
  strategy: string;
  direction: string;
  pnl: number;
  pnl_pct: number;
  exit_reason: string;
  exit_ts?: number;
  exit_price?: number;
  take_profit_price?: number;
  stop_price?: number;
  entry_time?: string; // ISO 8601 (ClosedTrade.entry_time serializzato)
  trailing_verdict?: string; // scritto dal bot (B1); se presente si usa questo, niente fetch Binance
  scale_stage_reached?: number; // quanti TP scaglionati raggiunti (0 = uscito allo SL prima del TP1)
  realized_partial?: number;    // PnL netto incassato dalle fette
  /** il referto del trade (bot/risk/setup_check.post_mortem, dal 23 set): classe
   *  della morte e verdetto in una riga. Assente sui trade chiusi prima. */
  post_mortem?: {
    classe?: string | null;
    stop_largo?: boolean;
    lock_mai_armato?: boolean;
    controtrend?: boolean;
    mfe_r?: number | null;
    verdetto?: string | null;
  } | null;
  /** keep del profit-lock usato dalla posizione (per coppia dal gate, 25 set) */
  profit_lock_keep?: number | null;
  /** il paper esplorativo (25 set, F1bis): trade di un quasi-passaggio del gate
   *  a un quarto della size, fuori dai pesi delle validate. Assente = validata. */
  esplorativa?: boolean | null;
};

/** Etichetta corta della classe del referto: dove e' morto il trade. */
const CLASSE_REFERTO: Record<string, string> = {
  ingresso: 'ingresso',
  uscita: 'uscita',
  protezione: 'protezione',
};

type Verdict = 'premature' | 'protected' | 'neutral' | 'pending' | 'unavailable';

const EVAL_HOURS = 24; // finestra dopo l'uscita entro cui simuliamo "se fossimo rimasti"
const MAX_TRADES = 500; // tetto di sicurezza sulle letture Firestore (copre lo storico attuale)

function fmtTime(ts: number | undefined): string {
  if (ts == null || !Number.isFinite(ts)) return '—';
  return new Date(ts * 1000).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
}

/** Ora di apertura (da entry_time ISO). Se aperta in un giorno diverso dalla
 *  chiusura, antepone la data breve così è chiaro che il trade ha scavallato. */
function fmtEntry(entryIso: string | undefined, exitTs: number | undefined): string {
  if (!entryIso) return '—';
  const d = new Date(entryIso);
  if (Number.isNaN(d.getTime())) return '—';
  const hhmm = d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
  if (exitTs != null) {
    const ex = new Date(exitTs * 1000);
    const sameDay =
      d.getFullYear() === ex.getFullYear() &&
      d.getMonth() === ex.getMonth() &&
      d.getDate() === ex.getDate();
    if (!sameDay) {
      return `${d.toLocaleDateString(undefined, { day: '2-digit', month: '2-digit' })} ${hhmm}`;
    }
  }
  return hhmm;
}

function dayKey(ts: number): string {
  const d = new Date(ts * 1000);
  return `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
}

function dayLabel(ts: number): string {
  const d = new Date(ts * 1000);
  const now = new Date();
  const startOf = (x: Date) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime();
  const diff = Math.round((startOf(now) - startOf(d)) / 86_400_000);
  const base = d.toLocaleDateString(undefined, {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
  if (diff === 0) return `Oggi · ${base}`;
  if (diff === 1) return `Ieri · ${base}`;
  return base;
}

function tradeKey(t: Trade): string {
  return t.trade_id ?? `${t.symbol}-${t.exit_ts ?? 0}`;
}

/** Etichetta + colore leggibili per l'exit_reason. `scale_out` = residuo uscito
 *  DOPO aver bancato >=1 TP (esito netto positivo) -> verde, distinto dal trailing
 *  protettivo (ambra) e dallo stop-loss pieno (rosso). */
const EXIT_LABEL: Record<string, { text: string; color: string }> = {
  take_profit: { text: 'Take profit', color: 'var(--green)' },
  scale_out: { text: 'Scale-out', color: 'var(--green)' },
  trailing_stop: { text: 'Trailing stop', color: 'var(--amber)' },
  stop_loss: { text: 'Stop loss', color: 'var(--red)' },
  time_exit: { text: 'Time exit', color: 'var(--text-dim)' },
  manual: { text: 'Manuale', color: 'var(--text-dim)' },
  kill_switch: { text: 'Kill switch', color: 'var(--text-dim)' },
  circuit_breaker: { text: 'Circuit breaker', color: 'var(--text-dim)' },
};

function exitLabel(reason: string | undefined): { text: string; color: string } {
  return EXIT_LABEL[reason ?? ''] ?? { text: reason ?? '—', color: 'var(--text-dim)' };
}

/**
 * Controfattuale: se NON fossimo usciti col trailing, cosa avrebbe toccato PRIMA
 * il prezzo — il TP configurato o lo stop-loss base? Simula sulle klines Binance
 * dall'uscita in avanti (finestra EVAL_HOURS), candela per candela in ordine.
 *   - TP per primo  -> "prematuro"  (avremmo vinto di più tenendo la posizione)
 *   - SL per primo  -> "corretto"   (tenendo saremmo finiti in stop: il trailing ha protetto)
 *   - nessuno dei due entro la finestra (completa) -> "neutro"
 */
async function evalTrailing(t: Trade): Promise<Verdict> {
  const tp = t.take_profit_price;
  const sl = t.stop_price;
  const exit = t.exit_ts;
  if (tp == null || sl == null || !Number.isFinite(tp) || !Number.isFinite(sl) || exit == null) {
    return 'unavailable';
  }
  const nowSec = Date.now() / 1000;
  const startMs = Math.floor(exit * 1000);
  const endMs = Math.floor(Math.min(nowSec, exit + EVAL_HOURS * 3600) * 1000);
  const long = t.direction?.toLowerCase() === 'long';
  try {
    const url =
      `https://fapi.binance.com/fapi/v1/klines?symbol=${encodeURIComponent(t.symbol)}` +
      `&interval=15m&startTime=${startMs}&endTime=${endMs}&limit=1500`;
    const res = await fetch(url);
    if (!res.ok) return 'unavailable';
    const kl = (await res.json()) as unknown[][];
    // klines in ordine cronologico crescente: [openTime, open, high, low, close, ...]
    for (const k of kl) {
      const high = Number(k[2]);
      const low = Number(k[3]);
      const tpHit = long ? high >= tp : low <= tp;
      const slHit = long ? low <= sl : high >= sl;
      // stessa candela colpisce entrambi: ordine intra-candela ignoto -> neutro
      if (tpHit && slHit) return 'neutral';
      if (tpHit) return 'premature';
      if (slHit) return 'protected';
    }
    // né TP né SL nella finestra: definitivo solo se la finestra è completa
    if (nowSec - exit >= EVAL_HOURS * 3600) return 'neutral';
    return 'pending';
  } catch {
    return 'unavailable';
  }
}

function VerdictBadge({ v }: { v: Verdict | undefined }) {
  if (v === 'premature') {
    return (
      <span style={{ color: 'var(--red)' }} title={`Restando in posizione il prezzo avrebbe toccato il TP entro ${EVAL_HOURS}h: il trailing ha tagliato un vincitore.`}>
        ❌ prematuro
      </span>
    );
  }
  if (v === 'protected') {
    return (
      <span style={{ color: 'var(--green)' }} title={`Restando in posizione il prezzo avrebbe toccato lo STOP LOSS entro ${EVAL_HOURS}h: il trailing ha protetto da una perdita.`}>
        ✅ corretto
      </span>
    );
  }
  if (v === 'neutral') {
    return (
      <span style={{ color: 'var(--text-dim)' }} title={`Entro ${EVAL_HOURS}h il prezzo non ha toccato né TP né SL (o li ha toccati nella stessa candela): esito indifferente.`}>
        ⚪ neutro
      </span>
    );
  }
  if (v === 'pending') {
    return <span style={{ color: 'var(--text-dim)' }} title={`Finestra di ${EVAL_HOURS}h non ancora completa.`}>in valutazione</span>;
  }
  if (v === 'unavailable') {
    return <span style={{ color: 'var(--text-dim)' }} title="TP/SL non registrati (trade vecchio) o Binance non raggiungibile dal browser.">n/d</span>;
  }
  return <span style={{ color: 'var(--text-dim)' }}>…</span>;
}

type DayGroup = { key: string; label: string; trades: Trade[]; net: number };

export default function ClosedTrades({ onSelect }: { onSelect?: (trade: Trade) => void } = {}) {
  const [rows, setRows] = useState<Trade[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [verdicts, setVerdicts] = useState<Record<string, Verdict>>({});
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [initDone, setInitDone] = useState(false);

  useEffect(() => {
    const q = query(collection(getDb(), 'trades'), orderBy('exit_ts', 'desc'), limit(MAX_TRADES));
    const unsub = onSnapshot(
      q,
      (snap) => {
        setRows(snap.docs.map((d) => d.data() as Trade));
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    return () => unsub();
  }, []);

  // raggruppa per giorno preservando l'ordine (rows già ordinate per exit_ts desc)
  const groups = useMemo<DayGroup[]>(() => {
    const map = new Map<string, DayGroup>();
    for (const t of rows) {
      const ts = t.exit_ts ?? 0;
      const key = dayKey(ts);
      let g = map.get(key);
      if (!g) {
        g = { key, label: dayLabel(ts), trades: [], net: 0 };
        map.set(key, g);
      }
      g.trades.push(t);
      g.net += t.pnl ?? 0;
    }
    return Array.from(map.values());
  }, [rows]);

  // apri di default il giorno più recente, una sola volta
  useEffect(() => {
    if (!initDone && groups.length > 0) {
      setExpanded(new Set([groups[0].key]));
      setInitDone(true);
    }
  }, [groups, initDone]);

  const toggle = (key: string) =>
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });

  // calcola i verdetti SOLO per le uscite trailing dei giorni ESPANSI, non valutate
  useEffect(() => {
    let cancelled = false;
    const todo = rows.filter(
      (t) =>
        (t.exit_reason === 'trailing_stop' || t.exit_reason === 'scale_out') &&
        !t.trailing_verdict && // se il bot ha già scritto il verdetto, non serve Binance
        expanded.has(dayKey(t.exit_ts ?? 0)) &&
        !(tradeKey(t) in verdicts),
    );
    if (todo.length === 0) return;
    (async () => {
      const results = await Promise.all(
        todo.map(async (t) => [tradeKey(t), await evalTrailing(t)] as const),
      );
      if (cancelled) return;
      setVerdicts((prev) => {
        const next = { ...prev };
        for (const [k, v] of results) next[k] = v;
        return next;
      });
    })();
    return () => {
      cancelled = true;
    };
  }, [rows, expanded, verdicts]);

  const total = rows.reduce((s, t) => s + (t.pnl ?? 0), 0);
  const cell = { padding: '6px 8px' } as const;
  // colonne della tabella meno quella del PnL (per i colSpan delle righe di gruppo)
  const COLONNE_SENZA_PNL = 10;

  return (
    <div className="panel">
      <h2>Trade chiusi</h2>
      <p className="subtitle">
        {rows.length} trade chiusi (paper) · clicca un giorno per espanderlo, un trade per vederlo sul grafico
      </p>
      {!loaded ? (
        <p className="muted">Caricamento…</p>
      ) : rows.length === 0 ? (
        <p className="muted">Nessun trade chiuso ancora (le posizioni aperte non hanno ancora toccato TP/SL).</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ textAlign: 'left', color: 'var(--text-dim)' }}>
                <th style={cell}>Aperta</th>
                <th style={cell}>Chiusa</th>
                <th style={cell}>Coin</th>
                <th style={cell}>Strategia</th>
                <th style={cell}>Lato</th>
                <th style={cell}>Uscita</th>
                <th style={cell} title="Quanti TP scaglionati raggiunti prima della chiusura">TP</th>
                <th style={cell} title="keep del profit-lock usato: quanto del massimo raggiunto si teneva">Keep</th>
                <th style={cell}>Trailing?</th>
                <th style={cell} title="il referto scritto alla chiusura: dove e' morto il trade e perche'">Referto</th>
                <th style={{ ...cell, textAlign: 'right' }}>PnL</th>
              </tr>
            </thead>
            <tbody>
              {groups.map((g) => {
                const open = expanded.has(g.key);
                return (
                  <Fragment key={g.key}>
                    <tr
                      onClick={() => toggle(g.key)}
                      style={{ cursor: 'pointer', borderTop: '2px solid var(--border)', background: 'var(--bg-elev)' }}
                    >
                      <td colSpan={COLONNE_SENZA_PNL} style={{ ...cell, fontWeight: 600 }}>
                        <span style={{ display: 'inline-block', width: 16, color: 'var(--text-dim)' }}>
                          {open ? '▾' : '▸'}
                        </span>
                        {g.label}
                        <span className="muted" style={{ marginLeft: 10, fontWeight: 400 }}>
                          {g.trades.length} trade
                        </span>
                      </td>
                      <td style={{ ...cell, textAlign: 'right', fontWeight: 700, color: g.net >= 0 ? 'var(--green)' : 'var(--red)' }}>
                        {g.net >= 0 ? '+' : ''}
                        {g.net.toFixed(2)}
                      </td>
                    </tr>
                    {open &&
                      g.trades.map((t, i) => (
                        <tr
                          key={`${g.key}-${i}`}
                          style={{ borderTop: '1px solid var(--border)', cursor: onSelect ? 'pointer' : 'default' }}
                          onClick={onSelect ? () => onSelect(t) : undefined}
                          title={onSelect ? 'Mostra sul grafico' : undefined}
                        >
                          <td style={{ ...cell, color: 'var(--text-dim)', whiteSpace: 'nowrap' }}>{fmtEntry(t.entry_time, t.exit_ts)}</td>
                          <td style={{ ...cell, color: 'var(--text-dim)', whiteSpace: 'nowrap' }}>{fmtTime(t.exit_ts)}</td>
                          <td style={{ ...cell, fontWeight: 600 }}>
                            {t.symbol}
                            {t.esplorativa ? (
                              <span
                                title="paper esplorativo: quasi-passaggio del gate, size a un quarto, fuori dai pesi delle validate"
                                style={{ marginLeft: 6, fontSize: 10, fontWeight: 600, padding: '1px 5px', borderRadius: 4, border: '1px solid var(--border)', color: 'var(--text-dim)' }}
                              >
                                espl.
                              </span>
                            ) : null}
                          </td>
                          <td style={cell}>{t.strategy}</td>
                          <td style={cell}>{t.direction}</td>
                          <td style={cell}>
                            <span style={{ color: exitLabel(t.exit_reason).color, fontWeight: 600 }}>
                              {exitLabel(t.exit_reason).text}
                            </span>
                          </td>
                          <td style={{ ...cell, whiteSpace: 'nowrap' }}>
                            {t.scale_stage_reached != null ? (
                              t.scale_stage_reached > 0 ? (
                                <span
                                  style={{ color: 'var(--green)' }}
                                  title={
                                    t.realized_partial != null
                                      ? `incassato dalle fette: ${t.realized_partial >= 0 ? '+' : ''}${t.realized_partial.toFixed(2)}`
                                      : undefined
                                  }
                                >
                                  ✓ {t.scale_stage_reached}
                                </span>
                              ) : (
                                <span style={{ color: 'var(--text-dim)' }} title="nessun TP raggiunto (uscito prima)">—</span>
                              )
                            ) : (
                              <span style={{ color: 'var(--text-dim)' }}>·</span>
                            )}
                          </td>
                          <td style={{ ...cell, whiteSpace: 'nowrap' }}>
                            {t.profit_lock_keep != null ? t.profit_lock_keep.toFixed(2) : <span style={{ color: 'var(--text-dim)' }}>·</span>}
                          </td>
                          <td style={{ ...cell, whiteSpace: 'nowrap' }}>
                            {t.exit_reason === 'trailing_stop' || t.exit_reason === 'scale_out' ? (
                              <VerdictBadge v={(t.trailing_verdict as Verdict | undefined) ?? verdicts[tradeKey(t)]} />
                            ) : null}
                          </td>
                          <td style={{ ...cell, maxWidth: 260 }}>
                            {t.post_mortem?.verdetto ? (
                              <span title={t.post_mortem.verdetto} style={{ display: 'inline-block', maxWidth: 260, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', verticalAlign: 'bottom' }}>
                                {t.post_mortem.classe ? (
                                  <span style={{ color: 'var(--text-dim)' }}>[{CLASSE_REFERTO[t.post_mortem.classe] ?? t.post_mortem.classe}] </span>
                                ) : null}
                                {t.post_mortem.verdetto}
                              </span>
                            ) : (
                              <span style={{ color: 'var(--text-dim)' }} title="trade chiuso prima dei referti (23 set)">·</span>
                            )}
                          </td>
                          <td style={{ ...cell, textAlign: 'right', color: (t.pnl ?? 0) >= 0 ? 'var(--green)' : 'var(--red)' }}>
                            {(t.pnl ?? 0).toFixed(2)}
                          </td>
                        </tr>
                      ))}
                  </Fragment>
                );
              })}
              <tr style={{ borderTop: '2px solid var(--border)', fontWeight: 700 }}>
                <td style={cell} colSpan={COLONNE_SENZA_PNL}>
                  Totale realizzato ({rows.length} trade)
                </td>
                <td style={{ ...cell, textAlign: 'right', color: total >= 0 ? 'var(--green)' : 'var(--red)' }}>
                  {total.toFixed(2)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
