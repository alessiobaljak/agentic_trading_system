'use client';

import { useEffect, useMemo, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import { getDb } from '../lib/firebase';

/**
 * Strategie ottimizzate (walk-forward) lette da strategy_params/current.
 * Mostra le coppie (coin · strategia) che hanno passato la validazione
 * out-of-sample, con parametri e metriche. È il "report senza copia-incolla":
 * tutto ciò che il job autonomo produce appare qui.
 */
type Entry = {
  symbol: string;
  strategy: string;
  params: Record<string, unknown>;
  oos_pf: number;
  oos_pnl_pct: number;
  oos_trades: number;
  oos_win_rate: number;
  passed: boolean;
};
type Doc = { updated_at?: number; entries?: Record<string, Entry>; passed?: string[] };

export default function OptimizedStrategies() {
  const [d, setD] = useState<Doc | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const unsub = onSnapshot(
      doc(getDb(), 'strategy_params', 'current'),
      (snap) => {
        setD(snap.exists() ? (snap.data() as Doc) : null);
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    return () => unsub();
  }, []);

  const rows = useMemo(() => {
    const entries = Object.values(d?.entries ?? {});
    return entries
      .filter((e) => e.passed)
      .sort((a, b) => (b.oos_pnl_pct ?? 0) - (a.oos_pnl_pct ?? 0));
  }, [d]);

  const updated = d?.updated_at ? new Date(d.updated_at * 1000).toLocaleString() : null;

  return (
    <div className="panel">
      <h2>Strategie ottimizzate (auto)</h2>
      <p className="subtitle">
        Coppie coin × strategia validate out-of-sample (al netto fee). Ri-ottimizzate ogni notte.
        {updated ? ` · aggiornato: ${updated}` : ''}
      </p>
      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : rows.length === 0 ? (
        <p className="muted">Nessuna strategia validata ancora (job non ancora eseguito o nessuna passata).</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ textAlign: 'left', color: '#8b96a5' }}>
                <th style={{ padding: '6px 8px' }}>Coin</th>
                <th style={{ padding: '6px 8px' }}>Strategia</th>
                <th style={{ padding: '6px 8px' }}>PF</th>
                <th style={{ padding: '6px 8px' }}>PnL OOS</th>
                <th style={{ padding: '6px 8px' }}>Trade</th>
                <th style={{ padding: '6px 8px' }}>Win</th>
                <th style={{ padding: '6px 8px' }}>Parametri</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((e) => (
                <tr key={`${e.symbol}|${e.strategy}`} style={{ borderTop: '1px solid #28303d' }}>
                  <td style={{ padding: '6px 8px', fontWeight: 600 }}>{e.symbol}</td>
                  <td style={{ padding: '6px 8px' }}>{e.strategy}</td>
                  <td style={{ padding: '6px 8px' }}>{e.oos_pf?.toFixed(2)}</td>
                  <td style={{ padding: '6px 8px', color: e.oos_pnl_pct >= 0 ? '#3fb950' : '#f85149' }}>
                    {(e.oos_pnl_pct * 100).toFixed(0)}%
                  </td>
                  <td style={{ padding: '6px 8px' }}>{e.oos_trades}</td>
                  <td style={{ padding: '6px 8px' }}>{(e.oos_win_rate * 100).toFixed(0)}%</td>
                  <td style={{ padding: '6px 8px', color: '#8b96a5', fontSize: 11 }}>
                    {Object.entries(e.params ?? {})
                      .map(([k, v]) => `${k}=${v}`)
                      .join(', ')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
