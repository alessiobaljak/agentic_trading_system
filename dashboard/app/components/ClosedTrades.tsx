'use client';

import { useEffect, useState } from 'react';
import { collection, limit, onSnapshot, orderBy, query } from 'firebase/firestore';
import { getDb } from '../lib/firebase';

/**
 * Trade chiusi (Firestore `trades`), ordinati per uscita. Mostra PnL e motivo.
 * Per le uscite `trailing_stop` calcola un VERDETTO controfattuale: dopo l'uscita
 * il prezzo avrebbe poi raggiunto il TP configurato? Se sì il trailing ha tagliato
 * un vincitore ("prematuro"); se no ha protetto un'inversione ("corretto").
 * Il verdetto usa le klines Binance lato browser: se Binance non è raggiungibile
 * (geo-block/CORS) degrada a "n/d" senza rompere nulla.
 */
type Trade = {
  trade_id?: string;
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
};

type Verdict = 'premature' | 'correct' | 'pending' | 'unavailable';

const EVAL_HOURS = 24; // finestra dopo l'uscita entro cui cerchiamo il TP

/** exit_ts è un timestamp Unix in SECONDI (trade.exit_time.timestamp()). */
function fmtDate(ts: number | undefined): string {
  if (ts == null || !Number.isFinite(ts)) return '—';
  return new Date(ts * 1000).toLocaleString(undefined, {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function tradeKey(t: Trade): string {
  return t.trade_id ?? `${t.symbol}-${t.exit_ts ?? 0}`;
}

/**
 * Il prezzo ha toccato il TP entro EVAL_HOURS dall'uscita?
 * Ritorna il verdetto controfattuale sul trailing.
 */
async function evalTrailing(t: Trade): Promise<Verdict> {
  const tp = t.take_profit_price;
  const exit = t.exit_ts;
  if (tp == null || !Number.isFinite(tp) || exit == null) return 'unavailable';
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
    // kline: [openTime, open, high, low, close, ...] -> high=2, low=3
    const touched = kl.some((k) => {
      const high = Number(k[2]);
      const low = Number(k[3]);
      return long ? high >= tp : low <= tp;
    });
    if (touched) return 'premature';
    // TP mai raggiunto: verdetto definitivo solo se la finestra è completa
    if (nowSec - exit >= EVAL_HOURS * 3600) return 'correct';
    return 'pending';
  } catch {
    return 'unavailable';
  }
}

function VerdictBadge({ v }: { v: Verdict | undefined }) {
  if (v === 'premature') {
    return (
      <span style={{ color: '#f85149' }} title={`Il prezzo ha raggiunto il TP entro ${EVAL_HOURS}h: il trailing ha tagliato un vincitore.`}>
        ❌ prematuro
      </span>
    );
  }
  if (v === 'correct') {
    return (
      <span style={{ color: '#3fb950' }} title={`Il prezzo NON ha raggiunto il TP entro ${EVAL_HOURS}h: il trailing ha protetto.`}>
        ✅ corretto
      </span>
    );
  }
  if (v === 'pending') {
    return <span style={{ color: '#8b96a5' }} title={`Finestra di ${EVAL_HOURS}h non ancora completa.`}>in valutazione</span>;
  }
  if (v === 'unavailable') {
    return <span style={{ color: '#8b96a5' }} title="TP non registrato o Binance non raggiungibile dal browser.">n/d</span>;
  }
  return <span style={{ color: '#8b96a5' }}>…</span>;
}

export default function ClosedTrades() {
  const [rows, setRows] = useState<Trade[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [verdicts, setVerdicts] = useState<Record<string, Verdict>>({});

  useEffect(() => {
    const q = query(collection(getDb(), 'trades'), orderBy('exit_ts', 'desc'), limit(30));
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

  // calcola i verdetti per le sole uscite trailing_stop non ancora valutate
  useEffect(() => {
    let cancelled = false;
    const todo = rows.filter(
      (t) => t.exit_reason === 'trailing_stop' && !(tradeKey(t) in verdicts),
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
  }, [rows, verdicts]);

  const total = rows.reduce((s, t) => s + (t.pnl ?? 0), 0);

  return (
    <div className="panel">
      <h2>Closed Trades</h2>
      <p className="subtitle">Ultimi trade chiusi (paper) · PnL realizzato · verdetto trailing</p>
      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : rows.length === 0 ? (
        <p className="muted">Nessun trade chiuso ancora (le posizioni aperte non hanno ancora toccato TP/SL).</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ textAlign: 'left', color: '#8b96a5' }}>
                <th style={{ padding: '6px 8px' }}>Data</th>
                <th style={{ padding: '6px 8px' }}>Coin</th>
                <th style={{ padding: '6px 8px' }}>Strategia</th>
                <th style={{ padding: '6px 8px' }}>Side</th>
                <th style={{ padding: '6px 8px' }}>Uscita</th>
                <th style={{ padding: '6px 8px' }}>Trailing?</th>
                <th style={{ padding: '6px 8px', textAlign: 'right' }}>PnL</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((t, i) => (
                <tr key={i} style={{ borderTop: '1px solid #28303d' }}>
                  <td style={{ padding: '6px 8px', color: '#8b96a5', whiteSpace: 'nowrap' }}>{fmtDate(t.exit_ts)}</td>
                  <td style={{ padding: '6px 8px', fontWeight: 600 }}>{t.symbol}</td>
                  <td style={{ padding: '6px 8px' }}>{t.strategy}</td>
                  <td style={{ padding: '6px 8px' }}>{t.direction}</td>
                  <td style={{ padding: '6px 8px', color: '#8b96a5' }}>{t.exit_reason}</td>
                  <td style={{ padding: '6px 8px', whiteSpace: 'nowrap' }}>
                    {t.exit_reason === 'trailing_stop' ? <VerdictBadge v={verdicts[tradeKey(t)]} /> : null}
                  </td>
                  <td
                    style={{
                      padding: '6px 8px',
                      textAlign: 'right',
                      color: (t.pnl ?? 0) >= 0 ? '#3fb950' : '#f85149',
                    }}
                  >
                    {(t.pnl ?? 0).toFixed(2)}
                  </td>
                </tr>
              ))}
              <tr style={{ borderTop: '2px solid #28303d', fontWeight: 700 }}>
                <td style={{ padding: '6px 8px' }} colSpan={6}>
                  Totale realizzato
                </td>
                <td
                  style={{ padding: '6px 8px', textAlign: 'right', color: total >= 0 ? '#3fb950' : '#f85149' }}
                >
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
