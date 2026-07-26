'use client';

import { useEffect, useMemo, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import { getDb } from '../lib/firebase';
import type { MemoryReport } from '../lib/types';

/**
 * Win rate per strategia × regime, come pillole colorate (rosso->verde) raggruppate
 * per strategia. Reads memory/30 -> win_rate_by_strategy_regime (chiavi "strat|regime").
 */
function pillColors(v: number): { bg: string; fg: string; bd: string } {
  const x = Math.max(0, Math.min(1, v));
  const hue = x * 130; // 0 rosso -> 130 verde
  return {
    bg: `hsla(${hue}, 60%, 45%, ${0.18 + x * 0.32})`,
    fg: '#e9eef5',
    bd: `hsla(${hue}, 60%, 55%, 0.5)`,
  };
}

const REG_SHORT: Record<string, string> = {
  bull_trending: 'BULL',
  bear_trending: 'BEAR',
  sideways: 'SIDE',
};

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

  const rows = useMemo(() => {
    const map = report?.win_rate_by_strategy_regime ?? {};
    const byStrat = new Map<string, { regime: string; wr: number }[]>();
    for (const [key, val] of Object.entries(map)) {
      const [strategy, regime] = key.split('|');
      if (!strategy || !regime) continue;
      if (!byStrat.has(strategy)) byStrat.set(strategy, []);
      byStrat.get(strategy)!.push({ regime, wr: val });
    }
    // ordina le pillole per regime, e le strategie per miglior win-rate
    for (const arr of byStrat.values()) arr.sort((a, b) => a.regime.localeCompare(b.regime));
    return Array.from(byStrat.entries())
      .map(([strategy, cells]) => ({ strategy, cells }))
      .sort((a, b) => Math.max(...b.cells.map((c) => c.wr)) - Math.max(...a.cells.map((c) => c.wr)));
  }, [report]);

  return (
    <div className="panel">
      <h2>Win rate · strategia × regime</h2>
      <p className="subtitle">Da memory/30 · pillola per regime, colore = win rate (rosso → verde)</p>
      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : rows.length === 0 ? (
        <p className="muted">Nessun report di memoria disponibile ancora.</p>
      ) : (
        <div style={{ maxHeight: 380, overflowY: 'auto' }}>
          {rows.map(({ strategy, cells }) => (
            <div className="rrow" key={strategy}>
              <span className="rstrat" title={strategy}>{strategy}</span>
              {cells.map(({ regime, wr }) => {
                const c = pillColors(wr);
                return (
                  <span
                    key={regime}
                    className="rpill"
                    style={{ background: c.bg, color: c.fg, borderColor: c.bd }}
                    title={`${strategy} · ${regime}: ${(wr * 100).toFixed(0)}%`}
                  >
                    <span className="rreg">{REG_SHORT[regime] ?? regime}</span>
                    <span className="mono" style={{ fontWeight: 700 }}>{(wr * 100).toFixed(0)}%</span>
                  </span>
                );
              })}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
