'use client';

import { useEffect, useMemo, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import { getDb } from '../lib/firebase';
import type { MemoryReport } from '../lib/types';

/**
 * Performance heatmap: strategy (rows) x regime (cols).
 * Reads memory/30 -> win_rate_by_strategy_regime, whose keys are "strategy|regime".
 * Cells are colored on a red->amber->green scale by win rate (0..1).
 */

function colorFor(v: number | undefined): { bg: string; fg: string } {
  if (v == null || !Number.isFinite(v)) return { bg: 'transparent', fg: '#8b96a5' };
  // clamp 0..1
  const x = Math.max(0, Math.min(1, v));
  // hue 0 (red) -> 130 (green)
  const hue = x * 130;
  const bg = `hsla(${hue}, 65%, 45%, ${0.25 + x * 0.5})`;
  return { bg, fg: '#e6edf3' };
}

export default function Heatmap() {
  const [report, setReport] = useState<MemoryReport | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const db = getDb();
    const unsub = onSnapshot(
      doc(db, 'memory', '30'),
      (snap) => {
        setReport(snap.exists() ? (snap.data() as MemoryReport) : null);
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    return () => unsub();
  }, []);

  const { strategies, regimes, cells } = useMemo(() => {
    const map = report?.win_rate_by_strategy_regime ?? {};
    const stratSet = new Set<string>();
    const regimeSet = new Set<string>();
    const cellMap = new Map<string, number>();
    for (const [key, val] of Object.entries(map)) {
      const [strategy, regime] = key.split('|');
      if (!strategy || !regime) continue;
      stratSet.add(strategy);
      regimeSet.add(regime);
      cellMap.set(`${strategy}|${regime}`, val);
    }
    return {
      strategies: Array.from(stratSet).sort(),
      regimes: Array.from(regimeSet).sort(),
      cells: cellMap,
    };
  }, [report]);

  return (
    <div className="panel">
      <h2>Strategy × Regime Win Rate</h2>
      <p className="subtitle">From memory/30 · win rate per strategy in each market regime</p>
      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : strategies.length === 0 ? (
        <p className="muted">No memory report available yet.</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>Strategy</th>
                {regimes.map((r) => (
                  <th key={r} style={{ textAlign: 'center' }}>
                    {r}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {strategies.map((s) => (
                <tr key={s}>
                  <td>
                    <strong>{s}</strong>
                  </td>
                  {regimes.map((r) => {
                    const v = cells.get(`${s}|${r}`);
                    const { bg, fg } = colorFor(v);
                    return (
                      <td key={r} style={{ padding: 4, textAlign: 'center' }}>
                        <div className="heatmap-cell" style={{ background: bg, color: fg }}>
                          {v != null ? `${(v * 100).toFixed(0)}%` : '—'}
                        </div>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
