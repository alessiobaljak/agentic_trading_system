'use client';

import { useEffect, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { getRtdb } from '../lib/firebase';
import type { Position } from '../lib/types';

function fmt(n: number | undefined, digits = 2): string {
  if (n == null || !Number.isFinite(n)) return '—';
  return n.toLocaleString(undefined, { maximumFractionDigits: digits });
}

export default function Positions() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const db = getRtdb();
    const unsub = onValue(ref(db, 'positions'), (snap) => {
      const val = snap.val() as Record<string, Position> | null;
      const list = val
        ? Object.entries(val).map(([symbol, p]) => ({ ...p, symbol: p.symbol ?? symbol }))
        : [];
      list.sort((a, b) => (a.symbol > b.symbol ? 1 : -1));
      setPositions(list);
      setLoaded(true);
    });
    return () => unsub();
  }, []);

  const totalUpnl = positions.reduce((acc, p) => acc + (p.unrealized_pnl ?? 0), 0);

  return (
    <div className="panel">
      <h2>Open Positions</h2>
      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : positions.length === 0 ? (
        <p className="muted">No open positions.</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Strategy</th>
                <th>Side</th>
                <th>Entry</th>
                <th>Mark</th>
                <th>Qty</th>
                <th>Lev</th>
                <th>Stop</th>
                <th>TP</th>
                <th>uPnL</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((p) => {
                const upnl = p.unrealized_pnl ?? 0;
                const side = (p.direction ?? '').toLowerCase();
                return (
                  <tr key={p.symbol}>
                    <td>
                      <strong>{p.symbol}</strong>
                      {p.dry_run ? <span className="badge amber" style={{ marginLeft: 6 }}>sim</span> : null}
                    </td>
                    <td className="muted">{p.strategy ?? '—'}</td>
                    <td className={side === 'long' ? 'pos' : side === 'short' ? 'neg' : ''}>
                      {p.direction ? p.direction.toUpperCase() : '—'}
                    </td>
                    <td className="mono">{fmt(p.entry_price, 4)}</td>
                    <td className="mono">{fmt(p.mark_price, 4)}</td>
                    <td className="mono">{fmt(p.quantity, 4)}</td>
                    <td className="mono">{p.leverage != null ? `${p.leverage}x` : '—'}</td>
                    <td className="mono">{fmt(p.stop_price, 4)}</td>
                    <td className="mono">{fmt(p.take_profit_price, 4)}</td>
                    <td className={`mono ${upnl >= 0 ? 'pos' : 'neg'}`}>
                      {upnl >= 0 ? '+' : ''}
                      {fmt(upnl)}
                      {p.trailing_active ? ' ↑' : ''}
                    </td>
                  </tr>
                );
              })}
            </tbody>
            <tfoot>
              <tr>
                <td colSpan={9} style={{ textAlign: 'right', fontWeight: 600 }}>
                  Total unrealized PnL
                </td>
                <td className={`mono ${totalUpnl >= 0 ? 'pos' : 'neg'}`} style={{ fontWeight: 700 }}>
                  {totalUpnl >= 0 ? '+' : ''}
                  {fmt(totalUpnl)}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      )}
    </div>
  );
}
