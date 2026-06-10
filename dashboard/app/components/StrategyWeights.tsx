'use client';

import { useEffect, useMemo, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { getDb } from '../lib/firebase';
import type { StrategyWeightsDoc, StrategyWeight } from '../lib/types';

/**
 * Current strategy weights (0..1) as bars. Reads strategy_weights/current.
 * Each weight is a (strategy, regime) pair; we label by "strategy · regime".
 */

const REGIME_COLORS: Record<string, string> = {};
const PALETTE = ['#4f9cf9', '#3fb950', '#d29922', '#a371f7', '#f85149', '#56d4dd'];

function colorForRegime(regime: string): string {
  if (!(regime in REGIME_COLORS)) {
    REGIME_COLORS[regime] = PALETTE[Object.keys(REGIME_COLORS).length % PALETTE.length];
  }
  return REGIME_COLORS[regime];
}

export default function StrategyWeights() {
  const [doc_, setDoc] = useState<StrategyWeightsDoc | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const db = getDb();
    const unsub = onSnapshot(
      doc(db, 'strategy_weights', 'current'),
      (snap) => {
        setDoc(snap.exists() ? (snap.data() as StrategyWeightsDoc) : null);
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    return () => unsub();
  }, []);

  const data = useMemo(() => {
    const weights: StrategyWeight[] = doc_?.weights ?? [];
    return [...weights]
      .sort((a, b) => (b.weight ?? 0) - (a.weight ?? 0))
      .map((w) => ({
        name: `${w.strategy} · ${w.regime}`,
        regime: w.regime,
        weight: Number((w.weight ?? 0).toFixed(3)),
        win_rate: w.win_rate,
        sample_size: w.sample_size,
      }));
  }, [doc_]);

  return (
    <div className="panel">
      <h2>Strategy Weights</h2>
      <p className="subtitle">Current adaptive weights per strategy × regime (0..1)</p>
      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : data.length === 0 ? (
        <p className="muted">No strategy weights published yet.</p>
      ) : (
        <ResponsiveContainer width="100%" height={Math.max(220, data.length * 28)}>
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 8, right: 16, left: 8, bottom: 0 }}
          >
            <CartesianGrid stroke="#28303d" strokeDasharray="3 3" horizontal={false} />
            <XAxis type="number" domain={[0, 1]} stroke="#8b96a5" fontSize={11} tickLine={false} />
            <YAxis
              type="category"
              dataKey="name"
              stroke="#8b96a5"
              fontSize={11}
              tickLine={false}
              width={160}
            />
            <Tooltip
              cursor={{ fill: 'rgba(255,255,255,0.04)' }}
              contentStyle={{
                background: '#141a24',
                border: '1px solid #28303d',
                borderRadius: 8,
                color: '#e6edf3',
              }}
              labelStyle={{ color: '#8b96a5' }}
              formatter={(v: number, _name, item) => {
                const p = item?.payload as { win_rate?: number; sample_size?: number };
                const extra =
                  p?.win_rate != null
                    ? ` (wr ${(p.win_rate * 100).toFixed(0)}%, n=${p.sample_size ?? '?'})`
                    : '';
                return [`${v}${extra}`, 'weight'];
              }}
            />
            <Bar dataKey="weight" radius={[0, 4, 4, 0]}>
              {data.map((d, i) => (
                <Cell key={i} fill={colorForRegime(d.regime)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
