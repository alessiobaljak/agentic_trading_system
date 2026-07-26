'use client';

import { useEffect, useMemo, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { collection, limit, onSnapshot, orderBy, query } from 'firebase/firestore';
import { getDb, getRtdb } from '../lib/firebase';
import { toMillis, type ClosedTrade, type Position } from '../lib/types';

/**
 * DailySnapshot — colpo d'occhio: ordini APERTI ora + aggregato dei trade
 * CHIUSI OGGI (numero, win rate, profitto, migliore/peggiore). SOLO LETTURA:
 * legge /positions (RTDB) e la collezione trades (Firestore), niente scritture.
 */
export default function DailySnapshot() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [trades, setTrades] = useState<ClosedTrade[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const unsubPos = onValue(ref(getRtdb(), 'positions'), (snap) => {
      const val = snap.val() as Record<string, Position> | null;
      const list = val
        ? Object.entries(val).map(([symbol, p]) => ({ ...p, symbol: p.symbol ?? symbol }))
        : [];
      list.sort((a, b) => (b.unrealized_pnl ?? 0) - (a.unrealized_pnl ?? 0));
      setPositions(list);
    });
    const q = query(collection(getDb(), 'trades'), orderBy('exit_ts', 'desc'), limit(500));
    const unsubTrades = onSnapshot(
      q,
      (snap) => {
        setTrades(snap.docs.map((d) => d.data() as ClosedTrade));
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    return () => {
      unsubPos();
      unsubTrades();
    };
  }, []);

  const openUpnl = positions.reduce((s, p) => s + (p.unrealized_pnl ?? 0), 0);

  const day = useMemo(() => {
    const start = new Date();
    start.setHours(0, 0, 0, 0);
    const startMs = start.getTime();
    const today = trades.filter((t) => {
      const ms = toMillis(t.exit_ts);
      return ms != null && ms >= startMs;
    });
    const n = today.length;
    const wins = today.filter((t) => t.is_win || (t.pnl ?? 0) > 0).length;
    const pnl = today.reduce((s, t) => s + (t.pnl ?? 0), 0);
    const pnls = today.map((t) => t.pnl ?? 0);
    const best = pnls.length ? Math.max(...pnls) : 0;
    const worst = pnls.length ? Math.min(...pnls) : 0;
    return { n, wins, losses: n - wins, pnl, best, worst };
  }, [trades]);

  const usd = (n: number) => `${n >= 0 ? '+' : ''}$${Math.abs(n).toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
  const winRate = day.n > 0 ? Math.round((day.wins / day.n) * 100) : null;
  const winPct = day.n > 0 ? (day.wins / day.n) * 100 : 0;

  return (
    <div className="panel">
      <h2>Snapshot di oggi</h2>
      <p className="subtitle">Ordini aperti ora e aggregato dei trade chiusi oggi · colpo d&apos;occhio</p>

      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : (
        <>
          {/* aperte ora */}
          <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))' }}>
            <div className="stat-tile accent">
              <div className="stat-label">Posizioni aperte</div>
              <div className="stat-value">{positions.length}</div>
              <div className="stat-sub">ordini attivi ora</div>
            </div>
            <div className={`stat-tile ${openUpnl >= 0 ? 'good' : 'bad'}`}>
              <div className="stat-label">uPnL aperto</div>
              <div className={`stat-value ${openUpnl >= 0 ? 'pos' : 'neg'}`}>{usd(openUpnl)}</div>
              <div className="stat-sub">non realizzato</div>
            </div>
          </div>

          {positions.length > 0 && (
            <div className="mini-list">
              {positions.slice(0, 5).map((p) => {
                const u = p.unrealized_pnl ?? 0;
                const side = (p.direction ?? '').toLowerCase();
                return (
                  <div className="mini-row" key={p.symbol}>
                    <span>
                      <span className="sym">{p.symbol}</span>{' '}
                      <span className={side === 'long' ? 'pos' : side === 'short' ? 'neg' : 'muted'} style={{ fontSize: 11 }}>
                        {p.direction ? p.direction.toUpperCase() : ''}
                      </span>{' '}
                      <span className="muted" style={{ fontSize: 11 }}>{p.strategy ?? ''}</span>
                    </span>
                    <span className={`mono ${u >= 0 ? 'pos' : 'neg'}`}>
                      {usd(u)}
                      {p.trailing_active ? ' ↑' : ''}
                    </span>
                  </div>
                );
              })}
              {positions.length > 5 && (
                <div className="muted" style={{ fontSize: 11, padding: '2px 4px' }}>
                  +{positions.length - 5} altre · vedi «Operatività»
                </div>
              )}
            </div>
          )}

          {/* chiusi oggi */}
          <div style={{ borderTop: '1px solid var(--border-soft)', margin: '16px 0 0', paddingTop: 14 }}>
            <div className="muted" style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 10 }}>
              Chiusi oggi
            </div>
            <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))' }}>
              <div className="stat-tile">
                <div className="stat-label">Trade</div>
                <div className="stat-value">{day.n}</div>
              </div>
              <div className={`stat-tile ${winRate != null && winRate >= 50 ? 'good' : winRate != null ? 'bad' : ''}`}>
                <div className="stat-label">Win rate</div>
                <div className="stat-value">{winRate != null ? `${winRate}%` : '—'}</div>
                <div className="stat-sub">{day.wins}W · {day.losses}L</div>
              </div>
              <div className={`stat-tile ${day.pnl >= 0 ? 'good' : 'bad'}`}>
                <div className="stat-label">Profitto</div>
                <div className={`stat-value ${day.pnl >= 0 ? 'pos' : 'neg'}`}>{day.n ? usd(day.pnl) : '—'}</div>
              </div>
              <div className="stat-tile">
                <div className="stat-label">Migliore / peggiore</div>
                <div className="stat-value" style={{ fontSize: 16 }}>
                  {day.n ? (
                    <>
                      <span className="pos">{usd(day.best)}</span>
                      <span className="muted"> / </span>
                      <span className="neg">{usd(day.worst)}</span>
                    </>
                  ) : (
                    '—'
                  )}
                </div>
              </div>
            </div>

            {day.n > 0 && (
              <div className="wl-bar" title={`${day.wins} vinti · ${day.losses} persi`}>
                <span className="win" style={{ width: `${winPct}%` }} />
                <span className="loss" style={{ width: `${100 - winPct}%` }} />
              </div>
            )}
            {day.n === 0 && (
              <p className="muted" style={{ fontSize: 12, marginTop: 8, marginBottom: 0 }}>
                Nessun trade chiuso oggi finora.
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
