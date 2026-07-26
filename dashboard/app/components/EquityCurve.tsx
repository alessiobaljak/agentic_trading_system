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

type RangeId = 'all' | '90d' | '30d' | '7d' | '1d';
const RANGES: { id: RangeId; label: string; ms: number }[] = [
  { id: 'all', label: 'Tutto', ms: Infinity },
  { id: '90d', label: '90g', ms: 90 * 864e5 },
  { id: '30d', label: '30g', ms: 30 * 864e5 },
  { id: '7d', label: '7g', ms: 7 * 864e5 },
  { id: '1d', label: '24h', ms: 864e5 },
];

/**
 * Equity curve derived from closed trades' cumulative PnL, ordered by exit_ts.
 * The y-axis is cumulative realized PnL (starts at 0). This avoids needing a
 * separate equity-history feed; it tracks realized performance over time.
 */
export default function EquityCurve() {
  const [trades, setTrades] = useState<ClosedTrade[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [range, setRange] = useState<RangeId>('all');

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
  // Nessuna sovrapposizione con lo Snapshot (solo oggi): qui win rate
  // complessivo, profit factor, max drawdown ed expectancy/trade.
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

  // dati del grafico filtrati per la finestra scelta (l'equity resta quella
  // reale, non azzerata: zoom sulla finestra, non ricalcolo da 0)
  const chartData = useMemo<Point[]>(() => {
    const r = RANGES.find((x) => x.id === range);
    if (!r || r.ms === Infinity) return data;
    const cutoff = Date.now() - r.ms;
    return data.filter((d) => d.t >= cutoff);
  }, [data, range]);

  const num = (v: number, d = 2) => v.toLocaleString(undefined, { maximumFractionDigits: d });

  return (
    <div className="panel">
      <h2>Equity Curve</h2>
      <p className="subtitle">PnL realizzato cumulato dai trade chiusi</p>
      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : data.length === 0 ? (
        <p className="muted">Ancora nessun trade chiuso.</p>
      ) : (
        <>
          {/* tutti i numeri sopra, su una sola riga */}
          <div className="metric-strip">
            <div className="metric">
              <span className="m-label">PnL cumulato</span>
              <span className={`m-val ${last >= 0 ? 'pos' : 'neg'}`}>
                {last >= 0 ? '+' : ''}
                {num(last)}
              </span>
            </div>
            <div className="metric">
              <span className="m-label">Trade</span>
              <span className="m-val">{data.length}</span>
            </div>
            <div className="metric">
              <span className="m-label">Win rate</span>
              <span className={`m-val ${stats.winRate >= 0.5 ? 'pos' : 'neg'}`}>
                {Math.round(stats.winRate * 100)}%
              </span>
            </div>
            <div className="metric">
              <span className="m-label">Profit factor</span>
              <span className={`m-val ${stats.pf >= 1 ? 'pos' : 'neg'}`}>
                {stats.pf === Infinity ? '∞' : num(stats.pf)}
              </span>
            </div>
            <div className="metric">
              <span className="m-label">Max drawdown</span>
              <span className="m-val neg">-{num(stats.maxDD)}</span>
            </div>
            <div className="metric">
              <span className="m-label">Expectancy</span>
              <span className={`m-val ${stats.expectancy >= 0 ? 'pos' : 'neg'}`}>
                {stats.expectancy >= 0 ? '+' : ''}
                {num(stats.expectancy)}
              </span>
            </div>
          </div>

          {/* filtro periodo del grafico */}
          <div className="toolbar" style={{ justifyContent: 'flex-end', margin: '16px 0 8px' }}>
            <span className="muted" style={{ fontSize: 12, marginRight: 'auto' }}>Periodo grafico</span>
            <div className="seg" role="tablist" aria-label="periodo">
              {RANGES.map((r) => (
                <button key={r.id} className={range === r.id ? 'on' : ''} onClick={() => setRange(r.id)}>
                  {r.label}
                </button>
              ))}
            </div>
          </div>

          {/* grafico sotto */}
          {chartData.length === 0 ? (
            <p className="muted" style={{ padding: '40px 0', textAlign: 'center' }}>
              Nessun trade chiuso in questa finestra.
            </p>
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <AreaChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="equityFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#4f9cf9" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="#4f9cf9" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#28303d" strokeDasharray="3 3" />
                <XAxis dataKey="label" stroke="#8b96a5" fontSize={11} tickLine={false} minTickGap={40} />
                <YAxis stroke="#8b96a5" fontSize={11} tickLine={false} width={56} />
                <Tooltip
                  contentStyle={{
                    background: '#141a24',
                    border: '1px solid #28303d',
                    borderRadius: 8,
                    color: '#e6edf3',
                  }}
                  labelStyle={{ color: '#8b96a5' }}
                  labelFormatter={(_label: unknown, payload?: ReadonlyArray<{ payload?: Point }>) => {
                    const t = payload?.[0]?.payload?.t;
                    return t
                      ? new Date(t).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' })
                      : '';
                  }}
                  formatter={(v: number, _name: unknown, item?: { payload?: Point }) => {
                    const pnl = item?.payload?.pnl ?? 0;
                    return [
                      `${Number(v).toFixed(2)}  (trade ${pnl >= 0 ? '+' : ''}${pnl.toFixed(2)})`,
                      'PnL cumulato',
                    ] as [string, string];
                  }}
                />
                <Area type="monotone" dataKey="equity" stroke="#4f9cf9" strokeWidth={2} fill="url(#equityFill)" />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </>
      )}
    </div>
  );
}
