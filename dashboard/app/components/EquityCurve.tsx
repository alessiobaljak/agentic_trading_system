'use client';

import { useEffect, useMemo, useState } from 'react';
import { collection, onSnapshot, orderBy, query } from 'firebase/firestore';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { getDb } from '../lib/firebase';
import { toMillis, type ClosedTrade } from '../lib/types';

interface Point {
  t: number;
  label: string;
  equity: number;
  pnl: number;
}

/**
 * Equity curve derived from closed trades' cumulative PnL, ordered by exit_ts.
 * The y-axis is cumulative realized PnL (starts at 0). This avoids needing a
 * separate equity-history feed; it tracks realized performance over time.
 */
export default function EquityCurve() {
  const [trades, setTrades] = useState<ClosedTrade[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const db = getDb();
    // exit_ts may not exist on every doc; we still order by it and sort client-side as a fallback.
    const q = query(collection(db, 'trades'), orderBy('exit_ts', 'asc'));
    const unsub = onSnapshot(
      q,
      (snap) => {
        setTrades(snap.docs.map((d) => d.data() as ClosedTrade));
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    return () => unsub();
  }, []);

  const data = useMemo<Point[]>(() => {
    const sorted = [...trades].sort(
      (a, b) => (toMillis(a.exit_ts) ?? 0) - (toMillis(b.exit_ts) ?? 0),
    );
    let cum = 0;
    return sorted.map((t) => {
      cum += t.pnl ?? 0;
      const ms = toMillis(t.exit_ts);
      return {
        t: ms ?? 0,
        label: ms ? new Date(ms).toLocaleDateString() : '',
        equity: Number(cum.toFixed(2)),
        pnl: t.pnl ?? 0,
      };
    });
  }, [trades]);

  const last = data.length ? data[data.length - 1].equity : 0;

  return (
    <div className="panel">
      <h2>Equity Curve</h2>
      <p className="subtitle">Cumulative realized PnL from closed trades</p>
      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : data.length === 0 ? (
        <p className="muted">No closed trades yet.</p>
      ) : (
        <>
          <div className="kpi" style={{ marginBottom: 12 }}>
            <div className="item">
              <div className="label">Cumulative PnL</div>
              <div className={`value mono ${last >= 0 ? 'pos' : 'neg'}`}>
                {last >= 0 ? '+' : ''}
                {last.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              </div>
            </div>
            <div className="item">
              <div className="label">Trades</div>
              <div className="value mono">{data.length}</div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="equityFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#4f9cf9" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="#4f9cf9" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#28303d" strokeDasharray="3 3" />
              <XAxis
                dataKey="label"
                stroke="#8b96a5"
                fontSize={11}
                tickLine={false}
                minTickGap={40}
              />
              <YAxis stroke="#8b96a5" fontSize={11} tickLine={false} width={56} />
              <Tooltip
                contentStyle={{
                  background: '#141a24',
                  border: '1px solid #28303d',
                  borderRadius: 8,
                  color: '#e6edf3',
                }}
                labelStyle={{ color: '#8b96a5' }}
                formatter={(v: number) => [v.toFixed(2), 'Cum PnL']}
              />
              <Area
                type="monotone"
                dataKey="equity"
                stroke="#4f9cf9"
                strokeWidth={2}
                fill="url(#equityFill)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  );
}
