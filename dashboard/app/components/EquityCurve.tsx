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

  // Metriche di performance ALL-TIME derivate dagli stessi trade chiusi.
  // Nessuna sovrapposizione con lo Snapshot (solo oggi) o con l'header
  // (PnL cumulato + n trade): qui win rate complessivo, profit factor,
  // max drawdown (peak-to-valley del PnL cumulato) ed expectancy/trade.
  const stats = useMemo(() => {
    const pnls = data.map((d) => d.pnl);
    const n = pnls.length;
    const wins = pnls.filter((v) => v > 0);
    const losses = pnls.filter((v) => v < 0);
    const grossWin = wins.reduce((s, v) => s + v, 0);
    const grossLoss = Math.abs(losses.reduce((s, v) => s + v, 0));
    const winRate = n ? wins.length / n : 0;
    const pf = grossLoss > 0 ? grossWin / grossLoss : grossWin > 0 ? Infinity : 0;
    const expectancy = n ? pnls.reduce((s, v) => s + v, 0) / n : 0;
    let peak = -Infinity;
    let maxDD = 0;
    for (const d of data) {
      if (d.equity > peak) peak = d.equity;
      const dd = peak - d.equity;
      if (dd > maxDD) maxDD = dd;
    }
    return { n, winRate, pf, expectancy, maxDD };
  }, [data]);

  const num = (v: number, d = 2) =>
    v.toLocaleString(undefined, { maximumFractionDigits: d });

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

          {/* metriche all-time: riempiono lo spazio senza duplicare l'header/Snapshot */}
          <div
            className="stat-grid"
            style={{ marginTop: 16, gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))' }}
          >
            <div className={`stat-tile ${stats.winRate >= 0.5 ? 'good' : 'bad'}`}>
              <div className="stat-label">Win rate</div>
              <div className="stat-value">{Math.round(stats.winRate * 100)}%</div>
              <div className="stat-sub">complessivo · {stats.n} trade</div>
            </div>
            <div className={`stat-tile ${stats.pf >= 1 ? 'good' : 'bad'}`}>
              <div className="stat-label">Profit factor</div>
              <div className="stat-value">
                {stats.pf === Infinity ? '∞' : num(stats.pf)}
              </div>
              <div className="stat-sub">profitti lordi / perdite lorde</div>
            </div>
            <div className="stat-tile bad">
              <div className="stat-label">Max drawdown</div>
              <div className="stat-value neg">-{num(stats.maxDD)}</div>
              <div className="stat-sub">calo max dal picco</div>
            </div>
            <div className={`stat-tile ${stats.expectancy >= 0 ? 'good' : 'bad'}`}>
              <div className="stat-label">Expectancy</div>
              <div className={`stat-value ${stats.expectancy >= 0 ? 'pos' : 'neg'}`}>
                {stats.expectancy >= 0 ? '+' : ''}
                {num(stats.expectancy)}
              </div>
              <div className="stat-sub">PnL medio / trade</div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
