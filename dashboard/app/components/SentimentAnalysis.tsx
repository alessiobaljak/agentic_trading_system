'use client';

import { useEffect, useMemo, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { collection, limit, onSnapshot, orderBy, query } from 'firebase/firestore';
import { getDb, getRtdb } from '../lib/firebase';
import type { BotStatus, ClosedTrade, Position } from '../lib/types';

/**
 * SentimentAnalysis — la fonte "sentiment" che alimenta le decisioni del bot,
 * resa visibile. SOLO LETTURA:
 *   - /bot_status.fear_greed        (Fear & Greed corrente, 0-100)
 *   - /positions                    (sentiment/F&G al momento dell'ingresso)
 *   - trades                        (sentiment/F&G all'ingresso + esito)
 * Il bot usa il Fear & Greed per il REGIME di mercato e il sentiment per-coin
 * (CoinGecko/LunarCrush) al momento di aprire. Qui vedi il valore corrente e
 * come quei livelli si sono correlati con gli esiti reali.
 */

function fgClass(v: number): { label: string; color: string } {
  if (v < 25) return { label: 'Extreme Fear', color: '#f85149' };
  if (v < 45) return { label: 'Fear', color: '#e3a92b' };
  if (v <= 55) return { label: 'Neutral', color: '#c9c94b' };
  if (v < 75) return { label: 'Greed', color: '#7ad17a' };
  return { label: 'Extreme Greed', color: '#3fb950' };
}

type Bucket = { label: string; test: (v: number) => boolean };
const FG_BUCKETS: Bucket[] = [
  { label: 'Extreme Fear', test: (v) => v < 25 },
  { label: 'Fear', test: (v) => v >= 25 && v < 45 },
  { label: 'Neutral', test: (v) => v >= 45 && v <= 55 },
  { label: 'Greed', test: (v) => v > 55 && v < 75 },
  { label: 'Extreme Greed', test: (v) => v >= 75 },
];
const SENT_BUCKETS: Bucket[] = [
  { label: 'Negativo (<0.45)', test: (v) => v < 0.45 },
  { label: 'Neutro (0.45–0.55)', test: (v) => v >= 0.45 && v <= 0.55 },
  { label: 'Positivo (>0.55)', test: (v) => v > 0.55 },
];

function bucketize(
  trades: ClosedTrade[],
  buckets: Bucket[],
  pick: (t: ClosedTrade) => number | undefined,
) {
  return buckets.map((b) => {
    const rows = trades.filter((t) => {
      const v = pick(t);
      return v != null && Number.isFinite(v) && b.test(v);
    });
    const n = rows.length;
    const wins = rows.filter((t) => t.is_win || (t.pnl ?? 0) > 0).length;
    const pnl = rows.reduce((s, t) => s + (t.pnl ?? 0), 0);
    return { label: b.label, n, winRate: n ? wins / n : 0, pnl };
  });
}

function BucketBars({
  title,
  rows,
}: {
  title: string;
  rows: { label: string; n: number; winRate: number; pnl: number }[];
}) {
  const any = rows.some((r) => r.n > 0);
  return (
    <div className="panel">
      <h2>{title}</h2>
      <p className="subtitle">Win rate dei trade chiusi, raggruppati per il livello all&apos;ingresso</p>
      {!any ? (
        <p className="muted">Ancora nessun trade con questo dato registrato.</p>
      ) : (
        <div>
          {rows.map((r) => {
            const pct = Math.round(r.winRate * 100);
            const color = r.n === 0 ? 'var(--text-faint)' : pct >= 50 ? 'var(--green)' : 'var(--red)';
            return (
              <div className="bucket-row" key={r.label}>
                <span className="b-label">{r.label}</span>
                <span className="bucket-track">
                  <span
                    className="bucket-fill"
                    style={{ width: `${r.n ? pct : 0}%`, background: color }}
                  />
                </span>
                <span className="mono" style={{ fontSize: 12, textAlign: 'right' }}>
                  {r.n ? `${pct}%` : '—'} <span className="muted">n={r.n}</span>
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function SentimentAnalysis() {
  const [status, setStatus] = useState<BotStatus | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [trades, setTrades] = useState<ClosedTrade[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const u1 = onValue(ref(getRtdb(), 'bot_status'), (s) =>
      setStatus(s.exists() ? (s.val() as BotStatus) : null),
    );
    const u2 = onValue(ref(getRtdb(), 'positions'), (s) => {
      const val = s.val() as Record<string, Position> | null;
      setPositions(
        val ? Object.entries(val).map(([sym, p]) => ({ ...p, symbol: p.symbol ?? sym })) : [],
      );
    });
    const q = query(collection(getDb(), 'trades'), orderBy('exit_ts', 'desc'), limit(500));
    const u3 = onSnapshot(
      q,
      (snap) => {
        setTrades(snap.docs.map((d) => d.data() as ClosedTrade));
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    return () => {
      u1();
      u2();
      u3();
    };
  }, []);

  const fg = status?.fear_greed;
  const fgc = fg != null ? fgClass(fg) : null;

  const fgBuckets = useMemo(() => bucketize(trades, FG_BUCKETS, (t) => t.fear_greed_at_entry), [trades]);
  const sentBuckets = useMemo(() => bucketize(trades, SENT_BUCKETS, (t) => t.sentiment_at_entry), [trades]);
  const withSent = positions.filter((p) => p.sentiment_at_entry != null);

  return (
    <>
      {/* Fear & Greed corrente */}
      <div className="panel">
        <h2>Fear &amp; Greed Index</h2>
        <p className="subtitle">
          Sentiment di mercato aggregato (0 = panico, 100 = euforia). Il bot lo usa per rilevare il
          regime di mercato.
        </p>
        {fg == null ? (
          <p className="muted">
            Valore corrente non ancora pubblicato dal bot. Comparirà qui appena il bot gira con il
            codice aggiornato (viene scritto ad ogni rilevazione del regime).
          </p>
        ) : (
          <>
            <div className="fg-hero">
              <div className="fg-num" style={{ color: fgc!.color }}>{Math.round(fg)}</div>
              <div>
                <div className="fg-cls" style={{ color: fgc!.color }}>{fgc!.label}</div>
                <div className="muted" style={{ fontSize: 12 }}>su 100 · regime attuale: {status?.regime ?? '—'}</div>
              </div>
            </div>
            <div className="fg-bar">
              <div className="fg-marker" style={{ left: `${Math.max(0, Math.min(100, fg))}%` }} />
            </div>
            <div className="fg-scale">
              <span>0 · panico</span>
              <span>50 · neutro</span>
              <span>euforia · 100</span>
            </div>
          </>
        )}
      </div>

      {/* Correlazione con gli esiti */}
      <div className="grid grid-2">
        <BucketBars title="Esiti per Fear & Greed all'ingresso" rows={fgBuckets} />
        <BucketBars title="Esiti per sentiment della coin" rows={sentBuckets} />
      </div>

      {/* Sentiment all'ingresso delle posizioni aperte */}
      <div className="panel">
        <h2>Sentiment all&apos;ingresso · posizioni aperte</h2>
        <p className="subtitle">
          Il sentiment per-coin (CoinGecko / LunarCrush) registrato quando il bot ha aperto la posizione
        </p>
        {!loaded ? (
          <p className="muted">Loading…</p>
        ) : withSent.length === 0 ? (
          <p className="muted">
            Nessuna posizione aperta con sentiment registrato. Il bot rileva il sentiment solo per la
            coin che sta per operare, al momento dell&apos;ingresso.
          </p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Side</th>
                  <th>Sentiment ingresso</th>
                  <th>F&amp;G ingresso</th>
                  <th>uPnL</th>
                </tr>
              </thead>
              <tbody>
                {withSent.map((p) => {
                  const s = p.sentiment_at_entry ?? 0;
                  const pct = Math.round(s * 100);
                  const side = (p.direction ?? '').toLowerCase();
                  const u = p.unrealized_pnl ?? 0;
                  return (
                    <tr key={p.symbol}>
                      <td><strong>{p.symbol}</strong></td>
                      <td className={side === 'long' ? 'pos' : side === 'short' ? 'neg' : ''}>
                        {p.direction ? p.direction.toUpperCase() : '—'}
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'flex-end' }}>
                          <span className="bucket-track" style={{ width: 90 }}>
                            <span
                              className="bucket-fill"
                              style={{ width: `${pct}%`, background: s >= 0.55 ? 'var(--green)' : s < 0.45 ? 'var(--red)' : 'var(--amber)' }}
                            />
                          </span>
                          <span className="mono">{s.toFixed(2)}</span>
                        </div>
                      </td>
                      <td className="mono">
                        {p.fear_greed_at_entry != null ? Math.round(p.fear_greed_at_entry) : '—'}
                      </td>
                      <td className={`mono ${u >= 0 ? 'pos' : 'neg'}`}>
                        {u >= 0 ? '+' : ''}
                        {u.toFixed(2)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
